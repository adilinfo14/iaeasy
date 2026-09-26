import json
from datetime import datetime
from pathlib import Path

from ..core.config import settings

# Instagram ne conserve pas d'historique interrogeable des abonnés/portée jour par jour — on
# capture et archive nous-mêmes un instantané quotidien pour construire une vraie courbe de
# croissance, plutôt qu'un chiffre isolé sans référence dans le temps.
_FICHIER = Path(settings.data_dir) / "instagram_compte_historique.json"
_MAX_ENTREES = 400


def _lire_brut() -> list[dict]:
    if not _FICHIER.exists():
        return []
    try:
        return json.loads(_FICHIER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def ajouter_instantane(donnees: dict) -> dict:
    """Un seul instantané par jour calendaire — un nouvel appel le même jour remplace le
    précédent plutôt que d'empiler des doublons sans intérêt pour la courbe de tendance."""
    entrees = _lire_brut()
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    entrees = [e for e in entrees if e.get("date") != aujourdhui]
    entree = {"date": aujourdhui, **donnees}
    entrees.append(entree)
    entrees = entrees[-_MAX_ENTREES:]
    _FICHIER.write_text(json.dumps(entrees, ensure_ascii=False, indent=2), encoding="utf-8")
    return entree


def lire_historique(limite: int = 90) -> list[dict]:
    return _lire_brut()[-limite:]
