"""API du module Brief IA — démo interactive du pipeline de génération de brief d'animation
commerciale (voir pipeline.py). Suit le même patron que aide/router.py : JobStore + flux_sse,
job en tâche de fond plutôt qu'une réponse bloquante.

Une "conversation" (thread_id) peut traverser PLUSIEURS jobs JobStore successifs : un premier job
jusqu'à la pause de validation humaine, puis un nouveau job à chaque reprise (voir _executer_*).
Le thread_id (= l'id du tout premier job) reste stable et sert de clé à `_ETATS_PENDANTS`, qui
retient le contexte le temps qu'un humain valide ou demande une révision — pas besoin d'un
checkpointer persistant comme en vraie prod multi-instance, iaeasy tourne en un seul process.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..core.jobs import JobStore, flux_sse
from . import donnees, pipeline

router = APIRouter(prefix="/brief-ia", tags=["brief_ia"])

# Chaque run fait plusieurs vrais appels Ollama (qwen2.5:7b-instruct) — même discipline que les
# autres endpoints coûteux du site (aide/théâtre) : concurrence bornée.
_JOBS = JobStore(max_concurrents=3, max_conserves=50)

_LABELS_ETAPES = {
    "extract_marque": "Lecture de la charte de marque",
    "map_sources": "Croisement des données (catalogue, prix, calendrier promo)",
    "retrieve_examples": "Recherche de briefs passés similaires",
    "generate_brief": "Rédaction du brief",
    "critique": "Relecture automatique",
}

# thread_id -> {"contexte", "charte", "exemples", "brouillon", "avis"} — l'état d'une conversation
# suspendue en attente de validation humaine.
_ETATS_PENDANTS: dict[str, dict] = {}


def _emettre_tentatives(job_id: str, tentatives: list[tuple]) -> None:
    for brief, avis in tentatives:
        _JOBS.ajouter_evenement(
            job_id,
            {
                "etape": "generate_brief",
                "libelle": _LABELS_ETAPES["generate_brief"],
                "donnees": {"brouillon": brief.model_dump()},
            },
        )
        _JOBS.ajouter_evenement(
            job_id,
            {
                "etape": "critique",
                "libelle": _LABELS_ETAPES["critique"],
                "donnees": {"avis": avis.model_dump()},
            },
        )


async def _executer_premiere_manche(job_id: str, thread_id: str) -> None:
    try:
        charte = await pipeline.extraire_charte(donnees.CHARTE_MARQUE_BRUTE)
        _JOBS.ajouter_evenement(
            job_id,
            {
                "etape": "extract_marque",
                "libelle": _LABELS_ETAPES["extract_marque"],
                "donnees": charte.model_dump(),
            },
        )

        contexte, exemples = pipeline.construire_contexte_initial()
        _JOBS.ajouter_evenement(
            job_id,
            {
                "etape": "map_sources",
                "libelle": _LABELS_ETAPES["map_sources"],
                "donnees": {"contexte": contexte},
            },
        )
        _JOBS.ajouter_evenement(
            job_id,
            {
                "etape": "retrieve_examples",
                "libelle": _LABELS_ETAPES["retrieve_examples"],
                "donnees": {"exemples": exemples},
            },
        )

        tentatives = await pipeline.generer_et_critiquer(contexte, charte, exemples, None)
        _emettre_tentatives(job_id, tentatives)
        brief, avis = tentatives[-1]

        _ETATS_PENDANTS[thread_id] = {
            "contexte": contexte,
            "charte": charte,
            "exemples": exemples,
            "brouillon": brief,
        }
        _JOBS.terminer(
            job_id,
            {
                "attente_validation": True,
                "brouillon": brief.model_dump(),
                "avis": avis.model_dump(),
                "avertissements": contexte["avertissements"],
            },
        )
    except Exception as exc:  # noqa: BLE001 — l'erreur doit remonter côté IHM, pas planter la tâche
        _JOBS.echouer(job_id, str(exc))


async def _executer_reprise(job_id: str, thread_id: str, approuve: bool, feedback: str | None) -> None:
    try:
        etat = _ETATS_PENDANTS.get(thread_id)
        if etat is None:
            raise ValueError("Cette conversation n'est plus en attente de validation.")

        if approuve:
            del _ETATS_PENDANTS[thread_id]
            _JOBS.terminer(
                job_id, {"attente_validation": False, "brief_final": etat["brouillon"].model_dump()}
            )
            return

        tentatives = await pipeline.generer_et_critiquer(
            etat["contexte"], etat["charte"], etat["exemples"], feedback
        )
        _emettre_tentatives(job_id, tentatives)
        brief, avis = tentatives[-1]

        _ETATS_PENDANTS[thread_id] = {**etat, "brouillon": brief}
        _JOBS.terminer(
            job_id,
            {
                "attente_validation": True,
                "brouillon": brief.model_dump(),
                "avis": avis.model_dump(),
                "avertissements": etat["contexte"]["avertissements"],
            },
        )
    except Exception as exc:  # noqa: BLE001
        _JOBS.echouer(job_id, str(exc))


@router.get("/mise-en-situation")
def mise_en_situation():
    """Contenu narratif + données mockées affichées avant de lancer une génération."""
    return {
        "campagne": donnees.CAMPAGNE,
        "charte_brute": donnees.CHARTE_MARQUE_BRUTE,
        "produits": donnees.PIM_PRODUITS,
    }


@router.post("/demarrer")
async def demarrer():
    try:
        job_id = _JOBS.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    # Le premier job_id sert aussi de thread_id pour toute la conversation — voir docstring du module.
    asyncio.create_task(_executer_premiere_manche(job_id, job_id))
    return {"job_id": job_id, "thread_id": job_id}


@router.get("/{job_id}/stream")
async def stream(job_id: str):
    return StreamingResponse(flux_sse(_JOBS, job_id, "etape"), media_type="text/event-stream")


class ValidationRequest(BaseModel):
    approuve: bool
    feedback: str | None = Field(default=None, max_length=1000)


@router.post("/{thread_id}/valider")
async def valider(thread_id: str, requete: ValidationRequest):
    if thread_id not in _ETATS_PENDANTS:
        raise HTTPException(404, "Cette conversation n'est plus en attente de validation.")

    try:
        job_id = _JOBS.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    asyncio.create_task(_executer_reprise(job_id, thread_id, requete.approuve, requete.feedback))
    return {"job_id": job_id}
