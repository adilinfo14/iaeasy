import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..core.jobs import JobStore, flux_sse
from ..core.ollama_client import ollama
from ..glossaire.termes import get_termes

router = APIRouter(prefix="/aide", tags=["aide"])

# Job en tâche de fond + flux SSE plutôt qu'un simple appel synchrone : si le visiteur change
# d'onglet/d'application sur mobile pendant la génération, la réponse continue de se construire
# côté serveur — il lui suffit de revenir sur l'app pour la voir apparaître (voir core/jobs.py).
_JOBS = JobStore(max_concurrents=5, max_conserves=100)

# Un petit modèle (3B) improvisait de fausses définitions de termes techniques (ex: RAG confondu
# avec "Random Agent") plutôt que d'admettre ne pas savoir — exactement le piège d'hallucination
# que ce site enseigne par ailleurs. On utilise donc le modèle le plus capable disponible ET on
# l'ancre sur le vrai glossaire du site, au lieu de compter uniquement sur sa mémoire paramétrique.
_MODELE_AIDE = "qwen2.5:7b-instruct"

# Le glossaire est passé de 29 à 83 termes (2026-07-09) — tout injecter dans le system prompt
# (~21 000 caractères mesurés) a fait RÉAPPARAÎTRE l'hallucination que l'ancrage était censé
# corriger : avec un contexte aussi long, le modèle "perd" la définition pourtant présente et en
# invente une autre (repro observé : "RAG" défini comme "Recent, Accurate, and Genuine" alors que
# la bonne définition était bien dans le prompt). Fix : ne transmettre QUE les termes dont un
# mot-clé apparaît dans la question — même principe que le RAG enseigné ailleurs sur le site
# (chercher les passages pertinents plutôt que tout donner au modèle).
_MAX_TERMES_CONTEXTE = 5


def _termes_pertinents(texte: str) -> list[dict]:
    texte_lower = texte.lower()
    pertinents = []
    for t in get_termes():
        mot_cle = t["terme"].split("(")[0].strip().lower()
        if mot_cle and mot_cle in texte_lower:
            pertinents.append(t)
    return pertinents[:_MAX_TERMES_CONTEXTE]


def _systeme(termes_trouves: list[dict]) -> str:
    base = (
        "Tu es l'assistant pédagogique du site iaeasy, une plateforme française d'apprentissage de "
        "l'intelligence artificielle 100% souveraine (auto-hébergée, modèles open-source), destinée à "
        "un public souvent débutant. Ton rôle : aider à comprendre un terme technique ou une notion "
        "d'IA rencontrée sur le site, en langage simple, sans jargon inutile, en 2 à 4 phrases maximum."
    )
    if termes_trouves:
        contexte = "\n".join(f"- {t['terme']} : {t['definition_simple']}" for t in termes_trouves)
        base += (
            "\n\nVoici la définition officielle du site pour le(s) terme(s) probablement concerné(s) "
            "par la question — à utiliser en PRIORITÉ absolue, ne t'en écarte pas et ne la remplace "
            f"jamais par une connaissance générale différente :\n{contexte}"
        )
    else:
        base += (
            "\n\nAucun terme du glossaire officiel du site ne correspond directement à cette question : "
            "réponds avec tes connaissances générales, mais dis clairement si tu n'es pas certain "
            "plutôt que d'inventer une définition."
        )
    base += (
        "\n\nSi la question sort du sujet de l'IA ou du site, recadre poliment vers ce sujet.\n\n"
        "Réponds TOUJOURS entièrement en français, du début à la fin, sans jamais basculer même "
        "brièvement dans une autre langue (pas de mot ni de caractère en anglais, chinois ou autre)."
    )
    return base


_LONGUEUR_MAX_MESSAGE = 500
_MAX_HISTORIQUE = 8


class MessageHistorique(BaseModel):
    role: str = Field(max_length=16)
    content: str = Field(max_length=_LONGUEUR_MAX_MESSAGE)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=_LONGUEUR_MAX_MESSAGE)
    historique: list[MessageHistorique] = Field(default_factory=list, max_length=_MAX_HISTORIQUE)


async def _executer_chat(job_id: str, messages: list[dict]) -> None:
    reponse_complete = ""
    try:
        async for morceau in ollama.chat_stream(_MODELE_AIDE, messages):
            delta = morceau.get("message", {}).get("content", "")
            if delta:
                reponse_complete += delta
                _JOBS.ajouter_evenement(job_id, {"delta": delta})
        _JOBS.terminer(job_id, {"reponse": reponse_complete})
    except Exception as exc:  # noqa: BLE001 — l'erreur doit remonter côté IHM, pas planter la tâche
        _JOBS.echouer(job_id, str(exc))


@router.post("/chat")
async def chat(requete: ChatRequest):
    contexte_recherche = requete.message + " " + " ".join(m.content for m in requete.historique[-2:])
    termes_trouves = _termes_pertinents(contexte_recherche)

    messages = [{"role": "system", "content": _systeme(termes_trouves)}]
    for m in requete.historique[-_MAX_HISTORIQUE:]:
        role = m.role if m.role in ("user", "assistant") else "user"
        messages.append({"role": role, "content": m.content})
    messages.append({"role": "user", "content": requete.message})

    try:
        job_id = _JOBS.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    asyncio.create_task(_executer_chat(job_id, messages))
    return {"job_id": job_id}


@router.get("/chat/{job_id}/stream")
async def chat_stream(job_id: str):
    return StreamingResponse(flux_sse(_JOBS, job_id, "morceau"), media_type="text/event-stream")
