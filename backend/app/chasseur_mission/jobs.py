import uuid

# En mémoire uniquement : une recherche perdue à un redémarrage n'est pas grave (il suffit de
# relancer depuis l'IHM), contrairement aux jobs de régénération de catalogue qui, eux, doivent
# survivre à un restart backend.
_jobs: dict[str, dict] = {}


def creer_job() -> str:
    job_id = uuid.uuid4().hex[:12]
    _jobs[job_id] = {"statut": "en_cours", "resultat": None, "erreur": None}
    return job_id


def lire_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def terminer_job(job_id: str, resultat: dict) -> None:
    _jobs[job_id] = {"statut": "termine", "resultat": resultat, "erreur": None}


def echouer_job(job_id: str, erreur: str) -> None:
    _jobs[job_id] = {"statut": "erreur", "resultat": None, "erreur": erreur}
