import asyncio
import base64
import io

_yolo_models: dict[str, object] = {}
_yolo_cls_models: dict[str, object] = {}
_yolo_seg_models: dict[str, object] = {}
_yolo_pose_models: dict[str, object] = {}
_caption_pipelines: dict[str, object] = {}
_classif_generique_pipelines: dict[str, object] = {}


def _sample_image_path() -> str:
    from ultralytics.utils import ASSETS

    return str(ASSETS / "bus.jpg")


# Imagenette (sous-ensemble d'ImageNet à 10 classes, images réelles, largement utilisé pour
# la démonstration/l'enseignement) — fournit une vraie variété visuelle pour les modèles de
# classification, alors que le seul bus.jpg fourni par ultralytics ne permettait qu'un seul
# essai toujours identique, sans lien avec la diversité annoncée dans les idées d'usage.
_SYNSET_PAR_ECHANTILLON = {
    "golf_ball": "n03445777",
    "chain_saw": "n03000684",
    "church": "n03028079",
    "garbage_truck": "n03417042",
    "english_springer": "n02102040",
}
_echantillons_imagenette: dict = {}


def _get_image_imagenette(echantillon_id: str):
    if not _echantillons_imagenette:
        from datasets import load_dataset

        jeu = load_dataset("johnowhitaker/imagenette2-320", split="train")
        noms_classes = jeu.features["label"].names
        idx_vers_cle = {noms_classes.index(s): cle for cle, s in _SYNSET_PAR_ECHANTILLON.items()}
        restants = set(idx_vers_cle)
        for exemple in jeu:
            if exemple["label"] in restants:
                cle = idx_vers_cle[exemple["label"]]
                _echantillons_imagenette[cle] = exemple["image"].convert("RGB")
                restants.discard(exemple["label"])
                if not restants:
                    break
    return _echantillons_imagenette.get(echantillon_id, _echantillons_imagenette.get("golf_ball"))


def _sample_image_path_personne() -> str:
    # zidane.jpg contient des personnes bien visibles — plus adapté que bus.jpg pour
    # l'estimation de pose (qui a besoin de corps humains entiers, pas de silhouettes lointaines).
    from ultralytics.utils import ASSETS

    return str(ASSETS / "zidane.jpg")


def _image_to_base64(annotated_bgr) -> str:
    from PIL import Image

    annotated_rgb = annotated_bgr[:, :, ::-1]
    img = Image.fromarray(annotated_rgb)
    tampon = io.BytesIO()
    img.save(tampon, format="JPEG", quality=85)
    return base64.b64encode(tampon.getvalue()).decode()


def _detect_sync(model_ref: str) -> dict:
    if model_ref not in _yolo_models:
        from ultralytics import YOLO

        _yolo_models[model_ref] = YOLO(model_ref)

    image_path = _sample_image_path()
    results = _yolo_models[model_ref](image_path, verbose=False)[0]

    detections = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        detections.append(
            {
                "etiquette": results.names[cls_id],
                "confiance": round(float(box.conf[0]), 3),
                "boite": [round(float(v), 1) for v in box.xyxy[0].tolist()],
            }
        )

    return {
        "type": "detection_objets",
        "image_annotee_base64": _image_to_base64(results.plot()),
        "objets_detectes": detections,
        "nb_objets": len(detections),
        "note": "Image d'exemple générique fournie par l'outil — remplaçable par une vraie photo aérienne.",
    }


def _classify_sync(model_ref: str, echantillon_id: str | None = None) -> dict:
    if model_ref not in _yolo_cls_models:
        from ultralytics import YOLO

        _yolo_cls_models[model_ref] = YOLO(model_ref)

    if echantillon_id and echantillon_id in _SYNSET_PAR_ECHANTILLON:
        image_source = _get_image_imagenette(echantillon_id)
    else:
        image_source = _sample_image_path()
    results = _yolo_cls_models[model_ref](image_source, verbose=False)[0]

    top5_idx = results.probs.top5
    top5_conf = results.probs.top5conf.tolist()
    predictions = [
        {"etiquette": results.names[i], "confiance": round(float(c), 4)}
        for i, c in zip(top5_idx, top5_conf)
    ]

    tampon = io.BytesIO()
    if isinstance(image_source, str):
        with open(image_source, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
    else:
        image_source.save(tampon, format="JPEG", quality=85)
        image_b64 = base64.b64encode(tampon.getvalue()).decode()

    return {
        "type": "classification_image",
        "image_base64": image_b64,
        "predictions": predictions,
        "note": "Modèle entraîné sur ImageNet (1000 catégories généralistes, pas seulement des "
        "objets d'un secteur) — change d'échantillon ci-dessus pour voir le top 5 varier "
        "réellement selon le sujet de la photo.",
    }


def _segment_sync(model_ref: str) -> dict:
    if model_ref not in _yolo_seg_models:
        from ultralytics import YOLO

        _yolo_seg_models[model_ref] = YOLO(model_ref)

    image_path = _sample_image_path()
    results = _yolo_seg_models[model_ref](image_path, verbose=False)[0]

    objets = []
    if results.masks is not None:
        for box, mask in zip(results.boxes, results.masks):
            cls_id = int(box.cls[0])
            objets.append(
                {
                    "etiquette": results.names[cls_id],
                    "confiance": round(float(box.conf[0]), 3),
                    "nb_points_contour": len(mask.xy[0]) if len(mask.xy) else 0,
                }
            )

    return {
        "type": "segmentation_image",
        "image_annotee_base64": _image_to_base64(results.plot()),
        "objets_segmentes": objets,
        "nb_objets": len(objets),
        "note": "Contrairement à la détection (rectangle), chaque objet est ici délimité par un "
        "contour précis (masque de pixels) — utile pour mesurer une surface ou détourer un objet.",
    }


def _pose_sync(model_ref: str) -> dict:
    if model_ref not in _yolo_pose_models:
        from ultralytics import YOLO

        _yolo_pose_models[model_ref] = YOLO(model_ref)

    image_path = _sample_image_path_personne()
    results = _yolo_pose_models[model_ref](image_path, verbose=False)[0]

    personnes = []
    if results.keypoints is not None:
        for i, kpts in enumerate(results.keypoints.xy):
            points_visibles = int((results.keypoints.conf[i] > 0.5).sum()) if results.keypoints.conf is not None else len(kpts)
            personnes.append({"personne": i + 1, "points_cles_detectes": points_visibles, "points_cles_total": len(kpts)})

    return {
        "type": "estimation_pose",
        "image_annotee_base64": _image_to_base64(results.plot()),
        "personnes_detectees": personnes,
        "nb_personnes": len(personnes),
        "note": "17 points clés recherchés par personne (yeux, épaules, coudes, genoux...) — la "
        "posture peut ensuite servir à détecter une chute, un geste ou une position de travail à risque.",
    }


def _caption_sync(model_ref: str) -> dict:
    from PIL import Image

    image_path = _sample_image_path()
    image = Image.open(image_path).convert("RGB")

    if model_ref not in _caption_pipelines:
        # nlpconnect/vit-gpt2-image-captioning assemble un ViT et un GPT-2 chargés séparément
        # (pas de "processeur" unifié) — les autres (BLIP, GIT) partagent une interface commune
        # via AutoProcessor/AutoModelForImageTextToText. Le pipeline() générique "image-to-text"
        # a été retiré des versions récentes de transformers, d'où le chargement direct des
        # modèles ci-dessous plutôt qu'un appel à pipeline().
        if model_ref == "nlpconnect/vit-gpt2-image-captioning":
            from transformers import AutoTokenizer, VisionEncoderDecoderModel, ViTImageProcessor

            _caption_pipelines[model_ref] = (
                "vit-gpt2",
                ViTImageProcessor.from_pretrained(model_ref),
                VisionEncoderDecoderModel.from_pretrained(model_ref),
                AutoTokenizer.from_pretrained(model_ref),
            )
        else:
            from transformers import AutoModelForImageTextToText, AutoProcessor

            processeur = AutoProcessor.from_pretrained(model_ref)
            _caption_pipelines[model_ref] = (
                "standard",
                processeur,
                AutoModelForImageTextToText.from_pretrained(model_ref),
                None,
            )

    mode, processeur, model, tokenizer = _caption_pipelines[model_ref]
    if mode == "vit-gpt2":
        pixel_values = processeur(images=[image], return_tensors="pt").pixel_values
        sortie = model.generate(pixel_values, max_new_tokens=30)
        legende = tokenizer.batch_decode(sortie, skip_special_tokens=True)[0].strip()
    else:
        entrees = processeur(images=image, return_tensors="pt")
        sortie = model.generate(**entrees, max_new_tokens=30)
        legende = processeur.batch_decode(sortie, skip_special_tokens=True)[0].strip()

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    return {
        "type": "legende_image",
        "image_base64": image_b64,
        "legende": legende,
        "note": "Image d'exemple générique fournie par l'outil, et légende en anglais (modèles "
        "entraînés sur des jeux de données anglophones) — le principe reste identique en français.",
    }


async def run_caption(model_ref: str) -> dict:
    return await asyncio.to_thread(_caption_sync, model_ref)


def _classification_generique_sync(model_ref: str, note: str) -> dict:
    if model_ref not in _classif_generique_pipelines:
        from transformers import pipeline

        _classif_generique_pipelines[model_ref] = pipeline("image-classification", model=model_ref)

    image_path = _sample_image_path()
    predictions = _classif_generique_pipelines[model_ref](image_path, top_k=5)

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    return {
        "type": "classification_image",
        "image_base64": image_b64,
        "predictions": [
            {"etiquette": p["label"], "confiance": round(float(p["score"]), 4)} for p in predictions
        ],
        "note": note,
    }


async def run_classification_generique(model_ref: str, note: str) -> dict:
    return await asyncio.to_thread(_classification_generique_sync, model_ref, note)


async def run_segmentation(model_ref: str) -> dict:
    return await asyncio.to_thread(_segment_sync, model_ref)


async def run_pose(model_ref: str) -> dict:
    return await asyncio.to_thread(_pose_sync, model_ref)


async def run_detection(model_ref: str) -> dict:
    return await asyncio.to_thread(_detect_sync, model_ref)


async def run_classification(model_ref: str) -> dict:
    return await asyncio.to_thread(_classify_sync, model_ref)


async def run_classification_echantillon(model_ref: str, echantillon_id: str | None) -> dict:
    return await asyncio.to_thread(_classify_sync, model_ref, echantillon_id)
