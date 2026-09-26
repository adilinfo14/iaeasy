import json
from pathlib import Path

from ..core.config import settings

# Fichier JSON plutôt qu'une vraie base : même principe que core/reglages.py, cohérent avec le
# reste du projet pour un historique qui reste petit (quelques dizaines/centaines d'entrées).
_FICHIER = Path(settings.data_dir) / "instagram_historique.json"
_MAX_ENTREES = 200


def _lire_brut() -> list[dict]:
    if not _FICHIER.exists():
        return []
    try:
        return json.loads(_FICHIER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def ajouter_entree(entree: dict) -> None:
    entrees = _lire_brut()
    entrees.append(entree)
    # Les plus récentes en tête, plafonnées pour ne pas grossir indéfiniment.
    entrees = entrees[-_MAX_ENTREES:]
    _FICHIER.write_text(json.dumps(entrees, ensure_ascii=False, indent=2), encoding="utf-8")


def lire_historique(limite: int = 30) -> list[dict]:
    entrees = _lire_brut()
    return list(reversed(entrees))[:limite]


def mettre_a_jour_par_horodatage(horodatage: float, **champs) -> None:
    """Utilisé pour mettre en cache les indicateurs d'engagement une fois récupérés (Instagram ne
    les pousse jamais tout seul) — horodatage sert de clé, unique en pratique (précision flottante
    de time.time(), un seul post publié à la fois via le JobStore)."""
    entrees = _lire_brut()
    for e in entrees:
        if e.get("horodatage") == horodatage:
            e.update(champs)
            break
    _FICHIER.write_text(json.dumps(entrees, ensure_ascii=False, indent=2), encoding="utf-8")
