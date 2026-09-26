import asyncio
import base64
import io

_pipeline_cache: dict = {}
_langid_model = None
_ner_pipeline_cache: dict = {}
_qa_pipeline_cache: dict = {}
_whisper_pipeline_cache: dict = {}
_audio_clf_pipeline_cache: dict = {}
_sample_audio_cache = None

LABELS_ZERO_SHOT_EN = ["technology", "sports", "politics", "health", "culture", "economy"]
LABELS_ZERO_SHOT_FR = ["technologie", "sport", "politique", "santé", "culture", "économie"]


def _get_pipeline(task: str, model_ref: str):
    key = (task, model_ref)
    if key not in _pipeline_cache:
        from transformers import pipeline

        _pipeline_cache[key] = pipeline(task, model=model_ref)
    return _pipeline_cache[key]


def _sentiment_sync(model_ref: str, input_text: str) -> dict:
    clf = _get_pipeline("text-classification", model_ref)
    result = clf(input_text)[0]
    return {
        "type": "classification",
        "etiquette": result["label"],
        "confiance": round(result["score"], 4),
    }


def _traduction_sync(model_ref: str, input_text: str) -> dict:
    # Le task générique "translation" du pipeline transformers a été retiré dans les
    # versions récentes ; on appelle donc directement le modèle seq2seq sous-jacent.
    key = ("seq2seq", model_ref)
    if key not in _pipeline_cache:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_ref)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_ref)
        _pipeline_cache[key] = (tokenizer, model)

    tokenizer, model = _pipeline_cache[key]
    entrees = tokenizer(input_text, return_tensors="pt", truncation=True)
    sortie = model.generate(**entrees, max_new_tokens=128)
    texte = tokenizer.decode(sortie[0], skip_special_tokens=True)
    return {"type": "traduction", "sortie": texte}


def _resume_sync(model_ref: str, input_text: str) -> dict:
    key = ("resume", model_ref)
    if key not in _pipeline_cache:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_ref)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_ref)
        _pipeline_cache[key] = (tokenizer, model)

    tokenizer, model = _pipeline_cache[key]
    entree = f"summarize: {input_text}" if "t5" in model_ref.lower() else input_text
    entrees = tokenizer(entree, return_tensors="pt", truncation=True, max_length=512)
    sortie = model.generate(**entrees, max_new_tokens=80, num_beams=4)
    texte = tokenizer.decode(sortie[0], skip_special_tokens=True)
    return {"type": "resume", "texte_original": input_text, "sortie": texte}


def _fusionner_entites_adjacentes(entites: list, texte: str) -> list:
    # aggregation_strategy="simple" ne fusionne que les tokens tagués I- à la suite d'un B- ;
    # certains modèles (constaté avec DrBERT-CASM2) prédisent B- sur CHAQUE sous-mot d'une même
    # entité ("bis" + "##oprolol" restent deux entités séparées au lieu de "bisoprolol") — on
    # fusionne donc nous-mêmes les entités contiguës de même catégorie, en relisant le texte
    # d'origine plutôt qu'en recollant les fragments "word" (qui portent des préfixes "##").
    if not entites:
        return entites
    fusionnees = [dict(entites[0])]
    for e in entites[1:]:
        precedente = fusionnees[-1]
        if e["entity_group"] == precedente["entity_group"] and e["start"] <= precedente["end"]:
            precedente["end"] = max(precedente["end"], e["end"])
            precedente["word"] = texte[precedente["start"] : precedente["end"]]
            precedente["score"] = min(precedente["score"], e["score"])
        else:
            fusionnees.append(dict(e))
    return fusionnees


def _ner_sync(model_ref: str, input_text: str) -> dict:
    if model_ref not in _ner_pipeline_cache:
        from transformers import pipeline

        _ner_pipeline_cache[model_ref] = pipeline("ner", model=model_ref, aggregation_strategy="simple")

    entites = _fusionner_entites_adjacentes(_ner_pipeline_cache[model_ref](input_text), input_text)
    return {
        "type": "extraction_entites",
        "texte_analyse": input_text,
        "entites": [
            {
                "texte": e["word"],
                "categorie": e["entity_group"],
                "confiance": round(float(e["score"]), 4),
            }
            for e in entites
        ],
    }


def _qa_sync(model_ref: str, input_text: str) -> dict:
    # Le task générique "question-answering" du pipeline transformers a lui aussi été
    # retiré dans les versions récentes ; on appelle donc directement le modèle sous-jacent.
    if model_ref not in _qa_pipeline_cache:
        import torch
        from transformers import AutoModelForQuestionAnswering, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_ref)
        model = AutoModelForQuestionAnswering.from_pretrained(model_ref)
        _qa_pipeline_cache[model_ref] = (tokenizer, model)

    tokenizer, model = _qa_pipeline_cache[model_ref]

    if "Contexte :" in input_text and "Question :" in input_text:
        contexte = input_text.split("Contexte :")[1].split("Question :")[0].strip()
        question = input_text.split("Question :")[1].strip()
    else:
        contexte, question = input_text, "Quel est le sujet principal ?"

    entrees = tokenizer(question, contexte, return_tensors="pt", truncation=True)
    with torch.no_grad():
        sortie = model(**entrees)

    debut = int(torch.argmax(sortie.start_logits))
    fin = int(torch.argmax(sortie.end_logits)) + 1
    confiance = float(
        torch.softmax(sortie.start_logits, dim=-1)[0, debut]
        * torch.softmax(sortie.end_logits, dim=-1)[0, fin - 1]
    )
    reponse = tokenizer.decode(entrees["input_ids"][0, debut:fin], skip_special_tokens=True)

    return {
        "type": "question_reponse",
        "contexte": contexte,
        "question": question,
        "reponse": reponse or "(aucune réponse trouvée dans le contexte)",
        "confiance": round(confiance, 4),
    }


def _classification_multi_labels_sync(model_ref: str, input_text: str) -> dict:
    # top_k=None (au lieu du top-1 par défaut de _sentiment_sync) : les modèles de modération
    # sont souvent multi-étiquettes (ex. toxique/menace/insulte à la fois) — masquer les scores
    # secondaires donnerait une fausse impression de verdict unique et tranché.
    clf = _get_pipeline("text-classification", model_ref)
    resultats = clf(input_text, top_k=None)
    return {
        "type": "classification_multi_labels",
        "texte_analyse": input_text,
        "predictions": [
            {"etiquette": r["label"], "confiance": round(float(r["score"]), 4)}
            for r in sorted(resultats, key=lambda r: -r["score"])
        ],
    }


def _zero_shot_sync(model_ref: str, input_text: str, labels: list[str]) -> dict:
    clf = _get_pipeline("zero-shot-classification", model_ref)
    resultat = clf(input_text, labels)
    return {
        "type": "classification_zero_shot",
        "texte_analyse": input_text,
        "predictions": [
            {"etiquette": label, "confiance": round(float(score), 4)}
            for label, score in zip(resultat["labels"], resultat["scores"])
        ],
    }


def _generation_questions_sync(model_ref: str, input_text: str) -> dict:
    key = ("qg", model_ref)
    if key not in _pipeline_cache:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_ref)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_ref)
        _pipeline_cache[key] = (tokenizer, model)

    tokenizer, model = _pipeline_cache[key]
    entrees = tokenizer(f"generate question: {input_text}", return_tensors="pt", truncation=True, max_length=512)
    sortie = model.generate(**entrees, max_new_tokens=64, num_beams=4)
    question = tokenizer.decode(sortie[0], skip_special_tokens=True)
    return {"type": "question_generee", "texte_source": input_text, "question_generee": question}


def _correction_grammaticale_sync(model_ref: str, input_text: str, prefixe: str) -> dict:
    key = ("gec", model_ref)
    if key not in _pipeline_cache:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_ref)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_ref)
        _pipeline_cache[key] = (tokenizer, model)

    tokenizer, model = _pipeline_cache[key]
    entrees = tokenizer(f"{prefixe}{input_text}", return_tensors="pt", truncation=True, max_length=512)
    sortie = model.generate(**entrees, max_new_tokens=128, num_beams=4)
    corrige = tokenizer.decode(sortie[0], skip_special_tokens=True)
    return {"type": "correction_grammaticale", "texte_original": input_text, "texte_corrige": corrige}


def _classification_audio_sync(model_ref: str) -> dict:
    if model_ref not in _audio_clf_pipeline_cache:
        from transformers import pipeline

        _audio_clf_pipeline_cache[model_ref] = pipeline("audio-classification", model=model_ref)

    echantillon = _get_sample_audio()
    # top_k=5 : sans cette limite, un modèle entraîné sur AudioSet (527 catégories) renvoie les
    # 527 scores d'un coup, illisible et inutile à afficher au-delà des toutes premières.
    resultats = _audio_clf_pipeline_cache[model_ref](echantillon["array"].copy(), top_k=5)

    import numpy as np
    import soundfile as sf

    audio_int16 = (np.clip(echantillon["array"], -1.0, 1.0) * 32767).astype(np.int16)
    tampon = io.BytesIO()
    sf.write(tampon, audio_int16, echantillon["sampling_rate"], format="WAV", subtype="PCM_16")
    audio_b64 = base64.b64encode(tampon.getvalue()).decode()

    return {
        "type": "classification_audio",
        "audio_base64": audio_b64,
        "predictions": [{"etiquette": r["label"], "confiance": round(float(r["score"]), 4)} for r in resultats],
        "note": "Échantillon audio de démonstration (voix humaine parlée, jeu de test standard) — "
        "utile pour observer les catégories reconnues, même si ce n'est pas un exemple typique "
        "(alarme, klaxon, aboiement...) pour ce modèle entraîné sur des sons ambiants.",
    }


def _get_sample_audio():
    # decode=False + lecture manuelle via soundfile : le backend de décodage audio par
    # défaut de `datasets` exige `torchcodec`, qui lui-même exige FFmpeg (absent de cette
    # image, coûteux à ajouter). On lit donc les octets bruts nous-mêmes.
    global _sample_audio_cache
    if _sample_audio_cache is None:
        import soundfile as sf
        from datasets import Audio, load_dataset

        jeu = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
        jeu = jeu.cast_column("audio", Audio(decode=False))
        entree = jeu[0]["audio"]
        if entree.get("bytes"):
            array, sampling_rate = sf.read(io.BytesIO(entree["bytes"]))
        else:
            array, sampling_rate = sf.read(entree["path"])
        _sample_audio_cache = {"array": array, "sampling_rate": sampling_rate}
    return _sample_audio_cache


def _transcription_sync(model_ref: str) -> dict:
    if model_ref not in _whisper_pipeline_cache:
        from transformers import pipeline

        _whisper_pipeline_cache[model_ref] = pipeline("automatic-speech-recognition", model=model_ref)

    echantillon = _get_sample_audio()
    resultat = _whisper_pipeline_cache[model_ref](echantillon["array"].copy())

    import numpy as np
    import soundfile as sf

    # soundfile écrit par défaut en PCM flottant (subtype DOUBLE/FLOAT) pour un tableau
    # numpy float — un format que le décodeur audio natif des navigateurs (<audio>) ne lit
    # pas de façon fiable (bouton lecture inerte, durée bloquée à 0:00/0:00). On force donc
    # un PCM 16 bits, universellement supporté.
    audio_int16 = (np.clip(echantillon["array"], -1.0, 1.0) * 32767).astype(np.int16)
    tampon = io.BytesIO()
    sf.write(tampon, audio_int16, echantillon["sampling_rate"], format="WAV", subtype="PCM_16")
    audio_b64 = base64.b64encode(tampon.getvalue()).decode()

    return {
        "type": "transcription_audio",
        "texte_transcrit": resultat["text"].strip(),
        "audio_base64": audio_b64,
        "note": "Échantillon audio en anglais fourni par le jeu de test standard de Whisper "
        "(librispeech_asr_dummy) — Whisper gère aussi le français, ce n'est qu'un exemple de démonstration fiable.",
    }


def _langid_sync(input_text: str) -> dict:
    # Le binding Python officiel de fastText est incompatible avec numpy>=2 (bug connu,
    # non corrigé en amont : `np.array(obj, copy=False)` sur les probabilités renvoyées).
    # py3langid est un portage pur Python du même principe (modèle statistique minuscule,
    # pas un LLM) sans cette dépendance fragile.
    from py3langid.langid import MODEL_FILE, LanguageIdentifier

    global _langid_model
    if _langid_model is None:
        _langid_model = LanguageIdentifier.from_pickled_model(MODEL_FILE, norm_probs=True)

    code, confiance = _langid_model.classify(input_text)
    return {
        "type": "detection_langue",
        "langue_detectee": code,
        "confiance": round(float(confiance), 4),
    }


async def run_sentiment(model_ref: str, input_text: str) -> dict:
    return await asyncio.to_thread(_sentiment_sync, model_ref, input_text)


async def run_traduction(model_ref: str, input_text: str) -> dict:
    return await asyncio.to_thread(_traduction_sync, model_ref, input_text)


async def run_langid(input_text: str) -> dict:
    return await asyncio.to_thread(_langid_sync, input_text)


async def run_resume(model_ref: str, input_text: str) -> dict:
    return await asyncio.to_thread(_resume_sync, model_ref, input_text)


async def run_ner(model_ref: str, input_text: str) -> dict:
    return await asyncio.to_thread(_ner_sync, model_ref, input_text)


async def run_qa(model_ref: str, input_text: str) -> dict:
    return await asyncio.to_thread(_qa_sync, model_ref, input_text)


async def run_transcription(model_ref: str) -> dict:
    return await asyncio.to_thread(_transcription_sync, model_ref)


async def run_classification_multi_labels(model_ref: str, input_text: str) -> dict:
    return await asyncio.to_thread(_classification_multi_labels_sync, model_ref, input_text)


async def run_zero_shot(model_ref: str, input_text: str, labels: list[str]) -> dict:
    return await asyncio.to_thread(_zero_shot_sync, model_ref, input_text, labels)


async def run_generation_questions(model_ref: str, input_text: str) -> dict:
    return await asyncio.to_thread(_generation_questions_sync, model_ref, input_text)


async def run_correction_grammaticale(model_ref: str, input_text: str, prefixe: str = "") -> dict:
    return await asyncio.to_thread(_correction_grammaticale_sync, model_ref, input_text, prefixe)


async def run_classification_audio(model_ref: str) -> dict:
    return await asyncio.to_thread(_classification_audio_sync, model_ref)
