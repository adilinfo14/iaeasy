BRIQUES = [
    {
        "id": "llm_seul",
        "ordre": 1,
        "titre": "LLM seul",
        "icone": "🧠",
        "description_pedagogique": (
            "Un modèle de langage reçoit un prompt et répond directement, sans aucune "
            "aide extérieure. C'est la brique de base de tout agent."
        ),
        "schema": [
            {"icone": "💬", "label": "Votre question"},
            {"icone": "🧠", "label": "LLM"},
            {"icone": "✅", "label": "Réponse directe"},
        ],
        "prerequis": [],
        "cas": [
            {
                "id": "btp",
                "secteur": "BTP / Artisan",
                "mise_en_situation": (
                    "Tu es développeur chez un artisan du bâtiment. Le patron te demande un premier "
                    "prototype : un assistant qui répond aux questions générales des clients, sans "
                    "rien connaître encore de l'entreprise."
                ),
                "avant": "Rien n'existe encore — chaque question est traitée à la main par un humain.",
                "apres": (
                    "L'assistant répond directement à partir de ce qu'il a appris pendant son "
                    "entraînement général, mais ne connaît rien de spécifique à l'entreprise."
                ),
                "entree_defaut": {"prompt": "Explique en une phrase ce qu'est un LLM."},
            },
            {
                "id": "banque_assurance",
                "secteur": "Banque / Assurance",
                "mise_en_situation": (
                    "Tu es développeur dans une agence bancaire, Norda Banque & Assurance. Le "
                    "directeur te demande un premier prototype : un assistant qui répond aux "
                    "questions générales des clients, sans rien connaître encore des produits et "
                    "procédures internes de l'agence."
                ),
                "avant": "Rien n'existe encore — chaque question est traitée à la main par un conseiller.",
                "apres": (
                    "L'assistant répond directement à partir de ce qu'il a appris pendant son "
                    "entraînement général, mais ne connaît rien de spécifique à l'agence."
                ),
                "entree_defaut": {
                    "prompt": "C'est quoi la différence entre un prêt à taux fixe et un prêt à taux variable ?"
                },
            },
            {
                "id": "agriculture",
                "secteur": "Agriculture",
                "mise_en_situation": (
                    "Tu es développeur chez la coopérative agricole Agri-Vallée. Le président te "
                    "demande un premier prototype : un assistant qui répond aux questions générales "
                    "des adhérents, sans rien connaître encore de la coopérative."
                ),
                "avant": "Rien n'existe encore — chaque question est traitée à la main par un conseiller agricole.",
                "apres": (
                    "L'assistant répond directement à partir de ce qu'il a appris pendant son "
                    "entraînement général, mais ne connaît rien de spécifique à la coopérative."
                ),
                "entree_defaut": {"prompt": "Quelle est la meilleure période pour semer du blé d'hiver ?"},
            },
            {
                "id": "rh_juridique",
                "secteur": "RH / Juridique",
                "mise_en_situation": (
                    "Tu es développeur au service RH d'une PME de 200 salariés. La DRH te demande un "
                    "premier prototype : un assistant qui répond aux questions générales des salariés "
                    "sur le droit du travail, sans rien connaître encore des règles internes de "
                    "l'entreprise."
                ),
                "avant": "Rien n'existe encore — chaque question est traitée à la main par un gestionnaire RH.",
                "apres": (
                    "L'assistant répond directement à partir de ce qu'il a appris pendant son "
                    "entraînement général, mais ne connaît rien de spécifique aux règles internes de "
                    "l'entreprise."
                ),
                "entree_defaut": {"prompt": "Combien de jours de congés payés a-t-on légalement par an en France ?"},
            },
            {
                "id": "ecommerce",
                "secteur": "E-commerce / Service client",
                "mise_en_situation": (
                    "Tu es développeur chez Lumira, une boutique en ligne. La responsable du service "
                    "client te demande un premier prototype : un assistant qui répond aux questions "
                    "générales des clients, sans rien connaître encore de la boutique."
                ),
                "avant": "Rien n'existe encore — chaque question est traitée à la main par un conseiller du service client.",
                "apres": (
                    "L'assistant répond directement à partir de ce qu'il a appris pendant son "
                    "entraînement général, mais ne connaît rien de spécifique à Lumira."
                ),
                "entree_defaut": {"prompt": "C'est quoi la différence entre un remboursement et un avoir ?"},
            },
        ],
        "quiz": [
            {
                "question": "Un LLM seul répond à une question en se basant sur...",
                "options": [
                    "Une recherche dans les documents de l'entreprise",
                    "Uniquement ce qu'il a appris pendant son entraînement général",
                    "Le résultat d'une calculatrice externe",
                ],
                "bonne_reponse": 1,
            },
            {
                "question": "Pourquoi un LLM seul ne peut-il pas connaître les conditions de garantie propres à une entreprise ?",
                "options": [
                    "Parce qu'il n'a jamais vu ce document interne pendant son entraînement",
                    "Parce qu'il refuse de répondre aux questions sur les garanties",
                    "Parce qu'il a besoin d'un outil pour ça",
                ],
                "bonne_reponse": 0,
            },
        ],
    },
    {
        "id": "rag",
        "ordre": 2,
        "titre": "RAG (retrieval)",
        "icone": "📚",
        "description_pedagogique": (
            "Avant de répondre, on cherche d'abord les passages les plus proches en sens "
            "dans un mini-corpus (via des embeddings), et on les ajoute au prompt du LLM. "
            "Le modèle répond alors avec des informations qu'il n'avait pas apprises par cœur."
        ),
        "schema": [
            {"icone": "❓", "label": "Votre question"},
            {"icone": "🔎", "label": "Recherche dans les documents"},
            {"icone": "📄", "label": "Passage retrouvé"},
            {"icone": "🧠", "label": "LLM + ce passage"},
            {"icone": "✅", "label": "Réponse"},
        ],
        "prerequis": ["llm_seul"],
        "cas": [
            {
                "id": "btp",
                "secteur": "BTP / Artisan",
                "mise_en_situation": (
                    "Un client demande les conditions de garantie exactes de l'entreprise. Un LLM "
                    "seul n'a jamais vu ce document interne — il ne peut pas connaître la réponse."
                ),
                "avant": "L'assistant invente ou botte en touche sur les informations propres à l'entreprise.",
                "apres": (
                    "Avant de répondre, l'assistant cherche d'abord le passage le plus pertinent "
                    "dans les documents de l'entreprise (via des embeddings), puis répond en "
                    "s'appuyant dessus."
                ),
                "entree_defaut": {
                    "prompt": "Quelles sont les conditions de garantie ?",
                    "document_utilisateur": "La garantie décennale couvre les dommages de gros œuvre pendant 10 ans après réception des travaux.",
                },
            },
            {
                "id": "banque_assurance",
                "secteur": "Banque / Assurance",
                "mise_en_situation": (
                    "Un client demande les conditions exactes de son contrat d'assurance "
                    "habitation, en particulier le montant de la franchise et le plafond "
                    "d'indemnisation. Un LLM seul n'a jamais vu ce document interne — il ne peut "
                    "pas connaître la réponse."
                ),
                "avant": "L'assistant invente ou botte en touche sur les informations propres au contrat du client.",
                "apres": (
                    "Avant de répondre, l'assistant cherche d'abord le passage le plus pertinent "
                    "dans les documents de l'agence (via des embeddings), puis répond en "
                    "s'appuyant dessus."
                ),
                "entree_defaut": {
                    "prompt": "Quelle est ma franchise en cas de dégât des eaux, et quel est le plafond d'indemnisation ?",
                    "document_utilisateur": "Contrat Habitation Sérénité - Norda Assurances. En cas de sinistre dégât des eaux, une franchise fixe de 350€ est appliquée sur chaque déclaration. Le plafond d'indemnisation pour ce type de sinistre est fixé à 15 000€ par an, tous sinistres confondus.",
                },
            },
            {
                "id": "agriculture",
                "secteur": "Agriculture",
                "mise_en_situation": (
                    "Un adhérent demande les conditions exactes d'une aide au maintien en "
                    "agriculture biologique proposée par la coopérative. Un LLM seul n'a jamais vu "
                    "ce document interne — il ne peut pas connaître la réponse."
                ),
                "avant": "L'assistant invente ou botte en touche sur les informations propres à la coopérative.",
                "apres": (
                    "Avant de répondre, l'assistant cherche d'abord le passage le plus pertinent "
                    "dans les documents de la coopérative (via des embeddings), puis répond en "
                    "s'appuyant dessus."
                ),
                "entree_defaut": {
                    "prompt": "Quelles sont les conditions pour bénéficier de l'aide au maintien en agriculture biologique cette année ?",
                    "document_utilisateur": "Aide au maintien en agriculture biologique : ouverte aux adhérents certifiés bio depuis plus de 2 ans, exploitant au moins 5 hectares. Le montant est de 130 €/hectare, plafonné à 15 hectares par exploitation. Dossier à déposer avant le 15 mai auprès de la coopérative.",
                },
            },
            {
                "id": "rh_juridique",
                "secteur": "RH / Juridique",
                "mise_en_situation": (
                    "Un salarié demande combien de jours de télétravail par semaine sont autorisés "
                    "selon le règlement intérieur de l'entreprise. Un LLM seul n'a jamais vu ce "
                    "document interne — il ne peut pas connaître la réponse."
                ),
                "avant": "L'assistant invente ou botte en touche sur les règles propres à l'entreprise.",
                "apres": (
                    "Avant de répondre, l'assistant cherche d'abord le passage le plus pertinent "
                    "dans les documents internes (via des embeddings), puis répond en s'appuyant "
                    "dessus."
                ),
                "entree_defaut": {
                    "prompt": "Combien de jours de télétravail par semaine sont autorisés selon le règlement intérieur ?",
                    "document_utilisateur": "Règlement intérieur - Article 12 : Télétravail. Les salariés en CDI ayant plus de 6 mois d'ancienneté peuvent télétravailler jusqu'à 2 jours par semaine, sur validation de leur manager. Les jours de télétravail doivent être posés au moins 48h à l'avance dans l'outil RH.",
                },
            },
            {
                "id": "ecommerce",
                "secteur": "E-commerce / Service client",
                "mise_en_situation": (
                    "Un client demande le délai exact de remboursement chez Lumira. Un LLM seul "
                    "n'a jamais vu la politique de retour interne — il ne peut pas connaître la "
                    "réponse."
                ),
                "avant": "L'assistant invente ou botte en touche sur les informations propres à Lumira (délais, conditions de retour).",
                "apres": (
                    "Avant de répondre, l'assistant cherche d'abord le passage le plus pertinent "
                    "dans les documents de Lumira (via des embeddings), puis répond en s'appuyant "
                    "dessus."
                ),
                "entree_defaut": {
                    "prompt": "Sous combien de jours suis-je remboursé si je retourne un article ?",
                    "document_utilisateur": "Politique de retour Lumira : les articles peuvent être retournés dans les 30 jours suivant la réception, à condition qu'ils soient non portés et avec leur étiquette d'origine. Le remboursement est effectué sous 5 jours ouvrés après réception du colis retourné, sur le moyen de paiement utilisé lors de l'achat.",
                },
            },
        ],
        "quiz": [
            {
                "question": "Que fait la brique RAG avant de laisser le LLM répondre ?",
                "options": [
                    "Elle appelle une calculatrice",
                    "Elle cherche d'abord le passage le plus pertinent dans les documents, via des embeddings",
                    "Elle demande à un second agent de vérifier la réponse",
                ],
                "bonne_reponse": 1,
            },
            {
                "question": "Un embedding sert principalement à...",
                "options": [
                    "Transformer un texte en nombres qui capturent son sens, pour comparer des textes entre eux",
                    "Exécuter un calcul mathématique précis",
                    "Décider quel outil un agent doit utiliser",
                ],
                "bonne_reponse": 0,
            },
        ],
    },
    {
        "id": "outil_mcp",
        "ordre": 3,
        "titre": "Outil / MCP",
        "icone": "🛠️",
        "description_pedagogique": (
            "Le modèle peut désormais appeler un vrai outil externe — ici une calculatrice "
            "et une recherche documentaire — exposé via le protocole MCP (Model Context "
            "Protocol), plutôt que de tout deviner par lui-même."
        ),
        "schema": [
            {"icone": "❓", "label": "Demande"},
            {"icone": "🛠️", "label": "Appel de l'outil (MCP)"},
            {"icone": "📊", "label": "Résultat de l'outil"},
            {"icone": "✅", "label": "Réponse"},
        ],
        "prerequis": ["rag"],
        "cas": [
            {
                "id": "btp",
                "secteur": "BTP / Artisan",
                "mise_en_situation": (
                    "Un client demande de calculer un montant TTC précis. Un LLM peut se tromper "
                    "en arithmétique — il vaut mieux qu'il utilise une vraie calculatrice."
                ),
                "avant": "L'assistant peut se tromper sur un calcul ou une recherche précise.",
                "apres": (
                    "L'assistant peut désormais appeler un vrai outil externe (calculatrice, "
                    "recherche documentaire) exposé via le protocole MCP (Model Context Protocol), "
                    "plutôt que de tout deviner par lui-même."
                ),
                "entree_defaut": {
                    "outil": "calculatrice",
                    "expression": "45 * 3.5 + 45 * 2.25",
                    "requete": "Qu'est-ce que le protocole MCP ?",
                },
                "exemples": [
                    {"label": "Coût main d'œuvre + matériaux", "outil": "calculatrice", "expression": "8 * 38 + 340"},
                    {"label": "Qu'est-ce qu'un agent unique ?", "outil": "recherche", "requete": "Qu'est-ce qu'un agent unique ?"},
                ],
            },
            {
                "id": "banque_assurance",
                "secteur": "Banque / Assurance",
                "mise_en_situation": (
                    "Un client demande de calculer le coût total exact d'un crédit, intérêts "
                    "compris. Un LLM peut se tromper en arithmétique — il vaut mieux qu'il utilise "
                    "une vraie calculatrice."
                ),
                "avant": "L'assistant peut se tromper sur un calcul ou une recherche précise.",
                "apres": (
                    "L'assistant peut désormais appeler un vrai outil externe (calculatrice, "
                    "recherche documentaire) exposé via le protocole MCP, plutôt que de tout "
                    "deviner par lui-même."
                ),
                "entree_defaut": {
                    "outil": "calculatrice",
                    "expression": "12000 + (12000 * 0.045 * 3)",
                    "requete": "Comment fonctionne une boucle ReAct ?",
                },
                "exemples": [
                    {"label": "Mensualité + frais de dossier", "outil": "calculatrice", "expression": "15000 / 60 + 45"},
                    {"label": "Comment fonctionne le multi-agent ?", "outil": "recherche", "requete": "Comment fonctionne un pipeline multi-agent ?"},
                ],
            },
            {
                "id": "agriculture",
                "secteur": "Agriculture",
                "mise_en_situation": (
                    "Un adhérent demande de calculer précisément le rendement à l'hectare de sa "
                    "parcelle de blé. Un LLM peut se tromper en arithmétique — il vaut mieux qu'il "
                    "utilise une vraie calculatrice."
                ),
                "avant": "L'assistant peut se tromper sur un calcul ou une recherche précise.",
                "apres": (
                    "L'assistant peut désormais appeler un vrai outil externe (calculatrice, "
                    "recherche documentaire) exposé via le protocole MCP, plutôt que de tout "
                    "deviner par lui-même."
                ),
                "entree_defaut": {
                    "outil": "calculatrice",
                    "expression": "68000 / 12",
                    "requete": "Comment un modèle de détection d'anomalie s'entraîne-t-il ?",
                },
                "exemples": [
                    {"label": "Coût de traitement à l'hectare", "outil": "calculatrice", "expression": "22 * 65"},
                    {"label": "Qu'est-ce qu'un embedding ?", "outil": "recherche", "requete": "Qu'est-ce qu'un embedding ?"},
                ],
            },
            {
                "id": "rh_juridique",
                "secteur": "RH / Juridique",
                "mise_en_situation": (
                    "Un salarié qui quitte l'entreprise demande le montant précis de son "
                    "indemnité de licenciement. Un LLM peut se tromper en arithmétique — il vaut "
                    "mieux qu'il utilise une vraie calculatrice."
                ),
                "avant": "L'assistant peut se tromper sur un calcul ou une recherche précise.",
                "apres": (
                    "L'assistant peut désormais appeler un vrai outil externe (calculatrice, "
                    "recherche documentaire) exposé via le protocole MCP, plutôt que de tout "
                    "deviner par lui-même."
                ),
                "entree_defaut": {
                    "outil": "calculatrice",
                    "expression": "3200 * 0.25 * 8",
                    "requete": "Qu'est-ce qu'un système multi-agent ?",
                },
                "exemples": [
                    {"label": "Total des primes trimestrielles", "outil": "calculatrice", "expression": "4 * 250"},
                    {"label": "Comment fonctionne le RAG ?", "outil": "recherche", "requete": "Comment fonctionne la recherche documentaire RAG ?"},
                ],
            },
            {
                "id": "ecommerce",
                "secteur": "E-commerce / Service client",
                "mise_en_situation": (
                    "Un client demande combien il sera remboursé après application de sa remise "
                    "de fidélité. Un LLM peut se tromper en arithmétique — il vaut mieux qu'il "
                    "utilise une vraie calculatrice."
                ),
                "avant": "L'assistant peut se tromper sur un calcul ou une recherche précise (montant remboursé, frais de port, TVA).",
                "apres": (
                    "L'assistant peut désormais appeler un vrai outil externe (calculatrice, "
                    "recherche documentaire) exposé via le protocole MCP, plutôt que de tout "
                    "deviner par lui-même."
                ),
                "entree_defaut": {
                    "outil": "calculatrice",
                    "expression": "129.99 - (129.99 * 0.15)",
                    "requete": "Qu'est-ce que le RAG ?",
                },
                "exemples": [
                    {"label": "Total panier + livraison", "outil": "calculatrice", "expression": "3 * 24.90 + 5.90"},
                    {"label": "Qu'est-ce qu'un outil MCP ?", "outil": "recherche", "requete": "Qu'est-ce qu'un outil MCP ?"},
                ],
            },
        ],
        "quiz": [
            {
                "question": "Pourquoi utiliser une calculatrice plutôt que de laisser le LLM calculer lui-même ?",
                "options": [
                    "Parce qu'un LLM peut se tromper en arithmétique, alors qu'une calculatrice ne se trompe jamais",
                    "Parce que c'est obligatoire pour toutes les questions",
                    "Parce que ça rend la réponse plus longue",
                ],
                "bonne_reponse": 0,
            },
            {
                "question": "MCP signifie...",
                "options": [
                    "Model Context Protocol — un standard pour que les modèles appellent des outils",
                    "Multiple Chat Processing",
                    "Machine Calculation Program",
                ],
                "bonne_reponse": 0,
            },
        ],
    },
    {
        "id": "agent_unique",
        "ordre": 4,
        "titre": "Agent unique (ReAct)",
        "icone": "🔁",
        "description_pedagogique": (
            "Le modèle raisonne en boucle : il décide d'utiliser un outil, observe le "
            "résultat, puis décide de la suite — jusqu'à obtenir une réponse finale. "
            "C'est le principe de la boucle ReAct (Reason + Act)."
        ),
        "schema": [
            {"icone": "❓", "label": "Tâche"},
            {"icone": "🤔", "label": "Le LLM réfléchit"},
            {"icone": "🛠️", "label": "Appelle un outil si besoin"},
            {"icone": "🔁", "label": "Répète jusqu'à avoir la réponse"},
            {"icone": "✅", "label": "Réponse finale"},
        ],
        "prerequis": ["outil_mcp"],
        "cas": [
            {
                "id": "btp",
                "secteur": "BTP / Artisan",
                "mise_en_situation": (
                    "Le patron veut que l'assistant décide LUI-MÊME quel outil utiliser selon la "
                    "question posée, sans qu'on lui dise à l'avance quoi faire."
                ),
                "avant": "Il fallait choisir manuellement RAG ou un outil selon le type de question.",
                "apres": (
                    "L'assistant raisonne en boucle : il décide d'utiliser un outil, observe le "
                    "résultat, puis décide de la suite — jusqu'à obtenir une réponse finale. "
                    "C'est le principe de la boucle ReAct (Reason + Act)."
                ),
                "entree_defaut": {"prompt": "Combien font 15 fois (2 + 6) ?"},
                "exemples": [
                    {
                        "label": "Coût de main d'œuvre sur un chantier",
                        "prompt": "Un chantier dure 12 jours à raison de 7h par jour à 42€/h : quel est le coût total de main d'œuvre ?",
                    }
                ],
            },
            {
                "id": "banque_assurance",
                "secteur": "Banque / Assurance",
                "mise_en_situation": (
                    "Le directeur veut que l'assistant décide LUI-MÊME quel outil utiliser selon "
                    "la question posée, sans qu'on lui dise à l'avance quoi faire."
                ),
                "avant": "Il fallait choisir manuellement RAG ou un outil selon le type de question.",
                "apres": (
                    "L'assistant raisonne en boucle : il décide d'utiliser un outil, observe le "
                    "résultat, puis décide de la suite — jusqu'à obtenir une réponse finale."
                ),
                "entree_defaut": {
                    "prompt": "Un client veut emprunter 20 000€ sur 5 ans à un taux fixe de 3,8% (intérêts simples) : peux-tu lui dire combien ce crédit lui coûtera au total ?"
                },
                "exemples": [
                    {
                        "label": "Placement à intérêt simple",
                        "prompt": "Un client place 8000€ à 2,5% d'intérêt simple pendant 4 ans : combien aura-t-il à l'échéance ?",
                    }
                ],
            },
            {
                "id": "agriculture",
                "secteur": "Agriculture",
                "mise_en_situation": (
                    "Le président veut que l'assistant décide LUI-MÊME quel outil utiliser selon "
                    "la question posée, sans qu'on lui dise à l'avance quoi faire."
                ),
                "avant": "Il fallait choisir manuellement RAG ou un outil selon le type de question.",
                "apres": (
                    "L'assistant raisonne en boucle : il décide d'utiliser un outil, observe le "
                    "résultat, puis décide de la suite — jusqu'à obtenir une réponse finale."
                ),
                "entree_defaut": {
                    "prompt": "J'ai récolté 92 tonnes de maïs sur 14 hectares, peux-tu me dire mon rendement moyen à l'hectare et me dire si c'est au-dessus de la moyenne régionale de 8 tonnes/ha ?"
                },
                "exemples": [
                    {
                        "label": "Prix de vente vs référence",
                        "prompt": "J'ai vendu 45 tonnes de blé à 220€/tonne, peux-tu me dire le montant total et si c'est au-dessus d'un prix de référence de 200€/tonne ?",
                    }
                ],
            },
            {
                "id": "rh_juridique",
                "secteur": "RH / Juridique",
                "mise_en_situation": (
                    "La DRH veut que l'assistant décide LUI-MÊME quel outil utiliser selon la "
                    "question posée, sans qu'on lui dise à l'avance quoi faire."
                ),
                "avant": "Il fallait choisir manuellement RAG ou un outil selon le type de question.",
                "apres": (
                    "L'assistant raisonne en boucle : il décide d'utiliser un outil, observe le "
                    "résultat, puis décide de la suite — jusqu'à obtenir une réponse finale."
                ),
                "entree_defaut": {
                    "prompt": "Un salarié a 6 ans d'ancienneté et un salaire brut mensuel de 2800 euros, il est licencié : combien va-t-il toucher d'indemnité légale ?"
                },
                "exemples": [
                    {
                        "label": "Jours de RTT restants",
                        "prompt": "Un salarié a pris 18 jours de RTT sur les 25 auxquels il a droit cette année, combien lui en reste-t-il ?",
                    }
                ],
            },
            {
                "id": "ecommerce",
                "secteur": "E-commerce / Service client",
                "mise_en_situation": (
                    "La responsable veut que l'assistant décide LUI-MÊME quel outil utiliser selon "
                    "la question posée — chercher dans la politique de retour ou calculer un "
                    "montant — sans qu'on lui dise à l'avance quoi faire."
                ),
                "avant": "Il fallait choisir manuellement RAG ou un outil selon le type de question.",
                "apres": (
                    "L'assistant raisonne en boucle : il décide d'utiliser un outil, observe le "
                    "résultat, puis décide de la suite — jusqu'à obtenir une réponse finale."
                ),
                "entree_defaut": {
                    "prompt": "Un client a commandé pour 156 euros et a un code promo de 20%. Calcule combien il doit payer au final."
                },
                "exemples": [
                    {
                        "label": "Montant final après remise",
                        "prompt": "Un client a acheté pour 340€ avec une remise de 12%, combien va-t-il payer au final ?",
                    }
                ],
            },
        ],
        "quiz": [
            {
                "question": "Qu'est-ce que la boucle ReAct ?",
                "options": [
                    "Le modèle alterne entre raisonner (Reason) et agir (Act) jusqu'à obtenir une réponse finale",
                    "Le modèle répète toujours la même réponse deux fois",
                    "Le modèle refuse d'utiliser des outils",
                ],
                "bonne_reponse": 0,
            },
            {
                "question": "Quel est l'avantage principal d'un agent unique par rapport à un enchaînement RAG + outil fixé à l'avance ?",
                "options": [
                    "Il décide lui-même quel outil utiliser selon la question, sans qu'on le lui impose",
                    "Il est toujours plus rapide, quelle que soit la question",
                    "Il n'a jamais besoin d'outils",
                ],
                "bonne_reponse": 0,
            },
        ],
    },
    {
        "id": "multi_agent",
        "ordre": 5,
        "titre": "Multi-agent",
        "icone": "🤝",
        "description_pedagogique": (
            "Deux agents se répartissent le travail : un agent 'chercheur' rassemble "
            "l'information, puis un agent 'rédacteur' la met en forme. Chacun a un rôle "
            "et un prompt différent."
        ),
        "schema": [
            {"icone": "❓", "label": "Tâche"},
            {"icone": "🔍", "label": "Agent chercheur"},
            {"icone": "📝", "label": "Notes brutes"},
            {"icone": "✍️", "label": "Agent rédacteur"},
            {"icone": "✅", "label": "Réponse finale"},
        ],
        "prerequis": ["agent_unique"],
        "cas": [
            {
                "id": "btp",
                "secteur": "BTP / Artisan",
                "mise_en_situation": (
                    "Le patron veut maintenant que l'assistant rédige de vrais emails clients, "
                    "pas juste des réponses brutes — une seule 'tête' a du mal à bien faire les deux."
                ),
                "avant": "Un seul agent devait à la fois chercher l'information ET bien la formuler.",
                "apres": (
                    "Deux agents se répartissent le travail : un agent 'chercheur' rassemble "
                    "l'information, puis un agent 'rédacteur' la met en forme claire et "
                    "professionnelle. Chacun a un rôle et un prompt différent."
                ),
                "entree_defaut": {"prompt": "Rédige un message pour expliquer à un client ce qu'est un agent IA."},
                "exemples": [
                    {
                        "label": "Annonce de report de chantier",
                        "prompt": "Rédige un message pour annoncer à un client un report de chantier de 5 jours pour cause d'intempéries.",
                    }
                ],
            },
            {
                "id": "banque_assurance",
                "secteur": "Banque / Assurance",
                "mise_en_situation": (
                    "Le directeur veut maintenant que l'assistant rédige de vrais emails clients "
                    "(validation de dossier, notification de sinistre), pas juste des réponses "
                    "brutes — une seule 'tête' a du mal à bien faire les deux."
                ),
                "avant": "Un seul agent devait à la fois chercher l'information ET bien la formuler.",
                "apres": (
                    "Deux agents se répartissent le travail : un agent 'chercheur' rassemble "
                    "l'information, puis un agent 'rédacteur' la met en forme claire et "
                    "professionnelle."
                ),
                "entree_defaut": {
                    "prompt": "Rédige un email pour informer un client que son dossier de sinistre dégât des eaux a été validé et que l'indemnisation de 3 200€ (franchise déjà déduite) sera versée sous 10 jours ouvrés."
                },
                "exemples": [
                    {
                        "label": "Relance dossier de prêt incomplet",
                        "prompt": "Rédige un email pour relancer un client dont le dossier de prêt est incomplet depuis 2 semaines.",
                    }
                ],
            },
            {
                "id": "agriculture",
                "secteur": "Agriculture",
                "mise_en_situation": (
                    "Le président veut maintenant que l'assistant rédige de vrais messages aux "
                    "adhérents, pas juste des réponses brutes — une seule 'tête' a du mal à bien "
                    "faire les deux."
                ),
                "avant": "Un seul agent devait à la fois chercher l'information ET bien la formuler.",
                "apres": (
                    "Deux agents se répartissent le travail : un agent 'chercheur' rassemble "
                    "l'information, puis un agent 'rédacteur' la met en forme claire et "
                    "professionnelle."
                ),
                "entree_defaut": {
                    "prompt": "Rédige un message clair pour informer les adhérents bio de la coopérative des conditions et de la date limite de dépôt du dossier d'aide au maintien en agriculture biologique."
                },
                "exemples": [
                    {
                        "label": "Changement de date de collecte",
                        "prompt": "Rédige un message pour informer les adhérents d'un changement de date de collecte des céréales.",
                    }
                ],
            },
            {
                "id": "rh_juridique",
                "secteur": "RH / Juridique",
                "mise_en_situation": (
                    "La DRH veut maintenant que l'assistant rédige de vrais courriers aux salariés "
                    "et candidats, pas juste des réponses brutes — une seule 'tête' a du mal à "
                    "bien faire les deux."
                ),
                "avant": "Un seul agent devait à la fois chercher l'information ET bien la formuler.",
                "apres": (
                    "Deux agents se répartissent le travail : un agent 'chercheur' rassemble "
                    "l'information, puis un agent 'rédacteur' la met en forme claire et "
                    "professionnelle."
                ),
                "entree_defaut": {
                    "prompt": "Rédige un email à un candidat pour lui annoncer qu'il est convoqué à un entretien la semaine prochaine, en précisant les documents à apporter."
                },
                "exemples": [
                    {
                        "label": "Acceptation d'un congé parental",
                        "prompt": "Rédige un email pour confirmer à un salarié l'acceptation de sa demande de congé parental.",
                    }
                ],
            },
            {
                "id": "ecommerce",
                "secteur": "E-commerce / Service client",
                "mise_en_situation": (
                    "La responsable veut maintenant que l'assistant rédige de vrais emails de "
                    "réponse aux clients, pas juste des réponses brutes — une seule 'tête' a du "
                    "mal à bien faire les deux."
                ),
                "avant": "Un seul agent devait à la fois chercher l'information ET bien la formuler.",
                "apres": (
                    "Deux agents se répartissent le travail : un agent 'chercheur' rassemble "
                    "l'information, puis un agent 'rédacteur' la met en forme claire et "
                    "professionnelle."
                ),
                "entree_defaut": {
                    "prompt": "Rédige un email de réponse pour un client qui se plaint que sa commande n'est toujours pas arrivée après 10 jours."
                },
                "exemples": [
                    {
                        "label": "Remboursement d'une commande défectueuse",
                        "prompt": "Rédige un email pour annoncer à un client le remboursement intégral de sa commande défectueuse.",
                    }
                ],
            },
        ],
        "quiz": [
            {
                "question": "Dans un pipeline chercheur + rédacteur, quel est le rôle de l'agent rédacteur ?",
                "options": [
                    "Rassembler les faits bruts en cherchant dans un corpus",
                    "Mettre en forme les informations rassemblées en une réponse claire et professionnelle",
                    "Appeler la calculatrice",
                ],
                "bonne_reponse": 1,
            },
            {
                "question": "Quel est le principal inconvénient d'un pipeline multi-agent par rapport à un agent unique ?",
                "options": [
                    "Il coûte et prend deux fois plus d'appels LLM",
                    "Il ne peut jamais utiliser d'outils",
                    "Il ne fonctionne que sur des questions de calcul",
                ],
                "bonne_reponse": 0,
            },
        ],
    },
]

CAS_DISPONIBLES = [
    {"id": "btp", "secteur": "BTP / Artisan", "icone": "🏗️"},
    {"id": "banque_assurance", "secteur": "Banque / Assurance", "icone": "🏦"},
    {"id": "agriculture", "secteur": "Agriculture", "icone": "🌾"},
    {"id": "rh_juridique", "secteur": "RH / Juridique", "icone": "📋"},
    {"id": "ecommerce", "secteur": "E-commerce / Service client", "icone": "🛒"},
]


def get_briques() -> list[dict]:
    return BRIQUES


def get_cas() -> list[dict]:
    return CAS_DISPONIBLES
