import json
from typing import AsyncIterator

import httpx

from .config import settings


class OllamaClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.ollama_url

    async def generate(self, model: str, prompt: str, stream: bool = False) -> str:
        # num_predict borne la longueur de réponse : sur CPU pur, un modèle 7B sans limite
        # peut mettre plusieurs minutes à générer une réponse — inacceptable dans un outil
        # pédagogique interactif.
        async with httpx.AsyncClient(timeout=280) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 300},
                },
            )
            resp.raise_for_status()
            return resp.json()["response"]

    async def chat(self, model: str, messages: list[dict], tools: list[dict] | None = None) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": 300},
        }
        if tools:
            payload["tools"] = tools
        async with httpx.AsyncClient(timeout=280) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]

    async def chat_stream(self, model: str, messages: list[dict]) -> AsyncIterator[dict]:
        """Diffuse la réponse morceau par morceau (effet de frappe côté IHM) — en plus de
        l'aspect visuel, transmettre des octets en continu évite qu'un proxy/tunnel (Cloudflare)
        ne considère la connexion inactive et ne la coupe pendant une génération un peu longue."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"num_predict": 300},
        }
        async with httpx.AsyncClient(timeout=280) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for ligne in resp.aiter_lines():
                    if ligne:
                        yield json.loads(ligne)

    async def embed(self, model: str, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text},
            )
            resp.raise_for_status()
            return resp.json()["embedding"]

    async def show(self, model: str) -> dict:
        """Détails réels du modèle tel qu'installé sur CET Ollama (quantization, famille,
        licence...) — à privilégier sur toute donnée statique qu'on pourrait mal renseigner."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.base_url}/api/show", json={"name": model})
            resp.raise_for_status()
            return resp.json()

    async def list_models(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            return resp.json().get("models", [])


ollama = OllamaClient()
