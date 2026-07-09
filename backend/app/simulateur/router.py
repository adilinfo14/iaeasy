import asyncio
import csv
import json
import re
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..catalogue.runners.vision_runner import run_detection
from ..core.ollama_client import ollama

router = APIRouter(prefix="/simulateur", tags=["simulateur"])

# Tailles approximatives en milliards de paramètres — chiffres publics arrondis, à but
# uniquement pédagogique (l'estimation d'énergie qui en découle est une approximation
# proportionnelle, PAS une mesure réelle de consommation).
_MODELES = [
    {"id": "gemma2:2b", "nom": "Gemma 2 (2B)", "parametres_milliards": 2.0},
    {"id": "llama3.2:3b", "nom": "Llama 3.2 (3B)", "parametres_milliards": 3.2},
    {"id": "phi3:mini", "nom": "Phi-3 Mini", "parametres_milliards": 3.8},
    {"id": "deepseek-coder:6.7b", "nom": "DeepSeek Coder (6.7B)", "parametres_milliards": 6.7},
    {"id": "mistral:7b-instruct", "nom": "Mistral 7B Instruct", "parametres_milliards": 7.0},
    {"id": "qwen2.5:7b-instruct", "nom": "Qwen 2.5 7B Instruct", "parametres_milliards": 7.6},
    {"id": "llama3:8b", "nom": "Llama 3 (8B)", "parametres_milliards": 8.0},
]

_PROMPT_DEFAUT = "Explique en 3 phrases ce qu'est la garantie décennale."
_LONGUEUR_MAX_PROMPT = 300
_IDS_AUTORISES = {m["id"] for m in _MODELES}

# La comparaison LLM interroge plusieurs modèles L'UN APRÈS L'AUTRE avant de renvoyer une seule
# réponse JSON complète — sur un choix de plusieurs modèles, le total peut dépasser le délai
# d'inactivité du tunnel Cloudflare (aucun octet renvoyé pendant la génération), qui coupe alors
# la connexion côté client (observé en production : `POST /comparer` en 499 sur nginx, aussi bien
# desktop que mobile). Fix : job en tâche de fond + flux SSE, un événement par modèle terminé, sur
# le même principe déjà utilisé par le module Entraînement (voir training/router.py `/stream`).
_comparer_jobs: dict[str, dict] = {}
_MAX_COMPARER_JOBS_CONCURRENTS = 3
_MAX_COMPARER_JOBS_CONSERVES = 50

# --- Fiche technique par modèle : informations PUBLIQUES connues (éditeur, licence de repli,
# spécialisation...), utilisées seulement quand Ollama ne les expose pas lui-même via /api/show
# (le license/contexte/quantization RÉELS de cette installation sont toujours préférés — voir
# _fiche_modele ci-dessous). Informatif, à jour au moment de la rédaction, non garanti à 100%.
_FICHE_EDITEUR = {
    "gemma2:2b": {
        "editeur": "Google DeepMind",
        "licence_repli": "Gemma Terms of Use",
        "annee_sortie": 2024,
        "specialisation": "Généraliste compact",
        "multilingue": "Principalement anglais",
        "function_calling": False,
    },
    "llama3.2:3b": {
        "editeur": "Meta",
        "licence_repli": "Llama 3.2 Community License",
        "annee_sortie": 2024,
        "specialisation": "Généraliste multilingue, optimisé edge/mobile",
        "multilingue": "8 langues officielles (dont le français)",
        "function_calling": True,
    },
    "phi3:mini": {
        "editeur": "Microsoft",
        "licence_repli": "MIT",
        "annee_sortie": 2024,
        "specialisation": "Raisonnement compact",
        "multilingue": "Principalement anglais",
        "function_calling": False,
    },
    "deepseek-coder:6.7b": {
        "editeur": "DeepSeek AI",
        "licence_repli": "DeepSeek License (usage commercial autorisé)",
        "annee_sortie": 2023,
        "specialisation": "Génération de code",
        "multilingue": "Anglais et chinois, français non prioritaire",
        "function_calling": False,
    },
    "mistral:7b-instruct": {
        "editeur": "Mistral AI",
        "licence_repli": "Apache 2.0",
        "annee_sortie": 2023,
        "specialisation": "Généraliste, bon support du français",
        "multilingue": "Français, anglais, allemand, espagnol, italien",
        "function_calling": True,
    },
    "qwen2.5:7b-instruct": {
        "editeur": "Alibaba Cloud (équipe Qwen)",
        "licence_repli": "Apache 2.0",
        "annee_sortie": 2024,
        "specialisation": "Généraliste, bon suivi d'instructions",
        "multilingue": "29 langues déclarées",
        "function_calling": True,
    },
    "llama3:8b": {
        "editeur": "Meta",
        "licence_repli": "Llama 3 Community License",
        "annee_sortie": 2024,
        "specialisation": "Généraliste",
        "multilingue": "Principalement anglais",
        "function_calling": False,
    },
}

# Bits par poids selon la quantization GGUF réellement utilisée (valeurs approximatives connues,
# pour une estimation de RAM nécessaire — PAS une mesure réelle de consommation mémoire).
_BITS_PAR_QUANTIZATION = {
    "Q2_K": 2.6,
    "Q3_K_M": 3.9,
    "Q4_0": 4.5,
    "Q4_K_S": 4.6,
    "Q4_K_M": 4.8,
    "Q5_0": 5.5,
    "Q5_K_M": 5.7,
    "Q6_K": 6.6,
    "Q8_0": 8.5,
    "F16": 16.0,
}

_CAS_USAGE_PAR_SPECIALISATION = {
    "Génération de code": ["Code", "Automatisation"],
    "Généraliste, bon support du français": ["Rédaction professionnelle", "Généraliste"],
    "Généraliste, bon suivi d'instructions": ["Rédaction", "Généraliste", "Raisonnement"],
    "Généraliste multilingue, optimisé edge/mobile": ["Généraliste léger", "Usage mobile"],
    "Raisonnement compact": ["Raisonnement", "Usage léger"],
    "Généraliste compact": ["Usage léger", "Tests rapides"],
    "Généraliste": ["Généraliste"],
}

_MODELE_JUGE = "qwen2.5:7b-instruct"

_show_cache: dict[str, dict] = {}
_tags_cache: list[dict] | None = None


async def _fiche_modele(model_id: str) -> dict:
    """Fiche technique : privilégie systématiquement les données RÉELLES de cette installation
    Ollama (/api/show, /api/tags) sur toute donnée publique de repli — évite d'afficher un chiffre
    inventé quand la vraie valeur est directement mesurable sur le serveur."""
    if model_id not in _show_cache:
        try:
            _show_cache[model_id] = await ollama.show(model_id)
        except Exception:  # noqa: BLE001 — dégrade sur la fiche publique plutôt que planter
            _show_cache[model_id] = {}
    show = _show_cache[model_id]
    details = show.get("details", {})
    mi = show.get("model_info", {})

    global _tags_cache
    if _tags_cache is None:
        try:
            _tags_cache = await ollama.list_models()
        except Exception:  # noqa: BLE001
            _tags_cache = []
    tag_entry = next((m for m in _tags_cache if m.get("name") == model_id), None)
    poids_fichier_go = round(tag_entry["size"] / 1e9, 2) if tag_entry and tag_entry.get("size") else None

    contexte = next((v for k, v in mi.items() if k.endswith(".context_length")), None)
    nb_couches = next((v for k, v in mi.items() if k.endswith(".block_count")), None)
    param_count = mi.get("general.parameter_count")
    quantization = details.get("quantization_level")
    bits_par_poids = _BITS_PAR_QUANTIZATION.get(quantization, 5.5)
    estimation_ram_go = round(param_count * bits_par_poids / 8 / 1e9, 1) if param_count else None

    repli = _FICHE_EDITEUR.get(model_id, {})
    specialisation = repli.get("specialisation", "Généraliste")

    return {
        "parametres_reels_milliards": round(param_count / 1e9, 2) if param_count else None,
        "quantization": quantization,
        "format_fichier": details.get("format"),
        "nb_couches": nb_couches,
        "fenetre_contexte_tokens": contexte,
        "poids_fichier_go": poids_fichier_go,
        "estimation_ram_go": estimation_ram_go,
        "editeur": repli.get("editeur", "Non renseigné"),
        "licence": mi.get("general.license") or repli.get("licence_repli", "Non renseignée"),
        "annee_sortie": repli.get("annee_sortie"),
        "specialisation": specialisation,
        "multilingue": repli.get("multilingue", "Non précisé"),
        "function_calling": repli.get("function_calling", False),
        "cas_usage_recommandes": _CAS_USAGE_PAR_SPECIALISATION.get(specialisation, ["Généraliste"]),
    }


_MOTS_ANGLAIS_COURANTS = {
    "the", "is", "and", "of", "to", "in", "for", "with", "this", "that", "you", "your", "are", "was",
}
_MARQUEURS_INCERTITUDE = [
    "peut-être", "je pense", "je ne suis pas sûr", "il se peut", "probablement",
    "sans certitude", "dans certains cas", "il semblerait",
]


def _analyser_reponse(texte: str, prompt: str) -> dict:
    """Analyse purement déterministe du texte généré (aucun appel modèle) : longueur, structure,
    diversité lexicale, cohérence avec le prompt — des heuristiques simples, pas des métriques
    linguistiques validées scientifiquement, mais utiles pour comparer objectivement des réponses."""
    phrases = [p.strip() for p in re.split(r"[.!?]+", texte) if p.strip()]
    mots = re.findall(r"[a-zA-Zàâäéèêëïîôöùûüÿçœæ]+", texte.lower())
    nb_mots = len(mots)
    nb_phrases = max(len(phrases), 1)
    diversite = round(100 * len(set(mots)) / nb_mots) if nb_mots else 0

    proportion_anglais = (
        sum(1 for m in mots if m in _MOTS_ANGLAIS_COURANTS) / nb_mots if nb_mots else 0
    )

    contient_chiffres = bool(re.search(r"\d", texte))
    contient_liste = bool(re.search(r"(^|\n)\s*[-*•]|\n\s*\d+[.)]", texte))
    nb_marqueurs = sum(texte.lower().count(m) for m in _MARQUEURS_INCERTITUDE)
    semble_tronquee = len(texte.strip()) > 50 and texte.strip()[-1] not in ".!?»\"'"

    match_longueur = re.search(r"(\d+)\s*phrases?", prompt.lower())
    respect_longueur = None
    if match_longueur:
        respect_longueur = abs(nb_phrases - int(match_longueur.group(1))) <= 1

    mots_prompt = set(re.findall(r"[a-zA-Zàâäéèêëïîôöùûüÿçœæ]{4,}", prompt.lower()))
    mots_reponse = {m for m in mots if len(m) >= 4}
    coherence = round(100 * len(mots_prompt & mots_reponse) / len(mots_prompt)) if mots_prompt else None

    longueur_moyenne_phrase = round(nb_mots / nb_phrases, 1)
    disclaimer_ia = bool(re.search(r"en tant qu.?ia|je suis une ia|je suis un mod[eè]le", texte.lower()))

    return {
        "nb_mots": nb_mots,
        "nb_phrases": nb_phrases,
        "longueur_moyenne_phrase_mots": longueur_moyenne_phrase,
        "diversite_lexicale_pourcent": diversite,
        "langue_correcte": proportion_anglais < 0.08,
        "contient_donnees_chiffrees": contient_chiffres,
        "contient_liste_structuree": contient_liste,
        "nb_marqueurs_incertitude": nb_marqueurs,
        "reponse_semble_tronquee": semble_tronquee,
        "respect_longueur_demandee": respect_longueur,
        "coherence_avec_prompt_pourcent": coherence,
        "presence_disclaimer_ia": disclaimer_ia,
    }


async def _juger_reponse(prompt: str, reponse: str) -> dict | None:
    """Évaluation qualitative par un modèle arbitre (qwen2.5:7b-instruct) — seul axe de cette
    fiche qui n'est pas une mesure ou un fait objectif, donc à prendre comme un avis parmi
    d'autres, pas une vérité absolue (surtout quand le modèle jugé est le juge lui-même)."""
    instruction = (
        "Tu es un évaluateur neutre. Note la réponse suivante à la question donnée, sur 5 axes, "
        "de 1 (très faible) à 5 (excellent). Réponds UNIQUEMENT avec un objet JSON valide, sans "
        "aucun texte autour, exactement au format : "
        '{"pertinence": 0, "clarte": 0, "concision": 0, "exactitude_percue": 0, '
        '"ton_professionnel": 0, "recommande": true, "justification": "une phrase"}\n\n'
        f"Question posée : {prompt}\n\nRéponse à évaluer : {reponse[:400]}"
    )
    try:
        brut = await ollama.generate(_MODELE_JUGE, instruction)
        match = re.search(r"\{.*\}", brut, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group(0))
        return {
            "score_pertinence": int(data.get("pertinence", 0)),
            "score_clarte": int(data.get("clarte", 0)),
            "score_concision": int(data.get("concision", 0)),
            "score_exactitude_percue": int(data.get("exactitude_percue", 0)),
            "score_ton_professionnel": int(data.get("ton_professionnel", 0)),
            "recommande_par_le_juge": bool(data.get("recommande", False)),
            "justification_juge": str(data.get("justification", ""))[:300],
        }
    except Exception:  # noqa: BLE001 — dégrade sans juge plutôt que planter la comparaison
        return None


def _niveau_materiel(params_milliards: float | None) -> str:
    if params_milliards is None:
        return "Non déterminé"
    if params_milliards < 4:
        return "Léger (CPU modeste, mini-PC)"
    if params_milliards < 8:
        return "Moyen (CPU multicœur récent)"
    return "Conséquent (serveur dédié recommandé)"


def _verdict_global(juge: dict | None, duree: float) -> str:
    if juge is None:
        return "Évaluation qualitative indisponible pour cette réponse — jugez directement sur le texte affiché ci-dessous."
    score_moyen = (
        juge["score_pertinence"] + juge["score_clarte"] + juge["score_concision"]
        + juge["score_exactitude_percue"] + juge["score_ton_professionnel"]
    ) / 5
    if juge["recommande_par_le_juge"] and score_moyen >= 3.5 and duree < 15:
        return "Bon compromis qualité/rapidité pour un usage professionnel courant."
    if juge["recommande_par_le_juge"] and score_moyen >= 3.5:
        return "Bonne qualité perçue, mais plus lent à répondre — à réserver aux tâches non urgentes."
    if score_moyen < 2.5:
        return "Qualité perçue limitée sur ce prompt précis — à réserver à des tâches simples."
    return "Résultat correct, sans avantage déterminant sur ce prompt précis."

# Les 3 modèles d'embeddings du Catalogue — comparables entre eux sur la durée et le score de
# similarité, contrairement aux LLM génératifs, mais selon une mécanique différente (2 phrases
# à comparer plutôt qu'un prompt libre).
_MODELES_EMBEDDINGS = [
    {"id": "all-minilm", "nom": "All-MiniLM", "parametres_millions": 23},
    {"id": "nomic-embed-text", "nom": "Nomic Embed Text", "parametres_millions": 137},
    {"id": "mxbai-embed-large", "nom": "Mxbai Embed Large", "parametres_millions": 335},
]
_IDS_EMBEDDINGS_AUTORISES = {m["id"] for m in _MODELES_EMBEDDINGS}
_PHRASE_A_DEFAUT = "Le chat dort sur le canapé."
_PHRASE_B_DEFAUT = "Un félin fait la sieste sur le sofa."
_LONGUEUR_MAX_PHRASE = 300

# 4 algorithmes "classiques" (pas de réseau de neurones), entraînés en direct sur le même
# petit jeu de données (spam/légitime, déjà utilisé par le module Entraînement) — comparables
# sur la durée d'entraînement et la précision, contrairement à un LLM qu'on interroge sans
# jamais l'entraîner soi-même.
_MODELES_CLASSIFICATION = [
    {"id": "regression_logistique", "nom": "Régression logistique"},
    {"id": "arbre_decision", "nom": "Arbre de décision"},
    {"id": "naive_bayes", "nom": "Naïve Bayes"},
    {"id": "knn", "nom": "K plus proches voisins (k=3)"},
]
_IDS_CLASSIFICATION_AUTORISEES = {m["id"] for m in _MODELES_CLASSIFICATION}
_DATASET_SPAM = Path(__file__).resolve().parent.parent / "training" / "datasets" / "toy_spam_fr.csv"
_MESSAGE_CLASSIFICATION_DEFAUT = "Cliquez ici pour gagner un iPhone gratuitement maintenant."
_LONGUEUR_MAX_MESSAGE = 300

# 2 variantes de taille du même modèle de détection d'objets, exécutées sur la même image
# d'exemple fournie par l'outil (aucun upload nécessaire) — comparables sur la durée et les
# objets détectés, contrairement à un LLM qui ne prend pas d'image en entrée.
_MODELES_VISION = [
    {"id": "yolo-vision", "nom": "YOLOv8 Nano (détection)", "moteur_ref": "yolov8n.pt", "parametres_millions": 3.2},
    {"id": "yolo-vision-small", "nom": "YOLOv8 Small (détection)", "moteur_ref": "yolov8s.pt", "parametres_millions": 11.2},
]
_IDS_VISION_AUTORISES = {m["id"] for m in _MODELES_VISION}


class ComparerRequest(BaseModel):
    prompt: str | None = Field(default=None, max_length=_LONGUEUR_MAX_PROMPT)
    # Liste blanche stricte : sans ça, un appel direct pourrait glisser l'id d'un modèle non
    # prévu ici (ex: un modèle bien plus lourd présent sur l'Ollama partagé du homelab).
    modeles_ids: list[str] | None = Field(default=None, max_length=len(_MODELES))


class ComparerEmbeddingsRequest(BaseModel):
    phrase_a: str | None = Field(default=None, max_length=_LONGUEUR_MAX_PHRASE)
    phrase_b: str | None = Field(default=None, max_length=_LONGUEUR_MAX_PHRASE)
    modeles_ids: list[str] | None = Field(default=None, max_length=len(_MODELES_EMBEDDINGS))


class ComparerClassificationRequest(BaseModel):
    message: str | None = Field(default=None, max_length=_LONGUEUR_MAX_MESSAGE)
    modeles_ids: list[str] | None = Field(default=None, max_length=len(_MODELES_CLASSIFICATION))


class ComparerVisionRequest(BaseModel):
    modeles_ids: list[str] | None = Field(default=None, max_length=len(_MODELES_VISION))


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norme_a = sum(x * x for x in a) ** 0.5
    norme_b = sum(y * y for y in b) ** 0.5
    return dot / (norme_a * norme_b) if norme_a and norme_b else 0.0


def _construire_classifieur(algo_id: str):
    if algo_id == "regression_logistique":
        from sklearn.linear_model import LogisticRegression

        return LogisticRegression(max_iter=1000)
    if algo_id == "arbre_decision":
        from sklearn.tree import DecisionTreeClassifier

        return DecisionTreeClassifier(max_depth=5, random_state=0)
    if algo_id == "naive_bayes":
        from sklearn.naive_bayes import MultinomialNB

        return MultinomialNB()
    if algo_id == "knn":
        from sklearn.neighbors import KNeighborsClassifier

        return KNeighborsClassifier(n_neighbors=3)
    raise ValueError(f"Algorithme inconnu : {algo_id}")


def _comparer_classification_sync(message: str, ids_choisis: list[str]) -> dict:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    textes, labels = [], []
    with open(_DATASET_SPAM, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            textes.append(row["texte"])
            labels.append(int(row["label"]))
    y = np.array(labels)

    vectorizer = TfidfVectorizer(max_features=200)
    X = vectorizer.fit_transform(textes)
    x_message = vectorizer.transform([message])

    modeles_a_comparer = (
        [m for m in _MODELES_CLASSIFICATION if m["id"] in ids_choisis] if ids_choisis else _MODELES_CLASSIFICATION
    )

    resultats = []
    for m in modeles_a_comparer:
        modele = _construire_classifieur(m["id"])

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        precisions = cross_val_score(modele, X, y, cv=cv)

        debut = time.monotonic()
        modele.fit(X, y)
        duree = time.monotonic() - debut

        proba = modele.predict_proba(x_message)[0]
        prediction = "spam" if proba[1] > proba[0] else "légitime"

        resultats.append(
            {
                "id": m["id"],
                "nom": m["nom"],
                "duree_secondes": round(duree, 4),
                "precision_validation_croisee_pourcent": round(100 * float(precisions.mean())),
                "prediction": prediction,
                "confiance": round(float(proba.max()), 3),
            }
        )

    return {"message": message, "resultats": resultats}


@router.get("/modeles")
def modeles():
    return _MODELES


@router.get("/modeles-embeddings")
def modeles_embeddings():
    return _MODELES_EMBEDDINGS


@router.get("/modeles-classification")
def modeles_classification():
    return _MODELES_CLASSIFICATION


@router.get("/modeles-vision")
def modeles_vision():
    return [{k: v for k, v in m.items() if k != "moteur_ref"} for m in _MODELES_VISION]


async def _executer_comparaison(job_id: str, prompt: str, modeles_a_comparer: list[dict]) -> None:
    plus_gros = max(m["parametres_milliards"] for m in _MODELES)
    try:
        for m in modeles_a_comparer:
            debut = time.monotonic()
            reponse = await ollama.generate(m["id"], prompt)
            duree = time.monotonic() - debut

            fiche = await _fiche_modele(m["id"])
            analyse = _analyser_reponse(reponse, prompt)
            juge = await _juger_reponse(prompt, reponse)

            debit = round(len(reponse) / duree) if duree > 0 else 0
            niveau_materiel = _niveau_materiel(fiche["parametres_reels_milliards"])
            cout_relatif_cpu = round(duree * m["parametres_milliards"] / plus_gros, 2)

            _comparer_jobs[job_id]["resultats"].append(
                {
                    "id": m["id"],
                    "nom": m["nom"],
                    "parametres_milliards": m["parametres_milliards"],
                    # Catégorie "Performance mesurée" — mesures réelles sur cette machine.
                    "performance": {
                        "duree_secondes": round(duree, 2),
                        "debit_caracteres_par_seconde": debit,
                        "longueur_reponse_caracteres": len(reponse),
                        "nb_mots": analyse["nb_mots"],
                        "nb_phrases": analyse["nb_phrases"],
                        "longueur_moyenne_phrase_mots": analyse["longueur_moyenne_phrase_mots"],
                        "estimation_energie_relative_pourcent": round(
                            100 * m["parametres_milliards"] / plus_gros
                        ),
                    },
                    # Catégorie "Fiche technique" — données réelles Ollama + fiche publique éditeur.
                    "fiche_technique": fiche,
                    # Catégorie "Analyse de la réponse" — heuristiques déterministes sur le texte.
                    "analyse_reponse": {
                        "diversite_lexicale_pourcent": analyse["diversite_lexicale_pourcent"],
                        "langue_correcte": analyse["langue_correcte"],
                        "contient_donnees_chiffrees": analyse["contient_donnees_chiffrees"],
                        "contient_liste_structuree": analyse["contient_liste_structuree"],
                        "nb_marqueurs_incertitude": analyse["nb_marqueurs_incertitude"],
                        "reponse_semble_tronquee": analyse["reponse_semble_tronquee"],
                        "respect_longueur_demandee": analyse["respect_longueur_demandee"],
                        "coherence_avec_prompt_pourcent": analyse["coherence_avec_prompt_pourcent"],
                        "presence_disclaimer_ia": analyse["presence_disclaimer_ia"],
                    },
                    # Catégorie "Évaluation qualitative" — avis d'un modèle arbitre (qwen2.5:7b-instruct).
                    "evaluation_qualitative": juge,
                    # Catégorie "Synthèse décisionnelle" — combine les catégories précédentes.
                    "synthese": {
                        "niveau_materiel_requis": niveau_materiel,
                        "cout_relatif_cpu": cout_relatif_cpu,
                        "cas_usage_recommandes": fiche["cas_usage_recommandes"],
                        "verdict_global": _verdict_global(juge, duree),
                    },
                    "reponse": reponse[:400],
                }
            )
        _comparer_jobs[job_id]["status"] = "termine"
    except Exception as exc:  # noqa: BLE001 — l'erreur doit remonter côté IHM, pas planter la tâche
        _comparer_jobs[job_id]["status"] = "erreur"
        _comparer_jobs[job_id]["erreur"] = str(exc)


@router.post("/comparer")
async def comparer(requete: ComparerRequest):
    prompt = (requete.prompt or "").strip() or _PROMPT_DEFAUT
    ids_choisis = [i for i in (requete.modeles_ids or []) if i in _IDS_AUTORISES]
    modeles_a_comparer = [m for m in _MODELES if m["id"] in ids_choisis] if ids_choisis else _MODELES

    en_cours = sum(1 for j in _comparer_jobs.values() if j["status"] == "en_cours")
    if en_cours >= _MAX_COMPARER_JOBS_CONCURRENTS:
        raise HTTPException(
            400,
            f"Trop de comparaisons en cours ({en_cours}/{_MAX_COMPARER_JOBS_CONCURRENTS}). "
            "Réessayez dans quelques instants.",
        )

    if len(_comparer_jobs) >= _MAX_COMPARER_JOBS_CONSERVES:
        plus_ancien = next(iter(_comparer_jobs))
        _comparer_jobs.pop(plus_ancien, None)

    job_id = uuid.uuid4().hex[:8]
    _comparer_jobs[job_id] = {"status": "en_cours", "resultats": [], "erreur": None}
    asyncio.create_task(_executer_comparaison(job_id, prompt, modeles_a_comparer))
    return {"job_id": job_id, "prompt": prompt}


@router.get("/comparer/{job_id}/stream")
async def comparer_stream(job_id: str):
    async def event_generator():
        envoyes = 0
        while True:
            job = _comparer_jobs.get(job_id)
            if job is None:
                yield "event: erreur\ndata: job inconnu\n\n"
                break

            resultats = job["resultats"]
            while envoyes < len(resultats):
                yield f"event: modele\ndata: {json.dumps(resultats[envoyes])}\n\n"
                envoyes += 1

            if job["status"] != "en_cours":
                payload = json.dumps({"status": job["status"], "erreur": job.get("erreur")})
                yield f"event: fin\ndata: {payload}\n\n"
                break

            await asyncio.sleep(0.4)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/comparer-embeddings")
async def comparer_embeddings(requete: ComparerEmbeddingsRequest):
    phrase_a = (requete.phrase_a or "").strip() or _PHRASE_A_DEFAUT
    phrase_b = (requete.phrase_b or "").strip() or _PHRASE_B_DEFAUT

    ids_choisis = [i for i in (requete.modeles_ids or []) if i in _IDS_EMBEDDINGS_AUTORISES]
    modeles_a_comparer = (
        [m for m in _MODELES_EMBEDDINGS if m["id"] in ids_choisis] if ids_choisis else _MODELES_EMBEDDINGS
    )

    resultats = []
    for m in modeles_a_comparer:
        debut = time.monotonic()
        vecteur_a = await ollama.embed(m["id"], phrase_a)
        vecteur_b = await ollama.embed(m["id"], phrase_b)
        duree = time.monotonic() - debut
        resultats.append(
            {
                "id": m["id"],
                "nom": m["nom"],
                "parametres_millions": m["parametres_millions"],
                "duree_secondes": round(duree, 2),
                "dimension_vecteur": len(vecteur_a),
                "similarite_cosinus": round(_cosine(vecteur_a, vecteur_b), 4),
            }
        )

    return {"phrase_a": phrase_a, "phrase_b": phrase_b, "resultats": resultats}


@router.post("/comparer-classification")
async def comparer_classification(requete: ComparerClassificationRequest):
    message = (requete.message or "").strip() or _MESSAGE_CLASSIFICATION_DEFAUT
    ids_choisis = [i for i in (requete.modeles_ids or []) if i in _IDS_CLASSIFICATION_AUTORISEES]
    return await asyncio.to_thread(_comparer_classification_sync, message, ids_choisis)


@router.post("/comparer-vision")
async def comparer_vision(requete: ComparerVisionRequest):
    ids_choisis = [i for i in (requete.modeles_ids or []) if i in _IDS_VISION_AUTORISES]
    modeles_a_comparer = [m for m in _MODELES_VISION if m["id"] in ids_choisis] if ids_choisis else _MODELES_VISION

    image_note = None
    resultats = []
    for m in modeles_a_comparer:
        debut = time.monotonic()
        detection = await run_detection(m["moteur_ref"])
        duree = time.monotonic() - debut
        image_note = detection["note"]
        resultats.append(
            {
                "id": m["id"],
                "nom": m["nom"],
                "parametres_millions": m["parametres_millions"],
                "duree_secondes": round(duree, 2),
                "nb_objets": detection["nb_objets"],
                "objets_detectes": detection["objets_detectes"],
                "image_annotee_base64": detection["image_annotee_base64"],
            }
        )

    return {"image_note": image_note, "resultats": resultats}
