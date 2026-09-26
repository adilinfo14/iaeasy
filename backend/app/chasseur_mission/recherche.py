import json
import re
from datetime import date

import httpx

from ..core.config import settings

_MODELE = "claude-sonnet-5"

# Contraintes CGU reprises telles quelles de l'étude de faisabilité initiale — un vrai appel
# web_search s'exécute côté serveur Anthropic, mais les règles de prudence par plateforme restent
# les mêmes qu'une recherche manuelle : on les redonne explicitement au modèle à chaque passe.
_CONTRAINTES = """Tu es un agent de recherche de missions et d'offres d'emploi, spécialisé sur deux
familles : conseil/IT et pilote de drone, en France et au Maroc, freelance et CDI.

Règles strictes (CGU des plateformes) à respecter impérativement pendant cette recherche :
- Ne jamais cibler linkedin.com par une requête de recherche dédiée à ce site ni y naviguer page
  par page : seules des mentions issues d'une recherche web généraliste sont acceptables.
- DroneConnect.fr : usage ponctuel et modéré seulement (quelques pages maximum), jamais de boucle.
- Indeed : usage modéré toléré.
- Rekrute.com : zone grise CGU — quelques pages maximum, usage ponctuel.
- Comet.co et Freelance.com : recherche web généraliste uniquement, jamais de visite directe et
  répétée de leurs pages de listing (CGU/robots.txt restrictifs sur ce point).
- ANAPEC (Maroc) : recherche et consultation ponctuelle autorisées.
- Cette recherche doit rester UNE passe raisonnable, jamais un crawl répété ou une collecte à
  haute fréquence.

Pour chaque mission ou offre réelle et vérifiable trouvée, donne les champs suivants (aucun champ
inventé — laisse une chaîne vide si une information manque) :
id (slug court unique, minuscules, tirets), intitule, entreprise, ville, pays ("France" ou
"Maroc"), famille ("conseil_it" ou "drone"), type_contrat ("freelance" ou "cdi"), remuneration
(texte libre, vide si absente), lien (URL réelle trouvée), source (nom du site d'origine).

Termine ta réponse par UNIQUEMENT un bloc JSON, sans aucun texte avant ou après, de la forme :
{"missions": [...], "notes": "un paragraphe honnête sur les limites de cette passe : offres
expirées écartées, sites inaccessibles rencontrés, incertitude sur la fraîcheur, etc."}
"""


def _extraire_json(texte: str) -> dict:
    # Un simple regex glouton \{.*\} peut déborder sur un texte qui contient d'autres accolades
    # avant/après le bloc utile (ex. citations, blocs de code dans les notes). On repère plutôt la
    # première accolade ouvrante puis on compte les accolades une à une (en ignorant celles à
    # l'intérieur des chaînes de caractères) pour trouver sa fermeture exacte.
    texte = texte.strip()
    texte = re.sub(r"^```(?:json)?\n?", "", texte)
    texte = re.sub(r"\n?```$", "", texte)

    debut = texte.find("{")
    if debut == -1:
        return {"missions": [], "notes": "Réponse non exploitable : aucun bloc JSON détecté."}

    profondeur = 0
    dans_chaine = False
    echappement = False
    fin = -1
    for i in range(debut, len(texte)):
        c = texte[i]
        if dans_chaine:
            if echappement:
                echappement = False
            elif c == "\\":
                echappement = True
            elif c == '"':
                dans_chaine = False
            continue
        if c == '"':
            dans_chaine = True
        elif c == "{":
            profondeur += 1
        elif c == "}":
            profondeur -= 1
            if profondeur == 0:
                fin = i
                break

    if fin == -1:
        return {"missions": [], "notes": "Réponse non exploitable : bloc JSON incomplet (probablement tronqué)."}

    try:
        return json.loads(texte[debut : fin + 1])
    except json.JSONDecodeError:
        return {"missions": [], "notes": "Bloc JSON malformé, résultat ignoré."}


async def rechercher_missions(mots_cles: str, pays: list[str]) -> dict:
    pays_txt = " et ".join(pays) if pays else "France et Maroc"
    consigne = (
        f"Recherche des missions/offres réelles et récentes en {pays_txt}"
        + (f", en ciblant particulièrement : {mots_cles}." if mots_cles else ".")
        + " Vise entre 5 et 15 missions vérifiables, pas plus — mieux vaut peu et fiable que"
        " beaucoup et douteux."
    )

    messages: list[dict] = [{"role": "user", "content": consigne}]
    nb_recherches = 0
    data: dict = {}

    # allowed_callers=["direct"] force un appel web_search direct plutôt que via le sandbox
    # code_execution (filtrage dynamique) : ce sandbox se heurtait systématiquement à une erreur
    # "Server tool use limit exceeded" en pratique, alors que l'appel direct est rapide et fiable.
    async with httpx.AsyncClient(timeout=400) as client:
        # Le tool web_search est exécuté côté serveur Anthropic (limité à 6 recherches ici) ; une
        # seule relance suffit si cette limite est atteinte (stop_reason "pause_turn").
        for _ in range(2):
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": _MODELE,
                    "max_tokens": 16000,
                    "system": _CONTRAINTES,
                    "tools": [
                        {
                            "type": "web_search_20260209",
                            "name": "web_search",
                            "max_uses": 8,
                            "allowed_callers": ["direct"],
                        }
                    ],
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data = resp.json()

            nb_recherches += sum(
                1 for bloc in data.get("content", []) if bloc.get("type") == "web_search_tool_result"
            )

            if data.get("stop_reason") != "pause_turn":
                break
            messages = [
                {"role": "user", "content": consigne},
                {"role": "assistant", "content": data["content"]},
            ]

    texte_final = "".join(
        bloc.get("text", "") for bloc in data.get("content", []) if bloc.get("type") == "text"
    )
    resultat = _extraire_json(texte_final)
    resultat.setdefault("missions", [])
    resultat.setdefault("notes", "")
    resultat["nb_recherches"] = nb_recherches

    aujourdhui = date.today().isoformat()
    for m in resultat["missions"]:
        if isinstance(m, dict):
            m.setdefault("date_collecte", aujourdhui)

    return resultat
