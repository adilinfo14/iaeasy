import time

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..core.ollama_client import ollama

router = APIRouter(prefix="/simulateur", tags=["simulateur"])

# Tailles approximatives en milliards de paramètres — chiffres publics arrondis, à but
# uniquement pédagogique (l'estimation d'énergie qui en découle est une approximation
# proportionnelle, PAS une mesure réelle de consommation).
_MODELES = [
    {"id": "gemma2:2b", "nom": "Gemma 2 (2B)", "parametres_milliards": 2.0},
    {"id": "llama3.2:3b", "nom": "Llama 3.2 (3B)", "parametres_milliards": 3.2},
    {"id": "phi3:mini", "nom": "Phi-3 Mini", "parametres_milliards": 3.8},
    {"id": "deepseek-coder:6.7b", "nom": "DeepSeek Coder (6.7B)", "parametres_milliards": 6.7},
    {"id": "mistral:7b-instruct", "nom": "Mistral 7B Instruct", "parametres_milliards": 7.0},
    {"id": "qwen2.5:7b-instruct", "nom": "Qwen 2.5 7B Instruct", "parametres_milliards": 7.6},
    {"id": "llama3:8b", "nom": "Llama 3 (8B)", "parametres_milliards": 8.0},
]

_PROMPT_DEFAUT = "Explique en 3 phrases ce qu'est la garantie décennale."
_LONGUEUR_MAX_PROMPT = 300
_IDS_AUTORISES = {m["id"] for m in _MODELES}

# Les 3 modèles d'embeddings du Catalogue — comparables entre eux sur la durée et le score de
# similarité, contrairement aux LLM génératifs, mais selon une mécanique différente (2 phrases
# à comparer plutôt qu'un prompt libre).
_MODELES_EMBEDDINGS = [
    {"id": "all-minilm", "nom": "All-MiniLM", "parametres_millions": 23},
    {"id": "nomic-embed-text", "nom": "Nomic Embed Text", "parametres_millions": 137},
    {"id": "mxbai-embed-large", "nom": "Mxbai Embed Large", "parametres_millions": 335},
]
_IDS_EMBEDDINGS_AUTORISES = {m["id"] for m in _MODELES_EMBEDDINGS}
_PHRASE_A_DEFAUT = "Le chat dort sur le canapé."
_PHRASE_B_DEFAUT = "Un félin fait la sieste sur le sofa."
_LONGUEUR_MAX_PHRASE = 300


class ComparerRequest(BaseModel):
    prompt: str | None = Field(default=None, max_length=_LONGUEUR_MAX_PROMPT)
    # Liste blanche stricte : sans ça, un appel direct pourrait glisser l'id d'un modèle non
    # prévu ici (ex: un modèle bien plus lourd présent sur l'Ollama partagé du homelab).
    modeles_ids: list[str] | None = Field(default=None, max_length=len(_MODELES))


class ComparerEmbeddingsRequest(BaseModel):
    phrase_a: str | None = Field(default=None, max_length=_LONGUEUR_MAX_PHRASE)
    phrase_b: str | None = Field(default=None, max_length=_LONGUEUR_MAX_PHRASE)
    modeles_ids: list[str] | None = Field(default=None, max_length=len(_MODELES_EMBEDDINGS))


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norme_a = sum(x * x for x in a) ** 0.5
    norme_b = sum(y * y for y in b) ** 0.5
    return dot / (norme_a * norme_b) if norme_a and norme_b else 0.0


@router.get("/modeles")
def modeles():
    return _MODELES


@router.get("/modeles-embeddings")
def modeles_embeddings():
    return _MODELES_EMBEDDINGS


@router.post("/comparer")
async def comparer(requete: ComparerRequest):
    prompt = (requete.prompt or "").strip() or _PROMPT_DEFAUT
    plus_gros = max(m["parametres_milliards"] for m in _MODELES)

    ids_choisis = [i for i in (requete.modeles_ids or []) if i in _IDS_AUTORISES]
    modeles_a_comparer = [m for m in _MODELES if m["id"] in ids_choisis] if ids_choisis else _MODELES

    resultats = []
    for m in modeles_a_comparer:
        debut = time.monotonic()
        reponse = await ollama.generate(m["id"], prompt)
        duree = time.monotonic() - debut
        resultats.append(
            {
                "id": m["id"],
                "nom": m["nom"],
                "parametres_milliards": m["parametres_milliards"],
                "duree_secondes": round(duree, 2),
                "longueur_reponse": len(reponse),
                "reponse": reponse[:400],
                "estimation_energie_relative_pourcent": round(100 * m["parametres_milliards"] / plus_gros),
            }
        )

    return {"prompt": prompt, "resultats": resultats}


@router.post("/comparer-embeddings")
async def comparer_embeddings(requete: ComparerEmbeddingsRequest):
    phrase_a = (requete.phrase_a or "").strip() or _PHRASE_A_DEFAUT
    phrase_b = (requete.phrase_b or "").strip() or _PHRASE_B_DEFAUT

    ids_choisis = [i for i in (requete.modeles_ids or []) if i in _IDS_EMBEDDINGS_AUTORISES]
    modeles_a_comparer = (
        [m for m in _MODELES_EMBEDDINGS if m["id"] in ids_choisis] if ids_choisis else _MODELES_EMBEDDINGS
    )

    resultats = []
    for m in modeles_a_comparer:
        debut = time.monotonic()
        vecteur_a = await ollama.embed(m["id"], phrase_a)
        vecteur_b = await ollama.embed(m["id"], phrase_b)
        duree = time.monotonic() - debut
        resultats.append(
            {
                "id": m["id"],
                "nom": m["nom"],
                "parametres_millions": m["parametres_millions"],
                "duree_secondes": round(duree, 2),
                "dimension_vecteur": len(vecteur_a),
                "similarite_cosinus": round(_cosine(vecteur_a, vecteur_b), 4),
            }
        )

    return {"phrase_a": phrase_a, "phrase_b": phrase_b, "resultats": resultats}
