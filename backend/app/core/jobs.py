import asyncio
import json
import uuid

# Découple un traitement long (chat, comparaison de modèles, entraînement) de la connexion HTTP
# du client : le traitement continue côté serveur (asyncio.create_task) même si le client change
# d'onglet ou d'application sur mobile et perd sa connexion — il lui suffit de se reconnecter au
# flux SSE pour reprendre là où il en était, plutôt que de perdre le travail déjà effectué.


class JobStore:
    def __init__(self, max_concurrents: int, max_conserves: int):
        self._jobs: dict[str, dict] = {}
        self._max_concurrents = max_concurrents
        self._max_conserves = max_conserves

    def creer(self) -> str:
        en_cours = sum(1 for j in self._jobs.values() if j["status"] == "en_cours")
        if en_cours >= self._max_concurrents:
            raise ValueError(
                f"Trop de traitements en cours ({en_cours}/{self._max_concurrents}). "
                "Réessayez dans quelques instants."
            )

        if len(self._jobs) >= self._max_conserves:
            plus_ancien = next(iter(self._jobs))
            self._jobs.pop(plus_ancien, None)

        job_id = uuid.uuid4().hex[:8]
        self._jobs[job_id] = {"status": "en_cours", "evenements": [], "erreur": None, "fin_extra": {}}
        return job_id

    def get(self, job_id: str) -> dict | None:
        return self._jobs.get(job_id)

    def ajouter_evenement(self, job_id: str, evenement: dict) -> None:
        self._jobs[job_id]["evenements"].append(evenement)

    def terminer(self, job_id: str, extra: dict | None = None) -> None:
        self._jobs[job_id]["status"] = "termine"
        if extra:
            self._jobs[job_id]["fin_extra"] = extra

    def echouer(self, job_id: str, erreur: str) -> None:
        self._jobs[job_id]["status"] = "erreur"
        self._jobs[job_id]["erreur"] = erreur


async def flux_sse(store: JobStore, job_id: str, nom_evenement: str = "evenement"):
    """Génère un flux SSE : rejoue tous les événements connus à chaque (re)connexion — c'est au
    client de repartir de zéro sur l'événement natif EventSource 'open' pour éviter les doublons
    lors d'une reconnexion (voir suivreFlux côté frontend)."""
    envoyes = 0
    while True:
        job = store.get(job_id)
        if job is None:
            yield "event: erreur\ndata: job inconnu\n\n"
            return

        evenements = job["evenements"]
        while envoyes < len(evenements):
            yield f"event: {nom_evenement}\ndata: {json.dumps(evenements[envoyes])}\n\n"
            envoyes += 1

        if job["status"] != "en_cours":
            payload = json.dumps({"status": job["status"], "erreur": job.get("erreur"), **job.get("fin_extra", {})})
            yield f"event: fin\ndata: {payload}\n\n"
            return

        await asyncio.sleep(0.4)
