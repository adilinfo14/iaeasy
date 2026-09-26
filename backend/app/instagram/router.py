import asyncio
import json
import logging
import re
import time
import uuid
from datetime import datetime
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field

from ..admin.router import _verifier_mot_de_passe
from ..core.anthropic_client import anthropic
from ..core.config import settings
from ..core.jobs import JobStore
from . import carrousel, compte, connaissances, derniers_posts, effets, historique, lien, planificateur, prompts, reel, story

router = APIRouter(prefix="/instagram", tags=["instagram"])

# Un seul appel à la fois : ce point d'entrée déclenche une vraie publication publique sur un
# compte Instagram réel, pas une simple génération de contenu — pas de file de plusieurs essais
# concurrents comme pour le chat ou le Théâtre.
_JOBS = JobStore(max_concurrents=1, max_conserves=20)

_IMAGES_VALIDES = {
    "logo", "presentation", "monogramme", "signature", "motif",
    "strategie", "automatisation", "performance", "innovation", "partenariat", "excellence",
}

# Trois angles éditoriaux plutôt qu'une seule légende imposée — le choix reste dans le ton déjà
# assumé par tkonsulting.fr (direct, transparent, sans jargon), seule la manière d'accrocher change.
_TONS = {
    "direct": (
        "Ton direct et orienté résultats, phrases courtes, aucune formule commerciale creuse "
        "('révolutionnaire', 'unique en son genre'). Va droit à l'idée utile pour un dirigeant de "
        "PME/TPE pressé."
    ),
    "pedagogique": (
        "Ton pédagogique : explique un concept en le rendant concret et accessible, comme si tu "
        "l'expliquais à quelqu'un qui découvre le sujet, sans jamais être condescendant."
    ),
    "storytelling": (
        "Ton storytelling : ouvre sur une mise en situation concrète et courte (un dirigeant, une "
        "PME, une difficulté réelle) avant d'arriver au message — sans en faire une nouvelle, "
        "3-4 phrases maximum au total."
    ),
}
_TON_DEFAUT = "direct"

# Mêmes secteurs que ceux déjà utilisés dans le Constructeur (agents/bricks.py CAS_DISPONIBLES) —
# pas une spécialisation sectorielle de TKonsulting (le cabinet reste généraliste PME/TPE), mais
# un moyen concret de parler le langage d'un prospect précis plutôt qu'un message générique qui
# ne parle à personne en particulier.
_SECTEURS = {
    "aucun": "",
    "btp": "un artisan ou une entreprise du BTP",
    "banque_assurance": "un responsable en banque ou assurance",
    "agriculture": "un exploitant ou une coopérative agricole",
    "rh_juridique": "un responsable RH ou juridique",
    "ecommerce": "un e-commerçant ou responsable service client",
}
_SECTEUR_DEFAUT = "aucun"

# Banque de hashtags par secteur — deux niveaux plutôt qu'une liste plate : les "larges" apportent
# du volume de recherche (portée), les "niches" ciblent qui doit vraiment voir le post (pertinence).
# Un mélange des deux bat systématiquement soit 5 hashtags génériques (beaucoup de vues, peu
# concernées), soit 5 hashtags trop pointus (personne ne les cherche) — d'où l'instruction de
# mélanger plutôt que de piocher au hasard dans une liste unique.
_HASHTAGS = {
    "aucun": {
        "larges": ["#PME", "#TPE", "#entrepreneuriat", "#chefdentreprise", "#business"],
        "niches": [
            "#conseilenentreprise", "#stratégieentreprise", "#pilotagedeprojet",
            "#automatisation", "#transformationdigitale", "#dirigeantpme",
        ],
    },
    "btp": {
        "larges": ["#BTP", "#artisan", "#construction", "#PME"],
        "niches": ["#entreprisedubatiment", "#gestiondechantier", "#artisanbtp", "#batiment", "#travauxpublics"],
    },
    "banque_assurance": {
        "larges": ["#banque", "#assurance", "#finance"],
        "niches": ["#conseillerbancaire", "#assureur", "#risquefinancier", "#courtierassurance", "#secteurbancaire"],
    },
    "agriculture": {
        "larges": ["#agriculture", "#agriculteur", "#PME"],
        "niches": ["#exploitationagricole", "#cooperativeagricole", "#agribusiness", "#mondeagricole", "#agroalimentaire"],
    },
    "rh_juridique": {
        "larges": ["#RH", "#juridique", "#ressourceshumaines"],
        "niches": ["#responsableRH", "#droitdutravail", "#servicejuridique", "#gestionRH", "#conformité"],
    },
    "ecommerce": {
        "larges": ["#ecommerce", "#business", "#digital"],
        "niches": ["#boutiqueenligne", "#serviceclient", "#venteenligne", "#marketplace", "#commerceconnecte"],
    },
}


def _hashtags_suggeres(secteur: str) -> str:
    banque = _HASHTAGS.get(secteur, _HASHTAGS["aucun"])
    return ", ".join(banque["larges"] + banque["niches"])


# ---------------------------------------------------------------------------
# Connaissances par sujet (Lesensia, Nextcloud, Knowledge Management) — injectées dans le prompt
# pour ancrer le texte généré dans de vrais faits plutôt que de laisser le LLM improviser sur des
# produits qu'il ne connaît pas. Pas une vraie base RAG (embeddings/recherche sémantique) : le
# corpus est volontairement restreint à quelques sujets récurrents, choisis explicitement par
# l'utilisateur plutôt que retrouvés par similarité — largement suffisant à cette échelle.
# ---------------------------------------------------------------------------


def _bloc_connaissance(cle: str) -> str:
    if cle == "aucune" or cle not in connaissances.DEFAUTS:
        return ""
    texte = connaissances.lire_texte(cle)
    cta = connaissances.lire_cta(cle)
    bloc = (
        "Connaissances factuelles disponibles sur ce sujet (réutilise-les si pertinent pour "
        f"rendre le post concret, n'invente rien d'autre à leur sujet) :\n{texte}\n"
    )
    if cta:
        bloc += (
            "Consigne d'appel à l'action à respecter EN PRIORITÉ, y compris si une consigne plus "
            f"bas suggère par défaut une invitation discrète ou sans lien — celle-ci prévaut : {cta}\n"
        )
    return bloc + "\n"


def _forcer_cta_derniere_slide(plan: dict, connaissance: str) -> dict:
    """Filet de sécurité déterministe : le modèle suit fidèlement la consigne de CTA dans la
    légende mais l'oublie souvent dans le texte de la dernière slide (constaté sur plusieurs
    générations réelles) — plutôt que de dépendre indéfiniment d'un prompt toujours plus
    insistant, on complète la slide nous-mêmes si le CTA n'y est pas déjà."""
    cta_texte = connaissances.lire_cta_texte(connaissance) if connaissance != "aucune" else ""
    if not cta_texte or not plan.get("slides"):
        return plan
    derniere = plan["slides"][-1]
    texte_actuel = derniere.get("texte") or ""
    if cta_texte.lower() not in texte_actuel.lower():
        derniere["texte"] = (texte_actuel + " " + cta_texte).strip()
    return plan


@router.get("/connaissances")
def lister_connaissances():
    return [{"id": cle, **infos} for cle, infos in connaissances.lire_tous().items()]


class ConnaissanceEnregistrerRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    cle: str = Field(pattern="^(lesensia|nextcloud|knowledge_management)$")
    titre: str = Field(max_length=100)
    texte: str = Field(max_length=4000)
    cta: str = Field(default="", max_length=300)
    cta_texte: str = Field(default="", max_length=150)


@router.post("/connaissances/enregistrer")
def enregistrer_connaissance(requete: ConnaissanceEnregistrerRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    connaissances.enregistrer(requete.cle, requete.titre, requete.texte, requete.cta, requete.cta_texte)
    return {"ok": True}


class ConnaissanceReinitialiserRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    cle: str = Field(pattern="^(lesensia|nextcloud|knowledge_management)$")


@router.post("/connaissances/reinitialiser")
def reinitialiser_connaissance(requete: ConnaissanceReinitialiserRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    connaissances.reinitialiser(requete.cle)
    return {"ok": True}


class SecteurApercuRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    secteur: str = Field(default=_SECTEUR_DEFAUT, max_length=20)


@router.post("/secteurs/apercu")
def apercu_secteur(requete: SecteurApercuRequest):
    """Pas d'estimation d'audience inventée (Instagram ne donne pas de volume de recherche par
    hashtag via cette API) — à la place, une vraie moyenne calculée sur TES posts précédents ayant
    réellement ciblé ce secteur, seule donnée honnête disponible sans API supplémentaire."""
    _verifier_mot_de_passe(requete.mot_de_passe)
    banque = _HASHTAGS.get(requete.secteur, _HASHTAGS["aucun"])
    entrees = historique.lire_historique(limite=1000)
    publies = [e for e in entrees if e.get("statut") == "publie" and e.get("secteur") == requete.secteur]
    avec_indicateurs = [e["indicateurs"] for e in publies if e.get("indicateurs")]
    moyenne = _moyenne_indicateurs(avec_indicateurs)
    return {
        "cible": _SECTEURS.get(requete.secteur, ""),
        "hashtags_larges": banque["larges"],
        "hashtags_niches": banque["niches"],
        "nb_posts_historique": len(publies),
        "nb_posts_avec_donnees": len(avec_indicateurs),
        "reach_moyen": moyenne["reach"] if moyenne else None,
    }


class LegendeRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    sujet: str = Field(min_length=3, max_length=500)
    ton: str = Field(default=_TON_DEFAUT, max_length=20)
    secteur: str = Field(default=_SECTEUR_DEFAUT, max_length=20)
    connaissance: str = Field(default="aucune", max_length=30)


def _prompt_legende(sujet: str, ton: str, secteur: str, connaissance_bloc: str = "") -> str:
    instruction_ton = _TONS.get(ton, _TONS[_TON_DEFAUT])
    cible = _SECTEURS.get(secteur, "")
    instruction_secteur = (
        f"\n\nCette légende s'adresse spécifiquement à {cible} — reformule l'angle et l'exemple "
        "pour que cette personne précise se reconnaisse immédiatement, sans jamais inventer de "
        "détail sectoriel faux. Termine par une invitation discrète à échanger (pas un lien, une "
        "phrase naturelle du type 'écris-nous en message si ça te parle')."
        if cible
        else ""
    )
    return prompts.substituer(
        prompts.lire("legende"),
        sujet=sujet,
        ton=instruction_ton,
        secteur=instruction_secteur,
        hashtags=_hashtags_suggeres(secteur),
        connaissance=connaissance_bloc,
    )


def _instruction_secteur_carrousel(secteur: str) -> str:
    """Variante de l'instruction secteur sans la phrase de CTA (déjà couverte par la structure
    du carrousel elle-même, dans le prompt de carrousel.py) — évite de la dupliquer deux fois."""
    cible = _SECTEURS.get(secteur, "")
    if not cible:
        return ""
    return (
        f"\n\nCe carrousel s'adresse spécifiquement à {cible} — reformule l'angle et les exemples "
        "pour que cette personne précise se reconnaisse immédiatement, sans jamais inventer de "
        "détail sectoriel faux."
    )


def _prompt_garde_fou(legende: str) -> str:
    return (
        "Cette légende Instagram respecte-t-elle STRICTEMENT toutes ces règles : ton direct, "
        "professionnel, aucun jargon commercial creux (ex. 'révolutionnaire', 'disruptif', "
        "'unique en son genre'), aucune promesse chiffrée invérifiable ? "
        "Réponds UNIQUEMENT par OUI ou NON, rien d'autre.\n\n"
        f"Légende : {legende}"
    )


async def _generer_legende(sujet: str, ton: str, secteur: str, connaissance: str = "aucune") -> tuple[str, bool]:
    """Génère la légende puis une relecture (garde-fou) qui déclenche UNE régénération si le ton
    dérape — imite la double-passe déjà utilisée pour la validation du Théâtre, appliquée ici à
    la qualité éditoriale plutôt qu'à la structure narrative."""
    connaissance_bloc = _bloc_connaissance(connaissance)
    legende = (await anthropic.generate(_prompt_legende(sujet, ton, secteur, connaissance_bloc))).strip()
    verdict = (await anthropic.generate(_prompt_garde_fou(legende), max_tokens=10)).strip().upper()
    regenere = False
    if not verdict.startswith("OUI"):
        regenere = True
        prompt_renforce = _prompt_legende(sujet, ton, secteur, connaissance_bloc) + (
            "\n\nATTENTION : évite absolument tout superlatif commercial creux et toute promesse "
            "chiffrée non vérifiable."
        )
        legende = (await anthropic.generate(prompt_renforce)).strip()
    return legende, regenere


@router.post("/legende")
async def generer_legende(requete: LegendeRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    try:
        legende, regenere = await _generer_legende(requete.sujet, requete.ton, requete.secteur, requete.connaissance)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la génération de la légende : {exc}") from exc
    return {"legende": legende, "regenere": regenere}


# ---------------------------------------------------------------------------
# Prompts éditables — "legende" (post simple), "story" (accroche courte, utilisée par une story
# à 1 carte ET un reel à 1 scène), "carrousel" (plan JSON, utilisé par le carrousel, un reel à
# plusieurs scènes ET une story à plusieurs cartes). {{SUJET}}/{{TON}}/{{SECTEUR}}/{{HASHTAGS}}/
# {{NB_SLIDES}} restent calculés en Python (ton/secteur choisis dans l'IHM, hashtags de la
# banque) puis substitués dans le template — seule la partie "règles/structure/ton" est éditable.
# ---------------------------------------------------------------------------


class PromptsRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


@router.post("/prompts")
def lire_prompts(requete: PromptsRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    return {"prompts": prompts.lire_tous(), "defauts": prompts.DEFAUTS}


class PromptEnregistrerRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    type: str = Field(pattern="^(legende|story|carrousel)$")
    texte: str = Field(max_length=6000)


@router.post("/prompts/enregistrer")
def enregistrer_prompt(requete: PromptEnregistrerRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    prompts.enregistrer(requete.type, requete.texte)
    return {"ok": True}


class PromptReinitialiserRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    type: str = Field(pattern="^(legende|story|carrousel)$")


@router.post("/prompts/reinitialiser")
def reinitialiser_prompt(requete: PromptReinitialiserRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    prompts.reinitialiser(requete.type)
    return {"ok": True}


class PublierRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    sujet: str = Field(min_length=3, max_length=500)
    # "aleatoire" (ou vide) laisse le workflow n8n tirer au sort, comme sur le formulaire n8n brut.
    image: str = Field(default="aleatoire", max_length=20)
    ton: str = Field(default=_TON_DEFAUT, max_length=20)
    secteur: str = Field(default=_SECTEUR_DEFAUT, max_length=20)
    # Légende déjà validée via /legende (aperçu avant envoi) — si fournie, n8n l'utilise telle
    # quelle au lieu d'en regénérer une, pour que le résultat publié corresponde exactement à ce
    # qui a été approuvé. Vide = comportement d'origine (n8n génère sa propre légende).
    legende: str = Field(default="", max_length=800)


def _enregistrer_historique(sujet: str, image: str, ton: str, secteur: str, legende: str, debut: float, **extra) -> None:
    historique.ajouter_entree(
        {
            "horodatage": time.time(),
            "sujet": sujet,
            "image": image,
            "ton": ton,
            "secteur": secteur,
            "legende": legende,
            "duree_s": round(time.time() - debut, 1),
            **extra,
        }
    )


async def _executer_publication(job_id: str, sujet: str, image: str, ton: str, secteur: str, legende: str) -> None:
    champ_image = image if image in _IMAGES_VALIDES else ""
    debut = time.time()
    try:
        # Réseau docker interne (proxy-net) plutôt que le domaine public n8n.noschoixpourvous.com :
        # évite le timeout ~10s du tunnel Cloudflare sur un appel qui dure 30 à 90s (Ollama +
        # Instagram). Le formulaire n8n attend des champs positionnels field-0/1/2/3 (confirmé en
        # inspectant sa page rendue), pas les libellés humains affichés à l'écran — et EXIGE du
        # multipart/form-data (constaté via l'erreur "Expected multipart/form-data" : un simple
        # data=... encode en application/x-www-form-urlencoded, rejeté par le nœud Form Trigger).
        # L'astuce files=... avec une valeur (None, texte) force httpx à encoder en multipart
        # même pour des champs texte, sans vrai fichier à envoyer.
        async with httpx.AsyncClient(timeout=150) as client:
            resp = await client.post(
                settings.n8n_instagram_url,
                files={
                    "field-0": (None, settings.admin_password),
                    "field-1": (None, sujet),
                    "field-2": (None, champ_image),
                    "field-3": (None, legende),
                },
            )
        if resp.status_code != 200:
            erreur = "La publication a échoué côté automatisation (n8n). Vérifie l'exécution dans n8n pour le détail."
            _JOBS.echouer(job_id, erreur)
            _enregistrer_historique(sujet, image, ton, secteur, legende, debut, statut="erreur", erreur=erreur)
            return
        _JOBS.terminer(job_id, {"resultat": resp.text})
        _enregistrer_historique(sujet, image, ton, secteur, legende, debut, statut="publie", resultat=resp.text)
    except httpx.TimeoutException:
        erreur = "Délai dépassé en attendant la fin de la publication."
        _JOBS.echouer(job_id, erreur)
        _enregistrer_historique(sujet, image, ton, secteur, legende, debut, statut="erreur", erreur=erreur)
    except Exception as exc:  # noqa: BLE001 — remonter un message plutôt qu'un 500 opaque
        erreur = f"Erreur inattendue : {exc}"
        _JOBS.echouer(job_id, erreur)
        _enregistrer_historique(sujet, image, ton, secteur, legende, debut, statut="erreur", erreur=erreur)


@router.post("/publier")
async def publier(requete: PublierRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    if not settings.admin_password:
        raise HTTPException(400, "Mot de passe non configuré côté serveur (IAEASY_ADMIN_PASSWORD).")
    try:
        job_id = _JOBS.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    asyncio.create_task(
        _executer_publication(job_id, requete.sujet, requete.image, requete.ton, requete.secteur, requete.legende)
    )
    return {"job_id": job_id}


@router.get("/publier/{job_id}")
def publier_statut(job_id: str):
    job = _JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, "Job inconnu.")
    if job["status"] == "en_cours":
        return {"status": "en_cours"}
    if job["status"] == "erreur":
        return {"status": "erreur", "erreur": job.get("erreur")}
    return {"status": job["status"], **job.get("fin_extra", {})}


class HistoriqueRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


@router.post("/historique")
def lire_historique(requete: HistoriqueRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    return historique.lire_historique()


class InsightsRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    media_id: str = Field(max_length=60)


def _extraire_media_id(resultat: str | None) -> str | None:
    if not resultat:
        return None
    try:
        return json.loads(resultat).get("id")
    except (json.JSONDecodeError, AttributeError):
        return None


async def _recuperer_indicateurs(media_id: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            settings.n8n_instagram_insights_url,
            json={"mot_de_passe": settings.admin_password, "media_id": media_id},
        )
    resp.raise_for_status()
    donnees = resp.json()
    if "data" not in donnees:
        raise ValueError(donnees.get("erreur") or "Réponse inattendue de l'API Instagram.")
    return {m["name"]: m["values"][0]["value"] for m in donnees["data"]}


@router.post("/insights")
async def insights(requete: InsightsRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    try:
        indicateurs = await _recuperer_indicateurs(requete.media_id)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la récupération des indicateurs : {exc}") from exc
    except ValueError as exc:
        raise HTTPException(502, str(exc)) from exc

    # Mis en cache pour le tableau de bord (Instagram ne pousse jamais ces chiffres tout seul) —
    # dès qu'un post correspondant à ce media_id est trouvé dans l'historique.
    for e in historique.lire_historique(limite=1000):
        if _extraire_media_id(e.get("resultat")) == requete.media_id:
            historique.mettre_a_jour_par_horodatage(e["horodatage"], indicateurs=indicateurs)
            break

    return indicateurs


class InsightsToutRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


@router.post("/insights/tout")
async def insights_tout(requete: InsightsToutRequest):
    """Rafraîchit les indicateurs de TOUS les posts publiés d'un coup — évite de cliquer post par
    post dans l'historique pour alimenter le tableau de bord. Un échec isolé (post supprimé,
    story expirée après 24h...) ne bloque pas les autres."""
    _verifier_mot_de_passe(requete.mot_de_passe)
    entrees = historique.lire_historique(limite=1000)
    maj = 0
    total_publies = 0
    for e in entrees:
        if e.get("statut") != "publie":
            continue
        total_publies += 1
        media_id = _extraire_media_id(e.get("resultat"))
        if not media_id:
            continue
        try:
            indicateurs = await _recuperer_indicateurs(media_id)
            historique.mettre_a_jour_par_horodatage(e["horodatage"], indicateurs=indicateurs)
            maj += 1
        except Exception:  # noqa: BLE001 — un post en échec ne doit pas arrêter les suivants
            continue
    return {"maj": maj, "total_publies": total_publies}


def _type_entree(e: dict) -> str:
    image = e.get("image", "")
    return image if image in ("carrousel", "story", "reel") else "simple"


def _moyenne_indicateurs(liste: list[dict]) -> dict | None:
    if not liste:
        return None
    cles = ["reach", "likes", "comments", "saved", "shares"]
    return {c: round(sum(i.get(c, 0) for i in liste) / len(liste), 1) for c in cles}


@router.post("/dashboard")
def lire_dashboard(requete: HistoriqueRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    entrees = historique.lire_historique(limite=1000)

    total = len(entrees)
    publies = [e for e in entrees if e.get("statut") == "publie"]
    echecs = [e for e in entrees if e.get("statut") == "erreur"]

    par_type: dict[str, int] = {}
    for e in entrees:
        t = _type_entree(e)
        par_type[t] = par_type.get(t, 0) + 1

    # Nombre de publications par semaine ISO — 12 dernières semaines où au moins un post est sorti
    # (pas 12 semaines calendaires fixes, pour ne pas afficher une rangée de zéros sans intérêt).
    par_semaine: dict[str, int] = {}
    for e in publies:
        cle = datetime.fromtimestamp(e["horodatage"]).strftime("%G-S%V")
        par_semaine[cle] = par_semaine.get(cle, 0) + 1
    tendance = sorted(par_semaine.items())[-12:]

    par_ton: dict[str, list[dict]] = {}
    for e in publies:
        indicateurs = e.get("indicateurs")
        if not indicateurs:
            continue
        ton = e.get("ton") or "aucun"
        par_ton.setdefault(ton, []).append(indicateurs)
    engagement_par_ton = {ton: _moyenne_indicateurs(liste) for ton, liste in par_ton.items()}

    avec_indicateurs = [e for e in publies if e.get("indicateurs")]
    meilleur = max(avec_indicateurs, key=lambda e: e["indicateurs"].get("reach", 0), default=None)

    return {
        "total": total,
        "publies": len(publies),
        "echecs": len(echecs),
        "taux_succes": round(len(publies) / total * 100, 1) if total else None,
        "par_type": par_type,
        "tendance_semaines": [{"semaine": s, "nb": n} for s, n in tendance],
        "engagement_par_ton": engagement_par_ton,
        "nb_avec_indicateurs": len(avec_indicateurs),
        "meilleur_post": (
            {"sujet": meilleur.get("sujet"), "horodatage": meilleur["horodatage"], "indicateurs": meilleur["indicateurs"]}
            if meilleur
            else None
        ),
    }


class CommentairesRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    media_id: str = Field(max_length=60)


@router.post("/commentaires")
async def lire_commentaires(requete: CommentairesRequest):
    """Vrais commentaires (texte + auteur), pas seulement le compteur agrégé de /insights —
    capter les réactions réelles des visiteurs plutôt qu'un simple chiffre."""
    _verifier_mot_de_passe(requete.mot_de_passe)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.n8n_instagram_commentaires_url,
                json={"mot_de_passe": settings.admin_password, "media_id": requete.media_id},
            )
        resp.raise_for_status()
        donnees = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la récupération des commentaires : {exc}") from exc

    if "data" not in donnees:
        raise HTTPException(502, donnees.get("erreur") or "Réponse inattendue de l'API Instagram.")
    return donnees["data"]


# ---------------------------------------------------------------------------
# Compte — croissance dans le temps (abonnés, portée et visites de profil du jour), capturée en
# instantanés quotidiens plutôt qu'un chiffre isolé sans référence.
# ---------------------------------------------------------------------------


class CompteRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


async def _recuperer_instantane_compte() -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            settings.n8n_instagram_compte_url,
            json={"mot_de_passe": settings.admin_password},
        )
    resp.raise_for_status()
    return resp.json()


@router.post("/compte/instantane")
async def prendre_instantane_compte(requete: CompteRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    try:
        donnees = await _recuperer_instantane_compte()
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la récupération des indicateurs du compte : {exc}") from exc
    return compte.ajouter_instantane(donnees)


@router.post("/compte/historique")
def lire_historique_compte(requete: CompteRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    return compte.lire_historique()


async def _boucle_instantane_compte_auto() -> None:
    """Capture un instantané par jour automatiquement, sans dépendre du fait que quelqu'un ouvre
    le tableau de bord — sinon la courbe de croissance aurait des trous les jours où personne ne
    l'a consulté."""
    while True:
        try:
            donnees = await _recuperer_instantane_compte()
            compte.ajouter_instantane(donnees)
        except Exception:  # noqa: BLE001 — un échec isolé ne doit jamais arrêter la boucle de fond
            logging.getLogger("uvicorn.error").warning("[instagram] échec de l'instantané quotidien du compte")
        await asyncio.sleep(24 * 3600)


def demarrer_instantanes_compte() -> None:
    """Lance la boucle de fond de capture quotidienne — appelé une fois depuis le lifespan de
    main.py, comme demarrer_planificateur()."""
    asyncio.create_task(_boucle_instantane_compte_auto())


# ---------------------------------------------------------------------------
# Derniers posts — aperçu embarqué sur tkonsulting.fr (section dédiée), alimenté par les vrais
# médias publiés plutôt qu'un lien externe fragile (identifiant erroné, compte renommé...).
# Route publique en lecture seule : n'expose que des données déjà publiques sur Instagram
# (images, légendes, permaliens), rafraîchies en fond plutôt qu'appelées en direct par le site.
# ---------------------------------------------------------------------------


async def _recuperer_derniers_posts() -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            settings.n8n_instagram_derniers_posts_url,
            json={"mot_de_passe": settings.admin_password},
        )
    resp.raise_for_status()
    bruts = resp.json().get("data", [])
    posts = []
    for m in bruts:
        # Une vidéo n'a pas d'image directement affichable via media_url (c'est le fichier vidéo
        # lui-même) — thumbnail_url est l'image de couverture dans ce cas.
        image = m.get("thumbnail_url") if m.get("media_type") == "VIDEO" else m.get("media_url")
        if not image:
            continue
        posts.append(
            {
                "id": m.get("id", ""),
                "image_url": image,
                "caption": (m.get("caption") or "")[:200],
                "permalink": m.get("permalink", ""),
                "media_type": m.get("media_type", ""),
            }
        )
    return posts


async def _boucle_derniers_posts_auto() -> None:
    """Rafraîchit le cache toutes les heures — le site public sert toujours cette version en
    cache, jamais un appel direct à l'API Graph par visiteur (plus rapide, et évite de cogner
    l'API à chaque chargement de page)."""
    while True:
        try:
            posts = await _recuperer_derniers_posts()
            derniers_posts.enregistrer(posts)
        except Exception:  # noqa: BLE001 — un échec isolé ne doit jamais arrêter la boucle de fond
            logging.getLogger("uvicorn.error").warning("[instagram] échec du rafraîchissement des derniers posts")
        await asyncio.sleep(3600)


def demarrer_derniers_posts() -> None:
    """Lance la boucle de fond — appelé une fois depuis le lifespan de main.py."""
    asyncio.create_task(_boucle_derniers_posts_auto())


@router.get("/derniers-posts")
def lire_derniers_posts():
    return derniers_posts.lire()


# ---------------------------------------------------------------------------
# Liens "en bio" — les liens cliquables qu'Instagram autorise sur un compte pro (jusqu'à 5), à
# coller une fois pour toutes dans les paramètres du profil (l'API ne permet pas de modifier la
# bio elle-même). Une route publique (pas de mot de passe : Instagram doit pouvoir la suivre) par
# lien connu compte le clic puis redirige vers la vraie destination — la clé est validée contre
# cette liste fermée plutôt qu'acceptée en clair, pour ne jamais servir de redirection ouverte.
# ---------------------------------------------------------------------------

_LIENS_BIO = {
    "tkonsulting": settings.lien_bio_url_tkonsulting,
    "lesensia": settings.lien_bio_url_lesensia,
    "iaeasy": settings.lien_bio_url_iaeasy,
}


class LienBioStatsRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


@router.get("/lien-bio/{cle}")
def suivre_clic_lien_bio(cle: str, request: Request):
    destination = _LIENS_BIO.get(cle)
    if destination is None:
        raise HTTPException(404, "Lien en bio inconnu")
    lien.enregistrer_clic(cle, request.headers.get("user-agent", ""))
    return RedirectResponse(destination, status_code=302)


@router.post("/lien/stats")
def lire_stats_lien_bio(requete: LienBioStatsRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    return {
        **lien.lire_stats(),
        "urls": {cle: f"{settings.public_base_url}/api/instagram/lien-bio/{cle}" for cle in _LIENS_BIO},
    }


# ---------------------------------------------------------------------------
# Messages privés (DM) — toujours lus et écrits par un humain depuis l'IHM, jamais de réponse
# générée ou envoyée automatiquement par l'IA elle-même.
# ---------------------------------------------------------------------------


class DMConversationsRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


@router.post("/dm/conversations")
async def lister_conversations_dm(requete: DMConversationsRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.n8n_instagram_dm_conversations_url,
                json={"mot_de_passe": settings.admin_password},
            )
        resp.raise_for_status()
        donnees = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la récupération des conversations : {exc}") from exc

    if "data" not in donnees:
        raise HTTPException(502, donnees.get("erreur") or "Réponse inattendue de l'API Instagram.")
    return donnees["data"]


class DMMessagesRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    conversation_id: str = Field(max_length=60)


@router.post("/dm/messages")
async def lire_messages_dm(requete: DMMessagesRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.n8n_instagram_dm_messages_url,
                json={"mot_de_passe": settings.admin_password, "conversation_id": requete.conversation_id},
            )
        resp.raise_for_status()
        donnees = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la récupération des messages : {exc}") from exc

    messages = (donnees.get("messages") or {}).get("data")
    if messages is None:
        raise HTTPException(502, donnees.get("erreur") or "Réponse inattendue de l'API Instagram.")
    return messages


class DMEnvoyerRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    destinataire_id: str = Field(max_length=60)
    texte: str = Field(min_length=1, max_length=1000)


@router.post("/dm/envoyer")
async def envoyer_dm(requete: DMEnvoyerRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    if not settings.admin_password:
        raise HTTPException(400, "Mot de passe non configuré côté serveur (IAEASY_ADMIN_PASSWORD).")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.n8n_instagram_dm_envoyer_url,
                json={
                    "mot_de_passe": settings.admin_password,
                    "destinataire_id": requete.destinataire_id,
                    "texte": requete.texte,
                },
            )
        resp.raise_for_status()
        donnees = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant l'envoi du message : {exc}") from exc

    if "error" in donnees:
        raise HTTPException(502, donnees["error"].get("message", "Erreur inconnue lors de l'envoi."))
    return donnees


# ---------------------------------------------------------------------------
# Carrousel — mini-article en plusieurs slides (contenu de fond, ex. "l'IA comme moteur de
# recherche interne", "gestion de la connaissance"), plutôt qu'un post simple image + légende.
# ---------------------------------------------------------------------------

_JOBS_CARROUSEL = JobStore(max_concurrents=1, max_conserves=20)


class CarrouselGenererRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    sujet: str = Field(min_length=3, max_length=500)
    ton: str = Field(default=_TON_DEFAUT, max_length=20)
    secteur: str = Field(default=_SECTEUR_DEFAUT, max_length=20)
    nb_slides: int = Field(default=5, ge=3, le=8)
    effet: str = Field(default=effets.DEFAUT, max_length=30)
    connaissance: str = Field(default="aucune", max_length=30)


@router.get("/effets")
def lister_effets():
    return [{"id": k, "label": v["label"], "categorie": v["categorie"]} for k, v in effets.PRESETS.items()]


_APERCUS_EFFETS_DIR = Path(settings.data_dir) / "instagram_apercus_effets"


@router.get("/effets/{cle}/apercu")
def apercu_effet(cle: str):
    # Rendu paresseux + mis en cache sur disque au premier appel (graine fixe = déterministe) :
    # 55 effets à générer à la volée à chaque clic serait inutilement coûteux alors que le
    # résultat ne change jamais pour un même effet.
    # Pas de suffixe ".jpg" dans le chemin : Cloudflare met en cache par défaut les extensions
    # d'assets statiques au niveau du edge, y compris une réponse de secours erronée (constaté en
    # conditions réelles avec un cache HIT de 4h sur une 404 masquée) — un chemin sans extension
    # évite cette heuristique de cache automatique, indépendamment des en-têtes renvoyés ici.
    if cle not in effets.PRESETS:
        raise HTTPException(404, "Effet introuvable.")
    _APERCUS_EFFETS_DIR.mkdir(parents=True, exist_ok=True)
    chemin = _APERCUS_EFFETS_DIR / f"{cle}.jpg"
    if not chemin.exists():
        image = effets.generer_fond(400, 400, cle, graine=7).convert("RGB")
        image.save(chemin, quality=85)
    return FileResponse(chemin, media_type="image/jpeg")


@router.post("/carrousel/generer")
async def generer_carrousel(requete: CarrouselGenererRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    instruction_ton = _TONS.get(requete.ton, _TONS[_TON_DEFAUT])
    instruction_secteur = _instruction_secteur_carrousel(requete.secteur)
    effet = requete.effet if requete.effet in effets.PRESETS else effets.DEFAUT
    try:
        plan = await carrousel.generer_plan(
            requete.sujet, instruction_ton, instruction_secteur, requete.nb_slides,
            _hashtags_suggeres(requete.secteur), _bloc_connaissance(requete.connaissance),
        )
        plan = _forcer_cta_derniere_slide(plan, requete.connaissance)
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, f"Erreur pendant la génération du carrousel : {exc}") from exc

    carrousel_id = uuid.uuid4().hex[:12]
    images = [
        carrousel.rendre_slide(i, len(plan["slides"]), s.get("titre", ""), s.get("texte", ""), i == 0, effet)
        for i, s in enumerate(plan["slides"])
    ]
    carrousel.sauvegarder_carrousel(carrousel_id, images)

    return {
        "carrousel_id": carrousel_id,
        "legende": plan.get("legende", ""),
        "slides": [
            {
                "titre": s.get("titre", ""),
                "texte": s.get("texte", ""),
                "image_url": carrousel.url_slide(carrousel_id, i),
            }
            for i, s in enumerate(plan["slides"])
        ],
    }


@router.get("/carrousel/{carrousel_id}/{index}.jpg")
def servir_slide_carrousel(carrousel_id: str, index: int):
    # Route publique délibérément SANS mot de passe : les serveurs de Meta doivent pouvoir
    # récupérer ces images pour publier le carrousel, comme pour la banque de templates statique
    # sur tkonsulting.fr — même niveau de confiance, id imprévisible (uuid4) en guise de protection.
    if not re.fullmatch(r"[0-9a-f]{8,32}", carrousel_id):
        raise HTTPException(404, "Carrousel introuvable.")
    chemin = carrousel.chemin_slide(carrousel_id, index)
    if chemin is None:
        raise HTTPException(404, "Slide introuvable.")
    return FileResponse(chemin, media_type="image/jpeg")


class CarrouselPublierRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    carrousel_id: str = Field(max_length=32)
    nb_slides: int = Field(ge=1, le=8)
    legende: str = Field(min_length=1, max_length=800)


async def _executer_publication_carrousel(job_id: str, carrousel_id: str, nb_slides: int, legende: str) -> None:
    debut = time.time()
    try:
        images = [carrousel.url_slide(carrousel_id, i) for i in range(nb_slides)]
        async with httpx.AsyncClient(timeout=150) as client:
            resp = await client.post(
                settings.n8n_instagram_carrousel_url,
                json={"mot_de_passe": settings.admin_password, "caption": legende, "images": images},
            )
        if resp.status_code != 200:
            erreur = "La publication a échoué côté automatisation (n8n). Vérifie l'exécution dans n8n pour le détail."
            _JOBS_CARROUSEL.echouer(job_id, erreur)
            _enregistrer_historique("(carrousel)", "carrousel", "", "", legende, debut, statut="erreur", erreur=erreur)
            return
        _JOBS_CARROUSEL.terminer(job_id, {"resultat": resp.text})
        _enregistrer_historique("(carrousel)", "carrousel", "", "", legende, debut, statut="publie", resultat=resp.text)
    except httpx.TimeoutException:
        erreur = "Délai dépassé en attendant la fin de la publication."
        _JOBS_CARROUSEL.echouer(job_id, erreur)
        _enregistrer_historique("(carrousel)", "carrousel", "", "", legende, debut, statut="erreur", erreur=erreur)
    except Exception as exc:  # noqa: BLE001 — remonter un message plutôt qu'un 500 opaque
        erreur = f"Erreur inattendue : {exc}"
        _JOBS_CARROUSEL.echouer(job_id, erreur)
        _enregistrer_historique("(carrousel)", "carrousel", "", "", legende, debut, statut="erreur", erreur=erreur)


@router.post("/carrousel/publier")
async def publier_carrousel(requete: CarrouselPublierRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    if not settings.admin_password:
        raise HTTPException(400, "Mot de passe non configuré côté serveur (IAEASY_ADMIN_PASSWORD).")
    if not re.fullmatch(r"[0-9a-f]{8,32}", requete.carrousel_id):
        raise HTTPException(400, "Identifiant de carrousel invalide.")
    try:
        job_id = _JOBS_CARROUSEL.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    asyncio.create_task(
        _executer_publication_carrousel(job_id, requete.carrousel_id, requete.nb_slides, requete.legende)
    )
    return {"job_id": job_id}


@router.get("/carrousel/publier/{job_id}")
def publier_carrousel_statut(job_id: str):
    job = _JOBS_CARROUSEL.get(job_id)
    if job is None:
        raise HTTPException(404, "Job inconnu.")
    if job["status"] == "en_cours":
        return {"status": "en_cours"}
    if job["status"] == "erreur":
        return {"status": "erreur", "erreur": job.get("erreur")}
    return {"status": job["status"], **job.get("fin_extra", {})}


# ---------------------------------------------------------------------------
# Story — format 1080x1920, une seule image, pas de légende côté API Instagram (contrairement
# au post/carrousel) : juste une accroche courte incrustée dans le visuel.
# ---------------------------------------------------------------------------

_JOBS_STORY = JobStore(max_concurrents=1, max_conserves=20)


class StoryGenererRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    sujet: str = Field(min_length=3, max_length=500)
    ton: str = Field(default=_TON_DEFAUT, max_length=20)
    secteur: str = Field(default=_SECTEUR_DEFAUT, max_length=20)
    # 1 = story classique (une seule carte) ; >1 = plusieurs cartes publiées à la suite (une
    # accroche par point d'un plan multi-slides, même génération que le carrousel/reel) —
    # l'équivalent story d'un carrousel, puisqu'Instagram ne permet pas plusieurs écrans dans
    # UNE story mais accepte plusieurs stories consécutives que le viewer feuillette pareil.
    nb_scenes: int = Field(default=1, ge=1, le=6)
    effet: str = Field(default=effets.DEFAUT, max_length=30)
    connaissance: str = Field(default="aucune", max_length=30)


@router.post("/story/generer")
async def generer_story(requete: StoryGenererRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    instruction_ton = _TONS.get(requete.ton, _TONS[_TON_DEFAUT])
    instruction_secteur = _instruction_secteur_carrousel(requete.secteur)
    effet = requete.effet if requete.effet in effets.PRESETS else effets.DEFAUT
    connaissance_bloc = _bloc_connaissance(requete.connaissance)
    try:
        if requete.nb_scenes <= 1:
            textes = [await story.generer_texte(requete.sujet, instruction_ton, instruction_secteur, connaissance_bloc)]
        else:
            plan = await carrousel.generer_plan(
                requete.sujet, instruction_ton, instruction_secteur, requete.nb_scenes, "", connaissance_bloc
            )
            textes = [s.get("titre", "") for s in plan["slides"]]
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la génération de la story : {exc}") from exc

    story_ids = []
    for texte in textes:
        sid = uuid.uuid4().hex[:12]
        story.sauvegarder_story(sid, story.rendre_story(texte, effet))
        story_ids.append(sid)

    return {
        "story_id": ",".join(story_ids),
        "story_ids": story_ids,
        "textes": textes,
        "image_urls": [story.url_story(sid) for sid in story_ids],
    }


@router.get("/story/{story_id}.jpg")
def servir_story(story_id: str):
    # Route publique délibérément SANS mot de passe — même raisonnement que pour les slides de
    # carrousel : les serveurs de Meta doivent pouvoir récupérer l'image pour publier la story.
    if not re.fullmatch(r"[0-9a-f]{8,32}", story_id):
        raise HTTPException(404, "Story introuvable.")
    chemin = story.chemin_story(story_id)
    if chemin is None:
        raise HTTPException(404, "Story introuvable.")
    return FileResponse(chemin, media_type="image/jpeg")


class StoryPublierRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    # Une ou plusieurs stories séparées par des virgules (plusieurs cartes à la suite) — voir
    # StoryGenererRequest.nb_scenes.
    story_id: str = Field(max_length=200)


def _story_ids_valides(story_id: str) -> list[str] | None:
    ids = story_id.split(",")
    if not ids or not all(re.fullmatch(r"[0-9a-f]{8,32}", sid) for sid in ids):
        return None
    return ids


async def _executer_publication_story(job_id: str, story_id: str) -> None:
    debut = time.time()
    ids = story_id.split(",")
    publiees = 0
    try:
        async with httpx.AsyncClient(timeout=150) as client:
            for sid in ids:
                resp = await client.post(
                    settings.n8n_instagram_story_url,
                    json={"mot_de_passe": settings.admin_password, "image_url": story.url_story(sid)},
                )
                if resp.status_code != 200:
                    # Les cartes déjà publiées avant l'échec sont réelles et ne peuvent pas être
                    # annulées — le message doit le dire explicitement plutôt que de laisser
                    # croire à un échec total.
                    erreur = (
                        f"Publication interrompue après {publiees}/{len(ids)} carte(s) publiée(s) "
                        "— échec côté automatisation (n8n), vérifie l'exécution dans n8n."
                    )
                    _JOBS_STORY.echouer(job_id, erreur)
                    _enregistrer_historique("(story)", "story", "", "", "", debut, statut="erreur", erreur=erreur)
                    return
                publiees += 1
        _JOBS_STORY.terminer(job_id, {"resultat": f"{publiees} carte(s) publiée(s)"})
        _enregistrer_historique("(story)", "story", "", "", "", debut, statut="publie", resultat=f"{publiees} carte(s)")
    except httpx.TimeoutException:
        erreur = f"Délai dépassé après {publiees}/{len(ids)} carte(s) publiée(s)."
        _JOBS_STORY.echouer(job_id, erreur)
        _enregistrer_historique("(story)", "story", "", "", "", debut, statut="erreur", erreur=erreur)
    except Exception as exc:  # noqa: BLE001 — remonter un message plutôt qu'un 500 opaque
        erreur = f"Erreur inattendue après {publiees}/{len(ids)} carte(s) : {exc}"
        _JOBS_STORY.echouer(job_id, erreur)
        _enregistrer_historique("(story)", "story", "", "", "", debut, statut="erreur", erreur=erreur)


@router.post("/story/publier")
async def publier_story(requete: StoryPublierRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    if not settings.admin_password:
        raise HTTPException(400, "Mot de passe non configuré côté serveur (IAEASY_ADMIN_PASSWORD).")
    if _story_ids_valides(requete.story_id) is None:
        raise HTTPException(400, "Identifiant de story invalide.")
    try:
        job_id = _JOBS_STORY.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    asyncio.create_task(_executer_publication_story(job_id, requete.story_id))
    return {"job_id": job_id}


@router.get("/story/publier/{job_id}")
def publier_story_statut(job_id: str):
    job = _JOBS_STORY.get(job_id)
    if job is None:
        raise HTTPException(404, "Job inconnu.")
    if job["status"] == "en_cours":
        return {"status": "en_cours"}
    if job["status"] == "erreur":
        return {"status": "erreur", "erreur": job.get("erreur")}
    return {"status": job["status"], **job.get("fin_extra", {})}


# ---------------------------------------------------------------------------
# Reel — vidéo verticale ~14s, même visuel de marque qu'une story mais animée (Ken Burns) et
# sonorisée d'une ambiance libre de droits (CC0, voir instagram/musiques/LICENCE.md). Publication
# Reels asynchrone côté Meta (contrairement à une image) : créer, attendre le traitement, publier.
# ---------------------------------------------------------------------------

_JOBS_REEL = JobStore(max_concurrents=1, max_conserves=10)


@router.get("/reel/musiques")
def lister_musiques_reel():
    return [{"id": k, "label": v["label"], "categorie": v["categorie"]} for k, v in reel.MUSIQUES.items()]


@router.get("/reel/musiques/{cle}.mp3")
def servir_musique_reel(cle: str):
    # Route publique délibérément SANS mot de passe — juste un aperçu audio pour choisir
    # l'ambiance dans l'IHM, aucune donnée sensible (les fichiers sont déjà CC0/publics).
    chemin = reel.chemin_musique(cle)
    if chemin is None:
        raise HTTPException(404, "Musique introuvable.")
    return FileResponse(chemin, media_type="audio/mpeg")


class ReelGenererRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    sujet: str = Field(min_length=3, max_length=500)
    ton: str = Field(default=_TON_DEFAUT, max_length=20)
    secteur: str = Field(default=_SECTEUR_DEFAUT, max_length=20)
    musique: str = Field(default=reel.MUSIQUE_DEFAUT, max_length=30)
    # 1 = reel classique (une seule accroche) ; >1 = reel façon carrousel, une scène par point
    # d'un plan multi-slides (même génération que le carrousel photo).
    nb_scenes: int = Field(default=1, ge=1, le=6)
    effet: str = Field(default=effets.DEFAUT, max_length=30)
    connaissance: str = Field(default="aucune", max_length=30)


@router.post("/reel/generer")
async def generer_reel(requete: ReelGenererRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    instruction_ton = _TONS.get(requete.ton, _TONS[_TON_DEFAUT])
    effet = requete.effet if requete.effet in effets.PRESETS else effets.DEFAUT
    connaissance_bloc = _bloc_connaissance(requete.connaissance)
    try:
        if requete.nb_scenes <= 1:
            instruction_secteur = _instruction_secteur_carrousel(requete.secteur)
            texte = await story.generer_texte(requete.sujet, instruction_ton, instruction_secteur, connaissance_bloc)
            legende, _regenere = await _generer_legende(requete.sujet, requete.ton, requete.secteur, requete.connaissance)
            # ffmpeg (subprocess bloquant, ~15-20s) — dans un thread pour ne pas geler la boucle
            # asyncio pendant le rendu, comme le reste de l'API continue de répondre ailleurs.
            reel_id = await asyncio.to_thread(reel.rendre_reel, texte, requete.musique, effet)
        else:
            instruction_secteur = _instruction_secteur_carrousel(requete.secteur)
            plan = await carrousel.generer_plan(
                requete.sujet, instruction_ton, instruction_secteur, requete.nb_scenes,
                _hashtags_suggeres(requete.secteur), connaissance_bloc,
            )
            titres = [s.get("titre", "") for s in plan["slides"]]
            texte = " · ".join(titres)
            legende = plan.get("legende", "")
            reel_id = await asyncio.to_thread(reel.rendre_reel_multiscenes, titres, requete.musique, 3.5, effet)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Erreur pendant la génération du reel : {exc}") from exc
    except Exception as exc:  # noqa: BLE001 — ffmpeg peut échouer pour mille raisons (fichier, codec…)
        raise HTTPException(502, f"Erreur pendant le rendu vidéo : {exc}") from exc

    return {"reel_id": reel_id, "texte": texte, "legende": legende, "video_url": reel.url_reel(reel_id)}


@router.get("/reel/{reel_id}.mp4")
def servir_reel(reel_id: str):
    # Route publique délibérément SANS mot de passe — même raisonnement que pour les stories et
    # slides de carrousel : les serveurs de Meta doivent pouvoir récupérer la vidéo pour la publier.
    if not re.fullmatch(r"[0-9a-f]{8,32}", reel_id):
        raise HTTPException(404, "Reel introuvable.")
    chemin = reel.chemin_reel(reel_id)
    if chemin is None:
        raise HTTPException(404, "Reel introuvable.")
    return FileResponse(chemin, media_type="video/mp4")


class ReelPublierRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    reel_id: str = Field(max_length=32)
    legende: str = Field(default="", max_length=800)


async def _executer_publication_reel(job_id: str, reel_id: str, legende: str) -> None:
    debut = time.time()
    try:
        video_url = reel.url_reel(reel_id)
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                settings.n8n_instagram_reel_creer_url,
                json={"mot_de_passe": settings.admin_password, "video_url": video_url, "caption": legende},
            )
        if resp.status_code != 200:
            raise RuntimeError("La création du Reel a été refusée côté automatisation (n8n).")
        creation_id = resp.json().get("id")
        if not creation_id:
            raise RuntimeError(f"Réponse inattendue à la création du Reel : {resp.text[:300]}")

        # Le traitement vidéo par Meta est asynchrone (contrairement à une image, publiée tout de
        # suite) — on vérifie périodiquement l'état plutôt que de tenter de publier immédiatement
        # un creation_id pas encore prêt.
        statut_final = None
        for _ in range(24):  # ~2 minutes maximum
            await asyncio.sleep(5)
            async with httpx.AsyncClient(timeout=30) as client:
                resp_statut = await client.post(
                    settings.n8n_instagram_reel_statut_url,
                    json={"mot_de_passe": settings.admin_password, "creation_id": creation_id},
                )
            statut_final = resp_statut.json().get("status_code")
            if statut_final in ("FINISHED", "ERROR"):
                break
        if statut_final != "FINISHED":
            raise RuntimeError(
                "Le traitement de la vidéo par Instagram a échoué ou pris trop de temps."
                if statut_final == "ERROR"
                else "Le traitement de la vidéo prend plus de 2 minutes — réessaie plus tard."
            )

        async with httpx.AsyncClient(timeout=60) as client:
            resp_pub = await client.post(
                settings.n8n_instagram_reel_publier_url,
                json={"mot_de_passe": settings.admin_password, "creation_id": creation_id},
            )
        if resp_pub.status_code != 200:
            raise RuntimeError("La publication a échoué côté automatisation (n8n).")
        _JOBS_REEL.terminer(job_id, {"resultat": resp_pub.text})
        _enregistrer_historique("(reel)", "reel", "", "", legende, debut, statut="publie", resultat=resp_pub.text)
    except Exception as exc:  # noqa: BLE001 — remonter un message plutôt qu'un 500 opaque
        erreur = str(exc)
        _JOBS_REEL.echouer(job_id, erreur)
        _enregistrer_historique("(reel)", "reel", "", "", legende, debut, statut="erreur", erreur=erreur)


@router.post("/reel/publier")
async def publier_reel(requete: ReelPublierRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    if not settings.admin_password:
        raise HTTPException(400, "Mot de passe non configuré côté serveur (IAEASY_ADMIN_PASSWORD).")
    if not re.fullmatch(r"[0-9a-f]{8,32}", requete.reel_id):
        raise HTTPException(400, "Identifiant de reel invalide.")
    try:
        job_id = _JOBS_REEL.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    asyncio.create_task(_executer_publication_reel(job_id, requete.reel_id, requete.legende))
    return {"job_id": job_id}


@router.get("/reel/publier/{job_id}")
def publier_reel_statut(job_id: str):
    job = _JOBS_REEL.get(job_id)
    if job is None:
        raise HTTPException(404, "Job inconnu.")
    if job["status"] == "en_cours":
        return {"status": "en_cours"}
    if job["status"] == "erreur":
        return {"status": "erreur", "erreur": job.get("erreur")}
    return {"status": job["status"], **job.get("fin_extra", {})}


# ---------------------------------------------------------------------------
# Planification — brouillons (publication différée à la main) et programmation (date/heure
# précise, déclenchée automatiquement par une boucle de fond démarrée depuis main.py).
# ---------------------------------------------------------------------------


class PlanifierRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    type: str = Field(pattern="^(simple|carrousel|story|reel)$")
    sujet: str = Field(default="", max_length=500)
    ton: str = Field(default=_TON_DEFAUT, max_length=20)
    secteur: str = Field(default=_SECTEUR_DEFAUT, max_length=20)
    # Vide et non requis pour une story/un reel (l'API Instagram n'accepte pas de légende sur une
    # story ; une légende de reel est optionnelle, contrairement au post simple).
    legende: str = Field(default="", max_length=800)
    image: str = Field(default="aleatoire", max_length=20)
    carrousel_id: str = Field(default="", max_length=32)
    nb_slides: int = Field(default=0, ge=0, le=8)
    story_id: str = Field(default="", max_length=200)
    reel_id: str = Field(default="", max_length=32)
    # Horodatage unix (secondes) ; absent/None = brouillon (jamais publié tout seul).
    programme_pour: float | None = None


@router.post("/planifier")
def planifier(requete: PlanifierRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    if requete.type == "carrousel":
        if not re.fullmatch(r"[0-9a-f]{8,32}", requete.carrousel_id) or requete.nb_slides < 1:
            raise HTTPException(400, "Carrousel invalide — génère-le d'abord via /carrousel/generer.")
    elif requete.type == "story":
        if _story_ids_valides(requete.story_id) is None:
            raise HTTPException(400, "Story invalide — génère-la d'abord via /story/generer.")
    elif requete.type == "reel":
        if not re.fullmatch(r"[0-9a-f]{8,32}", requete.reel_id):
            raise HTTPException(400, "Reel invalide — génère-le d'abord via /reel/generer.")
    elif not requete.legende.strip():
        raise HTTPException(400, "Légende requise pour un post simple.")
    if requete.programme_pour is not None and requete.programme_pour <= time.time():
        raise HTTPException(400, "La date programmée doit être dans le futur.")

    statut = "programme" if requete.programme_pour else "brouillon"
    id_ = planificateur.creer(
        {
            "type": requete.type,
            "statut": statut,
            "programme_pour": requete.programme_pour,
            "sujet": requete.sujet,
            "ton": requete.ton,
            "secteur": requete.secteur,
            "legende": requete.legende,
            "image": requete.image,
            "carrousel_id": requete.carrousel_id,
            "nb_slides": requete.nb_slides,
            "story_id": requete.story_id,
            "reel_id": requete.reel_id,
        }
    )
    return {"id": id_}


class ListePlanificationRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


@router.post("/planifier/liste")
def lister_planifications(requete: ListePlanificationRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    return planificateur.lister()


class ActionPlanificationRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


@router.post("/planifier/{id_}/annuler")
def annuler_planification(id_: str, requete: ActionPlanificationRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    entree = planificateur.obtenir(id_)
    if entree is None:
        raise HTTPException(404, "Entrée introuvable.")
    if entree["statut"] in ("publie", "en_cours"):
        raise HTTPException(400, "Impossible d'annuler : déjà publié ou en cours de publication.")
    planificateur.supprimer(id_)
    return {"ok": True}


async def _publier_planification_simple(entree: dict) -> None:
    job_id = _JOBS.creer()
    await _executer_publication(
        job_id, entree.get("sujet", ""), entree.get("image", "aleatoire"), entree.get("ton", ""),
        entree.get("secteur", ""), entree["legende"],
    )
    job = _JOBS.get(job_id)
    if job["status"] == "erreur":
        raise RuntimeError(job.get("erreur") or "Erreur inconnue.")


async def _publier_planification_carrousel(entree: dict) -> None:
    job_id = _JOBS_CARROUSEL.creer()
    await _executer_publication_carrousel(job_id, entree["carrousel_id"], entree["nb_slides"], entree["legende"])
    job = _JOBS_CARROUSEL.get(job_id)
    if job["status"] == "erreur":
        raise RuntimeError(job.get("erreur") or "Erreur inconnue.")


async def _publier_planification_story(entree: dict) -> None:
    job_id = _JOBS_STORY.creer()
    await _executer_publication_story(job_id, entree["story_id"])
    job = _JOBS_STORY.get(job_id)
    if job["status"] == "erreur":
        raise RuntimeError(job.get("erreur") or "Erreur inconnue.")


async def _publier_planification_reel(entree: dict) -> None:
    job_id = _JOBS_REEL.creer()
    await _executer_publication_reel(job_id, entree["reel_id"], entree.get("legende", ""))
    job = _JOBS_REEL.get(job_id)
    if job["status"] == "erreur":
        raise RuntimeError(job.get("erreur") or "Erreur inconnue.")


_PUBLISHERS_PLANIFICATION = {
    "simple": _publier_planification_simple,
    "carrousel": _publier_planification_carrousel,
    "story": _publier_planification_story,
    "reel": _publier_planification_reel,
}


async def _publier_maintenant_tache(id_: str, fonction) -> None:
    try:
        await fonction(planificateur.obtenir(id_))
        planificateur.mettre_a_jour(id_, statut="publie")
    except Exception as exc:  # noqa: BLE001 — journaliser sur l'entrée plutôt que planter la tâche
        planificateur.mettre_a_jour(id_, statut="erreur", erreur=str(exc))


@router.post("/planifier/{id_}/publier_maintenant")
def publier_maintenant_planification(id_: str, requete: ActionPlanificationRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    entree = planificateur.obtenir(id_)
    if entree is None:
        raise HTTPException(404, "Entrée introuvable.")
    if entree["statut"] in ("publie", "en_cours"):
        raise HTTPException(400, "Déjà publié ou en cours de publication.")
    if not settings.admin_password:
        raise HTTPException(400, "Mot de passe non configuré côté serveur (IAEASY_ADMIN_PASSWORD).")

    planificateur.mettre_a_jour(id_, statut="en_cours")
    fonction = _PUBLISHERS_PLANIFICATION[entree["type"]]
    asyncio.create_task(_publier_maintenant_tache(id_, fonction))
    return {"ok": True}


def demarrer_planificateur() -> None:
    """Lance la boucle de fond qui déclenche les posts programmés arrivés à échéance — appelé
    une fois depuis le lifespan de main.py."""
    asyncio.create_task(planificateur.boucle(_PUBLISHERS_PLANIFICATION))
