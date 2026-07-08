TERMES = [
    {
        "terme": "LLM (grand modèle de langage)",
        "categorie": "Général IA",
        "definition_simple": (
            "Un programme entraîné sur d'énormes quantités de texte, qui a appris à deviner le mot "
            "suivant le plus probable dans une phrase. C'est ce mécanisme, répété des milliers de fois, "
            "qui donne l'impression qu'il « comprend » et « répond »."
        ),
        "ou_le_voir": "Catalogue — llama3.2:3b, qwen2.5:7b-instruct",
    },
    {
        "terme": "Prompt",
        "categorie": "Général IA",
        "definition_simple": "Le texte qu'on envoie au modèle pour lui demander quelque chose — sa seule façon de recevoir une instruction.",
        "ou_le_voir": "Constructeur — champ « Prompt » de chaque brique",
    },
    {
        "terme": "Token",
        "categorie": "Général IA",
        "definition_simple": (
            "Le modèle ne lit pas des mots entiers mais des petits morceaux de texte (souvent une "
            "syllabe ou un mot court). Le prix et la vitesse d'un modèle se comptent en tokens, pas en mots."
        ),
        "ou_le_voir": None,
    },
    {
        "terme": "Hallucination",
        "categorie": "Général IA",
        "definition_simple": (
            "Une réponse inventée, présentée avec la même assurance qu'une réponse vraie. Le modèle ne "
            "« sait » pas qu'il se trompe : il génère toujours le mot le plus probable, vrai ou faux."
        ),
        "ou_le_voir": "Stratégie de tests — famille LLM génératif",
    },
    {
        "terme": "Fenêtre de contexte",
        "categorie": "Général IA",
        "definition_simple": "La quantité de texte (en tokens) que le modèle peut « garder en tête » en même temps pour répondre. Au-delà, il oublie le début.",
        "ou_le_voir": None,
    },
    {
        "terme": "Inférence",
        "categorie": "Général IA",
        "definition_simple": "Le moment où un modèle déjà entraîné produit une réponse. On dit « inférence » et pas « calcul » car le modèle ne sait rien avec certitude, il estime la réponse la plus probable.",
        "ou_le_voir": None,
    },
    {
        "terme": "Paramètres (d'un modèle)",
        "categorie": "Général IA",
        "definition_simple": (
            "Les millions ou milliards de « réglages internes » ajustés pendant l'entraînement. Plus il y "
            "en a, plus le modèle peut représenter de nuances — mais plus il est lourd et lent à faire tourner."
        ),
        "ou_le_voir": "Catalogue — champ « taille » de chaque modèle",
    },
    {
        "terme": "CPU vs GPU",
        "categorie": "Général IA",
        "definition_simple": (
            "Le GPU (carte graphique) calcule beaucoup d'opérations en parallèle et accélère énormément "
            "l'IA. Ce site tourne volontairement en CPU pur (sans GPU) pour rester simple à héberger soi-même."
        ),
        "ou_le_voir": None,
    },
    {
        "terme": "IA souveraine",
        "categorie": "Général IA",
        "definition_simple": (
            "Une IA qu'on héberge et qu'on contrôle soi-même (modèles open-source, serveur perso), plutôt "
            "que d'envoyer ses données à un service tiers dans le cloud. C'est le principe de ce site entier."
        ),
        "ou_le_voir": "Toute la plateforme iaeasy",
    },
    {
        "terme": "Embedding (vecteur)",
        "categorie": "Architecture / agents",
        "definition_simple": (
            "Une façon de transformer un texte en une liste de nombres qui capture son SENS. Deux textes "
            "au sens proche ont des listes de nombres proches, même s'ils n'ont aucun mot en commun."
        ),
        "ou_le_voir": "Catalogue — famille Embeddings ; Constructeur — brique Base vectorielle",
    },
    {
        "terme": "Similarité cosinus",
        "categorie": "Architecture / agents",
        "definition_simple": "La formule mathématique qui mesure à quel point deux vecteurs (deux embeddings) « pointent dans la même direction » — c'est ce score qui dit si deux textes se ressemblent en sens.",
        "ou_le_voir": "Constructeur — brique Base vectorielle",
    },
    {
        "terme": "RAG (Retrieval Augmented Generation)",
        "categorie": "Architecture / agents",
        "definition_simple": (
            "Au lieu de faire confiance uniquement à la mémoire du modèle, on va d'abord chercher les "
            "passages pertinents dans de vrais documents, puis on les donne au modèle avant qu'il réponde. "
            "Réduit fortement le risque d'hallucination."
        ),
        "ou_le_voir": "Constructeur — templates « Assistant RAG documentaire », « RAG simplifié »",
    },
    {
        "terme": "Chunking (découpage)",
        "categorie": "Architecture / agents",
        "definition_simple": "Couper un long document en petits morceaux avant de le comparer à une question — un document entier est trop gros pour être comparé efficacement d'un coup.",
        "ou_le_voir": "Constructeur — brique Découpage (chunking)",
    },
    {
        "terme": "Agent (IA agentique)",
        "categorie": "Architecture / agents",
        "definition_simple": "Un LLM à qui on donne la possibilité d'utiliser des outils (calculatrice, recherche...) et qui décide lui-même, étape par étape, ce qu'il doit faire pour répondre.",
        "ou_le_voir": "Constructeur — brique Agent (boucle ReAct)",
    },
    {
        "terme": "ReAct (Reason + Act)",
        "categorie": "Architecture / agents",
        "definition_simple": "Le principe derrière la plupart des agents IA : le modèle alterne des étapes de raisonnement (« que dois-je faire ? ») et d'action (appeler un outil), jusqu'à pouvoir répondre.",
        "ou_le_voir": "Constructeur — brique Agent (boucle ReAct)",
    },
    {
        "terme": "Multi-agent",
        "categorie": "Architecture / agents",
        "definition_simple": "Plusieurs agents spécialisés qui collaborent en séquence (ex : un « chercheur » qui rassemble les faits, un « rédacteur » qui les met en forme) plutôt qu'un seul agent qui fait tout.",
        "ou_le_voir": "Constructeur — brique Pipeline multi-agent",
    },
    {
        "terme": "MCP (Model Context Protocol)",
        "categorie": "Architecture / agents",
        "definition_simple": "Un standard qui définit comment un modèle IA appelle des outils et des sources de données externes de façon homogène, plutôt que chaque fournisseur ait son propre système incompatible.",
        "ou_le_voir": "Constructeur — brique Outil / MCP",
    },
    {
        "terme": "Modération (filtre de contenu)",
        "categorie": "Architecture / agents",
        "definition_simple": "Une vérification de la requête avant même d'appeler le modèle, pour bloquer les demandes inappropriées sans dépenser un appel IA inutile.",
        "ou_le_voir": "Constructeur — brique Filtre de modération",
    },
    {
        "terme": "Vérificateur / auto-critique",
        "categorie": "Architecture / agents",
        "definition_simple": "Le modèle génère une première réponse, puis un second appel la relit et la corrige si besoin — une façon simple d'améliorer la fiabilité sur les tâches à risque d'erreur (calculs, faits précis).",
        "ou_le_voir": "Constructeur — brique Vérificateur / auto-critique",
    },
    {
        "terme": "Entraînement (fine-tuning)",
        "categorie": "Entraînement",
        "definition_simple": "Ajuster un modèle déjà existant sur un petit jeu de données spécifique, plutôt que de tout ré-apprendre depuis zéro — beaucoup plus rapide et moins coûteux.",
        "ou_le_voir": "Module Entraînement — les 3 scénarios",
    },
    {
        "terme": "Loss (perte)",
        "categorie": "Entraînement",
        "definition_simple": "Un chiffre qui mesure à quel point le modèle se trompe pendant l'entraînement. Plus il descend, mieux le modèle apprend — s'il stagne ou oscille, quelque chose ne va pas.",
        "ou_le_voir": "Module Entraînement — courbe affichée en direct",
    },
    {
        "terme": "Epoch",
        "categorie": "Entraînement",
        "definition_simple": "Un passage complet sur l'ensemble des données d'entraînement. On répète souvent plusieurs epochs pour que le modèle ait le temps de bien apprendre.",
        "ou_le_voir": "Module Entraînement",
    },
    {
        "terme": "Taux d'apprentissage (learning rate)",
        "categorie": "Entraînement",
        "definition_simple": (
            "La taille des pas que le modèle fait à chaque correction pendant l'entraînement. Trop grand, "
            "il peut « rater » la bonne solution en oscillant ; trop petit, il apprend trop lentement."
        ),
        "ou_le_voir": "Module Entraînement — scénario sentiment (bug réel corrigé sur ce site)",
    },
    {
        "terme": "Surapprentissage (overfitting)",
        "categorie": "Entraînement",
        "definition_simple": "Quand un modèle apprend « par cœur » ses exemples d'entraînement au lieu de comprendre la logique générale — il devient très bon sur ces exemples précis, mais mauvais sur des cas nouveaux.",
        "ou_le_voir": None,
    },
    {
        "terme": "Classification",
        "categorie": "Entraînement",
        "definition_simple": "Faire ranger par un modèle chaque exemple dans une catégorie prédéfinie (spam/légitime, positif/négatif...), plutôt que générer du texte libre.",
        "ou_le_voir": "Module Entraînement — scénarios sentiment et spam",
    },
    {
        "terme": "Régression",
        "categorie": "Entraînement",
        "definition_simple": "Faire prédire à un modèle une valeur numérique continue (un prix, un chiffre d'affaires) plutôt qu'une catégorie fixe.",
        "ou_le_voir": "Module Entraînement — scénario prévision de CA",
    },
    {
        "terme": "Détection d'anomalie",
        "categorie": "Général IA",
        "definition_simple": "Repérer automatiquement une valeur qui sort de la normale (une transaction suspecte, une machine qui vibre anormalement), sans avoir défini de règle fixe à l'avance.",
        "ou_le_voir": "Catalogue — Isolation Forest (fraude, maintenance)",
    },
    {
        "terme": "Extraction d'entités (NER)",
        "categorie": "Général IA",
        "definition_simple": "Repérer automatiquement dans un texte les noms de personnes, de lieux ou d'organisations, pour les extraire sans avoir à les relire soi-même.",
        "ou_le_voir": "Catalogue — CamemBERT NER",
    },
    {
        "terme": "Biais algorithmique",
        "categorie": "Général IA",
        "definition_simple": "Quand un modèle reproduit ou amplifie, sans le vouloir, un déséquilibre présent dans ses données d'entraînement (ex : moins fiable sur un sous-groupe de la population que sur un autre).",
        "ou_le_voir": "Stratégie de tests — famille Classification classique",
    },
]


def get_termes() -> list[dict]:
    return TERMES
