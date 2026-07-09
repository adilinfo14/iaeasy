from fastapi import APIRouter

router = APIRouter(prefix="/videos", tags=["videos"])

VIDEOS = [
    {
        "id": "in-the-loop-evals",
        "titre": "Mettre en production des agents IA : établir les bases de la confiance",
        "youtube_id": "67fBGjTrrJc",
        "description": (
            "Tester un agent une fois qu'il est en production, c'est déjà trop tard si l'erreur a "
            "un impact réel. L'idée du « in the loop » : glisser des points de vérification "
            "DANS le déroulé de l'agent lui-même, pas seulement après coup dans un tableau de bord."
        ),
        "source": (
            "Les schémas décrits ci-dessous proviennent d'une présentation d'OCTO (part of "
            "Accenture), © 2025, tous droits réservés. Les visuels originaux ne sont pas reproduits "
            "ici : les explications qui suivent sont une description en nos propres mots des "
            "concepts qu'ils illustrent, à but pédagogique."
        ),
        "schemas": [
            {
                "titre": "RAG correctif : la vérification fait partie du graphe",
                "explication": (
                    "Ce schéma illustre un RAG « correctif » (Corrective RAG) : contrairement au RAG "
                    "simple de ce site (une seule recherche, une seule réponse), ici chaque étape est "
                    "vérifiée avant de continuer. Le déroulé : la question est d'abord aiguillée "
                    "(« Routing ») selon qu'elle concerne ou non les documents indexés. Si oui, les "
                    "documents sont récupérés puis notés (« Grade Documents ») — si un seul document "
                    "est jugé non pertinent, l'agent ne se contente pas d'une mauvaise réponse : il "
                    "bascule sur une recherche web pour compléter l'information, avant de générer sa "
                    "réponse. Une fois la réponse générée, deux nouveaux contrôles s'enchaînent : "
                    "« Hallucinations ? » (la réponse invente-t-elle des faits absents du contexte "
                    "fourni ?) puis « Answers question ? » (la réponse répond-elle vraiment à la "
                    "question posée ?). En cas d'échec à l'un de ces contrôles, l'agent boucle en "
                    "arrière — regénère, ou relance une recherche — au lieu de renvoyer un résultat "
                    "raté. C'est exactement le principe de la brique « Vérificateur / auto-critique » "
                    "du Constructeur de ce site, en plus développé : la vérification n'est pas une "
                    "étape séparée après la réponse, elle fait partie intégrante du chemin normal."
                ),
            },
            {
                "titre": "Qui fait la vérification : un LLM ou un humain",
                "explication": (
                    "Une fois qu'on a décidé de vérifier « dans la boucle », reste à choisir qui "
                    "vérifie. Deux approches complémentaires, montrées côte à côte : le « LLM in the "
                    "loop » utilise un second modèle comme correcteur — un « Scorer » qui note une "
                    "réponse de 0 à 100 selon des critères précis qu'on lui donne, avec justification "
                    "optionnelle. C'est peu coûteux et automatisable à grande échelle, mais reste un "
                    "jugement de machine. Le « Human in the loop » ajoute un vrai humain avant "
                    "l'exécution d'une action sensible, avec 3 issues possibles : approuver tel quel "
                    "(envoyer un brouillon d'email sans y toucher), modifier avant exécution (changer "
                    "le destinataire avant l'envoi), ou rejeter en expliquant pourquoi (renvoyer le "
                    "brouillon à l'agent avec une consigne de correction). Sur ce site, le filtre de "
                    "Modération du Constructeur est une version simplifiée et automatisée de ce même "
                    "principe : bloquer une action avant qu'elle ne parte, plutôt que de la corriger "
                    "après coup."
                ),
            },
            {
                "titre": "Un agent concret : trier des mails de candidature",
                "explication": (
                    "Un exemple d'agent complet qui assemble tout ce qui précède, avec les 4 façons "
                    "d'évaluer un agent réunies sur un seul schéma. Un premier LLM, léger, se contente "
                    "de classer chaque mail entrant (« Message d'un candidat ? »). Seulement « si "
                    "oui », le mail passe une évaluation « in the loop » avant de déclencher l'agent "
                    "principal — pas question de laisser un agent aux capacités larges se déclencher "
                    "sur n'importe quel mail. L'agent lui-même est défini par deux blocs bien séparés : "
                    "un « Goal » (la consigne en plusieurs étapes : ajouter le candidat dans un "
                    "tableur, consulter l'agenda, trouver les contacts RH, envoyer un mail de synthèse) "
                    "et un « Environment » (les outils réels auxquels il a accès : tableur, agenda, "
                    "Gmail, contacts). C'est la même logique que la brique « Outil / MCP » de ce site, "
                    "simplement avec 4 outils au lieu d'un seul. Autour de l'agent, 3 filets de "
                    "sécurité supplémentaires : des « Controllers » avant chaque action (humain ou "
                    "automatisé, cf. schéma précédent) ; une évaluation « Online » sur le trafic réel "
                    "en production (ici via l'outil Langfuse, qui trace chaque exécution) ; et une "
                    "évaluation « Offline », effectuée avant la mise en production sur un jeu de test "
                    "préparé à l'avance, avec des métriques chiffrées (ex : 100% de pertinence, 100% "
                    "de bons appels d'outils). C'est très exactement ce que fait le module « Stratégie "
                    "de tests » de ce site : un cahier de test réutilisable, pensé à l'avance, plutôt "
                    "que de découvrir les problèmes une fois l'agent déjà en service."
                ),
            },
            {
                "titre": "Évaluer un agent à 3 niveaux, pas juste sa réponse finale",
                "explication": (
                    "Ce schéma reprend exactement la boucle ReAct enseignée dans le Parcours de ce "
                    "site (l'agent décide d'utiliser un outil, observe le résultat, recommence) — "
                    "mais y superpose 3 niveaux de vérification, du plus fin au plus large. "
                    "« Single Step » : chaque appel d'outil, pris isolément, correspond-il à l'appel "
                    "attendu à ce moment précis ? « Multi-Step » : la SÉQUENCE complète des appels, "
                    "sur toute la tâche, suit-elle l'enchaînement attendu ? « Final Answer » : la "
                    "réponse finale correspond-elle à une réponse de référence — le seul critère qu'on "
                    "utiliserait pour évaluer un simple LLM sans outils. Le niveau « Multi-Step » est "
                    "le plus facile à négliger : un agent peut arriver à la bonne réponse finale en "
                    "passant par un chemin inefficace ou hasardeux — la réponse a l'air juste, mais le "
                    "raisonnement qui y a mené n'est pas fiable pour autant, et ne le sera pas "
                    "forcément la prochaine fois."
                ),
            },
            {
                "titre": "Guardrails : des garde-fous avant ET après le LLM",
                "explication": (
                    "Ce schéma (inspiré du projet open-source guardrails-ai) résume une architecture "
                    "de garde-fous en 2 temps, autour d'un appel LLM classique (Prompt → LLM → "
                    "Output). Avant que le prompt n'atteigne le modèle, un « Input Guard » vérifie "
                    "trois choses : contient-il des données personnelles (« Contains PII ») ? "
                    "Est-il hors sujet (« Off Topic ») ? Est-ce une tentative de contournement "
                    "(« Jailbreak Attempt ») ? Après que le LLM a répondu, un « Output Guard » "
                    "symétrique vérifie la réponse avant de la laisser partir : contient-elle des "
                    "hallucinations, des propos injurieux, ou mentionne-t-elle un concurrent par "
                    "erreur ? Le principe à retenir : un garde-fou en entrée ne suffit jamais à lui "
                    "seul, il faut aussi vérifier ce qui sort. Sur ce site, la brique « Modération » "
                    "du Constructeur est un Input Guard minimal (liste de mots bloqués), et la brique "
                    "« Vérificateur / auto-critique » joue le rôle d'un Output Guard (relit et corrige "
                    "avant de renvoyer la réponse) — les deux combinées reproduisent ce schéma."
                ),
            },
        ],
    },
]


@router.get("")
def lister():
    return VIDEOS
