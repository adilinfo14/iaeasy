from pathlib import Path

from PIL import Image, ImageDraw

from ..core.anthropic_client import anthropic
from ..core.config import settings
from . import effets, prompts
from .carrousel import W as _W  # 1080 — même largeur que le carrousel
from .carrousel import (
    MUTED,
    OR,
    OR_CLAIR,
    SS,
    TEXTE,
    _cormorant,
    _decouper_lignes,
    _inter,
    _monogramme,
    _texte_centre,
)

W = _W
H = 1920  # ratio 9:16 — format story Instagram natif, distinct du post carré

_STORIES_DIR = Path(settings.data_dir) / "instagram_stories"
_MAX_STORIES = 20


def _prompt_story(sujet: str, instruction_ton: str, instruction_secteur: str, connaissance_bloc: str = "") -> str:
    return prompts.substituer(
        prompts.lire("story"),
        sujet=sujet,
        ton=instruction_ton,
        secteur=instruction_secteur,
        connaissance=connaissance_bloc,
    )


async def generer_texte(
    sujet: str, instruction_ton: str, instruction_secteur: str, connaissance_bloc: str = ""
) -> str:
    texte = (
        await anthropic.generate(_prompt_story(sujet, instruction_ton, instruction_secteur, connaissance_bloc), max_tokens=60)
    ).strip()
    return texte.strip('"“”').strip()


def rendre_story(texte: str, effet: str = effets.DEFAUT) -> Image.Image:
    """Rendu 1080x1920 (charte noir & or) — même technique de composition que les slides de
    carrousel (calque transparent + alpha_composite), juste un canevas plus haut. Le fond est
    généré par effets.py (choisi côté IHM) puis le texte est dessiné par-dessus dans un calque
    séparé, toujours parfaitement lisible quel que soit l'effet."""
    WS, HS = W * SS, H * SS
    fond = effets.generer_fond(WS, HS, effet)
    calque = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    cx = WS / 2
    marge = 80 * SS

    _monogramme(draw, cx, HS * 0.22, 60 * SS)
    f_eyebrow = _inter(26 * SS, 500)
    _texte_centre(draw, cx, HS * 0.22 + 90 * SS, "TKONSULTING", f_eyebrow, MUTED, letter_spacing=7 * SS)

    f_titre = _cormorant(96 * SS, 600)
    lignes = _decouper_lignes(draw, texte, f_titre, WS - 2 * marge)
    hauteur_ligne = f_titre.size * 1.18
    y = HS * 0.5 - (len(lignes) * hauteur_ligne) / 2
    for ligne in lignes:
        _texte_centre(draw, cx, y, ligne, f_titre, OR_CLAIR)
        y += hauteur_ligne

    draw.line([(cx - 70 * SS, HS * 0.82), (cx + 70 * SS, HS * 0.82)], fill=OR + (255,), width=2 * SS)
    f_sous = _inter(28 * SS, 500)
    _texte_centre(draw, cx, HS * 0.82 + 30 * SS, "TKONSULTING.FR", f_sous, MUTED, letter_spacing=4 * SS)

    img = Image.alpha_composite(fond, calque).convert("RGB").resize((W, H), Image.LANCZOS)
    return img


def sauvegarder_story(story_id: str, image: Image.Image) -> None:
    _STORIES_DIR.mkdir(parents=True, exist_ok=True)
    image.save(_STORIES_DIR / f"{story_id}.jpg", quality=90)
    _purger_anciennes()


def _purger_anciennes() -> None:
    fichiers = sorted(_STORIES_DIR.glob("*.jpg"), key=lambda p: p.stat().st_mtime)
    while len(fichiers) > _MAX_STORIES:
        fichiers.pop(0).unlink(missing_ok=True)


def chemin_story(story_id: str) -> Path | None:
    chemin = _STORIES_DIR / f"{story_id}.jpg"
    return chemin if chemin.exists() else None


def url_story(story_id: str) -> str:
    return f"{settings.public_base_url}/api/instagram/story/{story_id}.jpg"
