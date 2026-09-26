import asyncio
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Awaitable, Callable

from ..core.config import settings

# Fichier JSON plutôt qu'une vraie base : même principe que historique.py — la file d'attente
# reste petite (quelques dizaines d'entrées en pratique), pas besoin de plus.
_FICHIER = Path(settings.data_dir) / "instagram_planificateur.json"
_INTERVALLE_S = 30  # fréquence de vérification des posts programmés arrivés à échéance

_log = logging.getLogger("uvicorn.error")


def _lire() -> list[dict]:
    if not _FICHIER.exists():
        return []
    try:
        return json.loads(_FICHIER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _ecrire(entrees: list[dict]) -> None:
    _FICHIER.write_text(json.dumps(entrees, ensure_ascii=False, indent=2), encoding="utf-8")


def creer(entree: dict) -> str:
    entrees = _lire()
    id_ = uuid.uuid4().hex[:10]
    entrees.append({"id": id_, "cree_le": time.time(), **entree})
    _ecrire(entrees)
    return id_


def lister() -> list[dict]:
    return sorted(_lire(), key=lambda e: e.get("programme_pour") or e["cree_le"])


def obtenir(id_: str) -> dict | None:
    return next((e for e in _lire() if e["id"] == id_), None)


def mettre_a_jour(id_: str, **champs) -> None:
    entrees = _lire()
    for e in entrees:
        if e["id"] == id_:
            e.update(champs)
            break
    _ecrire(entrees)


def supprimer(id_: str) -> bool:
    entrees = _lire()
    restantes = [e for e in entrees if e["id"] != id_]
    if len(restantes) == len(entrees):
        return False
    _ecrire(restantes)
    return True


async def boucle(publishers: dict[str, Callable[[dict], Awaitable[None]]]) -> None:
    """Vérifie périodiquement les entrées 'programme' arrivées à échéance et déclenche leur
    publication réelle — tourne en tâche de fond pendant toute la vie du processus (lancée
    depuis le lifespan de main.py). Une entrée refusée faute de créneau (JobStore déjà occupé)
    reste 'programme' et sera retentée au prochain passage, plutôt que marquée en échec.
    `publishers` associe un type d'entrée ('simple', 'carrousel', 'story', ...) à la fonction qui
    sait réellement la publier — un dict plutôt que des paramètres positionnels fixes, pour
    ajouter un nouveau type de publication sans changer la signature de cette fonction."""
    while True:
        try:
            maintenant = time.time()
            for e in lister():
                if e["statut"] != "programme" or not e.get("programme_pour") or e["programme_pour"] > maintenant:
                    continue
                fonction = publishers.get(e["type"])
                if fonction is None:
                    continue
                mettre_a_jour(e["id"], statut="en_cours")
                try:
                    await fonction(e)
                    mettre_a_jour(e["id"], statut="publie")
                except ValueError:
                    # Un post se publie déjà (JobStore saturé) — on retente au prochain passage.
                    mettre_a_jour(e["id"], statut="programme")
                except Exception as exc:  # noqa: BLE001 — journaliser plutôt que planter la boucle
                    mettre_a_jour(e["id"], statut="erreur", erreur=str(exc))
        except Exception:  # noqa: BLE001 — la boucle de fond ne doit jamais s'arrêter
            _log.exception("[instagram] erreur dans la boucle de planification")
        await asyncio.sleep(_INTERVALLE_S)
