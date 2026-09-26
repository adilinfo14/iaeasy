from io import BytesIO

import httpx
from PIL import Image

# Source de vérité unique pour la banque de templates — le workflow n8n (Code node "Choisir
# l'image...") utilise les mêmes URLs, dupliquées côté n8n faute de pouvoir importer ce module
# depuis là-bas. Toute image ajoutée ici doit aussi être ajoutée dans le Code node n8n.
IMAGES = {
    "logo": "https://tkonsulting.fr/instagram/logo-1.jpg",
    "presentation": "https://tkonsulting.fr/instagram/presentation-1.jpg",
    # Templates générés à partir de la charte graphique TKonsulting (noir #0A0A0A + or
    # C9A84C/E2C97A/A8872A, Cormorant Garamond + Inter, monogramme officiel) — des visuels
    # génériques réutilisables pour un post sans photo dédiée, plutôt que les 2 seuls contenus
    # d'origine (logo, présentation).
    # Suffixe -2 (pas -1) : le monogramme -1 avait un bug visuel (barre du "T" manquante, lu
    # "IK") corrigé après coup — nom de fichier changé plutôt que ré-uploadé à l'identique, pour
    # ne pas dépendre du cache navigateur/CDN qui aurait pu continuer à servir l'ancien fichier.
    "monogramme": "https://tkonsulting.fr/instagram/monogramme-2.jpg",
    "signature": "https://tkonsulting.fr/instagram/signature-2.jpg",
    "motif": "https://tkonsulting.fr/instagram/motif-2.jpg",
    # Templates thématiques — reprennent tels quels les pictogrammes filaires de la bibliothèque
    # de la charte (section Territoire, 50 icônes) pour illustrer directement le sujet du post
    # plutôt qu'un visuel générique.
    "strategie": "https://tkonsulting.fr/instagram/strategie-1.jpg",
    "automatisation": "https://tkonsulting.fr/instagram/automatisation-1.jpg",
    "performance": "https://tkonsulting.fr/instagram/performance-1.jpg",
    "innovation": "https://tkonsulting.fr/instagram/innovation-1.jpg",
    "partenariat": "https://tkonsulting.fr/instagram/partenariat-1.jpg",
    "excellence": "https://tkonsulting.fr/instagram/excellence-1.jpg",
}

# Plage tolérée par l'API Instagram (4:5 à 1.91:1) — un post publié en dehors de cette plage est
# rejeté par Meta avec "The aspect ratio is not supported", comme rencontré en conditions réelles
# sur l'image de présentation (0.53, bien en dessous du minimum).
_RATIO_MIN = 0.8
_RATIO_MAX = 1.91


async def verifier_ratios() -> list[str]:
    """Vérifie chaque image de la banque au démarrage plutôt que de laisser Instagram le
    découvrir au moment d'un vrai essai de publication — renvoie la liste des soucis trouvés
    (vide si tout est correct), à journaliser côté appelant."""
    problemes = []
    async with httpx.AsyncClient(timeout=15) as client:
        for nom, url in IMAGES.items():
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                im = Image.open(BytesIO(resp.content))
                ratio = im.width / im.height
                if not (_RATIO_MIN <= ratio <= _RATIO_MAX):
                    problemes.append(
                        f"Image '{nom}' ({url}) : ratio {ratio:.3f} hors de la plage Instagram "
                        f"[{_RATIO_MIN}-{_RATIO_MAX}] — la publication échouera si elle est choisie."
                    )
            except Exception as exc:  # noqa: BLE001 — un souci réseau ne doit pas bloquer le démarrage
                problemes.append(f"Image '{nom}' ({url}) : impossible à vérifier ({exc}).")
    return problemes
