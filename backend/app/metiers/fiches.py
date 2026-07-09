METIERS = [
    {
        "id": "artisan_batiment",
        "titre": "Artisan du bâtiment",
        "secteur": "BTP / Artisanat",
        "icone": "🔨",
        "description": (
            "Plombier, électricien, maçon, couvreur... L'IA ne remplace pas le métier, mais peut "
            "absorber les tâches répétitives autour du chantier : trier les avis, répondre aux "
            "questions courantes, anticiper la trésorerie."
        ),
        "cas_usage": [
            {
                "titre": "Trier automatiquement les avis clients",
                "description": (
                    "Un modèle entraîné en quelques secondes classe chaque avis en positif/négatif, "
                    "pour prioriser les réponses aux clients mécontents sans tout relire soi-même."
                ),
                "page": "/entrainement",
                "texte_lien": "Essayer le scénario « Trier des avis clients » →",
            },
            {
                "titre": "Répondre aux questions sur les devis et garanties, 24h/24",
                "description": (
                    "Un assistant qui va chercher la réponse dans vos vrais documents (conditions de "
                    "garantie, modalités de paiement) plutôt que d'inventer une réponse approximative."
                ),
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant RAG documentaire » →",
            },
            {
                "titre": "Anticiper la trésorerie des prochains mois",
                "description": "À partir de l'historique de facturation, un modèle simple prévoit la tendance du chiffre d'affaires à venir.",
                "page": "/entrainement",
                "texte_lien": "Essayer le scénario « Prévoir le chiffre d'affaires » →",
            },
        ],
    },
    {
        "id": "commerce",
        "titre": "Commerçant / e-commerce",
        "secteur": "Commerce / Distribution",
        "icone": "🛍️",
        "description": (
            "Boutique physique ou en ligne : l'IA aide à filtrer le bruit (spam, fraude) et à mieux "
            "orienter chaque client vers ce qui l'intéresse vraiment."
        ),
        "cas_usage": [
            {
                "titre": "Filtrer les emails de spam et de phishing",
                "description": "Un algorithme classique (pas de réseau de neurones) apprend en quelques secondes à distinguer un email légitime d'une tentative d'arnaque.",
                "page": "/entrainement",
                "texte_lien": "Essayer le scénario « Filtrer les emails indésirables » →",
            },
            {
                "titre": "Recommander des produits pertinents",
                "description": "À partir de l'historique d'achats ou de notes, un système de recommandation propose des produits cohérents avec les goûts du client.",
                "page": "/catalogue",
                "texte_lien": "Voir le modèle de recommandation dans le Catalogue →",
            },
            {
                "titre": "Détecter une transaction suspecte",
                "description": "Un modèle de détection d'anomalie repère les montants ou comportements très différents de l'habitude d'un client, sans règle fixe écrite à l'avance.",
                "page": "/catalogue",
                "texte_lien": "Voir Isolation Forest (fraude) dans le Catalogue →",
            },
        ],
    },
    {
        "id": "agriculture",
        "titre": "Agriculteur / agroalimentaire",
        "secteur": "Agriculture / Agroalimentaire",
        "icone": "🌾",
        "description": (
            "De la maintenance du matériel au suivi des cultures, l'IA aide à repérer un problème "
            "tôt — à condition de rester honnête sur les limites d'un modèle générique non spécialisé."
        ),
        "cas_usage": [
            {
                "titre": "Repérer une machine qui va tomber en panne",
                "description": "Un modèle de maintenance prédictive détecte une vibration ou une température anormale avant la panne réelle, à partir des données du capteur.",
                "page": "/catalogue",
                "texte_lien": "Voir Isolation Forest (maintenance) dans le Catalogue →",
            },
            {
                "titre": "Classer une photo de plante ou de culture",
                "description": (
                    "Un modèle de vision générique peut classer une image, mais ne connaît pas les "
                    "maladies spécifiques d'une culture — une vraie limite à connaître avant tout usage réel."
                ),
                "page": "/catalogue",
                "texte_lien": "Voir la classification d'image dans le Catalogue →",
            },
            {
                "titre": "Prévoir un volume ou une tendance sur plusieurs mois",
                "description": "Un modèle de prévision de séries temporelles projette une tendance à partir d'un historique, avec un intervalle de confiance qui s'élargit avec l'horizon.",
                "page": "/catalogue",
                "texte_lien": "Voir Chronos (prévisions) dans le Catalogue →",
            },
        ],
    },
    {
        "id": "profession_liberale",
        "titre": "Profession libérale / indépendant",
        "secteur": "Services professionnels",
        "icone": "⚖️",
        "description": (
            "Comptable, juriste, consultant... beaucoup de temps passé à lire, résumer et retrouver "
            "une information précise dans des documents longs — exactement ce que le RAG et le "
            "résumé automatique adressent."
        ),
        "cas_usage": [
            {
                "titre": "Résumer un long rapport ou contrat",
                "description": "Un document trop long pour être lu en entier est découpé, résumé morceau par morceau, puis synthétisé en un seul paragraphe cohérent.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Résumé hiérarchique » →",
            },
            {
                "titre": "Retrouver une réponse exacte dans un document",
                "description": "Un modèle de question-réponse extractive renvoie le passage exact du contexte fourni — jamais une réponse inventée.",
                "page": "/catalogue",
                "texte_lien": "Voir CamemBERT Question-Réponse dans le Catalogue →",
            },
            {
                "titre": "Traduire un document pour un client à l'étranger",
                "description": "Une traduction suivie d'une seconde passe de vérification, utile avant l'envoi d'un contenu contractuel ou technique à un client international.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Traduction assistée avec double vérification » →",
            },
        ],
    },
    {
        "id": "ressources_humaines",
        "titre": "Ressources humaines / recrutement",
        "secteur": "Services professionnels",
        "icone": "🧑‍💼",
        "description": "Répondre aux questions répétitives des salariés, préparer une offre d'emploi ou un entretien — des tâches rédactionnelles qui se prêtent bien à l'IA.",
        "cas_usage": [
            {
                "titre": "Rédiger une offre d'emploi ou des questions d'entretien",
                "description": "Deux agents collaborent : l'un rassemble les critères du poste, l'autre rédige le texte final.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant recrutement » →",
            },
            {
                "titre": "Répondre aux questions des nouveaux salariés",
                "description": "Un assistant documentaire répond aux questions courantes (congés, télétravail, arrêt maladie) à partir du livret d'accueil officiel.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant RH onboarding » →",
            },
            {
                "titre": "Extraire les informations clés d'un CV",
                "description": "Un modèle d'extraction d'entités repère automatiquement les noms de personnes, d'entreprises et de lieux dans un texte.",
                "page": "/catalogue",
                "texte_lien": "Voir CamemBERT NER dans le Catalogue →",
            },
        ],
    },
    {
        "id": "commercial",
        "titre": "Commercial / relation client",
        "secteur": "Services professionnels",
        "icone": "🤝",
        "description": "Préparer un appel, comprendre un message dans une langue inconnue, vérifier une réponse avant de l'envoyer — des gestes du quotidien commercial que l'IA peut accélérer.",
        "cas_usage": [
            {
                "titre": "Préparer un appel grâce à l'historique client",
                "description": "Un agent consulte l'historique disponible avant de préparer un argumentaire de relance personnalisé.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant commercial (CRM) » →",
            },
            {
                "titre": "Détecter la langue d'un message client international",
                "description": "Un détecteur de langue identifie automatiquement la langue d'un message, y compris sur un texte assez court.",
                "page": "/catalogue",
                "texte_lien": "Voir la détection de langue dans le Catalogue →",
            },
            {
                "titre": "Vérifier une réponse avant de l'envoyer",
                "description": "Le modèle rédige un brouillon, puis une seconde passe le relit et corrige si besoin — utile avant l'envoi d'une réponse sensible à un client.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Vérificateur / auto-critique » →",
            },
        ],
    },
    {
        "id": "restauration_hotellerie",
        "titre": "Restauration / hôtellerie",
        "secteur": "Commerce / Distribution",
        "icone": "🍽️",
        "description": (
            "Entre les avis en ligne, une clientèle parfois internationale et une affluence qui varie "
            "fortement selon le jour, ce secteur a beaucoup à gagner d'une IA qui reste à sa juste place."
        ),
        "cas_usage": [
            {
                "titre": "Trier les avis clients sur la cuisine et le service",
                "description": "Un modèle entraîné en quelques secondes classe chaque avis en positif/négatif, pour repérer vite un problème récurrent plutôt que de tout relire.",
                "page": "/entrainement",
                "texte_lien": "Essayer le scénario « Trier des avis clients » →",
            },
            {
                "titre": "Traduire un menu pour une clientèle internationale",
                "description": "Une traduction rapide du français vers l'anglais, à relire avant impression — utile pour un menu ou une affiche saisonnière.",
                "page": "/catalogue",
                "texte_lien": "Voir Helsinki-NLP (traduction) dans le Catalogue →",
            },
            {
                "titre": "Anticiper l'affluence pour mieux planifier le personnel",
                "description": "Un modèle de prévision de séries temporelles projette une tendance à partir de l'historique de fréquentation, pour ajuster les plannings à l'avance.",
                "page": "/catalogue",
                "texte_lien": "Voir Chronos (prévisions) dans le Catalogue →",
            },
        ],
    },
    {
        "id": "secretariat_medical",
        "titre": "Secrétariat médical / cabinet de santé",
        "secteur": "Santé / Social",
        "icone": "🏥",
        "description": (
            "Ici l'IA reste strictement administrative — jamais de diagnostic : elle absorbe la paperasse "
            "et l'accueil pour laisser plus de temps au soin lui-même."
        ),
        "cas_usage": [
            {
                "titre": "Transcrire un message vocal de patient",
                "description": "Un message laissé sur le répondeur du cabinet est transformé en texte, pour être traité aussi vite qu'un email plutôt que d'être réécouté en entier.",
                "page": "/catalogue",
                "texte_lien": "Voir Whisper Tiny (transcription) dans le Catalogue →",
            },
            {
                "titre": "Répondre aux questions administratives courantes",
                "description": "Horaires, pièces à apporter, modalités de prise de rendez-vous : un assistant documentaire répond à partir des vraies informations du cabinet plutôt que d'inventer une réponse.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant RAG documentaire » →",
            },
            {
                "titre": "Orienter un patient étranger vers un interprète",
                "description": "Un détecteur de langue identifie automatiquement la langue d'un message écrit, pour orienter vite vers la bonne ressource.",
                "page": "/catalogue",
                "texte_lien": "Voir la détection de langue dans le Catalogue →",
            },
        ],
    },
    {
        "id": "travailleur_social",
        "titre": "Travailleur social / associatif",
        "secteur": "Santé / Social",
        "icone": "🤲",
        "description": (
            "Beaucoup de dossiers longs à synthétiser et de questions répétitives sur les aides et "
            "démarches — du temps administratif qui peut être en partie repris par l'IA, sans jamais "
            "remplacer le jugement humain sur une situation sensible."
        ),
        "cas_usage": [
            {
                "titre": "Résumer un dossier long avant une réunion de synthèse",
                "description": "Un dossier trop long pour être relu en entier est découpé, résumé morceau par morceau, puis synthétisé en un seul paragraphe cohérent.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Résumé hiérarchique » →",
            },
            {
                "titre": "Répondre aux questions fréquentes sur les aides et démarches",
                "description": "Un assistant documentaire va chercher la réponse dans les vraies fiches d'information de la structure plutôt que d'approximer.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant RAG documentaire » →",
            },
            {
                "titre": "Rédiger un compte-rendu d'entretien",
                "description": "Deux agents se répartissent le travail : l'un rassemble les points clés évoqués, l'autre les met en forme dans un compte-rendu clair.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Pipeline multi-agent » →",
            },
        ],
    },
    {
        "id": "enseignant_formateur",
        "titre": "Enseignant / formateur",
        "secteur": "Éducation / Formation",
        "icone": "🎓",
        "description": (
            "Préparer un cours, l'adapter à un public varié, gagner du temps sur la correction — autant "
            "de tâches où l'IA peut aider, à condition de toujours vérifier ce qu'elle propose."
        ),
        "cas_usage": [
            {
                "titre": "Générer des questions de révision sur un thème donné",
                "description": "Un modèle génératif propose rapidement plusieurs questions à partir d'un thème de cours, à relire et ajuster avant de les distribuer.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « LLM seul (référence) » →",
            },
            {
                "titre": "Résumer un support de cours trop long",
                "description": "Un document découpé en morceaux, résumé partie par partie, puis synthétisé — utile pour préparer une fiche de révision condensée.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Résumé hiérarchique » →",
            },
            {
                "titre": "Traduire un support pour un élève allophone",
                "description": "Une première traduction suivie d'une seconde passe de vérification, avant de la donner telle quelle à un élève.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Traduction assistée avec double vérification » →",
            },
        ],
    },
    {
        "id": "agent_immobilier",
        "titre": "Agent immobilier",
        "secteur": "Immobilier",
        "icone": "🏠",
        "description": (
            "Rapprocher des biens, répondre vite aux questions sur un mandat, rédiger une annonce qui "
            "donne envie — des tâches très concrètes que l'IA peut accélérer sans remplacer la visite."
        ),
        "cas_usage": [
            {
                "titre": "Retrouver des biens au style architectural proche",
                "description": "Une photo de façade est transformée en vecteur qui capture son style visuel, pour comparer des biens par ressemblance plutôt que par mots-clés.",
                "page": "/catalogue",
                "texte_lien": "Voir ResNet-18 (similarité visuelle) dans le Catalogue →",
            },
            {
                "titre": "Répondre aux questions sur un mandat de vente",
                "description": "Un assistant documentaire répond à partir des vraies clauses du mandat plutôt que d'improviser une réponse.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant RAG documentaire » →",
            },
            {
                "titre": "Rédiger une première version d'annonce",
                "description": "Un modèle génératif propose un texte d'annonce à partir des caractéristiques du bien, à relire et personnaliser avant publication.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « LLM seul (référence) » →",
            },
        ],
    },
    {
        "id": "logistique_transport",
        "titre": "Logisticien / transporteur",
        "secteur": "Transport / Logistique",
        "icone": "🚚",
        "description": (
            "Anticiper les volumes, retrouver vite une information sur un bon de livraison papier, "
            "repérer un retard inhabituel — l'IA appliquée aux flux plutôt qu'aux personnes."
        ),
        "cas_usage": [
            {
                "titre": "Anticiper les volumes à traiter dans un entrepôt",
                "description": "Un modèle de prévision de séries temporelles projette une tendance à partir de l'historique, avec un intervalle qui s'élargit avec l'horizon.",
                "page": "/catalogue",
                "texte_lien": "Voir Chronos (prévisions) dans le Catalogue →",
            },
            {
                "titre": "Extraire les informations d'un bon de livraison scanné",
                "description": "Le texte d'un document (références, quantités) est extrait automatiquement plutôt que ressaisi à la main.",
                "page": "/catalogue",
                "texte_lien": "Voir Tesseract OCR dans le Catalogue →",
            },
            {
                "titre": "Repérer un délai de livraison anormal",
                "description": "Un modèle de détection d'anomalie signale un délai qui sort nettement de l'habitude, sans règle de seuil fixée à l'avance.",
                "page": "/catalogue",
                "texte_lien": "Voir Isolation Forest (détection d'anomalie) dans le Catalogue →",
            },
        ],
    },
    {
        "id": "agent_collectivite",
        "titre": "Agent de collectivité / service public",
        "secteur": "Secteur public / Collectivité",
        "icone": "🏛️",
        "description": (
            "Répondre aux administrés, filtrer les demandes sensibles, traduire pour un public non "
            "francophone — avec une exigence de fiabilité et de traçabilité particulièrement forte."
        ),
        "cas_usage": [
            {
                "titre": "Répondre aux questions administratives courantes",
                "description": "Horaires, démarches, pièces à fournir : un assistant documentaire s'appuie sur les vraies fiches pratiques de la collectivité.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Assistant RAG documentaire » →",
            },
            {
                "titre": "Filtrer les demandes sensibles avant traitement",
                "description": "Un filtre de modération vérifie la requête avant de la laisser continuer, avec un lien conditionnel qui bloque réellement la suite en cas de contenu inapproprié.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Filtre de modération avant réponse » →",
            },
            {
                "titre": "Traduire un message pour un administré non francophone",
                "description": "Une traduction suivie d'une seconde passe de vérification, utile avant l'envoi d'une information officielle.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « Traduction assistée avec double vérification » →",
            },
        ],
    },
    {
        "id": "maintenance_industrielle",
        "titre": "Technicien de maintenance industrielle",
        "secteur": "Industrie",
        "icone": "🔧",
        "description": (
            "Anticiper une panne, retrouver vite une référence sur un document papier, transcrire un "
            "rapport d'intervention oral — la maintenance prédictive appliquée au terrain."
        ),
        "cas_usage": [
            {
                "titre": "Repérer un four qui dérive avant la panne",
                "description": "Un modèle de détection d'anomalie apprend en direct sur les mesures de température d'un four industriel, pour repérer un écart avant l'incident.",
                "page": "/catalogue",
                "texte_lien": "Voir Isolation Forest (four industriel) dans le Catalogue →",
            },
            {
                "titre": "Transcrire un rapport d'intervention oral",
                "description": "Un compte-rendu dicté sur le terrain est transformé en texte exploitable, sans ressaisie manuelle a posteriori.",
                "page": "/catalogue",
                "texte_lien": "Voir Whisper Tiny (transcription) dans le Catalogue →",
            },
            {
                "titre": "Extraire une référence sur une plaque ou un bon fournisseur",
                "description": "Le texte d'une photo de document ou d'étiquette est extrait automatiquement plutôt que retapé à la main.",
                "page": "/catalogue",
                "texte_lien": "Voir Tesseract OCR dans le Catalogue →",
            },
        ],
    },
    {
        "id": "securite_travail",
        "titre": "Sécurité au travail / HSE",
        "secteur": "Industrie",
        "icone": "🦺",
        "description": (
            "La vision par ordinateur appliquée à la prévention : repérer une posture à risque ou un "
            "équipement de sécurité absent sur une photo, en complément (jamais à la place) d'une vraie "
            "démarche de prévention humaine."
        ),
        "cas_usage": [
            {
                "titre": "Détecter une posture à risque sur une photo de poste de travail",
                "description": "Un modèle d'estimation de pose repère les points clés du corps (dos courbé en manutention, par exemple), base de nombreux usages de sécurité au travail.",
                "page": "/catalogue",
                "texte_lien": "Voir YOLOv8 (estimation de pose) dans le Catalogue →",
            },
            {
                "titre": "Vérifier la présence d'équipements sur une image",
                "description": "Un modèle de détection localise les personnes et objets visibles sur une photo — utile comme brique de base avant d'aller plus loin sur un cas d'usage métier précis.",
                "page": "/catalogue",
                "texte_lien": "Voir YOLOv8 (détection) dans le Catalogue →",
            },
            {
                "titre": "Rédiger un rapport d'incident à partir de notes brutes",
                "description": "Un modèle génératif met en forme des notes éparses en un rapport structuré, à relire avant diffusion.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « LLM seul (référence) » →",
            },
        ],
    },
    {
        "id": "accessibilite",
        "titre": "Accessibilité / assistance aux personnes",
        "secteur": "Services professionnels",
        "icone": "♿",
        "description": (
            "L'IA au service de l'autonomie : lire un document à voix haute, transcrire un échange, "
            "simplifier un texte administratif — des briques simples mais concrètement utiles au quotidien."
        ),
        "cas_usage": [
            {
                "titre": "Lire un document à voix haute pour une personne malvoyante",
                "description": "Un moteur de synthèse vocale convertit un texte libre en audio — léger et quasi instantané, avec une voix plus robotique qu'un moteur neuronal moderne.",
                "page": "/catalogue",
                "texte_lien": "Voir eSpeak NG (synthèse vocale) dans le Catalogue →",
            },
            {
                "titre": "Transcrire un échange pour une personne malentendante",
                "description": "Un signal audio est transformé en texte lisible en direct, pour suivre une conversation ou une réunion.",
                "page": "/catalogue",
                "texte_lien": "Voir Whisper Tiny (transcription) dans le Catalogue →",
            },
            {
                "titre": "Simplifier un texte administratif complexe",
                "description": "Un modèle génératif reformule un texte juridique ou technique en langage courant, à vérifier avant de le transmettre tel quel.",
                "page": "/constructeur",
                "texte_lien": "Voir le template « LLM seul (référence) » →",
            },
        ],
    },
]


def get_metiers() -> list[dict]:
    return METIERS
