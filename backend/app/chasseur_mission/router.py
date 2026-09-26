from datetime import date
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from ..admin.router import _verifier_mot_de_passe
from . import jobs as job_store
from . import recherche, stockage

router = APIRouter(prefix="/chasseur-mission", tags=["chasseur-mission"])


class Mission(BaseModel):
    id: str = Field(max_length=64)
    intitule: str = Field(max_length=200)
    entreprise: str = Field(max_length=150)
    ville: str = Field(max_length=100)
    pays: Literal["France", "Maroc"]
    famille: Literal["conseil_it", "drone"]
    type_contrat: Literal["freelance", "cdi"]
    remuneration: str = Field(default="", max_length=100)
    lien: str = Field(max_length=500)
    source: str = Field(max_length=100)
    date_collecte: str = Field(max_length=20)


class MissionsAjouterRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    missions: list[Mission] = Field(max_length=200)


class MissionSupprimerRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    mission_id: str = Field(max_length=64)


class RechercheRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)
    mots_cles: str = Field(default="", max_length=300)
    pays: list[Literal["France", "Maroc"]] = Field(default_factory=lambda: ["France", "Maroc"])


class VerifRequest(BaseModel):
    mot_de_passe: str = Field(max_length=200)


# Toute la page est protégée (usage personnel, pas de contenu public) — mot de passe toujours
# dans le corps d'une requête POST, jamais en query string (voir admin/router.py), donc même les
# lectures passent par POST ici.


@router.post("/missions/lister")
def lister_missions(requete: VerifRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    return stockage.lire_toutes()


@router.post("/missions/ajouter")
def ajouter_missions(requete: MissionsAjouterRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    return stockage.ajouter([m.model_dump() for m in requete.missions])


@router.post("/missions/supprimer")
def supprimer_mission(requete: MissionSupprimerRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    if not stockage.supprimer(requete.mission_id):
        raise HTTPException(404, "Mission introuvable.")
    return {"ok": True}


@router.post("/stats")
def stats(requete: VerifRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    missions = stockage.lire_toutes()
    total = len(missions)

    def _repartition(champ: str) -> dict:
        compteur: dict[str, int] = {}
        for m in missions:
            cle = m.get(champ, "inconnu")
            compteur[cle] = compteur.get(cle, 0) + 1
        return compteur

    # Évolution mensuelle (nombre de missions collectées par mois, selon leur date_collecte) —
    # se remplit naturellement au fil des relances ponctuelles de l'agent, jamais recalculée à
    # partir d'un flux continu.
    par_mois: dict[str, int] = {}
    for m in missions:
        d = m.get("date_collecte", "")
        cle_mois = d[:7] if len(d) >= 7 else "inconnu"
        par_mois[cle_mois] = par_mois.get(cle_mois, 0) + 1

    return {
        "total": total,
        "par_pays": _repartition("pays"),
        "par_famille": _repartition("famille"),
        "par_type_contrat": _repartition("type_contrat"),
        "par_source": _repartition("source"),
        "par_mois": dict(sorted(par_mois.items())),
        "derniere_collecte": max((m.get("date_collecte", "") for m in missions), default=None),
    }


@router.post("/rechercher")
async def lancer_recherche(requete: RechercheRequest, tasks: BackgroundTasks):
    _verifier_mot_de_passe(requete.mot_de_passe)
    job_id = job_store.creer_job()

    async def _executer() -> None:
        try:
            resultat = await recherche.rechercher_missions(requete.mots_cles, requete.pays)
            valides: list[dict] = []
            rejetees = 0
            for brute in resultat["missions"]:
                try:
                    valides.append(Mission(**brute).model_dump())
                except Exception:
                    rejetees += 1
            ajout = stockage.ajouter(valides)
            job_store.terminer_job(
                job_id,
                {
                    **ajout,
                    "rejetees": rejetees,
                    "notes": resultat["notes"],
                    "recherches_effectuees": resultat["nb_recherches"],
                },
            )
        except Exception as e:  # une recherche qui échoue ne doit pas planter le job en silence
            job_store.echouer_job(job_id, str(e) or repr(e) or "Erreur inconnue (probablement un délai dépassé).")

    tasks.add_task(_executer)
    return {"job_id": job_id}


@router.post("/rechercher/{job_id}")
def statut_recherche(job_id: str, requete: VerifRequest):
    _verifier_mot_de_passe(requete.mot_de_passe)
    job = job_store.lire_job(job_id)
    if job is None:
        raise HTTPException(404, "Recherche introuvable.")
    return job


def date_du_jour() -> str:
    return date.today().isoformat()
