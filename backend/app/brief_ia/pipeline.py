"""Pipeline de génération de brief, sur Ollama (qwen2.5:7b-instruct — même modèle que l'aide et
le Théâtre, choisi pour sa fiabilité à suivre une consigne de format JSON strict).

Remplace une première version basée sur LangGraph + Vertex AI/Gemini : le choix initial (rester
fidèle au squelette `ecommerce-brief-agent` livré séparément) impliquait un compte GCP facturé,
jugé disproportionné pour une simple démo interne — cette version retombe sur les mêmes outils
que le reste d'iaeasy (appels Ollama en REST direct, JSON extrait et validé à la main), au prix
de perdre la reprise automatique via checkpointer LangGraph : ici, l'état "en attente de
validation" vit dans un simple dict en mémoire (voir router.py), suffisant puisqu'iaeasy tourne
en un seul process.
"""

from __future__ import annotations

import json
import re
from datetime import date, timedelta

from ..core.ollama_client import ollama
from . import donnees
from .schemas import AvisRelecteur, BriefCreatif, CharteMarque

_MODELE = "qwen2.5:7b-instruct"
_MAX_TENTATIVES = 2
_MAX_ESSAIS_JSON = 3


async def _appeler_json(prompt: str, schema_cls):
    """Appelle Ollama et valide la réponse contre un schéma Pydantic — même pattern que
    `_valider_episode` du Théâtre : extraction du 1er objet JSON de la réponse brute, retenté
    plusieurs fois avant d'abandonner (un LLM local peut renvoyer un JSON mal formé ou entouré de
    texte malgré la consigne)."""
    derniere_erreur: Exception | None = None
    for _ in range(_MAX_ESSAIS_JSON):
        try:
            brut = await ollama.generate(_MODELE, prompt)
            match = re.search(r"\{.*\}", brut, re.DOTALL)
            if not match:
                raise ValueError("Pas d'objet JSON trouvé dans la réponse du modèle.")
            return schema_cls.model_validate(json.loads(match.group(0)))
        except Exception as exc:  # noqa: BLE001 — on retente, l'erreur finale est levée après coup
            derniere_erreur = exc
    raise RuntimeError(
        f"Le modèle n'a pas produit de JSON valide après {_MAX_ESSAIS_JSON} tentatives "
        f"({derniere_erreur})."
    )


async def extraire_charte(texte_charte: str) -> CharteMarque:
    prompt = (
        "Tu extrais une charte de marque structurée à partir d'un texte brut. Ne devine jamais "
        "une information absente. Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte "
        'autour, exactement au format : {"ton": "...", "palette": ["#RRGGBB", ...], '
        '"mots_interdits": ["...", ...], "mention_obligatoire": "..."}\n\n'
        f"Texte : {texte_charte}"
    )
    return await _appeler_json(prompt, CharteMarque)


def _corriger_deadline(brief: BriefCreatif, contexte: dict) -> BriefCreatif:
    """Garde-fou déterministe : la deadline ne doit jamais dépasser le début de la promotion —
    pas la peine de compter sur le LLM pour une contrainte simplement vérifiable en code."""
    debut_promo = date.fromisoformat(contexte["campagne"]["date_debut"])
    try:
        deadline = date.fromisoformat(brief.deadline)
    except ValueError:
        deadline = debut_promo - timedelta(days=3)
    if deadline >= debut_promo:
        deadline = debut_promo - timedelta(days=3)
    brief.deadline = deadline.isoformat()
    return brief


async def generer_brief(
    contexte: dict, charte: CharteMarque, exemples: list[dict], feedback: str
) -> BriefCreatif:
    prompt = (
        "Tu es directeur·rice artistique en motion design e-commerce. À partir du contexte de "
        "campagne, de la charte de marque et d'exemples de briefs qui ont bien fonctionné, "
        "rédige un brief créatif structuré.\n\n"
        "Règles strictes : n'invente jamais un prix, une remise ou une mention légale — reprends "
        "exactement ceux du contexte fourni. produits_vedettes doit être une liste de SKUs "
        "présents dans le contexte, jamais inventés. Si un feedback de relecture est fourni, "
        "corrige précisément les points soulevés.\n\n"
        "Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte autour, exactement au "
        'format : {"titre": "...", "objectif": "...", "message_cle": "...", '
        '"produits_vedettes": ["SKU1", ...], "ton": "...", "mentions_obligatoires": ["..."], '
        '"formats": ["9:16", "1:1"], "duree_secondes": 15, "appel_action": "...", '
        '"deadline": "AAAA-MM-JJ"}\n\n'
        f"Contexte de campagne : {json.dumps(contexte, ensure_ascii=False)}\n\n"
        f"Charte de marque : {charte.model_dump_json()}\n\n"
        f"Exemples de briefs passés ayant bien performé : {json.dumps(exemples, ensure_ascii=False)}\n\n"
        f"Feedback de la relecture précédente (vide si première génération) : {feedback or '(aucun)'}"
    )
    brief = await _appeler_json(prompt, BriefCreatif)
    return _corriger_deadline(brief, contexte)


async def critiquer(contexte: dict, charte: CharteMarque, brief: BriefCreatif) -> AvisRelecteur:
    prompt = (
        "Évalue ce brief créatif (score 1 à 5). valide=true seulement si le score est >= 4 ET "
        "qu'aucune donnée n'est inventée (prix, remise, mention légale, SKU absent du contexte).\n\n"
        "Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte autour, exactement au "
        'format : {"score": 1-5, "valide": true|false, "remarques": ["...", ...]}\n\n'
        f"Contexte de campagne : {json.dumps(contexte, ensure_ascii=False)}\n\n"
        f"Charte de marque : {charte.model_dump_json()}\n\n"
        f"Brief à évaluer : {brief.model_dump_json()}"
    )
    return await _appeler_json(prompt, AvisRelecteur)


async def generer_et_critiquer(
    contexte: dict, charte: CharteMarque, exemples: list[dict], feedback_initial: str | None
) -> list[tuple[BriefCreatif, AvisRelecteur]]:
    """Boucle génération → relecture, comme le retry `critique ⇄ generate_brief` du squelette
    LangGraph d'origine. Retourne la liste de TOUTES les tentatives (pas seulement la dernière) :
    le router en émet un événement SSE par tentative, pour montrer la reboucle à l'utilisateur
    plutôt que de la cacher.
    """
    tentatives: list[tuple[BriefCreatif, AvisRelecteur]] = []
    feedback = feedback_initial or ""
    while True:
        brief = await generer_brief(contexte, charte, exemples, feedback)
        avis = await critiquer(contexte, charte, brief)
        tentatives.append((brief, avis))
        if avis.valide or len(tentatives) >= _MAX_TENTATIVES:
            return tentatives
        feedback = " ; ".join(avis.remarques) or "Améliore la pertinence et la fidélité aux données."


def construire_contexte_initial() -> tuple[dict, list[dict]]:
    return donnees.construire_contexte_campagne(), donnees.EXEMPLES_BRIEFS_PASSES
