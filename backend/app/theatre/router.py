import asyncio
import json
import re
import secrets

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from ..core.jobs import JobStore
from ..core.ollama_client import ollama
from . import voix
from .episodes import DECORS, EMOTIONS, EPISODES, PERSONNAGES

router = APIRouter(prefix="/theatre", tags=["theatre"])

_MODELE_CONTEUR = "qwen2.5:7b-instruct"

# Génération mesurée à ~45s (parfois 2 essais en cas de JSON mal formé) — un simple POST bloquant
# a le même défaut que le chat/comparateur avant leur fix : si le visiteur change d'onglet sur
# mobile, la connexion peut être coupée avant la fin. Job en tâche de fond + poll, plutôt qu'une
# réponse bloquante : le résultat continue d'être généré côté serveur quoi qu'il arrive au client.
_JOBS = JobStore(max_concurrents=3, max_conserves=50)

# Sujets réels et bien documentés, distincts des 5 épisodes déjà écrits à la main — pour la
# variété du bouton "Nouvelle histoire", sans laisser le modèle inventer librement un sujet
# (risque d'anachronisme ou d'événement halluciné).
_SUJETS = [
    "l'invention de l'imprimerie par Gutenberg vers 1450",
    "la ruée vers l'or en Californie à partir de 1848",
    "la construction du canal de Suez, achevée en 1869",
    "la traversée de l'Atlantique par Christophe Colomb en 1492",
    "la découverte de la tombe de Toutânkhamon par Howard Carter en 1922",
    "le naufrage du Titanic en 1912",
    "la construction de la Grande Muraille de Chine",
    "l'éruption du Vésuve qui ensevelit Pompéi en 79 après J.-C.",
    "la première ascension de l'Everest par Hillary et Norgay en 1953",
    "le tour du monde de Magellan entre 1519 et 1522",
    "la construction des pyramides de Gizeh dans l'Égypte antique",
    "la prise de la Bastille le 14 juillet 1789",
    "la ruée vers l'or du Klondike à la fin du 19e siècle",
    "la construction du premier chemin de fer transcontinental américain, achevé en 1869",
    "la première traversée de la Manche en ballon par Blanchard et Jeffries en 1785",
    "l'incendie de Rome sous l'empereur Néron en 64 après J.-C.",
]

_SCHEMA_ATTENDU = (
    '{"titre": "...", "annee": "...", "scenes": [{"decor": "'
    + '" | "'.join(DECORS)
    + '", "repliques": [{"personnage": "clio" ou "marco", "emotion": "'
    + '" | "'.join(EMOTIONS)
    + '", "texte": "..."}, ...]}, ...]}'
)

# Un prompt trop rigide produisait toujours la même mécanique conversationnelle (Clio demande
# "peux-tu m'expliquer... ?", Marco répond "c'est un véritable exploit...") d'une génération à
# l'autre, même sur des sujets différents — signalé en conditions réelles ("toujours les mêmes
# textes"). Un style d'ouverture tiré au sort à chaque génération casse ce moule.
_STYLES_OUVERTURE = [
    "Marco lance une phrase surprenante ou un chiffre marquant AVANT même que Clio ne dise quoi que ce soit.",
    "Clio commence en réagissant à ce qu'elle voit ou ressent dans ce décor précis, avant de poser sa question.",
    "Clio commence par une objection ou un doute (« ça semble impossible » / « je ne te crois pas »), que Marco doit lever.",
    "Marco commence par une question rhétorique piège posée à Clio, pour la surprendre.",
    "La scène démarre in medias res, comme si Clio et Marco étaient déjà en plein débat animé sur le sujet.",
    "Clio commence par comparer ce sujet à quelque chose de la vie quotidienne moderne, avant que Marco ne corrige ou complète.",
]


def _instruction(sujet: str) -> str:
    style = secrets.choice(_STYLES_OUVERTURE)
    return (
        "Tu écris un court dialogue théâtral, en français, entre deux personnages qui racontent "
        "un événement historique RÉEL et bien documenté à un public. Reste factuellement exact — "
        "n'invente aucun événement, aucune date, aucun personnage.\n\n"
        "Personnages : Clio (curieuse, pose des questions, s'étonne) et Marco (le conteur, sait, "
        "explique avec plaisir et un peu de dramatisation). Varie leurs formulations d'une "
        "génération à l'autre : évite de toujours faire démarrer Clio par « Marco, peux-tu "
        "m'expliquer... » ou Marco par « C'est un véritable exploit... » — invente des tournures "
        "différentes à chaque fois.\n\n"
        f"Sujet imposé : {sujet}\n\n"
        f"Style d'ouverture imposé pour la première réplique : {style}\n\n"
        "Structure OBLIGATOIRE : exactement 2 scènes, exactement 4 répliques dans CHAQUE scène "
        "(8 répliques au total, jamais moins) — une histoire trop courte est incompréhensible, "
        "ne t'arrête jamais avant la 4e réplique d'une scène. Alterne Clio et Marco.\n\n"
        "Choisis UN SEUL décor pour tout l'épisode (le MÊME dans les 2 scènes — ne change jamais "
        "de décor en cours d'histoire, ça ne doit décrire qu'un seul lieu/une seule ambiance), "
        f"dans cette liste fermée (jamais un autre mot) : {', '.join(DECORS)}.\n\n"
        "Chaque réplique porte aussi un champ \"emotion\" reflétant ce que RESSENT le personnage "
        f"en la prononçant, choisie dans cette liste fermée (jamais un autre mot) : {', '.join(EMOTIONS)}. "
        "Varie les émotions selon le contenu réel de la réplique (un fait terrible = triste ou "
        "inquiet, une révélation étonnante = surprise, une conclusion triomphante = joyeux) — "
        "pas la même émotion sur toutes les répliques.\n\n"
        "Le champ \"annee\" doit être l'année ou la période HISTORIQUE de l'événement décrit dans "
        "le sujet imposé ci-dessus (jamais l'année actuelle, jamais une autre époque).\n\n"
        "Réponds TOUJOURS entièrement en français, du début à la fin, sans jamais basculer même "
        "brièvement dans une autre langue (pas de mot ni de caractère en anglais, chinois ou "
        "autre) — y compris à l'intérieur d'une même réplique.\n\n"
        "Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte autour, exactement au "
        f"format : {_SCHEMA_ATTENDU}"
    )


# Un modèle instruit d'écrire "entièrement en français" peut malgré tout basculer brièvement
# vers une autre langue en cours de réplique (déjà observé sur l'assistant d'aide, reproduit ici
# en testant : une réplique générée contenait un fragment en chinois). Plutôt que de compter
# uniquement sur la consigne, on rejette explicitement toute réplique contenant des caractères
# hors alphabet latin — le retry (ou le repli sur un épisode écrit à la main) prend le relais.
_CARACTERES_NON_LATINS = re.compile(r"[一-鿿぀-ヿ가-힯Ѐ-ӿ]")


# Bugs réels trouvés en conditions réelles ("on ne comprend pas l'histoire du tout") : le modèle
# a un jour renvoyé seulement 2 répliques dans une scène au lieu de 4 (histoire tronquée, abrupte)
# ET changé de décor entre les 2 scènes d'un même récit continu (une traversée océanique qui
# bascule sur une plaine venteuse en 2e scène) — les deux structurellement valides selon l'ancien
# schéma (Pydantic/JSON n'imposait qu'un décor par scène, sans borne sur le nombre de répliques
# ni de contrainte inter-scènes), mais racontant quelque chose d'incohérent. D'où les 2 contrôles
# ci-dessous, en plus de la consigne renforcée dans le prompt — la consigne seule ne suffit pas.
_MIN_REPLIQUES_PAR_SCENE = 4


def _valider_episode(data: dict) -> dict:
    if not isinstance(data.get("titre"), str) or not data["titre"].strip():
        raise ValueError("titre manquant")
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or len(scenes) < 2:
        raise ValueError("il faut au moins 2 scènes")

    scenes_validees = []
    decor_episode = None
    for scene in scenes:
        decor = scene.get("decor")
        if decor not in DECORS:
            raise ValueError(f"décor inconnu : {decor}")
        if decor_episode is None:
            decor_episode = decor
        elif decor != decor_episode:
            raise ValueError(f"décor incohérent entre les scènes : {decor_episode} puis {decor}")

        repliques = scene.get("repliques")
        if not isinstance(repliques, list) or len(repliques) < _MIN_REPLIQUES_PAR_SCENE:
            raise ValueError(
                f"scène trop courte ({len(repliques) if isinstance(repliques, list) else 0} répliques, "
                f"minimum {_MIN_REPLIQUES_PAR_SCENE}) — histoire tronquée"
            )
        repliques_validees = []
        for r in repliques:
            personnage = r.get("personnage")
            texte = r.get("texte")
            emotion = r.get("emotion") if r.get("emotion") in EMOTIONS else "neutre"
            if personnage not in PERSONNAGES:
                raise ValueError(f"personnage inconnu : {personnage}")
            if not isinstance(texte, str) or not texte.strip():
                raise ValueError("réplique vide")
            if _CARACTERES_NON_LATINS.search(texte):
                raise ValueError("caractères non latins détectés dans la réplique")
            repliques_validees.append({"personnage": personnage, "emotion": emotion, "texte": texte.strip()[:500]})
        scenes_validees.append({"decor": decor, "repliques": repliques_validees})

    return {
        "id": "genere-" + secrets.token_hex(4),
        "titre": data["titre"].strip()[:120],
        "annee": str(data.get("annee", "")).strip()[:20],
        "scenes": scenes_validees,
        "genere_par_ia": True,
    }


@router.get("/episodes")
def episodes():
    return [{"id": e["id"], "titre": e["titre"], "annee": e["annee"]} for e in EPISODES]


@router.get("/episodes/{episode_id}")
def episode(episode_id: str):
    for e in EPISODES:
        if e["id"] == episode_id:
            return e
    raise HTTPException(404, "Épisode inconnu.")


class VoixRequest(BaseModel):
    texte: str = Field(min_length=1, max_length=600)
    personnage: str = Field(max_length=16)


@router.post("/voix")
async def synthese_vocale(requete: VoixRequest):
    if requete.personnage not in PERSONNAGES:
        raise HTTPException(400, "Personnage inconnu.")
    audio = await asyncio.to_thread(voix.synthetiser, requete.texte, requete.personnage)
    return Response(content=audio, media_type="audio/wav")


async def _executer_generation(job_id: str) -> None:
    sujet = secrets.choice(_SUJETS)
    episode_final = None

    # La validation plus stricte (2 scènes, 4 répliques min., décor unique) rejette plus souvent
    # qu'avant — 3 essais plutôt que 2 pour ne pas trop souvent retomber sur le repli, sans
    # jamais assouplir les contrôles qui garantissent une histoire compréhensible.
    for _ in range(3):
        try:
            brut = await ollama.generate(_MODELE_CONTEUR, _instruction(sujet))
            match = re.search(r"\{.*\}", brut, re.DOTALL)
            if not match:
                continue
            data = json.loads(match.group(0))
            episode_final = _valider_episode(data)
            break
        except Exception:  # noqa: BLE001 — on retente une fois, sinon on dégrade proprement
            continue

    # Dégradation propre : un épisode déjà écrit à la main plutôt qu'une erreur affichée au visiteur.
    if episode_final is None:
        episode_final = secrets.choice(EPISODES)

    _JOBS.terminer(job_id, {"episode": episode_final})


@router.post("/generer")
async def generer():
    try:
        job_id = _JOBS.creer()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    asyncio.create_task(_executer_generation(job_id))
    return {"job_id": job_id}


@router.get("/generer/{job_id}")
def generer_statut(job_id: str):
    job = _JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, "Job inconnu.")
    if job["status"] == "en_cours":
        return {"status": "en_cours"}
    return {"status": job["status"], **job.get("fin_extra", {})}
