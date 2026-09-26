_MODELES_DISPONIBLES = [
    "qwen2.5:7b-instruct",
    "llama3.2:3b",
    "deepseek-coder:6.7b",
    "llama3:8b",
    "mistral:7b-instruct",
    "gemma2:2b",
    "phi3:mini",
]

COMPOSANTS = [
    {
        "id": "source_document", "titre": "Source de documents", "icone": "📄", "categorie": "source",
        "description": (
            "Le point de départ d'un pipeline RAG : un document brut (contrat, FAQ, notice, "
            "compte-rendu…) que l'on souhaite exploiter. Ce nœud ne fait aucun calcul, il fournit "
            "simplement le texte de départ aux briques suivantes."
        ),
        "entree_sortie": "Entrée : rien (texte défini dans la config) → Sortie : le texte brut du document",
        "champs_config": [
            {
                "cle": "texte", "label": "Texte du document source", "type": "textarea",
                "exemples": [
                    {"label": "Conditions de garantie", "valeur": (
                        "La garantie décennale couvre les dommages de gros œuvre pendant 10 ans après réception. "
                        "La garantie biennale couvre les équipements dissociables (chauffe-eau, volets) pendant 2 ans. "
                        "Le paiement se fait en 3 fois : 30% à la commande, 40% à mi-chantier, 30% à la réception. "
                        "Les interventions sont planifiées du lundi au vendredi, de 8h à 17h, hors jours fériés."
                    )},
                    {"label": "Rapport de chantier", "valeur": (
                        "Le chantier de la rue des Lilas a pris trois semaines de retard sur le gros œuvre en raison "
                        "d'intempéries prolongées et d'un délai de livraison du béton. L'équipe a été renforcée de deux "
                        "compagnons supplémentaires à partir du 20 juin pour rattraper le planning."
                    )},
                    {"label": "Compte-rendu de réunion", "valeur": (
                        "Lors de la réunion hebdomadaire du 12 juin, l'équipe a validé le nouveau planning de livraison "
                        "pour trois chantiers en cours. Le chantier Dupont est en avance d'une semaine, le chantier Martin "
                        "est dans les temps, et le chantier Lefebvre accuse un retard lié à un problème d'approvisionnement."
                    )},
                ],
            },
        ],
    },
    {
        "id": "chunking", "titre": "Découpage (chunking)", "icone": "✂️", "categorie": "traitement",
        "description": (
            "Un document trop long ne peut pas être comparé efficacement à une question : ce nœud "
            "le découpe en petits morceaux (chunks) de quelques phrases chacun. Étape purement "
            "mécanique (pas de modèle IA), mais essentielle : un découpage mal fait dégrade toute "
            "la suite du pipeline."
        ),
        "entree_sortie": "Entrée : un document texte → Sortie : une liste de chunks",
        "champs_config": [
            {"cle": "taille_chunk", "label": "Taille d'un chunk (caractères)", "type": "nombre", "defaut": 120},
        ],
    },
    {
        "id": "base_vectorielle", "titre": "Base vectorielle", "icone": "🗄️", "categorie": "stockage",
        "description": (
            "Transforme chaque chunk en vecteur (embedding), fait de même pour la question posée, "
            "puis retrouve les chunks dont le vecteur est le plus proche (similarité cosinus). "
            "C'est le cœur du RAG : l'endroit où le pipeline va chercher l'information pertinente "
            "avant de répondre. ⚠️ Important : les chunks proviennent des nœuds connectés en amont "
            "(« Source de documents » → « Découpage »). Sans rien connecté avant elle, cette brique "
            "ne reste pas vide : elle cherche par défaut dans un petit corpus de démonstration "
            "intégré (quelques phrases sur le RAG, MCP, ReAct...), pas dans un document que vous "
            "auriez fourni. Le passage réellement trouvé est visible dans le « Déroulé complet » "
            "après exécution, ou en cliquant à nouveau sur le nœud."
        ),
        "entree_sortie": (
            "Entrée : des chunks (fournis par « Source de documents » → « Découpage » en amont, "
            "sinon un mini-corpus de démonstration intégré par défaut) + une question → "
            "Sortie : les 2 passages les plus pertinents"
        ),
        "champs_config": [
            {
                "cle": "prompt", "label": "Question posée à la base documentaire", "type": "textarea",
                "exemples": [
                    {"label": "Garantie décennale", "valeur": "Quelles sont les conditions de garantie ?"},
                    {"label": "Modalités de paiement", "valeur": "Comment se déroule le paiement ?"},
                    {"label": "Horaires d'intervention", "valeur": "Quels sont les horaires des interventions ?"},
                ],
            },
        ],
    },
    {
        "id": "llm_agent", "titre": "LLM", "icone": "🧠", "categorie": "modele",
        "description": (
            "Le modèle de langage qui génère la réponse finale. S'il reçoit des passages retrouvés "
            "par une base vectorielle en amont, il les utilise comme contexte pour répondre plus "
            "précisément (RAG) ; sinon, il répond directement à partir de ses connaissances générales."
        ),
        "entree_sortie": "Entrée : une question (+ contexte optionnel) → Sortie : la réponse finale",
        "champs_config": [
            {
                "cle": "prompt", "label": "Question / prompt", "type": "textarea",
                "exemples": [
                    {"label": "Garantie décennale", "valeur": "Quelles sont les conditions de garantie ?"},
                    {"label": "Modalités de paiement", "valeur": "Comment se déroule le paiement ?"},
                    {"label": "Horaires d'intervention", "valeur": "Quels sont les horaires des interventions ?"},
                ],
            },
            {"cle": "modele", "label": "Modèle", "type": "select", "options": _MODELES_DISPONIBLES, "defaut": "qwen2.5:7b-instruct"},
        ],
    },
    {
        "id": "outil_mcp", "titre": "Outil / MCP", "icone": "🛠️", "categorie": "outil",
        "description": (
            "Un outil externe que l'on appelle pour des tâches où un LLM seul n'est pas fiable "
            "(calcul précis, recherche exacte). Exposé via le protocole MCP (Model Context "
            "Protocol) — le même principe que celui utilisé par Claude Code pour appeler des outils."
        ),
        "entree_sortie": "Entrée : une expression ou une requête → Sortie : le résultat brut de l'outil",
        "champs_config": [
            {"cle": "outil", "label": "Outil appelé", "type": "select", "options": ["rechercher", "calculatrice"], "defaut": "rechercher"},
            {
                # "requete" (pas "prompt") : c'est le nom de champ que engine.py._handler_outil_mcp
                # lit réellement pour la branche recherche (config.get("requete")) — avec "prompt"
                # ici, la saisie de l'utilisateur n'atteignait jamais le handler, qui retombait
                # silencieusement sur la requête de secours "MCP" (même bug déjà corrigé côté
                # Parcours guidé, jamais propagé à cette définition du canvas libre).
                "cle": "requete", "label": "Requête (si outil = rechercher)", "type": "texte",
                "exemples": [
                    {"label": "Définition MCP", "valeur": "Qu'est-ce que le protocole MCP ?"},
                    {"label": "Principe du RAG", "valeur": "Comment fonctionne le RAG ?"},
                ],
            },
            {
                "cle": "expression", "label": "Expression (si outil = calculatrice)", "type": "texte",
                "exemples": [
                    {"label": "Calcul simple", "valeur": "3.5 * 12 + 45"},
                    {"label": "Avec parenthèses", "valeur": "(120 - 15) / 3"},
                ],
            },
        ],
    },
    {
        "id": "agent_unique", "titre": "Agent (boucle ReAct)", "icone": "🔁", "categorie": "modele",
        "description": (
            "Un LLM qui raisonne en boucle : à chaque étape, il décide s'il doit appeler un outil "
            "(calculatrice, recherche) ou s'il peut donner sa réponse finale. C'est le principe "
            "ReAct (Reason + Act) — contrairement aux briques précédentes qui suivent un chemin "
            "fixe, celle-ci choisit elle-même son parcours."
        ),
        "entree_sortie": "Entrée : une tâche → Sortie : la réponse finale, après 1 à 4 étapes de raisonnement",
        "champs_config": [
            {
                "cle": "prompt", "label": "Tâche confiée à l'agent", "type": "textarea",
                "exemples": [
                    {"label": "Facture artisan", "valeur": "Un artisan facture 45€/heure. Il a travaillé 3h30 lundi et 2h15 mardi. Calcule le total."},
                    {"label": "Remise sur devis", "valeur": "Un devis de 1200€ bénéficie d'une remise de 15%. Quel est le montant final ?"},
                    {"label": "Définition MCP", "valeur": "Qu'est-ce que le protocole MCP ?"},
                ],
            },
        ],
    },
    {
        "id": "multi_agent", "titre": "Pipeline multi-agent", "icone": "🤝", "categorie": "modele",
        "description": (
            "Deux agents aux rôles différents collaborent en séquence : un agent « chercheur » "
            "rassemble les faits, puis un agent « rédacteur » les transforme en réponse claire. "
            "Chacun a son propre prompt système, ce qui les rend plus fiables sur leur tâche "
            "spécifique que s'ils devaient tout faire seuls."
        ),
        "entree_sortie": "Entrée : une tâche → Sortie : la réponse rédigée par le second agent",
        "champs_config": [
            {
                "cle": "prompt", "label": "Tâche confiée au pipeline", "type": "textarea",
                "exemples": [
                    {"label": "Expliquer un agent IA", "valeur": "Explique ce qu'est un agent IA à un client non technique."},
                    {"label": "Email client (retard)", "valeur": "Rédige un email pour expliquer un retard de chantier de 2 semaines."},
                    {"label": "Résumé pédagogique du RAG", "valeur": "Résume ce qu'est le RAG pour un débutant."},
                ],
            },
        ],
    },
    {
        "id": "llm_seul", "titre": "LLM seul (sans contexte)", "icone": "💬", "categorie": "modele",
        "description": (
            "La brique la plus simple : un LLM répond directement à un prompt, sans document, sans "
            "outil, sans mémoire. Sert de point de comparaison pour mesurer l'apport réel des "
            "autres briques (RAG, outils, agents)."
        ),
        "entree_sortie": "Entrée : un prompt → Sortie : la réponse générée directement",
        "champs_config": [
            {
                "cle": "prompt", "label": "Prompt", "type": "textarea",
                "exemples": [
                    {"label": "Question générale", "valeur": "Explique en 2 phrases ce qu'est une garantie décennale, en général."},
                    {"label": "Reformulation polie", "valeur": "Reformule poliment : 'vous devez payer sinon on arrête tout'."},
                    {"label": "Brainstorm", "valeur": "Propose 3 idées pour fidéliser des clients artisans."},
                ],
            },
            {"cle": "modele", "label": "Modèle", "type": "select", "options": _MODELES_DISPONIBLES, "defaut": "qwen2.5:7b-instruct"},
        ],
    },
    {
        "id": "rag", "titre": "RAG simplifié", "icone": "📚", "categorie": "modele",
        "description": (
            "Une version « tout-en-un » du RAG qui combine en un seul nœud la recherche du passage "
            "pertinent et la génération de la réponse, au lieu de les séparer en Base vectorielle + "
            "LLM. Pratique pour assembler un pipeline rapidement."
        ),
        "entree_sortie": "Entrée : une question → Sortie : la réponse augmentée par un passage retrouvé",
        "champs_config": [
            {
                "cle": "prompt", "label": "Question", "type": "textarea",
                "exemples": [
                    {"label": "Garantie décennale", "valeur": "Quelles sont les conditions de garantie ?"},
                    {"label": "Modalités de paiement", "valeur": "Comment se déroule le paiement ?"},
                ],
            },
            {
                "cle": "document_utilisateur", "label": "Ajouter un passage au corpus (optionnel)", "type": "textarea",
                "exemples": [
                    {"label": "Majoration week-end", "valeur": "Le samedi, les interventions sont facturées avec une majoration de 20%."},
                ],
            },
        ],
    },
    {
        "id": "comparateur", "titre": "Comparateur de modèles", "icone": "🆚", "categorie": "modele",
        "description": (
            "Envoie le même prompt à deux modèles différents (par exemple un petit modèle rapide "
            "et un plus gros modèle plus capable) et renvoie les deux réponses côte à côte. Utile "
            "pour évaluer objectivement quel modèle convient le mieux à une tâche donnée."
        ),
        "entree_sortie": "Entrée : un prompt → Sortie : 2 réponses, une par modèle",
        "champs_config": [
            {
                "cle": "prompt", "label": "Prompt envoyé aux deux modèles", "type": "textarea",
                "exemples": [
                    {"label": "Explication courte", "valeur": "Explique ce qu'est le RAG en une phrase."},
                    {"label": "Calcul", "valeur": "Combien font 17 fois 23 ?"},
                    {"label": "Message d'excuse", "valeur": "Rédige un message d'excuse pour un retard de livraison."},
                ],
            },
            {"cle": "modele_a", "label": "Modèle A", "type": "select", "options": _MODELES_DISPONIBLES, "defaut": "llama3.2:3b"},
            {"cle": "modele_b", "label": "Modèle B", "type": "select", "options": _MODELES_DISPONIBLES, "defaut": "qwen2.5:7b-instruct"},
        ],
    },
    {
        "id": "synthese_map_reduce", "titre": "Résumé hiérarchique", "icone": "🧩", "categorie": "traitement",
        "description": (
            "Résume chaque chunk indépendamment (l'étape « map »), puis combine tous ces résumés "
            "partiels en une synthèse finale cohérente (l'étape « reduce »). Permet de résumer des "
            "documents bien plus longs qu'un seul appel LLM ne le permettrait."
        ),
        "entree_sortie": "Entrée : une liste de chunks → Sortie : une synthèse finale",
        "champs_config": [],
    },
    {
        "id": "moderation", "titre": "Filtre de modération", "icone": "🚧", "categorie": "outil",
        "description": (
            "Vérifie la requête par rapport à une liste de mots-clés interdits avant de la laisser "
            "continuer vers le LLM. Reliez-le à la suite avec un lien « Si autorisé » : si un mot "
            "bloqué est détecté, ce lien ne s'active pas et les nœuds qui n'en dépendent que par lui "
            "ne s'exécutent pas — le pipeline s'arrête réellement ici, pas juste en apparence."
        ),
        "entree_sortie": "Entrée : une requête → Sortie : inchangée (lien « Si autorisé » actif) ou blocage (lien « Si bloqué » actif)",
        "champs_config": [
            {
                "cle": "prompt", "label": "Requête à vérifier", "type": "textarea",
                "exemples": [
                    {"label": "Question normale", "valeur": "Quelles sont les conditions de garantie ?"},
                    {"label": "Question bloquée", "valeur": "Comment pirater le système de facturation d'un concurrent ?"},
                    {"label": "Question limite", "valeur": "Comment contourner la loi sur les délais de paiement ?"},
                ],
            },
        ],
    },
    {
        "id": "verification", "titre": "Vérificateur / auto-critique", "icone": "✅", "categorie": "modele",
        "description": (
            "Le LLM génère d'abord un brouillon de réponse, puis un second appel relit ce brouillon "
            "pour vérifier les calculs/faits et le corriger si besoin. Coûte deux appels au lieu "
            "d'un, mais améliore la fiabilité sur les tâches à risque d'erreur."
        ),
        "entree_sortie": "Entrée : une question → Sortie : la réponse vérifiée/corrigée",
        "champs_config": [
            {
                "cle": "prompt", "label": "Question", "type": "textarea",
                "exemples": [
                    {"label": "Calcul", "valeur": "Combien font 17 fois 23 ?"},
                    {"label": "Fait précis", "valeur": "En quelle année la garantie décennale est-elle devenue obligatoire en France ?"},
                    {"label": "Raisonnement en plusieurs étapes", "valeur": "Un artisan facture 3 interventions de 2h à 45€/h. Quel est le total ?"},
                ],
            },
        ],
    },
]

_TEXTE_RAPPORT_CHANTIER = (
    "Le chantier de la rue des Lilas a pris trois semaines de retard sur le gros œuvre en raison "
    "d'intempéries prolongées et d'un délai de livraison du béton. L'équipe a été renforcée de deux "
    "compagnons supplémentaires à partir du 20 juin pour rattraper le planning. Le client a été informé "
    "par téléphone et par courrier du nouveau délai, et a accepté les conditions proposées, y compris "
    "une réduction de 5% sur la facture finale en compensation. La météo s'est stabilisée depuis, et "
    "l'équipe prévoit de terminer le second œuvre dans les délais initiaux malgré le retard initial."
)

_TEXTE_ARTICLE_PRESSE = (
    "Le secteur du bâtiment traverse une période de transition marquée par la hausse du coût des "
    "matériaux et une demande croissante de rénovation énergétique. Selon une étude professionnelle, "
    "les artisans qui investissent dans des outils numériques de gestion de chantier réduisent leurs "
    "délais moyens de 15%. La filière appelle toutefois à un soutien renforcé de l'État pour "
    "accompagner la transition, notamment via des aides à la formation des artisans indépendants sur "
    "ces nouveaux outils, jugés encore complexes à adopter pour les plus petites structures."
)

_TEXTE_COMPTE_RENDU = (
    "Lors de la réunion hebdomadaire du 12 juin, l'équipe a validé le nouveau planning de livraison "
    "pour trois chantiers en cours. Le chantier Dupont est en avance d'une semaine, le chantier Martin "
    "est dans les temps, et le chantier Lefebvre accuse un retard lié à un problème d'approvisionnement "
    "en menuiserie. Il a été décidé de prioriser les livraisons du fournisseur habituel pour ce dernier "
    "chantier. La prochaine réunion est fixée au 19 juin pour faire un nouveau point d'avancement."
)

_TEXTE_LIVRET_ACCUEIL = (
    "Les salariés bénéficient de 25 jours de congés payés par an, à poser au moins 2 semaines à "
    "l'avance auprès du responsable d'équipe. Le télétravail est possible 2 jours par semaine sur "
    "accord préalable du manager, hors périodes de chantier nécessitant une présence terrain. En cas "
    "d'arrêt maladie, l'arrêt doit être transmis aux ressources humaines dans les 48 heures. La période "
    "d'essai est de 2 mois renouvelable une fois pour les postes non-cadres."
)

_TEXTE_FACTURE_CLIENT = (
    "Facture n°245 émise le 3 mars pour le client Dupont : pose de carrelage 45m² à 38€/m² HT, soit "
    "1710€ HT. Fourniture de matériaux complémentaires : 320€ HT. Total HT : 2030€, TVA à 10% : 203€, "
    "total TTC : 2233€. Acompte déjà versé à la commande : 600€. Solde restant dû : 1633€, payable sous "
    "30 jours. Facture n°246 émise le 5 mars pour le client Martin, montant total TTC de 1150€, "
    "intégralement réglée par virement le 8 mars."
)

_TEXTE_RAPPORT_MARCHE = (
    "Un concurrent régional vient de lancer une offre de rénovation énergétique clé en main avec "
    "financement intégré, ciblant particulièrement les propriétaires de logements anciens. Le marché "
    "de la rénovation énergétique devrait croître de 12% cette année selon une étude de la filière, "
    "porté par le renforcement des aides publiques. Plusieurs artisans indépendants du secteur signalent "
    "toutefois des difficultés à recruter de la main d'œuvre qualifiée, ce qui limite leur capacité à "
    "répondre à la demande malgré la croissance du marché."
)

TEMPLATES = [
    {
        "id": "assistant_rag",
        "categorie": "rag",
        "titre": "Assistant RAG documentaire",
        "description": "Répond aux questions à partir des documents de l'entreprise : Document → Découpage → Base vectorielle → LLM.",
        "avantages": [
            "Réponses ancrées dans les vrais documents de l'entreprise",
            "Pas besoin de ré-entraîner un modèle pour mettre à jour les connaissances",
            "Réduit les hallucinations du LLM",
        ],
        "inconvenients": [
            "Dépend fortement de la qualité du découpage (chunking)",
            "Ne répond qu'à partir des documents fournis",
            "Plus lent qu'un LLM seul (plusieurs étapes)",
        ],
        "nodes": [
            {"id": "1", "type": "source_document", "config": {}, "position": {"x": 40, "y": 120}},
            {"id": "2", "type": "chunking", "config": {}, "position": {"x": 280, "y": 120}},
            {"id": "3", "type": "base_vectorielle", "config": {"prompt": "Quelles sont les conditions de garantie ?"}, "position": {"x": 520, "y": 120}},
            {"id": "4", "type": "llm_agent", "config": {}, "position": {"x": 760, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "3", "target": "4"}],
        "exemples": [
            {"label": "Garantie décennale", "valeurs": {"3": {"prompt": "Quelles sont les conditions de garantie ?"}}},
            {"label": "Modalités de paiement", "valeurs": {"3": {"prompt": "Comment se déroule le paiement ?"}}},
            {"label": "Horaires d'intervention", "valeurs": {"3": {"prompt": "Quels sont les horaires des interventions ?"}}},
        ],
    },
    {
        "id": "agent_calculatrice",
        "categorie": "agents_outils",
        "titre": "Agent avec un outil (calculatrice)",
        "description": "Un agent qui décide seul de faire appel à une calculatrice pour répondre précisément.",
        "avantages": [
            "Fiable sur les calculs précis (pas d'erreur d'arithmétique comme un LLM seul)",
            "Simple à mettre en place (un seul nœud)",
            "S'arrête dès qu'il a obtenu la réponse",
        ],
        "inconvenients": [
            "Ne gère qu'un seul type de tâche à la fois",
            "Pas de mémoire entre deux exécutions",
            "Le LLM doit deviner qu'il faut utiliser l'outil",
        ],
        "nodes": [{"id": "1", "type": "agent_unique", "config": {"prompt": "Un artisan facture 45€/heure. Il a travaillé 3h30 lundi et 2h15 mardi. Calcule le total."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Facture artisan", "valeurs": {"1": {"prompt": "Un artisan facture 45€/heure. Il a travaillé 3h30 lundi et 2h15 mardi. Calcule le total."}}},
            {"label": "Remise sur devis", "valeurs": {"1": {"prompt": "Un devis de 1200€ bénéficie d'une remise de 15%. Quel est le montant final ?"}}},
            {"label": "Conversion + coût", "valeurs": {"1": {"prompt": "Convertis 3h45 en minutes, puis calcule le coût à 40€/heure."}}},
        ],
    },
    {
        "id": "agent_recherche",
        "categorie": "agents_outils",
        "titre": "Agent avec recherche documentaire",
        "description": "Un agent qui décide seul de chercher dans un mini-corpus avant de répondre.",
        "avantages": [
            "Peut chercher l'information avant de répondre",
            "Décide seul quand chercher, sans qu'on le lui impose",
            "Traçable : on voit exactement ce qu'il a cherché",
        ],
        "inconvenients": [
            "Dépend de la qualité et de la taille du mini-corpus",
            "Peut chercher inutilement sur des questions simples",
            "Plus lent qu'une réponse directe",
        ],
        "nodes": [{"id": "1", "type": "agent_unique", "config": {"prompt": "Qu'est-ce que le protocole MCP ?"}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Définition MCP", "valeurs": {"1": {"prompt": "Qu'est-ce que le protocole MCP ?"}}},
            {"label": "Principe du RAG", "valeurs": {"1": {"prompt": "Comment fonctionne le RAG ?"}}},
            {"label": "Maintenance prédictive", "valeurs": {"1": {"prompt": "Comment détecter une anomalie mécanique avant la panne ?"}}},
        ],
    },
    {
        "id": "pipeline_multi_agent",
        "categorie": "agents_outils",
        "titre": "Pipeline multi-agent",
        "description": "Deux agents spécialisés qui collaborent : un chercheur rassemble l'information, un rédacteur la met en forme.",
        "avantages": [
            "Sépare la recherche de la rédaction : chaque agent est spécialisé",
            "Meilleure qualité rédactionnelle finale",
            "Facile d'ajouter un 3e agent (relecteur, traducteur…)",
        ],
        "inconvenients": [
            "Deux fois plus d'appels LLM (plus lent, plus cher)",
            "Une erreur du chercheur se répercute sur le rédacteur",
            "Coordination à gérer entre les agents",
        ],
        "nodes": [{"id": "1", "type": "multi_agent", "config": {"prompt": "Explique ce qu'est un agent IA à un client non technique."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Expliquer un agent IA", "valeurs": {"1": {"prompt": "Explique ce qu'est un agent IA à un client non technique."}}},
            {"label": "Email client (retard)", "valeurs": {"1": {"prompt": "Rédige un email pour expliquer un retard de chantier de 2 semaines."}}},
            {"label": "Résumé pédagogique du RAG", "valeurs": {"1": {"prompt": "Résume ce qu'est le RAG pour un débutant."}}},
        ],
    },
    {
        "id": "llm_seul_reference",
        "categorie": "fondamentaux",
        "titre": "LLM seul (référence)",
        "description": "L'architecture la plus simple, utile comme point de comparaison avec les autres.",
        "avantages": [
            "Le plus simple et le plus rapide",
            "Le moins cher (un seul appel)",
            "Suffit pour des questions génériques",
        ],
        "inconvenients": [
            "Aucune connaissance spécifique à l'entreprise",
            "Peut halluciner sur des faits précis",
            "Pas d'outils, pas de mémoire",
        ],
        "nodes": [{"id": "1", "type": "llm_seul", "config": {"prompt": "Explique en 2 phrases ce qu'est une garantie décennale, en général."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Question générale", "valeurs": {"1": {"prompt": "Explique en 2 phrases ce qu'est une garantie décennale, en général."}}},
            {"label": "Reformulation polie", "valeurs": {"1": {"prompt": "Reformule poliment : 'vous devez payer sinon on arrête tout'."}}},
            {"label": "Brainstorm", "valeurs": {"1": {"prompt": "Propose 3 idées pour fidéliser des clients artisans."}}},
        ],
    },
    {
        "id": "rag_agent_combine",
        "categorie": "rag",
        "titre": "RAG + Agent combiné",
        "description": "Combine retrieval documentaire et agent à outils : Document → Découpage → Base vectorielle → Agent.",
        "avantages": [
            "Combine la fiabilité du RAG (infos vérifiées) et la flexibilité de l'agent (outils)",
            "Peut à la fois consulter les documents ET faire un calcul",
            "Le plus proche d'un assistant métier complet",
        ],
        "inconvenients": [
            "Architecture la plus complexe du catalogue",
            "Plus de points de défaillance (chaque étage peut échouer)",
            "Plus lent qu'un RAG ou un agent utilisés seuls",
        ],
        "nodes": [
            {"id": "1", "type": "source_document", "config": {}, "position": {"x": 40, "y": 120}},
            {"id": "2", "type": "chunking", "config": {}, "position": {"x": 280, "y": 120}},
            {"id": "3", "type": "base_vectorielle", "config": {"prompt": "Quelles sont les conditions de garantie, et calcule 30% d'un devis de 4000€."}, "position": {"x": 520, "y": 120}},
            {"id": "4", "type": "agent_unique", "config": {}, "position": {"x": 760, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "3", "target": "4"}],
        "exemples": [
            {"label": "Garantie + calcul", "valeurs": {"3": {"prompt": "Quelles sont les conditions de garantie, et calcule 30% d'un devis de 4000€."}}},
            {"label": "Modalités de paiement", "valeurs": {"3": {"prompt": "Quelles sont les modalités de paiement de l'entreprise ?"}}},
            {"label": "Horaires + calcul", "valeurs": {"3": {"prompt": "À quelles heures les interventions sont-elles possibles, et combien font 12 fois 3.5 ?"}}},
        ],
    },
    {
        "id": "comparateur_modeles",
        "categorie": "fondamentaux",
        "titre": "Comparateur de deux modèles",
        "description": "Envoie le même prompt à deux modèles (Llama 3.2 et Qwen 2.5) et affiche les deux réponses côte à côte.",
        "avantages": [
            "Permet de choisir objectivement le meilleur modèle pour un usage donné",
            "Montre concrètement les différences de style/qualité entre modèles",
            "Aucun risque : juste de l'évaluation, pas de mise en production",
        ],
        "inconvenients": [
            "Double le coût de calcul (2 appels par requête)",
            "Pas utile en production (seulement pour évaluer)",
            "Ne compare que sur un seul exemple à la fois",
        ],
        "nodes": [{"id": "1", "type": "comparateur", "config": {"prompt": "Explique ce qu'est le RAG en une phrase."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Explication courte", "valeurs": {"1": {"prompt": "Explique ce qu'est le RAG en une phrase."}}},
            {"label": "Calcul", "valeurs": {"1": {"prompt": "Combien font 17 fois 23 ?"}}},
            {"label": "Message d'excuse", "valeurs": {"1": {"prompt": "Rédige un message d'excuse pour un retard de livraison."}}},
        ],
    },
    {
        "id": "resume_hierarchique",
        "categorie": "rag",
        "titre": "Résumé hiérarchique (map-reduce)",
        "description": "Découpe un long document, résume chaque morceau, puis combine les résumés en une synthèse finale.",
        "avantages": [
            "Peut résumer des documents bien plus longs qu'un seul appel LLM ne le permettrait",
            "Chaque morceau est résumé indépendamment (parallélisable)",
            "Robuste face aux très longs textes",
        ],
        "inconvenients": [
            "Perd des détails à chaque étape de résumé",
            "Plusieurs appels LLM (plus lent)",
            "La synthèse finale peut lisser des nuances importantes",
        ],
        "nodes": [
            {"id": "1", "type": "source_document", "config": {"texte": _TEXTE_RAPPORT_CHANTIER}, "position": {"x": 80, "y": 120}},
            {"id": "2", "type": "chunking", "config": {}, "position": {"x": 340, "y": 120}},
            {"id": "3", "type": "synthese_map_reduce", "config": {}, "position": {"x": 600, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
        "exemples": [
            {"label": "Rapport de chantier", "valeurs": {"1": {"texte": _TEXTE_RAPPORT_CHANTIER}}},
            {"label": "Article de presse", "valeurs": {"1": {"texte": _TEXTE_ARTICLE_PRESSE}}},
            {"label": "Compte-rendu de réunion", "valeurs": {"1": {"texte": _TEXTE_COMPTE_RENDU}}},
        ],
    },
    {
        "id": "filtre_moderation",
        "categorie": "garde_fous",
        "titre": "Filtre de modération avant réponse",
        "description": "Vérifie la requête avec une liste de mots-clés avant de la transmettre (ou non) au LLM.",
        "avantages": [
            "Bloque les questions inappropriées avant même d'appeler le LLM (rapide, pas cher)",
            "Simple à auditer (liste de mots-clés visible et modifiable)",
            "Première ligne de défense facile à ajouter à n'importe quelle architecture",
        ],
        "inconvenients": [
            "Filtre par mots-clés : facile à contourner par reformulation",
            "Peut bloquer des questions légitimes (faux positifs)",
            "Ne remplace pas une vraie modération de contenu",
        ],
        "nodes": [
            {"id": "1", "type": "moderation", "config": {"prompt": "Quelles sont les conditions de garantie ?"}, "position": {"x": 120, "y": 120}},
            {"id": "2", "type": "llm_agent", "config": {}, "position": {"x": 420, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2", "condition": "autorise"}],
        "exemples": [
            {"label": "Question normale", "valeurs": {"1": {"prompt": "Quelles sont les conditions de garantie ?"}}},
            {"label": "Question bloquée", "valeurs": {"1": {"prompt": "Comment pirater le système de facturation d'un concurrent ?"}}},
            {"label": "Question limite", "valeurs": {"1": {"prompt": "Comment contourner la loi sur les délais de paiement ?"}}},
        ],
    },
    {
        "id": "verification_auto_critique",
        "categorie": "garde_fous",
        "titre": "Vérificateur / auto-critique",
        "description": "Le LLM génère un brouillon, puis une seconde passe vérifie et corrige la réponse si besoin.",
        "avantages": [
            "Meilleure fiabilité : le modèle relit et corrige sa propre réponse",
            "Utile pour les tâches à risque d'erreur (calculs, faits précis)",
            "Le brouillon ET la correction restent visibles (traçable)",
        ],
        "inconvenients": [
            "Deux fois plus lent et plus cher (2 appels LLM)",
            "Ne garantit pas l'absence totale d'erreur",
            "Peut parfois « corriger » une réponse qui était déjà juste",
        ],
        "nodes": [{"id": "1", "type": "verification", "config": {"prompt": "Combien font 17 fois 23 ?"}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Calcul", "valeurs": {"1": {"prompt": "Combien font 17 fois 23 ?"}}},
            {"label": "Fait précis", "valeurs": {"1": {"prompt": "En quelle année la garantie décennale est-elle devenue obligatoire en France ?"}}},
            {"label": "Raisonnement en plusieurs étapes", "valeurs": {"1": {"prompt": "Un artisan facture 3 interventions de 2h à 45€/h. Quel est le total ?"}}},
        ],
    },
    {
        "id": "assistant_it_helpdesk",
        "categorie": "metiers",
        "titre": "Support IT interne (helpdesk)",
        "description": "Un agent qui répond aux questions IT courantes des salariés et décide seul de chercher dans la base de connaissances.",
        "avantages": [
            "Déployé aujourd'hui dans la plupart des grandes DSI pour absorber les tickets de premier niveau",
            "Disponible 24h/24, réduit la charge des équipes IT sur les questions répétitives",
            "Traçable : on voit exactement ce que l'agent a cherché avant de répondre",
        ],
        "inconvenients": [
            "Ne peut pas agir lui-même (réinitialiser un mot de passe, ouvrir un ticket) sans intégration supplémentaire",
            "Dépend entièrement de la qualité et de la fraîcheur de la base de connaissances",
            "Risque de donner un faux sentiment de résolution sur un problème de sécurité qui mériterait une escalade humaine",
        ],
        "nodes": [{"id": "1", "type": "agent_unique", "config": {"prompt": "Comment réinitialiser mon mot de passe VPN ?"}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Mot de passe VPN", "valeurs": {"1": {"prompt": "Comment réinitialiser mon mot de passe VPN ?"}}},
            {"label": "Imprimante réseau", "valeurs": {"1": {"prompt": "Mon imprimante réseau n'apparaît plus sur mon poste, que faire ?"}}},
            {"label": "Demande de matériel", "valeurs": {"1": {"prompt": "Quelle est la procédure pour demander un nouvel ordinateur portable ?"}}},
        ],
    },
    {
        "id": "assistant_rh_onboarding",
        "categorie": "metiers",
        "titre": "Assistant RH onboarding",
        "description": "Répond aux questions des nouveaux salariés à partir du livret d'accueil : Document → Découpage → Base vectorielle → LLM.",
        "avantages": [
            "Pattern très répandu en RH pour absorber les questions répétitives des nouveaux arrivants",
            "Réponses cohérentes et alignées sur le document officiel, jour et nuit",
            "Libère du temps aux équipes RH pour les cas individuels complexes",
        ],
        "inconvenients": [
            "Dépend entièrement de la mise à jour du livret d'accueil source",
            "Ne gère pas les situations personnelles particulières (négociation, cas exceptionnel)",
            "Une erreur ou une ambiguïté dans le document source se répercute directement sur la réponse",
        ],
        "nodes": [
            {"id": "1", "type": "source_document", "config": {"texte": _TEXTE_LIVRET_ACCUEIL}, "position": {"x": 40, "y": 120}},
            {"id": "2", "type": "chunking", "config": {}, "position": {"x": 280, "y": 120}},
            {"id": "3", "type": "base_vectorielle", "config": {"prompt": "Combien de jours de congés payés ai-je par an ?"}, "position": {"x": 520, "y": 120}},
            {"id": "4", "type": "llm_agent", "config": {}, "position": {"x": 760, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "3", "target": "4"}],
        "exemples": [
            {"label": "Congés payés", "valeurs": {"3": {"prompt": "Combien de jours de congés payés ai-je par an ?"}}},
            {"label": "Télétravail", "valeurs": {"3": {"prompt": "Quelle est la procédure de télétravail ?"}}},
            {"label": "Arrêt maladie", "valeurs": {"3": {"prompt": "Comment déclarer un arrêt maladie ?"}}},
        ],
    },
    {
        "id": "assistant_conformite_rgpd",
        "categorie": "garde_fous",
        "titre": "Assistant conformité avec garde-fou",
        "description": "Filtre la question avant de la transmettre à un assistant documentaire : Modération → Base vectorielle → LLM.",
        "avantages": [
            "Pattern standard dans les secteurs réglementés (juridique, santé, finance) avant tout assistant documentaire",
            "Le blocage est tracé dans le déroulé — auditable a posteriori",
            "Ajoute une ligne de défense sans changer le reste du pipeline documentaire",
        ],
        "inconvenients": [
            "Filtre par mots-clés : contournable par reformulation, comme tout filtre de ce type",
            "Ne remplace en aucun cas une vraie revue juridique humaine sur un sujet sensible",
            "Le lien conditionnel ne couvre que ce pipeline précis : chaque nouvelle branche doit être étiquetée à la main",
        ],
        "nodes": [
            {"id": "1", "type": "moderation", "config": {"prompt": "Quelles sont nos obligations de conservation des données clients ?"}, "position": {"x": 80, "y": 120}},
            {"id": "2", "type": "base_vectorielle", "config": {}, "position": {"x": 340, "y": 120}},
            {"id": "3", "type": "llm_agent", "config": {}, "position": {"x": 600, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2", "condition": "autorise"}, {"source": "2", "target": "3"}],
        "exemples": [
            {"label": "Question normale", "valeurs": {"1": {"prompt": "Quelles sont nos obligations de conservation des données clients ?"}}},
            {"label": "Question bloquée", "valeurs": {"1": {"prompt": "Comment contourner la loi sur les délais de paiement ?"}}},
            {"label": "Question limite", "valeurs": {"1": {"prompt": "Comment arnaquer un client sur le montant d'un devis ?"}}},
        ],
    },
    {
        "id": "assistant_comptable_factures",
        "categorie": "metiers",
        "titre": "Assistant comptable (factures + calcul)",
        "description": "Combine consultation de factures et calcul fiable : Document → Découpage → Base vectorielle → Agent.",
        "avantages": [
            "Réunit dans un même assistant la consultation documentaire ET le calcul, un besoin comptable très courant",
            "Le calcul passe par une vraie calculatrice, pas par l'arithmétique approximative d'un LLM seul",
            "Rapide sur les questions répétitives (montants, soldes, TVA)",
        ],
        "inconvenients": [
            "Suppose des documents source bien structurés et à jour",
            "Risque d'erreur si le LLM interprète mal la ligne de facture à extraire avant de calculer",
            "Ne remplace pas un vrai logiciel de comptabilité pour la tenue légale des comptes",
        ],
        "nodes": [
            {"id": "1", "type": "source_document", "config": {"texte": _TEXTE_FACTURE_CLIENT}, "position": {"x": 40, "y": 120}},
            {"id": "2", "type": "chunking", "config": {}, "position": {"x": 280, "y": 120}},
            {"id": "3", "type": "base_vectorielle", "config": {"prompt": "Quel est le solde restant dû sur la facture 245 ?"}, "position": {"x": 520, "y": 120}},
            {"id": "4", "type": "agent_unique", "config": {}, "position": {"x": 760, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "3", "target": "4"}],
        "exemples": [
            {"label": "Solde dû", "valeurs": {"3": {"prompt": "Quel est le solde restant dû sur la facture 245 ?"}}},
            {"label": "Statut de paiement", "valeurs": {"3": {"prompt": "La facture 246 du client Martin a-t-elle été payée ?"}}},
            {"label": "Calcul de TVA", "valeurs": {"3": {"prompt": "Calcule 20% de TVA sur un montant HT de 2030€."}}},
        ],
    },
    {
        "id": "veille_concurrentielle",
        "categorie": "metiers",
        "titre": "Veille concurrentielle et marché",
        "description": "Résume de longs rapports ou articles de marché en une synthèse exploitable : Document → Découpage → Résumé hiérarchique.",
        "avantages": [
            "Usage très répandu en veille stratégique pour dépouiller rapidement rapports et articles longs",
            "Traite des documents bien plus longs qu'un simple prompt ne le permettrait",
            "Chaque section est résumée indépendamment, donc parallélisable à grande échelle",
        ],
        "inconvenients": [
            "Un signal faible mais stratégiquement important peut être lissé/perdu lors de la synthèse finale",
            "Plusieurs appels LLM : plus lent et plus coûteux qu'un résumé direct",
            "Ne remplace pas l'analyse humaine pour une décision stratégique importante",
        ],
        "nodes": [
            {"id": "1", "type": "source_document", "config": {"texte": _TEXTE_RAPPORT_MARCHE}, "position": {"x": 80, "y": 120}},
            {"id": "2", "type": "chunking", "config": {}, "position": {"x": 340, "y": 120}},
            {"id": "3", "type": "synthese_map_reduce", "config": {}, "position": {"x": 600, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
        "exemples": [
            {"label": "Rapport de marché", "valeurs": {"1": {"texte": _TEXTE_RAPPORT_MARCHE}}},
            {"label": "Article de presse", "valeurs": {"1": {"texte": _TEXTE_ARTICLE_PRESSE}}},
            {"label": "Compte-rendu de réunion", "valeurs": {"1": {"texte": _TEXTE_COMPTE_RENDU}}},
        ],
    },
    {
        "id": "assistant_commercial_crm",
        "categorie": "metiers",
        "titre": "Assistant commercial (consultation CRM)",
        "description": "Un agent qui consulte l'historique client avant de répondre, pour préparer un appel ou une relance commerciale.",
        "avantages": [
            "Pattern de plus en plus intégré aux CRM (Salesforce, HubSpot...) pour préparer les commerciaux avant un appel",
            "Accès rapide à l'information client sans changer d'outil",
            "Peut aider à rédiger une relance personnalisée à partir de l'historique retrouvé",
        ],
        "inconvenients": [
            "Ce mini-corpus de démonstration ne reflète pas un vrai CRM (nécessiterait une vraie intégration)",
            "Risque de réponse trop générique si l'agent ne trouve rien de pertinent dans sa base",
            "Ne doit jamais remplacer la vérification humaine avant l'envoi d'une communication client sensible",
        ],
        "nodes": [{"id": "1", "type": "agent_unique", "config": {"prompt": "Prépare un argumentaire pour relancer un client inactif depuis 6 mois."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Relance client inactif", "valeurs": {"1": {"prompt": "Prépare un argumentaire pour relancer un client inactif depuis 6 mois."}}},
            {"label": "Historique client", "valeurs": {"1": {"prompt": "Que sait-on du protocole MCP, pour argumenter face à un client technique ?"}}},
            {"label": "Calcul de remise commerciale", "valeurs": {"1": {"prompt": "Un client fidèle depuis 5 ans demande une remise. Calcule 8% de remise sur un devis de 3400€."}}},
        ],
    },
    {
        "id": "assistant_recrutement",
        "categorie": "metiers",
        "titre": "Assistant recrutement (sourcing + rédaction)",
        "description": "Deux agents collaborent : un agent rassemble les critères du poste, un second rédige l'annonce ou les questions d'entretien.",
        "avantages": [
            "Usage de plus en plus courant en RH pour accélérer la rédaction des offres et des trames d'entretien",
            "Sépare la collecte d'informations de la rédaction finale, chacun des deux agents reste spécialisé",
            "Gain de temps réel sur les tâches rédactionnelles répétitives des recruteurs",
        ],
        "inconvenients": [
            "Ne remplace jamais le jugement humain sur l'adéquation réelle d'un candidat",
            "Risque de style trop générique ou de biais hérité des données d'entraînement du modèle",
            "Deux fois plus d'appels LLM que passer directement par un agent unique",
        ],
        "nodes": [{"id": "1", "type": "multi_agent", "config": {"prompt": "Rédige une offre d'emploi pour un poste de plombier confirmé."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Rédiger une offre d'emploi", "valeurs": {"1": {"prompt": "Rédige une offre d'emploi pour un poste de plombier confirmé."}}},
            {"label": "Questions d'entretien", "valeurs": {"1": {"prompt": "Prépare 5 questions d'entretien pour un poste de chef de chantier."}}},
            {"label": "Message de refus bienveillant", "valeurs": {"1": {"prompt": "Rédige un message de refus bienveillant pour un candidat non retenu."}}},
        ],
    },
    {
        "id": "traduction_assistee_verifiee",
        "categorie": "metiers",
        "titre": "Traduction assistée avec double vérification",
        "description": "Une première traduction est générée, puis une seconde passe relit et corrige avant l'envoi à un client international.",
        "avantages": [
            "Pratique courante avant l'envoi de contenu contractuel ou technique à un client à l'étranger",
            "Réduit le risque d'erreur de traduction sur un terme technique ou juridique sensible",
            "Le brouillon ET la correction restent visibles, donc vérifiables par un humain avant envoi",
        ],
        "inconvenients": [
            "Coûte deux fois plus cher/lent qu'une traduction simple en un seul appel",
            "Le prompt de vérification reste générique (pensé pour des calculs/faits), pas spécialisé traduction",
            "Ne remplace pas un traducteur professionnel pour du contenu à fort enjeu juridique",
        ],
        "nodes": [{"id": "1", "type": "verification", "config": {"prompt": "Traduis en anglais : Veuillez trouver ci-joint le devis signé."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Devis signé", "valeurs": {"1": {"prompt": "Traduis en anglais : Veuillez trouver ci-joint le devis signé."}}},
            {"label": "Garantie décennale", "valeurs": {"1": {"prompt": "Traduis en anglais : la garantie décennale couvre le gros œuvre."}}},
            {"label": "Formule de politesse", "valeurs": {"1": {"prompt": "Traduis en anglais : nous restons à votre disposition pour toute question."}}},
        ],
    },
    {
        "id": "choix_modele_migration",
        "categorie": "metiers",
        "titre": "Choix de modèle avant migration (réduction de coûts)",
        "description": "Compare un modèle actuel et un modèle candidat moins coûteux sur des cas réels, avant de décider de migrer.",
        "avantages": [
            "Démarche standard en entreprise avant de réduire les coûts d'inférence en changeant de modèle",
            "Décision basée sur des cas d'usage réels plutôt que sur des benchmarks génériques publics",
            "Documente objectivement l'écart de qualité perçu avant tout engagement de migration",
        ],
        "inconvenients": [
            "Ne teste qu'un échantillon limité de cas, pas exhaustif de tous les usages réels",
            "La « meilleure » réponse reste in fine un jugement humain subjectif",
            "Double le coût d'inférence pendant toute la phase d'évaluation elle-même",
        ],
        "nodes": [{"id": "1", "type": "comparateur", "config": {"prompt": "Rédige une réponse standard à un client demandant un délai de paiement supplémentaire."}, "position": {"x": 200, "y": 120}}],
        "edges": [],
        "exemples": [
            {"label": "Réponse client (délai de paiement)", "valeurs": {"1": {"prompt": "Rédige une réponse standard à un client demandant un délai de paiement supplémentaire."}}},
            {"label": "Résumé de compte-rendu", "valeurs": {"1": {"prompt": "Résume ce compte-rendu de réunion en 3 points : " + _TEXTE_COMPTE_RENDU}}},
            {"label": "Explication acompte/arrhes", "valeurs": {"1": {"prompt": "Explique la différence entre acompte et arrhes à un client."}}},
        ],
    },
    {
        "id": "assistant_marketing_garde_fou",
        "categorie": "garde_fous",
        "titre": "Générateur de contenu marketing avec garde-fou de marque",
        "description": "Filtre les sujets sensibles avant de laisser un outil de génération de contenu en libre-service produire un texte.",
        "avantages": [
            "Pattern de plus en plus déployé pour sécuriser les outils de génération de contenu en libre-service",
            "Évite qu'un contenu marketing associé à un sujet sensible ou interdit pour la marque ne soit généré",
            "Chaque refus est tracé dans le déroulé, exploitable pour un audit de conformité éditoriale",
        ],
        "inconvenients": [
            "Filtre par mots-clés simple : à combiner avec une vraie relecture humaine avant toute publication",
            "Peut bloquer une demande légitime contenant un mot sensible utilisé dans un autre contexte",
            "Ne juge en rien la qualité ou la pertinence marketing du contenu généré, seulement sa conformité",
        ],
        "nodes": [
            {"id": "1", "type": "moderation", "config": {"prompt": "Rédige un post pour annoncer notre nouvelle offre de rénovation énergétique."}, "position": {"x": 120, "y": 120}},
            {"id": "2", "type": "llm_agent", "config": {}, "position": {"x": 420, "y": 120}},
        ],
        "edges": [{"source": "1", "target": "2", "condition": "autorise"}],
        "exemples": [
            {"label": "Post normal", "valeurs": {"1": {"prompt": "Rédige un post pour annoncer notre nouvelle offre de rénovation énergétique."}}},
            {"label": "Sujet bloqué", "valeurs": {"1": {"prompt": "Rédige un post expliquant comment contourner la loi sur les délais de paiement pour paraître plus flexible."}}},
            {"label": "Sujet limite", "valeurs": {"1": {"prompt": "Rédige un post qui compare notre entreprise à un concurrent en le tournant en dérision."}}},
        ],
    },
]


def get_composants() -> list[dict]:
    return COMPOSANTS


def get_templates() -> list[dict]:
    return TEMPLATES
