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
                "schema": [
                    {"icone": "❓", "label": "Question"},
                    {"icone": "🔀", "label": "Aiguillage"},
                    {"icone": "📄", "label": "Recherche docs"},
                    {"icone": "✅", "label": "Notation docs"},
                    {"icone": "🌐", "label": "Web (si besoin)"},
                    {"icone": "🧠", "label": "Génération"},
                    {"icone": "🔁", "label": "Vérifications"},
                    {"icone": "✅", "label": "Réponse"},
                ],
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
                "schema": [
                    {"icone": "📤", "label": "Action proposée"},
                    {"icone": "🔀", "label": "Contrôleur (LLM ou humain)"},
                    {"icone": "✅✏️❌", "label": "Approuver / Modifier / Rejeter"},
                    {"icone": "▶️", "label": "Exécution"},
                ],
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
                "schema": [
                    {"icone": "📧", "label": "Mail reçu"},
                    {"icone": "🧠", "label": "LLM classifieur"},
                    {"icone": "🚪", "label": "Éval. in-the-loop"},
                    {"icone": "🤖", "label": "Agent (Goal + Environment)"},
                    {"icone": "✅", "label": "Action exécutée"},
                ],
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
                "schema": [
                    {"icone": "❓", "label": "Tâche"},
                    {"icone": "🤔", "label": "Le LLM réfléchit"},
                    {"icone": "🛠️", "label": "Appelle un outil"},
                    {"icone": "🔁", "label": "Répète si besoin"},
                    {"icone": "✅", "label": "Réponse finale"},
                ],
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
                "schema": [
                    {"icone": "📝", "label": "Prompt"},
                    {"icone": "🛡️", "label": "Input Guard"},
                    {"icone": "🧠", "label": "LLM"},
                    {"icone": "🛡️", "label": "Output Guard"},
                    {"icone": "✅", "label": "Réponse"},
                ],
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
    {
        "id": "octo-rag-entreprise",
        "titre": "Maîtriser le RAG : connecter les modèles d'IA Gen aux données de l'entreprise",
        "youtube_id": "9tmlseutQM8",
        "description": (
            "Le RAG expliqué du point de vue de l'entreprise qui doit le déployer : où va "
            "réellement l'argent, comment savoir s'il fonctionne, et jusqu'où pousser la "
            "sobriété — bien au-delà de la seule mécanique retrieval + génération déjà vue "
            "dans la brique RAG de ce site."
        ),
        "source": (
            "Le schéma décrit ci-dessous provient d'une présentation d'OCTO Technology (part of "
            "Accenture), série « Le Comptoir OCTO », © 2025, tous droits réservés. Les visuels "
            "originaux ne sont pas reproduits ici : l'explication qui suit est une description en "
            "nos propres mots des concepts qu'ils illustrent, à but pédagogique."
        ),
        "schemas": [
            {
                "titre": "Le coût réel d'un RAG : où va l'argent",
                "schema": [
                    {"icone": "❓", "label": "Question"},
                    {"icone": "🔎", "label": "Recherche vectorielle (coût marginal)"},
                    {"icone": "📄", "label": "Passages retrouvés"},
                    {"icone": "🧠", "label": "Appel LLM (~99% du coût total)"},
                    {"icone": "✅", "label": "Réponse"},
                ],
                "explication": (
                    "Un constat chiffré qui surprend souvent : dans un pipeline RAG (le même "
                    "principe que la brique RAG de ce site — retrouver un passage pertinent puis "
                    "laisser un LLM répondre en s'appuyant dessus), la recherche vectorielle "
                    "elle-même coûte presque rien à faire tourner. C'est l'appel au LLM pour "
                    "générer la réponse finale qui concentre environ 99% du coût réel du système. "
                    "Concrètement, cela veut dire que pour réduire la facture d'un RAG en "
                    "production, optimiser l'indexation ou la recherche a peu d'effet — c'est sur "
                    "le choix du modèle générateur (sa taille, son fournisseur) que se joue "
                    "l'essentiel des économies. La vidéo évoque aussi deux prolongements utiles : "
                    "des cadres d'évaluation dédiés au RAG (RAGAS, TruLens) pour mesurer "
                    "objectivement la qualité des réponses plutôt qu'à l'œil, et un outil de mesure "
                    "d'impact environnemental (CodeCarbon) — la sobriété numérique n'étant pas "
                    "qu'une question de coût, mais aussi d'empreinte carbone. Elle pointe enfin vers "
                    "une tendance à surveiller : remplacer un LLM généraliste massif par un petit "
                    "modèle de langage (SLM) exécuté localement, pour les cas où la tâche ne "
                    "justifie pas la puissance — et donc le coût — d'un très gros modèle."
                ),
            },
        ],
    },
    {
        "id": "octo-agents-ia",
        "titre": "Agents IA : Tout ce qu'il faut savoir",
        "youtube_id": "z2j5RfWNrNk",
        "description": (
            "Une distinction essentielle et souvent confondue : un « workflow agentique » (des "
            "étapes connues à l'avance, orchestrées) n'est pas la même chose qu'un « agent IA » "
            "autonome — avec des critères concrets pour savoir lequel choisir."
        ),
        "source": (
            "Le schéma décrit ci-dessous provient d'une présentation d'OCTO Technology (part of "
            "Accenture), série « Le Comptoir OCTO », © 2025, tous droits réservés. Les visuels "
            "originaux ne sont pas reproduits ici : l'explication qui suit est une description en "
            "nos propres mots des concepts qu'ils illustrent, à but pédagogique."
        ),
        "schemas": [
            {
                "titre": "Workflow orchestré ou agent autonome : la question à se poser",
                "schema": [
                    {"icone": "❓", "label": "Les étapes sont-elles connues à l'avance ?"},
                    {"icone": "✅", "label": "Oui → workflow (chaînage, routage, parallélisation)"},
                    {"icone": "❌", "label": "Non → agent autonome (mémoire + outils + décision)"},
                ],
                "explication": (
                    "La vidéo distingue deux familles qu'on confond souvent sous le même mot "
                    "« agent ». Un « agentic workflow » enchaîne des étapes prédéfinies par un "
                    "humain — prompt chaining (une sortie nourrit le prompt suivant), routage "
                    "(aiguiller vers le bon traitement selon la demande), exécution en parallèle, "
                    "ou un couple évaluateur-optimiseur qui boucle jusqu'à un résultat satisfaisant. "
                    "Rien de tout cela ne décide vraiment par lui-même : le chemin est fixé à "
                    "l'avance, seul le contenu varie. Un « agent IA » au sens strict, lui, décide "
                    "SEUL de la suite à chaque étape — c'est très exactement la boucle ReAct de la "
                    "brique « Agent unique » de ce site : le modèle choisit d'utiliser un outil, "
                    "observe le résultat, puis décide de la suite, sans qu'on lui impose le chemin. "
                    "La vidéo introduit aussi le protocole MCP (Model Context Protocol, déjà "
                    "rencontré dans la brique « Outil / MCP » de ce site) comme le standard qui "
                    "permet à un agent d'appeler des outils de façon uniforme, plutôt que de coder "
                    "une intégration différente pour chaque service. Le message pratique à retenir "
                    ": un vrai agent autonome coûte plus cher et est moins prévisible qu'un workflow "
                    "— à réserver aux cas où le chemin ne PEUT pas être connu à l'avance, pas à "
                    "utiliser par défaut dès qu'une tâche implique plusieurs étapes."
                ),
            },
        ],
    },
    {
        "id": "octo-evaluer-rag",
        "titre": "Évaluer un projet de RAG",
        "youtube_id": "BQhkeGqA3XI",
        "description": (
            "Comment savoir si un RAG « marche » vraiment, avec des chiffres plutôt qu'une "
            "impression — jeux de test, métriques classiques vs un LLM qui juge un autre LLM, "
            "et une méthode inspirée du développement piloté par les tests."
        ),
        "source": (
            "Le schéma décrit ci-dessous provient d'une présentation d'OCTO Technology (part of "
            "Accenture), série « Le Comptoir OCTO », © 2025, tous droits réservés. Les visuels "
            "originaux ne sont pas reproduits ici : l'explication qui suit est une description en "
            "nos propres mots des concepts qu'ils illustrent, à but pédagogique."
        ),
        "schemas": [
            {
                "titre": "LLM as Judge : faire noter une réponse par un second modèle",
                "schema": [
                    {"icone": "❓", "label": "Question + contexte de référence"},
                    {"icone": "🧠", "label": "LLM à évaluer → réponse"},
                    {"icone": "⚖️", "label": "LLM juge (critères précis donnés à l'avance)"},
                    {"icone": "📊", "label": "Score (~85% d'accord avec un humain)"},
                ],
                "explication": (
                    "Avant même de parler de méthode, la vidéo pose une contrainte statistique "
                    "concrète : il faut environ 100 questions-contextes-réponses dans un jeu de "
                    "test pour pouvoir affirmer, de façon fiable, qu'un système RAG est meilleur "
                    "qu'un autre avec plus de 10% d'écart — en dessous, la différence observée peut "
                    "n'être que du bruit. Pour noter chaque réponse, deux familles de méthodes "
                    "s'opposent. Les métriques classiques (ROUGE, BLEU, BERTScore) comparent le "
                    "texte généré à une réponse de référence, mot à mot ou par similarité — rapides "
                    "mais rigides, elles pénalisent une reformulation pourtant correcte. Le « LLM as "
                    "Judge » confie plutôt la notation à un second LLM, à qui l'on donne des "
                    "critères explicites (exactitude, complétude, absence d'invention) : la vidéo "
                    "cite un taux d'accord d'environ 85% avec un jugement humain majoritaire — pas "
                    "parfait, mais nettement plus proche du jugement humain que les métriques "
                    "classiques, pour un coût très inférieur à une évaluation humaine systématique. "
                    "La démarche générale proposée, l'« Evaluation Driven Development » (EDD), "
                    "reprend l'esprit du TDD (écrire le test avant le code) appliqué à l'IA : "
                    "exploration (définir ce qu'on va mesurer avant de construire), mise en "
                    "production (évaluer avant de déployer), puis maintenance (réévaluer en continu "
                    "pour détecter une dérive) — exactement l'esprit du module « Stratégie de "
                    "tests » de ce site, avec cette fois des chiffres et des seuils concrets."
                ),
            },
        ],
    },
    {
        "id": "octo-modernisation-ia",
        "titre": "Comment l'IA générative peut-elle moderniser efficacement vos SI Brownfield ?",
        "youtube_id": "90EeaP-HX-g",
        "description": (
            "Un cas d'usage très concret et loin des chatbots : utiliser l'IA générative pour "
            "comprendre et migrer du code legacy dont la logique métier a été perdue — avec un "
            "message clair sur le rôle qui reste humain."
        ),
        "source": (
            "Le schéma décrit ci-dessous provient d'une présentation d'OCTO Technology (part of "
            "Accenture), série « Le Comptoir OCTO », © 2025, tous droits réservés. Les visuels "
            "originaux ne sont pas reproduits ici : l'explication qui suit est une description en "
            "nos propres mots des concepts qu'ils illustrent, à but pédagogique."
        ),
        "schemas": [
            {
                "titre": "Moderniser du code legacy avec l'IA : le pilotage reste humain",
                "schema": [
                    {"icone": "📜", "label": "Code legacy, logique métier perdue"},
                    {"icone": "🤖", "label": "IA (reverse-engineering assisté)"},
                    {"icone": "👤", "label": "Ingénieur senior (pilote et valide)"},
                    {"icone": "🏗️", "label": "Code modernisé"},
                ],
                "explication": (
                    "Un « système d'information brownfield » désigne un système existant, ancien, "
                    "qu'il faut faire évoluer plutôt que reconstruire à neuf — par opposition à un "
                    "projet « greenfield » parti de zéro. La vidéo montre comment l'IA générative "
                    "aide sur deux difficultés très concrètes de ce contexte : retrouver une "
                    "logique métier enfouie dans du vieux code sans documentation à jour (le modèle "
                    "aide à reformuler en langage clair ce qu'un bout de code obscur fait "
                    "réellement), et accélérer la migration de grosses applications Java grâce à des "
                    "IDE augmentés par l'IA qui proposent des transformations de code assistées. Le "
                    "message central de la présentation, à retenir au-delà du cas Java : « piloter "
                    "l'IA est un vrai travail d'ingénierie », qui suppose de la séniorité technique "
                    "pour juger si une suggestion de l'IA est correcte avant de l'accepter — l'IA "
                    "accélère et explore, mais ne remplace pas le jugement de quelqu'un qui "
                    "comprend déjà le système. C'est le même principe que la relecture humaine déjà "
                    "présente ailleurs sur ce site (le « Human in the loop » de la première vidéo "
                    "de cette page) appliqué cette fois à un contexte de développement logiciel "
                    "plutôt qu'à un agent conversationnel."
                ),
            },
        ],
    },
]


@router.get("")
def lister():
    return VIDEOS
