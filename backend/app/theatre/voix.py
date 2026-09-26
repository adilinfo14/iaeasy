import wave
from io import BytesIO
from pathlib import Path

from piper import PiperVoice, SynthesisConfig
from piper.download_voices import download_voice

from ..core.config import settings

# Voix neuronales auto-hébergées (Piper, CPU, ~0.2s de synthèse par réplique mesuré) — remplace
# la voix du navigateur (Web Speech API), de qualité très inégale selon l'appareil et jugée
# insuffisante en conditions réelles. Les modèles (~61 Mo chacun) sont stockés dans le volume
# persistant plutôt que dans l'image Docker, sur le même principe que HF_HOME pour les autres
# modèles téléchargés à la demande.
_VOIX_DIR = Path(settings.data_dir) / "piper_voices"
_VOIX_DIR.mkdir(parents=True, exist_ok=True)

_VOIX_PAR_PERSONNAGE = {
    "clio": "fr_FR-siwis-medium",
    "marco": "fr_FR-tom-medium",
}

_voix_chargees: dict[str, PiperVoice] = {}

# "tom" (Marco) signalé en conditions réelles comme saccadé, même après un premier réglage
# (length_scale=1.08, noise_w_scale=0.6) — encore un peu ralenti et la variance de durée entre
# phonèmes encore réduite pour stabiliser le débit davantage. Pas touché pour Clio (siwis), dont
# le rythme n'a pas été signalé comme problématique.
_REGLAGES_PAR_PERSONNAGE: dict[str, SynthesisConfig] = {
    "marco": SynthesisConfig(length_scale=1.18, noise_scale=0.45, noise_w_scale=0.45),
}


def _obtenir_voix(personnage: str) -> PiperVoice:
    nom = _VOIX_PAR_PERSONNAGE.get(personnage, "fr_FR-siwis-medium")
    if nom not in _voix_chargees:
        download_voice(nom, download_dir=_VOIX_DIR)
        _voix_chargees[nom] = PiperVoice.load(str(_VOIX_DIR / f"{nom}.onnx"))
    return _voix_chargees[nom]


def synthetiser(texte: str, personnage: str) -> bytes:
    """Synthèse synchrone (CPU) — à appeler via asyncio.to_thread depuis un endpoint async pour
    ne pas bloquer la boucle événementielle pendant les ~0,2 à 2s (1er appel, chargement inclus)."""
    voix = _obtenir_voix(personnage)
    syn_config = _REGLAGES_PAR_PERSONNAGE.get(personnage)
    tampon = BytesIO()
    with wave.open(tampon, "wb") as wav_file:
        voix.synthesize_wav(texte, wav_file, syn_config=syn_config)
    return tampon.getvalue()


def precharger_voix() -> None:
    """Charge les 2 voix au démarrage du serveur — sans ça, le tout premier visiteur après un
    déploiement paie le coût du téléchargement (~61 Mo/voix, jusqu'à ~25s mesuré) au milieu de
    sa lecture, au lieu qu'il soit absorbé une fois pour toutes au boot du conteneur."""
    for personnage in _VOIX_PAR_PERSONNAGE:
        _obtenir_voix(personnage)
