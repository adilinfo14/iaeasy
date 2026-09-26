import asyncio
import base64
import io

_modeles: dict[str, tuple] = {}
_echantillon_cache = None


def _get_echantillon_manuscrit():
    # Teklia/IAM-line : vraies images scannées de la base IAM Handwriting Database (écriture
    # manuscrite anglaise réelle, pas un texte dessiné informatiquement comme pour l'OCR imprimé)
    # — la même source que celle utilisée dans la documentation officielle de TrOCR.
    global _echantillon_cache
    if _echantillon_cache is None:
        from datasets import load_dataset

        jeu = load_dataset("Teklia/IAM-line", split="test")
        _echantillon_cache = jeu[0]
    return _echantillon_cache


def _ocr_manuscrit_sync(model_ref: str) -> dict:
    from PIL import Image

    if model_ref not in _modeles:
        # TrOCRProcessor.from_pretrained() échoue avec les versions récentes de transformers
        # (tentative de conversion vers un tokenizer "fast" qui échoue), alors que le dépôt
        # fournit en réalité un tokenizer SentencePiece (fichier "sentencepiece.bpe.model") —
        # chargement direct des composants pour contourner ce bug de conversion.
        from transformers import AutoImageProcessor, VisionEncoderDecoderModel, XLMRobertaTokenizer

        processeur_image = AutoImageProcessor.from_pretrained(model_ref)
        tokenizer = XLMRobertaTokenizer.from_pretrained(model_ref)
        modele = VisionEncoderDecoderModel.from_pretrained(model_ref)
        _modeles[model_ref] = (processeur_image, tokenizer, modele)

    processeur_image, tokenizer, modele = _modeles[model_ref]
    echantillon = _get_echantillon_manuscrit()
    image = echantillon["image"]
    if not isinstance(image, Image.Image):
        image = Image.open(io.BytesIO(image["bytes"]))
    image = image.convert("RGB")

    pixel_values = processeur_image(image, return_tensors="pt").pixel_values
    sortie = modele.generate(pixel_values, max_new_tokens=64)
    texte_extrait = tokenizer.batch_decode(sortie, skip_special_tokens=True)[0].strip()

    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    image_b64 = base64.b64encode(tampon.getvalue()).decode()

    return {
        "type": "ocr_texte",
        "image_base64": image_b64,
        "texte_extrait": texte_extrait,
        "note": "Vraie ligne d'écriture manuscrite scannée (base IAM Handwriting Database, "
        "anglais — aucun modèle léger équivalent n'existe en français) — contrairement à "
        "Tesseract (moteur classique pour texte imprimé), TrOCR est un transformer "
        "encodeur-décodeur entraîné spécifiquement sur de l'écriture manuscrite.",
    }


async def run_ocr_manuscrit(model_ref: str) -> dict:
    return await asyncio.to_thread(_ocr_manuscrit_sync, model_ref)
