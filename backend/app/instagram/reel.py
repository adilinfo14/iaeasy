import subprocess
import uuid
from pathlib import Path

from ..core.config import settings
from . import effets
from .story import rendre_story

_MUSIQUES_DIR = Path(__file__).resolve().parent / "musiques"
_REELS_DIR = Path(settings.data_dir) / "instagram_reels"
_MAX_REELS = 10  # fichiers vidéo bien plus lourds qu'une image — plafond plus bas que les autres formats
_DUREE_S = 14

# Toutes CC0 (domaine public), voir musiques/LICENCE.md pour la source exacte de chaque piste.
# "categorie" sert uniquement à grouper l'affichage côté IHM (20 pistes à plat serait illisible).
MUSIQUES = {
    # Calme / posé
    "creature-comforts": {"fichier": "creature-comforts.mp3", "label": "Creature Comforts", "categorie": "Calme"},
    "calm-currents": {"fichier": "calm-currents.mp3", "label": "Calm Currents", "categorie": "Calme"},
    "into-the-mist": {"fichier": "into-the-mist.mp3", "label": "Into The Mist", "categorie": "Calme"},
    "wetlands": {"fichier": "wetlands.mp3", "label": "Wetlands", "categorie": "Calme"},
    "waiting-around": {"fichier": "waiting-around.mp3", "label": "Waiting Around", "categorie": "Calme"},
    "mundane": {"fichier": "mundane.mp3", "label": "Mundane", "categorie": "Calme"},
    "clouds": {"fichier": "clouds.mp3", "label": "Clouds", "categorie": "Calme"},
    "foggy-headed": {"fichier": "foggy-headed.mp3", "label": "Foggy Headed", "categorie": "Calme"},
    "static": {"fichier": "static.mp3", "label": "Static", "categorie": "Calme"},
    "ease-into-night": {"fichier": "ease-into-night.mp3", "label": "Ease Into Night", "categorie": "Calme"},
    "infinite-echoes": {"fichier": "infinite-echoes.mp3", "label": "Infinite Echoes", "categorie": "Calme"},
    "peaceful-drift": {"fichier": "peaceful-drift.mp3", "label": "Peaceful Drift", "categorie": "Calme"},
    "saturation": {"fichier": "saturation.mp3", "label": "Saturation", "categorie": "Calme"},
    "yet-again": {"fichier": "yet-again.mp3", "label": "Yet Again", "categorie": "Calme"},
    "cold-salt-water": {"fichier": "cold-salt-water.mp3", "label": "Cold Salt Water", "categorie": "Calme"},
    # Doux / nostalgique
    "autumn": {"fichier": "autumn.mp3", "label": "Autumn", "categorie": "Nostalgique"},
    "dreamy-reverie": {"fichier": "dreamy-reverie.mp3", "label": "Dreamy Reverie", "categorie": "Nostalgique"},
    "one-night-in-france": {"fichier": "one-night-in-france.mp3", "label": "One Night In France", "categorie": "Nostalgique"},
    "color-of-a-soul": {"fichier": "color-of-a-soul.mp3", "label": "Color Of A Soul", "categorie": "Nostalgique"},
    "tokyo-sunset": {"fichier": "tokyo-sunset.mp3", "label": "Tokyo Sunset", "categorie": "Nostalgique"},
    "reminders": {"fichier": "reminders.mp3", "label": "Reminders", "categorie": "Nostalgique"},
    "seasons-change": {"fichier": "seasons-change.mp3", "label": "Seasons Change", "categorie": "Nostalgique"},
    "letting-go-of-the-past": {"fichier": "letting-go-of-the-past.mp3", "label": "Letting Go Of The Past", "categorie": "Nostalgique"},
    "pretty-little-lies": {"fichier": "pretty-little-lies.mp3", "label": "Pretty Little Lies", "categorie": "Nostalgique"},
    "vintage": {"fichier": "vintage.mp3", "label": "Vintage", "categorie": "Nostalgique"},
    "complicated-feelings": {"fichier": "complicated-feelings.mp3", "label": "Complicated Feelings", "categorie": "Nostalgique"},
    "going-home": {"fichier": "going-home.mp3", "label": "Going Home", "categorie": "Nostalgique"},
    "moon-unit": {"fichier": "moon-unit.mp3", "label": "Moon Unit", "categorie": "Nostalgique"},
    "still-life": {"fichier": "still-life.mp3", "label": "Still Life", "categorie": "Nostalgique"},
    "currents-we-used-to-know": {"fichier": "currents-we-used-to-know.mp3", "label": "Currents We Used To Know", "categorie": "Nostalgique"},
    "summer-felt-longer-then": {"fichier": "summer-felt-longer-then.mp3", "label": "Summer Felt Longer Then", "categorie": "Nostalgique"},
    # Motivant / positif
    "walking-away": {"fichier": "walking-away.mp3", "label": "Walking Away", "categorie": "Motivant"},
    "tranquil-mindscape": {"fichier": "tranquil-mindscape.mp3", "label": "Tranquil Mindscape", "categorie": "Motivant"},
    "hope-on-repeat": {"fichier": "hope-on-repeat.mp3", "label": "Hope On Repeat", "categorie": "Motivant"},
    "one-good-day": {"fichier": "one-good-day.mp3", "label": "One Good Day", "categorie": "Motivant"},
    "something-in-the-air": {"fichier": "something-in-the-air.mp3", "label": "Something In The Air", "categorie": "Motivant"},
    "everything-you-ever-dreamed": {"fichier": "everything-you-ever-dreamed.mp3", "label": "Everything You Ever Dreamed", "categorie": "Motivant"},
    "warm-fuzz": {"fichier": "warm-fuzz.mp3", "label": "Warm Fuzz", "categorie": "Motivant"},
    "spring-in-sight": {"fichier": "spring-in-sight.mp3", "label": "Spring In Sight", "categorie": "Motivant"},
    "feeling-human-again": {"fichier": "feeling-human-again.mp3", "label": "Feeling Human Again", "categorie": "Motivant"},
    # Été / lumineux
    "morning-coffee": {"fichier": "morning-coffee.mp3", "label": "Morning Coffee", "categorie": "Lumineux"},
    "august-never-lasts": {"fichier": "august-never-lasts.mp3", "label": "August Never Lasts", "categorie": "Lumineux"},
    "faded-in-the-sunlight": {"fichier": "faded-in-the-sunlight.mp3", "label": "Faded In The Sunlight", "categorie": "Lumineux"},
    "ocean-memory": {"fichier": "ocean-memory.mp3", "label": "Ocean Memory", "categorie": "Lumineux"},
    "washed-up": {"fichier": "washed-up.mp3", "label": "Washed Up", "categorie": "Lumineux"},
    "new-shoes": {"fichier": "new-shoes.mp3", "label": "New Shoes", "categorie": "Lumineux"},
    "puppy-love": {"fichier": "puppy-love.mp3", "label": "Puppy Love", "categorie": "Lumineux"},
    "bubbles": {"fichier": "bubbles.mp3", "label": "Bubbles", "categorie": "Lumineux"},
    "shimmer": {"fichier": "shimmer.mp3", "label": "Shimmer", "categorie": "Lumineux"},
    "roof-tops": {"fichier": "roof-tops.mp3", "label": "Roof Tops", "categorie": "Lumineux"},
    "the-last-long-day": {"fichier": "the-last-long-day.mp3", "label": "The Last Long Day", "categorie": "Lumineux"},
    "toy-box": {"fichier": "toy-box.mp3", "label": "Toy Box", "categorie": "Lumineux"},
}
MUSIQUE_DEFAUT = "morning-coffee"


def rendre_reel(texte: str, musique: str, effet: str = effets.DEFAUT) -> str:
    """Génère un Reel (MP4, 1080x1920, ~14s) : le même visuel de marque qu'une story (monogramme
    + accroche, charte noir & or), animé d'un léger zoom (Ken Burns, via le filtre ffmpeg
    zoompan) et sonorisé d'une ambiance CC0 — rendu par un appel ffmpeg en sous-processus plutôt
    qu'une dépendance Python vidéo, cohérent avec l'usage déjà fait de tesseract/espeak en CLI."""
    reel_id = uuid.uuid4().hex[:12]
    _REELS_DIR.mkdir(parents=True, exist_ok=True)
    dossier_tmp = _REELS_DIR / f"_tmp_{reel_id}"
    dossier_tmp.mkdir(parents=True, exist_ok=True)

    try:
        image = rendre_story(texte, effet)
        chemin_image = dossier_tmp / "fond.jpg"
        image.save(chemin_image, quality=95)

        cle_musique = musique if musique in MUSIQUES else MUSIQUE_DEFAUT
        chemin_musique = _MUSIQUES_DIR / MUSIQUES[cle_musique]["fichier"]
        chemin_sortie = _REELS_DIR / f"{reel_id}.mp4"

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1", "-framerate", "30", "-i", str(chemin_image),
                "-i", str(chemin_musique),
                "-filter_complex",
                "[0:v]scale=1080:1920,zoompan=z='min(zoom+0.0007,1.15)':d=1:s=1080x1920:fps=30[v]",
                "-map", "[v]", "-map", "1:a",
                "-t", str(_DUREE_S),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k",
                "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={_DUREE_S - 3}:d=3",
                "-shortest",
                # Déplace l'atome moov au début du fichier — sans ça, Instagram a rejeté un
                # premier Reel réel avec "status_code: ERROR" quasi instantané (constaté en
                # conditions réelles), un souci d'ingestion vidéo classique sur un MP4 dont les
                # métadonnées sont en fin de fichier plutôt qu'en tête.
                "-movflags", "+faststart",
                str(chemin_sortie),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
    finally:
        for f in dossier_tmp.iterdir():
            f.unlink(missing_ok=True)
        dossier_tmp.rmdir()

    _purger_anciens()
    return reel_id


def rendre_reel_multiscenes(
    titres: list[str], musique: str, duree_par_scene: float = 3.5, effet: str = effets.DEFAUT
) -> str:
    """Reel façon carrousel : une scène par point (même accroche courte qu'une story, réutilisée
    telle quelle), assemblées bout à bout (coupures nettes, pas de fondu — plus simple et plus
    fiable à assembler que des transitions xfade en chaîne) puis sonorisées d'une seule musique
    continue sur toute la durée. Même effet de fond sur toutes les scènes, pour une cohérence
    visuelle sur l'ensemble du reel."""
    reel_id = uuid.uuid4().hex[:12]
    _REELS_DIR.mkdir(parents=True, exist_ok=True)
    dossier_tmp = _REELS_DIR / f"_tmp_{reel_id}"
    dossier_tmp.mkdir(parents=True, exist_ok=True)

    try:
        clips = []
        for i, titre in enumerate(titres):
            image = rendre_story(titre, effet)
            chemin_image = dossier_tmp / f"scene_{i}.jpg"
            image.save(chemin_image, quality=95)
            chemin_clip = dossier_tmp / f"clip_{i}.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-loop", "1", "-framerate", "30", "-i", str(chemin_image),
                    "-filter_complex",
                    "[0:v]scale=1080:1920,zoompan=z='min(zoom+0.0009,1.12)':d=1:s=1080x1920:fps=30[v]",
                    "-map", "[v]",
                    "-t", str(duree_par_scene),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(chemin_clip),
                ],
                check=True, capture_output=True, timeout=60,
            )
            clips.append(chemin_clip)

        liste_concat = dossier_tmp / "liste.txt"
        liste_concat.write_text("\n".join(f"file '{c.name}'" for c in clips), encoding="utf-8")

        chemin_video_muette = dossier_tmp / "assemble.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "liste.txt", "-c", "copy", "assemble.mp4"],
            check=True, capture_output=True, timeout=60, cwd=str(dossier_tmp),
        )

        duree_totale = duree_par_scene * len(titres)
        cle_musique = musique if musique in MUSIQUES else MUSIQUE_DEFAUT
        chemin_musique = _MUSIQUES_DIR / MUSIQUES[cle_musique]["fichier"]
        chemin_sortie = _REELS_DIR / f"{reel_id}.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(chemin_video_muette), "-i", str(chemin_musique),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={max(duree_totale - 3, 0)}:d=3",
                "-shortest",
                "-movflags", "+faststart",
                str(chemin_sortie),
            ],
            check=True, capture_output=True, timeout=60,
        )
    finally:
        for f in dossier_tmp.iterdir():
            f.unlink(missing_ok=True)
        dossier_tmp.rmdir()

    _purger_anciens()
    return reel_id


def _purger_anciens() -> None:
    fichiers = sorted(_REELS_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    while len(fichiers) > _MAX_REELS:
        fichiers.pop(0).unlink(missing_ok=True)


def chemin_reel(reel_id: str) -> Path | None:
    chemin = _REELS_DIR / f"{reel_id}.mp4"
    return chemin if chemin.exists() else None


def url_reel(reel_id: str) -> str:
    return f"{settings.public_base_url}/api/instagram/reel/{reel_id}.mp4"


def chemin_musique(cle: str) -> Path | None:
    """Sert le fichier CC0 tel quel, pour une écoute d'aperçu côté IHM avant de choisir
    l'ambiance — le même fichier que celui utilisé par ffmpeg dans rendre_reel()."""
    if cle not in MUSIQUES:
        return None
    chemin = _MUSIQUES_DIR / MUSIQUES[cle]["fichier"]
    return chemin if chemin.exists() else None
