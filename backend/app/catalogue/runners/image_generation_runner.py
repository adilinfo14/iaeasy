import asyncio
import base64
import io

_pipelines: dict[str, object] = {}


def _generer_sync(model_ref: str, prompt: str) -> dict:
    if model_ref not in _pipelines:
        import torch
        from diffusers import AutoPipelineForText2Image

        pipe = AutoPipelineForText2Image.from_pretrained(model_ref, torch_dtype=torch.float32)
        pipe.to("cpu")
        _pipelines[model_ref] = pipe

    # sd-turbo est un modèle "distillé par étape" (une seule étape de débruitage suffit, contre
    # ~50 pour un Stable Diffusion classique) — c'est ce qui le rend utilisable en CPU pur en
    # quelques secondes plutôt qu'en plusieurs minutes. guidance_scale=0.0 est requis par ce
    # modèle spécifique (entraîné sans guidance).
    image = _pipelines[model_ref](
        prompt=prompt, num_inference_steps=1, guidance_scale=0.0
    ).images[0]

    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    image_b64 = base64.b64encode(tampon.getvalue()).decode()

    return {
        "type": "image_generee",
        "prompt": prompt,
        "image_base64": image_b64,
        "note": "Génération en 1 seule étape de débruitage (au lieu d'une cinquantaine pour un "
        "Stable Diffusion classique) — c'est ce compromis qui rend la génération d'image "
        "possible en quelques secondes sur CPU, au prix d'un rendu moins raffiné qu'un modèle "
        "complet tournant sur GPU pendant plusieurs dizaines de secondes.",
    }


async def run_generation_image(model_ref: str, prompt: str) -> dict:
    return await asyncio.to_thread(_generer_sync, model_ref, prompt)
