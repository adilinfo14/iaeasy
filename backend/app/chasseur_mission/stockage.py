import json
from pathlib import Path

from ..core.config import settings

# Persistance en fichier JSON (même principe que les autres modules du site : prompts.py,
# connaissances.py, historique.py...) — un volume de quelques centaines de missions au grand
# maximum, largement dans les limites raisonnables d'un simple fichier plutôt qu'une vraie base.
_FICHIER = Path(settings.data_dir) / "chasseur_mission.json"


def lire_toutes() -> list[dict]:
    if not _FICHIER.exists():
        return []
    try:
        return json.loads(_FICHIER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _ecrire(missions: list[dict]) -> None:
    _FICHIER.parent.mkdir(parents=True, exist_ok=True)
    _FICHIER.write_text(json.dumps(missions, ensure_ascii=False, indent=2), encoding="utf-8")


def ajouter(nouvelles: list[dict]) -> dict:
    """Ajoute des missions en ignorant les doublons (même lien) — l'agent de recherche est
    relancé ponctuellement, jamais en boucle continue (voir contraintes ToS), donc un même
    lien peut légitimement être re-proposé lors d'une relance ultérieure."""
    existantes = lire_toutes()
    liens_connus = {m.get("lien") for m in existantes if m.get("lien")}
    ajoutees = [m for m in nouvelles if m.get("lien") not in liens_connus]
    _ecrire(existantes + ajoutees)
    return {"ajoutees": len(ajoutees), "ignorees_doublons": len(nouvelles) - len(ajoutees), "total": len(existantes) + len(ajoutees)}


def supprimer(mission_id: str) -> bool:
    existantes = lire_toutes()
    filtrees = [m for m in existantes if m.get("id") != mission_id]
    if len(filtrees) == len(existantes):
        return False
    _ecrire(filtrees)
    return True
