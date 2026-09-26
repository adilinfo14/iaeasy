import httpx

from .config import settings

_MODELE_DEFAUT = "claude-haiku-4-5-20251001"


class AnthropicClient:
    """Utilisé uniquement pour les textes Instagram (légendes, accroches, plans de carrousel) —
    le reste de la plateforme (catalogue, entraînement, agents) reste sur Ollama en local. Un
    petit modèle 7B produit des textes corrects mais nettement plus génériques qu'un vrai modèle
    de copywriting sur ce genre de format court ; le coût par génération est marginal (quelques
    centimes) face au gain de qualité perçu par un vrai lecteur Instagram."""

    async def generate(self, prompt: str, max_tokens: int = 600, model: str = _MODELE_DEFAUT) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]


anthropic = AnthropicClient()
