import json
from pathlib import Path

from ..core.config import settings

# Petite base de connaissances par sujet, injectée dans le prompt via {{CONNAISSANCE}} — pas une
# vraie base vectorielle (embeddings/ChromaDB) : le corpus est volontairement restreint à
# quelques sujets récurrents (2 applications + une thématique), une vraie base RAG serait
# disproportionnée pour ce volume. Même mécanique de surcharge éditable que prompts.py.
_FICHIER = Path(settings.data_dir) / "instagram_connaissances.json"

DEFAUTS = {
    "lesensia": {
        "titre": "Lesensia (lesensia.com)",
        "texte": (
            "Lesensia est une plateforme SaaS de gestion pour les artisans et entreprises du "
            "bâtiment (BTP), développée par TKonsulting. Elle centralise en un seul endroit ce qui "
            "est habituellement dispersé entre plusieurs carnets et applications : devis, "
            "factures, bons de livraison, avec numérotation et statuts métier réels (brouillon, "
            "envoyé, accepté, facturé...). Elle inclut un estimateur de devis assisté par IA "
            "(moteur statistique croisé avec une IA de raisonnement, avec des garde-fous pour "
            "éviter les dérapages de prix), un chronométrage des interventions sur chantier "
            "(application mobile, plusieurs ouvriers simultanément, lié directement à la ligne de "
            "devis concernée), et un catalogue de matériaux avec prix par artisan. Elle gère aussi "
            "la facturation électronique (norme Factur-X). Accessible du téléphone comme du "
            "bureau, hébergée en France. Public cible : artisans, chefs de chantier, TPE/PME du "
            "bâtiment qui jonglent aujourd'hui entre plusieurs carnets et applications."
        ),
        "cta": "Termine par un appel à l'action explicite qui nomme le site : invite à découvrir lesensia.com ou à demander une démo gratuite.",
        "cta_texte": "Découvrez lesensia.com ou demandez une démo gratuite.",
    },
    "nextcloud": {
        "titre": "Nextcloud — espace client TKonsulting",
        "texte": (
            "TKonsulting propose à ses clients un espace collaboratif privé basé sur Nextcloud, "
            "hébergé sur une infrastructure propre (pas un cloud américain générique) avec une "
            "identité visuelle personnalisée noir & or aux couleurs de TKonsulting. Chaque client "
            "dispose de son propre espace sécurisé pour partager des documents, suivre l'avancement "
            "d'une mission et collaborer, sans dépendre d'un outil grand public (Google Drive, "
            "Dropbox...). La sécurité de l'infrastructure a été durcie spécifiquement pour cet "
            "usage professionnel. Cet espace illustre concrètement l'approche de TKonsulting : du "
            "digital sur mesure, hébergé en interne, plutôt qu'un abonnement à un service tiers."
        ),
        "cta": "Termine par une invitation explicite à échanger sur la mise en place d'un espace client équivalent (écrire en message, pas de lien).",
        "cta_texte": "Écrivez-nous en message pour un espace client équivalent.",
    },
    "knowledge_management": {
        "titre": "Knowledge Management (gestion des connaissances)",
        "texte": (
            "Le Knowledge Management (KM) consiste à transformer le savoir-faire dispersé dans une "
            "organisation — souvent uniquement dans la tête de quelques personnes clés — en un "
            "actif collectif documenté et transmissible. Sans démarche KM, un départ ou une "
            "réorganisation peut faire perdre des années d'expertise du jour au lendemain. "
            "TKonsulting structure sa démarche KM en s'appuyant sur la norme internationale ISO "
            "30401, en 6 étapes concrètes : (1) Audit des connaissances — cartographier les savoirs "
            "critiques et les zones de vulnérabilité ; (2) Structuration & documentation — "
            "procédures, bases de connaissances, wikis métier ; (3) Digital Workplace & portail "
            "interne — un environnement numérique centralisé pour retrouver l'information ; (4) "
            "Communautés de pratique — animer le partage entre experts internes ; (5) IA & "
            "recherche sémantique — indexation intelligente des documents, assistants "
            "conversationnels sur les données de l'entreprise ; (6) Conduite du changement — "
            "formation, adoption des outils, mesure de la maturité. Bénéfices concrets : moins de "
            "silos, décisions plus rapides, continuité assurée même en cas de départ d'un "
            "collaborateur clé."
        ),
        "cta": "Termine par une invitation explicite à demander un audit KM (écrire en message, pas de lien).",
        "cta_texte": "Écrivez-nous en message pour un audit KM.",
    },
}


def _lire_overrides() -> dict:
    if not _FICHIER.exists():
        return {}
    try:
        return json.loads(_FICHIER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def lire_tous() -> dict:
    overrides = _lire_overrides()
    resultat = {}
    for cle, defaut in DEFAUTS.items():
        o = overrides.get(cle, {})
        resultat[cle] = {
            "titre": o.get("titre", defaut["titre"]),
            "texte": o.get("texte", defaut["texte"]),
            "cta": o.get("cta", defaut.get("cta", "")),
            "cta_texte": o.get("cta_texte", defaut.get("cta_texte", "")),
        }
    return resultat


def lire_texte(cle: str) -> str:
    if cle not in DEFAUTS:
        return ""
    overrides = _lire_overrides()
    return overrides.get(cle, {}).get("texte", DEFAUTS[cle]["texte"])


def lire_cta(cle: str) -> str:
    if cle not in DEFAUTS:
        return ""
    overrides = _lire_overrides()
    return overrides.get(cle, {}).get("cta", DEFAUTS[cle].get("cta", ""))


def lire_cta_texte(cle: str) -> str:
    """Phrase de CTA courte et prête à afficher, insérée de façon déterministe sur la dernière
    slide d'un carrousel — contrairement à `cta` (une consigne pour le LLM), le modèle oubliait
    trop souvent d'appliquer la consigne sur le texte de la slide (constaté 0/3 en test), d'où ce
    filet de sécurité qui ne dépend plus de sa docilité."""
    if cle not in DEFAUTS:
        return ""
    overrides = _lire_overrides()
    return overrides.get(cle, {}).get("cta_texte", DEFAUTS[cle].get("cta_texte", ""))


def enregistrer(cle: str, titre: str, texte: str, cta: str = "", cta_texte: str = "") -> None:
    if cle not in DEFAUTS:
        raise ValueError(f"Sujet de connaissance inconnu : {cle}")
    overrides = _lire_overrides()
    overrides[cle] = {"titre": titre, "texte": texte, "cta": cta, "cta_texte": cta_texte}
    _FICHIER.write_text(json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8")


def reinitialiser(cle: str) -> None:
    overrides = _lire_overrides()
    overrides.pop(cle, None)
    _FICHIER.write_text(json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8")
