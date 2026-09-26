from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

from .runners import (
    handwriting_runner,
    image_embedding_runner,
    image_generation_runner,
    ml_classique_runner,
    ocr_runner,
    ollama_runner,
    timeseries_runner,
    transformers_runner,
    tts_runner,
    vision_runner,
)
from .schemas import EssaiRequest, ModelCard

router = APIRouter(prefix="/catalogue", tags=["catalogue"])

_DATA_PATH = Path(__file__).parent / "data" / "models.yaml"


def _load_models() -> dict[str, dict]:
    with open(_DATA_PATH, encoding="utf-8") as f:
        entries = yaml.safe_load(f)
    return {entry["id"]: entry for entry in entries}


_MODELS = _load_models()


# Chaque entrée : soit une fonction sans argument (modèles à données bundlées/synthétiques),
# soit une fonction (ref, texte) pour les modèles qui prennent une entrée libre.
_DISPATCH_SANS_TEXTE = {
    "yolo-vision": lambda ref: vision_runner.run_detection(ref),
    "yolo-vision-small": lambda ref: vision_runner.run_detection(ref),
    "whisper-transcription": lambda ref: transformers_runner.run_transcription(ref),
    "chronos-previsions": lambda ref: timeseries_runner.run_prevision(ref),
    "isolation-forest-maintenance": lambda ref: timeseries_runner.run_anomalie(),
    "isolation-forest-fraude": lambda ref: timeseries_runner.run_fraude(),
    "isolation-forest-four": lambda ref: timeseries_runner.run_anomalie_four(),
    "scoring-credit": lambda ref: ml_classique_runner.run_scoring_credit(),
    "scoring-pret-immobilier": lambda ref: ml_classique_runner.run_scoring_pret(),
    "recommandation-films": lambda ref: ml_classique_runner.run_recommandation(),
    "recommandation-materiaux": lambda ref: ml_classique_runner.run_recommandation_materiaux(),
    "yolo-segmentation": lambda ref: vision_runner.run_segmentation(ref),
    "yolo-pose": lambda ref: vision_runner.run_pose(ref),
    "kmeans-clustering-clients": lambda ref: ml_classique_runner.run_clustering(),
    "resnet-similarite-image": lambda ref: image_embedding_runner.run_similarite(),
    "blip-legende-image": lambda ref: vision_runner.run_caption(ref),
    "git-legende-image": lambda ref: vision_runner.run_caption(ref),
    "vitgpt2-legende-image": lambda ref: vision_runner.run_caption(ref),
    "ast-classification-audio": lambda ref: transformers_runner.run_classification_audio(ref),
    "scoring-tarification-auto": lambda ref: ml_classique_runner.run_scoring_auto(),
    "isolation-forest-sinistre-auto": lambda ref: timeseries_runner.run_anomalie_sinistres_auto(),
    "chronos-previsions-frequence-sinistres": lambda ref: timeseries_runner.run_prevision_sinistres_frequence(ref),
    "tesseract-ocr-facture-reparation": lambda ref: ocr_runner.run_ocr_facture_reparation(),
    "scoring-risque-sante": lambda ref: ml_classique_runner.run_scoring_sante(),
    "isolation-forest-remboursement-sante": lambda ref: timeseries_runner.run_anomalie_remboursements_sante(),
    "chronos-previsions-depenses-sante": lambda ref: timeseries_runner.run_prevision_depenses_sante(ref),
    "tesseract-ocr-feuille-soins": lambda ref: ocr_runner.run_ocr_feuille_soins(),
    "sdxl-detector-image-ia": lambda ref: vision_runner.run_classification_generique(
        ref,
        "Photo réelle fournie par l'outil (pas une image générée) — testée en conditions réelles, "
        "ce modèle la classe pourtant comme « artificielle » avec une forte confiance : un vrai "
        "faux positif, pas un bug de cette démo. C'est justement la meilleure preuve qu'un score "
        "de détection n'est jamais une certitude, y compris sur une photo authentique.",
    ),
    "deepfake-detector-visage": lambda ref: vision_runner.run_classification_generique(
        ref,
        "Photo réelle fournie par l'outil (pas un deepfake) — testée en conditions réelles, ce "
        "modèle la classe pourtant comme « fake » avec une forte confiance : un vrai faux "
        "positif, pas un bug de cette démo. C'est justement la meilleure preuve qu'un score de "
        "détection n'est jamais une certitude, y compris sur une photo authentique.",
    ),
    "trocr-ocr-manuscrit": lambda ref: handwriting_runner.run_ocr_manuscrit(ref),
}

# Modèles "sans texte" mais avec plusieurs échantillons prédéfinis sélectionnables (chips), pour
# montrer une vraie variété de résultats plutôt qu'une unique démo figée à chaque clic — l'id de
# l'échantillon choisi transite par le champ input_text déjà utilisé pour les exemples textuels.
_DISPATCH_SANS_TEXTE_ECHANTILLON = {
    "tesseract-ocr": lambda ref, echantillon: ocr_runner.run_ocr_variante(echantillon),
    "yolo-classification": lambda ref, echantillon: vision_runner.run_classification_echantillon(ref, echantillon),
    "yolo-classification-small": lambda ref, echantillon: vision_runner.run_classification_echantillon(
        ref, echantillon
    ),
}

LABELS_ZERO_SHOT_SINISTRE = [
    "dégât des eaux",
    "vol",
    "incendie",
    "bris de glace",
    "catastrophe naturelle",
    "accident responsable",
]

LABELS_ZERO_SHOT_ACTE_MEDICAL = [
    "consultation généraliste",
    "consultation spécialiste",
    "pharmacie",
    "hospitalisation",
    "dentaire",
    "optique",
]

_DISPATCH_AVEC_TEXTE = {
    "nomic-embeddings": lambda ref, texte: ollama_runner.run_embeddings(ref, texte),
    "mxbai-embeddings": lambda ref, texte: ollama_runner.run_embeddings(ref, texte),
    "minilm-embeddings": lambda ref, texte: ollama_runner.run_embeddings(ref, texte),
    "camembert-sentiment": lambda ref, texte: transformers_runner.run_sentiment(ref, texte),
    "helsinki-traduction": lambda ref, texte: transformers_runner.run_traduction(ref, texte),
    "barthez-resume": lambda ref, texte: transformers_runner.run_resume(ref, texte),
    "camembert-ner": lambda ref, texte: transformers_runner.run_ner(ref, texte),
    "camembert-qa": lambda ref, texte: transformers_runner.run_qa(ref, texte),
    "fasttext-langue": lambda ref, texte: transformers_runner.run_langid(texte),
    "espeak-tts": lambda ref, texte: tts_runner.run_tts(texte),
    "toxic-bert-moderation": lambda ref, texte: transformers_runner.run_classification_multi_labels(ref, texte),
    "roberta-toxicite": lambda ref, texte: transformers_runner.run_classification_multi_labels(ref, texte),
    "distilbert-toxicite-legere": lambda ref, texte: transformers_runner.run_classification_multi_labels(ref, texte),
    "xlmr-toxicite-multilingue": lambda ref, texte: transformers_runner.run_classification_multi_labels(ref, texte),
    "distilbert-zero-shot": lambda ref, texte: transformers_runner.run_zero_shot(
        ref, texte, transformers_runner.LABELS_ZERO_SHOT_EN
    ),
    "mdeberta-zero-shot-fr": lambda ref, texte: transformers_runner.run_zero_shot(
        ref, texte, transformers_runner.LABELS_ZERO_SHOT_FR
    ),
    "t5-generation-questions-fr": lambda ref, texte: transformers_runner.run_generation_questions(ref, texte),
    "t5-correction-grammaticale": lambda ref, texte: transformers_runner.run_correction_grammaticale(ref, texte, "grammar: "),
    "t5-correction-grammaticale-legere": lambda ref, texte: transformers_runner.run_correction_grammaticale(ref, texte, ""),
    "t5-correction-grammaticale-fr": lambda ref, texte: transformers_runner.run_correction_grammaticale(ref, texte, "grammaire: "),
    "mdeberta-zero-shot-type-sinistre": lambda ref, texte: transformers_runner.run_zero_shot(
        ref, texte, LABELS_ZERO_SHOT_SINISTRE
    ),
    "camembert-ner-constat-auto": lambda ref, texte: transformers_runner.run_ner(ref, texte),
    "barthez-resume-expertise-degats": lambda ref, texte: transformers_runner.run_resume(ref, texte),
    "xlmr-toxicite-reclamation-assurance": lambda ref, texte: transformers_runner.run_classification_multi_labels(
        ref, texte
    ),
    "camembert-qa-contrat-habitation": lambda ref, texte: transformers_runner.run_qa(ref, texte),
    "t5-correction-courrier-reclamation": lambda ref, texte: transformers_runner.run_correction_grammaticale(
        ref, texte, "grammaire: "
    ),
    "mdeberta-zero-shot-type-acte-medical": lambda ref, texte: transformers_runner.run_zero_shot(
        ref, texte, LABELS_ZERO_SHOT_ACTE_MEDICAL
    ),
    "drbert-ner-compte-rendu-medical": lambda ref, texte: transformers_runner.run_ner(ref, texte),
    "barthez-resume-dossier-medical": lambda ref, texte: transformers_runner.run_resume(ref, texte),
    "camembert-sentiment-avis-patients": lambda ref, texte: transformers_runner.run_sentiment(ref, texte),
    "camembert-qa-remboursement-mutuelle": lambda ref, texte: transformers_runner.run_qa(ref, texte),
    "nomic-embeddings-garanties-sante": lambda ref, texte: ollama_runner.run_embeddings(ref, texte),
    "sd-turbo-generation-image": lambda ref, texte: image_generation_runner.run_generation_image(ref, texte),
    "roberta-detection-texte-ia": lambda ref, texte: transformers_runner.run_sentiment(ref, texte),
    "chatgpt-detector-roberta": lambda ref, texte: transformers_runner.run_sentiment(ref, texte),
}


@router.get("", response_model=list[ModelCard])
def lister_modeles():
    return list(_MODELS.values())


@router.get("/{model_id}", response_model=ModelCard)
def detail_modele(model_id: str):
    if model_id not in _MODELS:
        raise HTTPException(404, "Modèle inconnu")
    return _MODELS[model_id]


@router.post("/{model_id}/essayer")
async def essayer_modele(model_id: str, requete: EssaiRequest):
    if model_id not in _MODELS:
        raise HTTPException(404, "Modèle inconnu")
    modele = _MODELS[model_id]
    ref = modele["moteur_ref"]

    try:
        if model_id in _DISPATCH_SANS_TEXTE_ECHANTILLON:
            return await _DISPATCH_SANS_TEXTE_ECHANTILLON[model_id](ref, requete.input_text)

        if model_id in _DISPATCH_SANS_TEXTE:
            return await _DISPATCH_SANS_TEXTE[model_id](ref)

        exemples = modele["cas_usage"].get("exemples", [])
        defaut = exemples[0]["input"] if exemples else ""
        texte = requete.input_text or defaut

        if model_id in _DISPATCH_AVEC_TEXTE:
            return await _DISPATCH_AVEC_TEXTE[model_id](ref, texte)

        if modele["moteur"] == "ollama":
            return await ollama_runner.run_generatif(ref, texte)
    except Exception as exc:  # noqa: BLE001 — on veut un message pédagogique, pas une 500 brute
        raise HTTPException(500, f"Échec de l'exécution du modèle '{model_id}': {exc}") from exc

    raise HTTPException(500, f"Aucun exécuteur défini pour le modèle '{model_id}'")
