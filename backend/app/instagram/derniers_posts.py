import json
from pathlib import Path

from ..core.config import settings

# Cache des derniers posts publiés — rafraîchi périodiquement en fond (voir
# router.py:_boucle_derniers_posts_auto), pas interrogé en direct à chaque visite du site public :
# plus rapide pour le visiteur, et n'appelle l'API Graph qu'une fois par cycle plutôt qu'une fois
# par chargement de page.
_FICHIER = Path(settings.data_dir) / "instagram_derniers_posts.json"


def enregistrer(posts: list[dict]) -> None:
    _FICHIER.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")


def lire() -> list[dict]:
    if not _FICHIER.exists():
        return []
    try:
        return json.loads(_FICHIER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
