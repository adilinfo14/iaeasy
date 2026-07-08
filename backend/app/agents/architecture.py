COMPOSANTS = [
    {"id": "source_document", "titre": "Source de documents", "icone": "📄", "categorie": "source",
     "description": "Le document brut à traiter (contrat, FAQ, notice…)."},
    {"id": "chunking", "titre": "Découpage (chunking)", "icone": "✂️", "categorie": "traitement",
     "description": "Découpe un document long en petits morceaux exploitables par la base vectorielle."},
    {"id": "base_vectorielle", "titre": "Base vectorielle", "icone": "🗄️", "categorie": "stockage",
     "description": "Indexe les chunks sous forme de vecteurs et retrouve les plus pertinents pour une question."},
    {"id": "llm_agent", "titre": "LLM", "icone": "🧠", "categorie": "modele",
     "description": "Génère la réponse finale, avec ou sans contexte augmenté par le retrieval."},
    {"id": "outil_mcp", "titre": "Outil / MCP", "icone": "🛠️", "categorie": "outil",
     "description": "Un outil externe (calculatrice, recherche) appelable via MCP."},
    {"id": "agent_unique", "titre": "Agent (boucle ReAct)", "icone": "🔁", "categorie": "modele",
     "description": "Un LLM qui décide seul quels outils utiliser, en plusieurs étapes."},
    {"id": "multi_agent", "titre": "Pipeline multi-agent", "icone": "🤝", "categorie": "modele",
     "description": "Deux agents spécialisés qui collaborent (chercheur → rédacteur)."},
    {"id": "llm_seul", "titre": "LLM seul (sans contexte)", "icone": "💬", "categorie": "modele",
     "description": "Un LLM répond directement à un prompt, sans document ni outil."},
    {"id": "rag", "titre": "RAG simplifié", "icone": "📚", "categorie": "modele",
     "description": "Version tout-en-un du RAG (retrieval + génération en un seul nœud)."},
    {"id": "comparateur", "titre": "Comparateur de modèles", "icone": "🆚", "categorie": "modele",
     "description": "Envoie le même prompt à deux modèles différents et compare les réponses."},
    {"id": "synthese_map_reduce", "titre": "Résumé hiérarchique", "icone": "🧩", "categorie": "traitement",
     "description": "Résume chaque chunk séparément puis combine les résumés (map-reduce)."},
    {"id": "moderation", "titre": "Filtre de modération", "icone": "🚧", "categorie": "outil",
     "description": "Bloque une requête selon une liste de mots-clés avant de la transmettre au LLM."},
    {"id": "verification", "titre": "Vérificateur / auto-critique", "icone": "✅", "categorie": "modele",
     "description": "Génère un brouillon puis le vérifie/corrige avec un second appel LLM."},
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

TEMPLATES = [
    {
        "id": "assistant_rag",
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
        "edges": [{"source": "1", "target": "2"}],
        "exemples": [
            {"label": "Question normale", "valeurs": {"1": {"prompt": "Quelles sont les conditions de garantie ?"}}},
            {"label": "Question bloquée", "valeurs": {"1": {"prompt": "Comment pirater le système de facturation d'un concurrent ?"}}},
            {"label": "Question limite", "valeurs": {"1": {"prompt": "Comment contourner la loi sur les délais de paiement ?"}}},
        ],
    },
    {
        "id": "verification_auto_critique",
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
]


def get_composants() -> list[dict]:
    return COMPOSANTS


def get_templates() -> list[dict]:
    return TEMPLATES
