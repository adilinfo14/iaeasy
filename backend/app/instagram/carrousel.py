import json
import re
import shutil
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..core.anthropic_client import anthropic
from ..core.config import settings
from . import effets, prompts

W = H = 1080
SS = 2  # supersampling — dessiné à 2x puis réduit en LANCZOS pour lisser cercles/texte
NOIR = (10, 10, 10)
OR = (201, 168, 76)
OR_CLAIR = (226, 201, 122)
TEXTE = (232, 232, 232)
MUTED = (147, 147, 141)

_POLICES_DIR = Path(__file__).resolve().parent / "polices"
_CARROUSELS_DIR = Path(settings.data_dir) / "instagram_carrousels"
_MAX_CARROUSELS = 20  # anciens carrousels purgés au-delà — mêmes contraintes que l'historique


def _prompt_plan(
    sujet: str,
    instruction_ton: str,
    instruction_secteur: str,
    nb_slides: int,
    hashtags_suggeres: str,
    connaissance_bloc: str = "",
) -> str:
    return prompts.substituer(
        prompts.lire("carrousel"),
        sujet=sujet,
        ton=instruction_ton,
        secteur=instruction_secteur,
        nb_slides=str(nb_slides),
        hashtags=hashtags_suggeres,
        connaissance=connaissance_bloc,
    )


def _extraire_json(brut: str) -> dict | None:
    nettoye = re.sub(r"^```(?:json)?|```$", "", brut.strip(), flags=re.MULTILINE).strip()
    debut, fin = nettoye.find("{"), nettoye.rfind("}")
    if debut == -1 or fin == -1:
        return None
    try:
        return json.loads(nettoye[debut : fin + 1])
    except json.JSONDecodeError:
        return None


async def generer_plan(
    sujet: str,
    instruction_ton: str,
    instruction_secteur: str,
    nb_slides: int,
    hashtags_suggeres: str = "",
    connaissance_bloc: str = "",
) -> dict:
    """Génère le plan (légende + slides) via Claude Haiku, avec UNE relance si le JSON est
    malformé — même logique de tolérance que la double-passe légende/garde-fou du post simple."""
    prompt = _prompt_plan(sujet, instruction_ton, instruction_secteur, nb_slides, hashtags_suggeres, connaissance_bloc)
    brut = await anthropic.generate(prompt, max_tokens=1200)
    plan = _extraire_json(brut)
    if plan is None or "slides" not in plan or not isinstance(plan["slides"], list):
        brut = await anthropic.generate(
            prompt + "\n\nATTENTION : ta réponse doit être UNIQUEMENT le JSON demandé, rien avant, "
            "rien après, aucune balise markdown.",
            max_tokens=1200,
        )
        plan = _extraire_json(brut)
    if plan is None or "slides" not in plan or not isinstance(plan["slides"], list) or not plan["slides"]:
        raise ValueError("Le plan généré n'est pas un JSON exploitable après relance.")
    plan["slides"] = plan["slides"][:nb_slides]
    plan.setdefault("legende", "")

    # Le modèle laisse parfois un titre vide (constaté en conditions réelles sur la slide de
    # couverture) — plutôt que de publier une slide sans texte du tout, on comble avec une version
    # courte du sujet, jamais une slide entièrement blanche.
    for s in plan["slides"]:
        if not (s.get("titre") or "").strip():
            s["titre"] = sujet[:60].rstrip() + ("…" if len(sujet) > 60 else "")

    return plan


def _police(nom_fichier: str, taille: int, poids: int = 400) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(_POLICES_DIR / nom_fichier), taille)
    try:
        f.set_variation_by_axes([poids])
    except Exception:
        try:
            f.set_variation_by_axes([poids, 14])
        except Exception:
            pass
    return f


def _cormorant(taille: int, poids: int = 600) -> ImageFont.FreeTypeFont:
    return _police("CormorantGaramond.ttf", taille, poids)


def _inter(taille: int, poids: int = 400) -> ImageFont.FreeTypeFont:
    return _police("Inter.ttf", taille, poids)


def _texte_centre(draw, cx, y, texte, font, fill, letter_spacing=0):
    if letter_spacing:
        largeur = sum(draw.textlength(c, font=font) + letter_spacing for c in texte) - letter_spacing
        x = cx - largeur / 2
        for c in texte:
            draw.text((x, y), c, font=font, fill=fill)
            x += draw.textlength(c, font=font) + letter_spacing
    else:
        w = draw.textlength(texte, font=font)
        draw.text((cx - w / 2, y), texte, font=font, fill=fill)


def _decouper_lignes(draw, texte: str, font, largeur_max: float) -> list[str]:
    mots = texte.split()
    lignes, ligne = [], ""
    for mot in mots:
        essai = f"{ligne} {mot}".strip()
        if draw.textlength(essai, font=font) <= largeur_max or not ligne:
            ligne = essai
        else:
            lignes.append(ligne)
            ligne = mot
    if ligne:
        lignes.append(ligne)
    return lignes


def _monogramme(draw, cx, cy, rayon):
    s = rayon / 12.0

    def pt(x, y):
        return (cx + (x - 12) * s, cy + (y - 12) * s)

    ep = max(2, round(1.6 * s))
    draw.ellipse([cx - rayon, cy - rayon, cx + rayon, cy + rayon], outline=OR + (255,), width=max(1, round(0.6 * s)))
    # "T" = jambage vertical + barre horizontale (celle-ci manquait, ce qui faisait lire un "I").
    draw.line([pt(7, 6), pt(7, 18)], fill=OR_CLAIR + (255,), width=ep, joint="curve")
    draw.line([pt(4.5, 6), pt(9.5, 6)], fill=OR_CLAIR + (255,), width=ep, joint="curve")
    draw.line([pt(13, 6), pt(13, 18)], fill=OR + (255,), width=ep, joint="curve")
    draw.line([pt(13, 12), pt(19, 6)], fill=OR + (255,), width=ep, joint="curve")
    draw.line([pt(13, 12), pt(19, 18)], fill=OR + (255,), width=ep, joint="curve")


def rendre_slide(
    index: int, total: int, titre: str, texte: str, est_couverture: bool, effet: str = effets.DEFAUT
) -> Image.Image:
    """Rendu carte de charte (Cormorant Garamond + Inter, noir & or) — dessiné sur un calque
    transparent puis composé sur fond opaque (alpha_composite), seule façon d'obtenir un vrai
    mélange semi-transparent avec ImageDraw (qui, sinon, écrase le pixel plutôt que le mélanger).
    Le fond est généré par effets.py (même effet sur toutes les slides d'un même carrousel, pour
    une cohérence visuelle sur l'ensemble du post) ; le texte se dessine ensuite par-dessus dans
    un calque séparé, toujours lisible quel que soit l'effet choisi."""
    WS, HS = W * SS, H * SS
    fond = effets.generer_fond(WS, HS, effet)
    calque = Image.new("RGBA", (WS, HS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    cx = WS / 2
    marge = 90 * SS

    if est_couverture:
        _monogramme(draw, cx, 170 * SS, 55 * SS)
        f_eyebrow = _inter(26 * SS, 500)
        _texte_centre(draw, cx, 250 * SS, "TKONSULTING", f_eyebrow, MUTED, letter_spacing=7 * SS)

        f_titre = _cormorant(112 * SS, 600)
        lignes = _decouper_lignes(draw, titre, f_titre, WS - 2 * marge)
        hauteur_ligne = f_titre.size * 1.16
        y = HS / 2 - (len(lignes) * hauteur_ligne) / 2
        for ligne in lignes:
            _texte_centre(draw, cx, y, ligne, f_titre, OR_CLAIR)
            y += hauteur_ligne

        draw.line([(cx - 70 * SS, HS - 220 * SS), (cx + 70 * SS, HS - 220 * SS)], fill=OR + (255,), width=2 * SS)
        f_sous = _inter(28 * SS, 500)
        _texte_centre(draw, cx, HS - 188 * SS, "FAITES DÉFILER →", f_sous, MUTED, letter_spacing=4 * SS)
    else:
        f_eyebrow = _inter(26 * SS, 500)
        _texte_centre(draw, cx, 80 * SS, f"{index + 1} / {total}", f_eyebrow, MUTED, letter_spacing=6 * SS)

        f_titre = _cormorant(88 * SS, 600)
        lignes_titre = _decouper_lignes(draw, titre, f_titre, WS - 2 * marge)
        y = 200 * SS
        hauteur_titre = f_titre.size * 1.14
        for ligne in lignes_titre:
            _texte_centre(draw, cx, y, ligne, f_titre, OR_CLAIR)
            y += hauteur_titre

        y += 36 * SS
        draw.line([(cx - 50 * SS, y), (cx + 50 * SS, y)], fill=OR + (255,), width=2 * SS)
        y += 56 * SS

        # Le monogramme est fixe en bas (centre HS-100*SS, rayon 30*SS) — un corps de texte long
        # (plusieurs lignes) pouvait déborder par-dessus lui faute de limite. On réduit la taille
        # de police par paliers jusqu'à ce que le texte tienne dans l'espace disponible au-dessus.
        espace_disponible = (HS - 150 * SS) - y
        for taille_corps in (50, 44, 38, 34, 30):
            f_corps = _inter(taille_corps * SS, 400)
            lignes_corps = _decouper_lignes(draw, texte, f_corps, WS - 2 * marge)
            hauteur_corps = f_corps.size * 1.45
            if len(lignes_corps) * hauteur_corps <= espace_disponible or taille_corps == 30:
                break

        for ligne in lignes_corps:
            _texte_centre(draw, cx, y, ligne, f_corps, TEXTE)
            y += hauteur_corps

        _monogramme(draw, cx, HS - 100 * SS, 30 * SS)

    img = Image.alpha_composite(fond, calque).convert("RGB").resize((W, H), Image.LANCZOS)
    return img


def sauvegarder_carrousel(carrousel_id: str, images: list[Image.Image]) -> None:
    dossier = _CARROUSELS_DIR / carrousel_id
    dossier.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(images):
        img.save(dossier / f"{i}.jpg", quality=90)
    _purger_anciens()


def _purger_anciens() -> None:
    if not _CARROUSELS_DIR.exists():
        return
    dossiers = sorted(
        (p for p in _CARROUSELS_DIR.iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
    )
    while len(dossiers) > _MAX_CARROUSELS:
        shutil.rmtree(dossiers.pop(0), ignore_errors=True)


def chemin_slide(carrousel_id: str, index: int) -> Path | None:
    chemin = _CARROUSELS_DIR / carrousel_id / f"{index}.jpg"
    return chemin if chemin.exists() else None


def url_slide(carrousel_id: str, index: int) -> str:
    return f"{settings.public_base_url}/api/instagram/carrousel/{carrousel_id}/{index}.jpg"
