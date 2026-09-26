import json

from ..core.ollama_client import ollama
from . import tools

MODELE_LLM = "qwen2.5:7b-instruct"
MODELE_EMBED = "nomic-embed-text"

# Liste blanche stricte : le graphe est piloté par un payload JSON librement modifiable par
# l'appelant (config par nœud), donc rien n'empêche d'y glisser le nom d'un modèle non prévu —
# notamment le 70B présent sur l'Ollama partagé du homelab mais volontairement écarté ailleurs
# pour sa lourdeur. Sans ce filtre, un appel direct à /api/agents/run pourrait forcer son
# chargement et dégrader tous les autres services du serveur.
_MODELES_AUTORISES = {
    "qwen2.5:7b-instruct",
    "llama3.2:3b",
    "deepseek-coder:6.7b",
    "llama3:8b",
    "mistral:7b-instruct",
    "gemma2:2b",
    "phi3:mini",
}


def _modele_valide(config: dict, cle: str, defaut: str) -> str:
    valeur = config.get(cle)
    return valeur if valeur in _MODELES_AUTORISES else defaut


# Longueur max d'un champ texte libre (prompt, document...) injecté dans un appel Ollama —
# évite qu'un payload énorme ne ralentisse ou ne fasse échouer le modèle partagé.
_LONGUEUR_MAX_TEXTE = 4000


def _texte_borne(valeur, defaut: str) -> str:
    if not isinstance(valeur, str) or not valeur.strip():
        return defaut
    return valeur[:_LONGUEUR_MAX_TEXTE]

_MINI_CORPUS_RAG = tools._MINI_CORPUS

_MOTS_BLOQUES = ["pirater", "arnaque", "contourner la loi", "fabriquer une arme"]

_TOOLS_OLLAMA_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Évalue une expression arithmétique simple.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rechercher",
            "description": "Cherche un passage pertinent dans un petit corpus documentaire.",
            "parameters": {
                "type": "object",
                "properties": {"requete": {"type": "string"}},
                "required": ["requete"],
            },
        },
    },
]


def _topological_sort(nodes: list[dict], edges: list[dict]) -> list[str]:
    ids = [n["id"] for n in nodes]
    depend_de: dict[str, set[str]] = {i: set() for i in ids}
    for e in edges:
        depend_de[e["target"]].add(e["source"])

    ordre: list[str] = []
    restants = set(ids)
    while restants:
        prets = [i for i in restants if depend_de[i] <= set(ordre)]
        if not prets:
            raise ValueError("Le graphe contient un cycle ou une dépendance manquante")
        prets.sort(key=ids.index)
        ordre.append(prets[0])
        restants.discard(prets[0])
    return ordre


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def _normaliser_arguments(arguments) -> dict:
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except json.JSONDecodeError:
            return {}
    return arguments or {}


def _executer_outil(nom: str, arguments: dict) -> str:
    if nom == "calculer":
        return str(tools.calculatrice(arguments.get("expression", ""))["resultat"])
    if nom == "rechercher":
        return tools.recherche_mini_corpus(arguments.get("requete", ""))["passage"]
    return f"Outil inconnu: {nom}"


async def _handler_llm_seul(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    prompt = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Explique en une phrase ce qu'est un agent IA.")
    modele = _modele_valide(config, "modele", MODELE_LLM)
    reponse = await ollama.generate(modele, prompt)
    etapes.append({"brique": "llm_seul", "detail": f"Prompt envoyé à {modele} : « {prompt} »"})
    contexte["derniere_reponse"] = reponse
    return contexte


async def _handler_rag(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    requete = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Qu'est-ce que MCP ?")
    vecteur_requete = await ollama.embed(MODELE_EMBED, requete)

    # Quand un document d'entreprise est fourni (cas btp/banque/agriculture... de bricks.py), la
    # démo porte sur CE document précis — il ne doit jamais avoir à concurrencer le corpus
    # pédagogique générique (_MINI_CORPUS_RAG, des phrases sur RAG/MCP/ReAct/Isolation Forest,
    # sans rapport avec la question posée). Les mélanger faisait gagner un passage hors sujet par
    # similarité cosinus (signalé en conditions réelles : question sur une garantie décennale,
    # passage retrouvé sur l'entraînement d'un Isolation Forest). Sans document fourni, on retombe
    # sur le corpus générique pour l'exploration libre (pas de cas d'usage ciblé).
    document_utilisateur = config.get("document_utilisateur")
    if isinstance(document_utilisateur, str) and document_utilisateur.strip():
        corpus = [document_utilisateur[:_LONGUEUR_MAX_TEXTE]]
    else:
        corpus = list(_MINI_CORPUS_RAG)

    meilleur_passage, meilleur_score = corpus[0], -1.0
    for passage in corpus:
        vecteur_passage = await ollama.embed(MODELE_EMBED, passage)
        score = _cosine(vecteur_requete, vecteur_passage)
        if score > meilleur_score:
            meilleur_passage, meilleur_score = passage, score

    etapes.append(
        {
            "brique": "rag",
            "detail": f"Passage retrouvé (similarité {meilleur_score:.2f}) : « {meilleur_passage} »",
        }
    )
    prompt_augmente = (
        f"Contexte retrouvé : {meilleur_passage}\n\nQuestion : {requete}\n"
        "Réponds en t'appuyant sur ce contexte."
    )
    reponse = await ollama.generate(MODELE_LLM, prompt_augmente)
    contexte["derniere_reponse"] = reponse
    contexte["passage_retrouve"] = meilleur_passage
    return contexte


async def _handler_outil_mcp(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    outil = config.get("outil", "recherche")
    if outil == "calculatrice":
        expression = _texte_borne(config.get("expression"), "2 + 2")[:200]
        resultat = tools.calculatrice(expression)
        etapes.append(
            {"brique": "outil_mcp", "detail": f"Outil MCP 'calculer' sur « {expression} » -> {resultat}"}
        )
        contexte["resultat_outil"] = resultat
    else:
        # "requete" est le nom du champ déclaré par le schéma JSON de l'outil MCP "rechercher"
        # (voir bricks.py) — lire "prompt" ici (comme avant) faisait chercher dans le corpus le
        # texte de la DERNIÈRE expression calculatrice encore présente côté frontend, jamais une
        # vraie requête de recherche (signalé en conditions réelles : sélectionner "Recherche
        # documentaire" gardait "45 * 3.5 + 45 * 2.25" affiché et envoyé tel quel).
        requete = _texte_borne(config.get("requete") or contexte.get("prompt"), "MCP")
        resultat = tools.recherche_mini_corpus(requete)
        etapes.append(
            {
                "brique": "outil_mcp",
                "detail": f"Outil MCP 'rechercher' sur « {requete} » -> {resultat['passage']}",
            }
        )
        contexte["resultat_outil"] = resultat
    return contexte


async def _handler_agent_unique(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    tache = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Combien font 12 fois (3+4) ?")
    passages = contexte.get("passages_retrouves")
    if passages:
        tache = "Contexte documentaire disponible :\n" + "\n".join(passages) + f"\n\nTâche : {tache}"

    messages = [
        {
            "role": "system",
            "content": "Tu es un agent qui peut utiliser des outils (calculer, rechercher) pour répondre précisément.",
        },
        {"role": "user", "content": tache},
    ]

    for iteration in range(4):
        message = await ollama.chat(MODELE_LLM, messages, tools=_TOOLS_OLLAMA_SCHEMA)
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            etapes.append(
                {"brique": "agent_unique", "detail": f"Étape {iteration + 1} — réponse finale : {message['content']}"}
            )
            contexte["derniere_reponse"] = message["content"]
            return contexte

        messages.append(message)
        for appel in tool_calls:
            nom = appel["function"]["name"]
            arguments = _normaliser_arguments(appel["function"].get("arguments"))
            resultat = _executer_outil(nom, arguments)
            etapes.append(
                {
                    "brique": "agent_unique",
                    "detail": f"Étape {iteration + 1} — appel outil « {nom}({arguments}) » -> {resultat}",
                }
            )
            messages.append({"role": "tool", "content": resultat})

    contexte["derniere_reponse"] = "Nombre maximal d'itérations atteint sans réponse finale."
    return contexte


async def _handler_multi_agent(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    tache = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Résume ce qu'est le RAG pour un débutant.")

    messages_chercheur = [
        {
            "role": "system",
            "content": (
                "Tu es un agent CHERCHEUR : tu rassembles des faits bruts et précis, sans les "
                "mettre en forme, en t'aidant si besoin de l'outil 'rechercher'."
            ),
        },
        {"role": "user", "content": tache},
    ]
    reponse_chercheur = await ollama.chat(MODELE_LLM, messages_chercheur, tools=_TOOLS_OLLAMA_SCHEMA)
    if reponse_chercheur.get("tool_calls"):
        messages_chercheur.append(reponse_chercheur)
        for appel in reponse_chercheur["tool_calls"]:
            arguments = _normaliser_arguments(appel["function"].get("arguments"))
            resultat = _executer_outil(appel["function"]["name"], arguments)
            messages_chercheur.append({"role": "tool", "content": resultat})
        reponse_chercheur = await ollama.chat(MODELE_LLM, messages_chercheur)

    notes = reponse_chercheur["content"]
    etapes.append({"brique": "multi_agent", "detail": f"Agent chercheur -> notes brutes : {notes}"})

    messages_redacteur = [
        {
            "role": "system",
            "content": (
                "Tu es un agent RÉDACTEUR : tu reformules des notes brutes en une réponse claire "
                "et pédagogique, en 3-4 phrases maximum."
            ),
        },
        {"role": "user", "content": f"Notes du chercheur :\n{notes}\n\nTâche d'origine : {tache}"},
    ]
    reponse_redacteur = await ollama.chat(MODELE_LLM, messages_redacteur)
    etapes.append(
        {"brique": "multi_agent", "detail": f"Agent rédacteur -> réponse finale : {reponse_redacteur['content']}"}
    )

    contexte["derniere_reponse"] = reponse_redacteur["content"]
    return contexte


async def _handler_source_document(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    texte = _texte_borne(config.get("texte"), None) or (
        "La garantie décennale couvre les dommages de gros œuvre pendant 10 ans après réception. "
        "La garantie biennale couvre les équipements dissociables (chauffe-eau, volets) pendant 2 ans. "
        "Le paiement se fait en 3 fois : 30% à la commande, 40% à mi-chantier, 30% à la réception. "
        "Les interventions sont planifiées du lundi au vendredi, de 8h à 17h, hors jours fériés."
    )
    etapes.append({"brique": "source_document", "detail": f"Document source chargé ({len(texte)} caractères)."})
    contexte["document"] = texte
    return contexte


def _decouper_en_chunks(document: str, taille: int = 120) -> list[str]:
    phrases = [p.strip() for p in document.replace("\n", " ").split(".") if p.strip()]
    chunks: list[str] = []
    courant = ""
    for p in phrases:
        if courant and len(courant) + len(p) > taille:
            chunks.append(courant.strip())
            courant = ""
        courant += p + ". "
    if courant.strip():
        chunks.append(courant.strip())
    return chunks


async def _handler_chunking(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    document = contexte.get("document", "")
    taille_chunk = config.get("taille_chunk", 120)
    if not isinstance(taille_chunk, (int, float)) or isinstance(taille_chunk, bool) or not (20 <= taille_chunk <= 2000):
        taille_chunk = 120
    chunks = _decouper_en_chunks(document, int(taille_chunk))
    etapes.append({"brique": "chunking", "detail": f"Document découpé en {len(chunks)} morceaux (chunks)."})
    contexte["chunks"] = chunks
    return contexte


async def _handler_base_vectorielle(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    chunks = contexte.get("chunks") or list(_MINI_CORPUS_RAG)
    requete = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Quelles sont les conditions de garantie ?")

    vecteur_requete = await ollama.embed(MODELE_EMBED, requete)
    scores = []
    for chunk in chunks:
        vecteur_chunk = await ollama.embed(MODELE_EMBED, chunk)
        scores.append((chunk, _cosine(vecteur_requete, vecteur_chunk)))
    scores.sort(key=lambda x: x[1], reverse=True)
    top_k = scores[:2]

    etapes.append(
        {
            "brique": "base_vectorielle",
            "detail": (
                f"Base vectorielle interrogée : {len(chunks)} chunks indexés, meilleur score "
                f"{top_k[0][1]:.2f} : « {top_k[0][0][:100]} »"
            ),
        }
    )
    contexte["passages_retrouves"] = [c for c, _ in top_k]
    contexte["prompt"] = requete
    return contexte


async def _handler_llm_agent(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    if contexte.get("bloque"):
        return contexte

    passages = contexte.get("passages_retrouves")
    requete = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Résume la situation.")
    modele = _modele_valide(config, "modele", MODELE_LLM)

    if passages:
        prompt_final = (
            "Contexte :\n" + "\n".join(passages) + f"\n\nQuestion : {requete}\n"
            "Réponds uniquement à partir de ce contexte."
        )
    else:
        prompt_final = requete

    reponse = await ollama.generate(modele, prompt_final)
    etapes.append({"brique": "llm_agent", "detail": f"{modele} interrogé avec le prompt final (augmenté si un retrieval a eu lieu)."})
    contexte["derniere_reponse"] = reponse
    return contexte


async def _handler_comparateur(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    prompt = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Explique ce qu'est le RAG en une phrase.")
    modele_a = _modele_valide(config, "modele_a", "llama3.2:3b")
    modele_b = _modele_valide(config, "modele_b", "qwen2.5:7b-instruct")

    reponse_a = await ollama.generate(modele_a, prompt)
    etapes.append({"brique": "comparateur", "detail": f"{modele_a} -> {reponse_a}"})
    reponse_b = await ollama.generate(modele_b, prompt)
    etapes.append({"brique": "comparateur", "detail": f"{modele_b} -> {reponse_b}"})

    contexte["reponse_a"] = reponse_a
    contexte["reponse_b"] = reponse_b
    contexte["derniere_reponse"] = f"[{modele_a}] {reponse_a}\n\n[{modele_b}] {reponse_b}"
    return contexte


async def _handler_synthese_map_reduce(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    chunks = contexte.get("chunks") or _decouper_en_chunks(contexte.get("document", ""))
    resumes_partiels = []
    for i, chunk in enumerate(chunks):
        resume = await ollama.generate(MODELE_LLM, f"Résume ce passage en une phrase courte :\n{chunk}")
        resumes_partiels.append(resume)
        etapes.append({"brique": "synthese_map_reduce", "detail": f"Résumé du morceau {i + 1}/{len(chunks)} : {resume}"})

    synthese_finale = await ollama.generate(
        MODELE_LLM,
        "Synthétise ces résumés partiels en un seul paragraphe cohérent :\n" + "\n".join(resumes_partiels),
    )
    etapes.append({"brique": "synthese_map_reduce", "detail": "Synthèse finale des résumés partiels générée."})
    contexte["derniere_reponse"] = synthese_finale
    return contexte


async def _handler_moderation(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    prompt = _texte_borne(config.get("prompt") or contexte.get("prompt"), "")
    prompt_minuscule = prompt.lower()
    mot_bloque = next((m for m in _MOTS_BLOQUES if m in prompt_minuscule), None)

    if mot_bloque:
        etapes.append({"brique": "moderation", "detail": f"Requête bloquée (mot-clé détecté : « {mot_bloque} »)."})
        contexte["bloque"] = True
        contexte["derniere_reponse"] = "Désolé, je ne peux pas répondre à cette demande."
    else:
        etapes.append({"brique": "moderation", "detail": "Requête acceptée par le filtre de modération."})
        contexte["bloque"] = False
        contexte["prompt"] = prompt
    return contexte


async def _handler_verification(config: dict, contexte: dict, etapes: list[dict]) -> dict:
    if contexte.get("bloque"):
        return contexte

    prompt = _texte_borne(config.get("prompt") or contexte.get("prompt"), "Combien font 17 fois 23 ?")
    brouillon = await ollama.generate(MODELE_LLM, prompt)
    etapes.append({"brique": "verification", "detail": f"Brouillon de réponse : {brouillon}"})

    verification_prompt = (
        f"Question d'origine : {prompt}\nRéponse proposée : {brouillon}\n"
        "Vérifie cette réponse (notamment les calculs et les faits). Si elle est correcte, "
        "renvoie-la telle quelle. Si elle contient une erreur, corrige-la et explique brièvement pourquoi."
    )
    reponse_corrigee = await ollama.generate(MODELE_LLM, verification_prompt)
    etapes.append({"brique": "verification", "detail": f"Réponse après vérification/correction : {reponse_corrigee}"})

    contexte["derniere_reponse"] = reponse_corrigee
    return contexte


_HANDLERS = {
    "llm_seul": _handler_llm_seul,
    "rag": _handler_rag,
    "outil_mcp": _handler_outil_mcp,
    "agent_unique": _handler_agent_unique,
    "multi_agent": _handler_multi_agent,
    "source_document": _handler_source_document,
    "chunking": _handler_chunking,
    "base_vectorielle": _handler_base_vectorielle,
    "llm_agent": _handler_llm_agent,
    "comparateur": _handler_comparateur,
    "synthese_map_reduce": _handler_synthese_map_reduce,
    "moderation": _handler_moderation,
    "verification": _handler_verification,
}


_MAX_NOEUDS = 20
_MAX_ARETES = 40


async def executer_graphe(nodes: list[dict], edges: list[dict]) -> dict:
    # Chaque nœud peut déclencher plusieurs appels à Ollama (jusqu'à 4 itérations pour un
    # agent ReAct, un appel par chunk pour le résumé hiérarchique...) : sans plafond, un
    # graphe démesurément grand pourrait saturer l'Ollama partagé du homelab.
    if len(nodes) > _MAX_NOEUDS:
        raise ValueError(f"Trop de nœuds dans le graphe (max {_MAX_NOEUDS}).")
    if len(edges) > _MAX_ARETES:
        raise ValueError(f"Trop d'arêtes dans le graphe (max {_MAX_ARETES}).")

    ordre = _topological_sort(nodes, edges)
    noeuds_par_id = {n["id"]: n for n in nodes}
    aretes_entrantes: dict[str, list[dict]] = {n["id"]: [] for n in nodes}
    for e in edges:
        aretes_entrantes[e["target"]].append(e)

    contexte: dict = {}
    etapes: list[dict] = []
    resultats_par_noeud: dict[str, dict] = {}
    executes: set[str] = set()

    def _noeud_actif(node_id: str) -> bool:
        entrantes = aretes_entrantes[node_id]
        if not entrantes:
            return True
        bloque_actuel = bool(contexte.get("bloque"))
        for arete in entrantes:
            if arete["source"] not in executes:
                continue  # le nœud source a lui-même été ignoré : ce lien ne compte pas
            condition = arete.get("condition")
            if condition is None:
                return True
            if condition == "autorise" and not bloque_actuel:
                return True
            if condition == "bloque" and bloque_actuel:
                return True
        return False

    for node_id in ordre:
        noeud = noeuds_par_id[node_id]
        type_brique = noeud["type"]
        handler = _HANDLERS.get(type_brique)
        if handler is None:
            raise ValueError(f"Type de brique inconnu : {type_brique}")

        if not _noeud_actif(node_id):
            etapes.append(
                {
                    "brique": type_brique,
                    "detail": "Nœud ignoré : la condition du lien entrant n'est pas remplie (branche non empruntée).",
                }
            )
            resultats_par_noeud[node_id] = {"ignore": True}
            continue

        contexte = await handler(noeud.get("config", {}), contexte, etapes)
        executes.add(node_id)
        resultats_par_noeud[node_id] = dict(contexte)

    return {
        "etapes": etapes,
        "reponse_finale": contexte.get("derniere_reponse"),
        "resultats_par_noeud": resultats_par_noeud,
    }
