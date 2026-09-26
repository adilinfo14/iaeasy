import asyncio
import base64
import io


_LIGNES_FACTURE_DEFAUT = [
    "FACTURE N° 2847",
    "Montant TTC : 1233,00 EUR",
    "Echeance : 15/09/2026",
]

# Variantes proposées via les chips du modèle générique tesseract-ocr — mêmes moteur et mécanisme
# à chaque fois (Tesseract ne change pas), seul le document synthétique change, pour montrer que
# la fiabilité de l'OCR dépend surtout de la mise en page et de la densité de texte du document,
# pas du "type" de document en tant que tel.
_VARIANTES_OCR_GENERIQUE = {
    "facture": _LIGNES_FACTURE_DEFAUT,
    "devis": [
        "DEVIS N° D-1042",
        "Renovation salle de bain",
        "Montant TTC : 6450,00 EUR",
    ],
    "bon_livraison": [
        "BON DE LIVRAISON N° BL-778",
        "12 sacs de ciment, 4 palettes",
        "Livre le 22/09/2026",
    ],
    "recu": [
        "RECU DE PAIEMENT N° R-390",
        "Acompte espece",
        "Montant : 500,00 EUR",
    ],
    "note_frais": [
        "NOTE DE FRAIS N° NF-215",
        "Deplacement client + repas",
        "Total a rembourser : 87,50 EUR",
    ],
}

_LIGNES_FACTURE_REPARATION_AUTO = [
    "FACTURE REPARATION N° R-5521",
    "Remplacement pare-choc avant",
    "Montant TTC : 1840,00 EUR",
]

_LIGNES_FEUILLE_SOINS = [
    "FEUILLE DE SOINS N° FS-9034",
    "Consultation specialiste",
    "Montant rembourse : 42,00 EUR",
]


def _generer_image_document(lignes=None):
    from PIL import Image, ImageDraw, ImageFont

    largeur, hauteur = 640, 240
    image = Image.new("RGB", (largeur, hauteur), color="white")
    dessin = ImageDraw.Draw(image)

    police = None
    for chemin_police in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            police = ImageFont.truetype(chemin_police, 30)
            break
        except OSError:
            continue
    if police is None:
        police = ImageFont.load_default()

    y = 30
    for ligne in lignes or _LIGNES_FACTURE_DEFAUT:
        dessin.text((30, y), ligne, fill="black", font=police)
        y += 65

    return image


def _image_vers_base64(image) -> str:
    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    return base64.b64encode(tampon.getvalue()).decode()


def _ocr_sync(lignes=None, note=None) -> dict:
    import pytesseract

    image = _generer_image_document(lignes)
    texte_extrait = pytesseract.image_to_string(image, lang="fra")

    return {
        "type": "ocr_texte",
        "image_base64": _image_vers_base64(image),
        "texte_extrait": texte_extrait.strip(),
        "note": note
        or "Image de facture générée à la volée (pas une vraie photo) pour un test 100% "
        "reproductible sans dépendre d'un fichier externe — remplaçable par une vraie photo de "
        "document scanné, avec une fiabilité qui dépend alors fortement de la netteté et de l'angle.",
    }


async def run_ocr() -> dict:
    return await asyncio.to_thread(_ocr_sync)


async def run_ocr_variante(echantillon_id: str | None) -> dict:
    lignes = _VARIANTES_OCR_GENERIQUE.get(echantillon_id or "facture", _LIGNES_FACTURE_DEFAUT)
    return await asyncio.to_thread(_ocr_sync, lignes)


async def run_ocr_facture_reparation() -> dict:
    return await asyncio.to_thread(
        _ocr_sync,
        _LIGNES_FACTURE_REPARATION_AUTO,
        "Facture de réparation générée à la volée (pas une vraie photo) — remplaçable par une "
        "vraie facture de garagiste scannée, transmise à l'assureur pour indemnisation.",
    )


async def run_ocr_feuille_soins() -> dict:
    return await asyncio.to_thread(
        _ocr_sync,
        _LIGNES_FEUILLE_SOINS,
        "Feuille de soins générée à la volée (pas une vraie photo) — remplaçable par un vrai "
        "document transmis par un professionnel de santé pour remboursement.",
    )
