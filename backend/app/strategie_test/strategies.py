STRATEGIES = [
    {
        "famille": "llm_generatif",
        "titre": "LLM génératif",
        "objectif": (
            "Vérifier que le modèle reste cohérent, factuellement correct et suit bien les "
            "instructions — sans se fier uniquement à la fluidité apparente de sa réponse."
        ),
        "categories_test": [
            {"nom": "Cas nominal", "description": "Une question claire, sans piège, pour vérifier le socle."},
            {"nom": "Robustesse", "description": "La même question reformulée, avec des fautes, dans un style différent — la réponse doit rester équivalente."},
            {"nom": "Factualité", "description": "Une affirmation vérifiable (date, calcul, fait) pour détecter une hallucination."},
            {"nom": "Instructions précises", "description": "Une consigne de forme stricte (longueur, format, langue) pour voir si elle est vraiment respectée."},
            {"nom": "Sécurité", "description": "Une demande à la limite pour vérifier que le modèle refuse ou recadre correctement."},
        ],
        "metriques": ["Taux de réponses correctes sur un jeu de référence", "Taux d'hallucination détecté", "Respect du format demandé"],
        "piege_frequent": (
            "Un LLM peut donner une réponse fluide, bien écrite et pleine d'assurance — tout en étant "
            "factuellement fausse (hallucination). La fluidité n'est jamais une preuve d'exactitude : "
            "toujours vérifier séparément les faits vérifiables (calculs, dates, chiffres)."
        ),
        "cahier_exemple": [
            {"cas": "Calcul en plusieurs étapes", "entree": "Facture de 3h30 à 45€/h + 2h15 à 45€/h, total ?", "attendu": "247,50 €", "constat": "À vérifier à la calculette : les LLM se trompent souvent sur les calculs en plusieurs étapes."},
            {"cas": "Fait vérifiable", "entree": "En quelle année la garantie décennale est-elle devenue obligatoire en France ?", "attendu": "Réponse exacte et sourcée mentalement", "constat": "Vérifier la date réelle — un LLM peut inventer une date plausible mais fausse."},
            {"cas": "Reformulation", "entree": "Même question posée 3 fois avec des mots différents", "attendu": "Réponse équivalente à chaque fois", "constat": "Une réponse qui change de sens selon la formulation révèle une compréhension fragile."},
        ],
    },
    {
        "famille": "embeddings",
        "titre": "Embeddings",
        "objectif": (
            "Vérifier que la similarité mesurée reflète vraiment le SENS des phrases, et pas "
            "seulement les mots qu'elles ont en commun."
        ),
        "categories_test": [
            {"nom": "Synonymes", "description": "Deux phrases formulées différemment mais avec le même sens — score attendu élevé."},
            {"nom": "Négation", "description": "Deux phrases quasi identiques mais dont l'une contient une négation — score attendu faible malgré le vocabulaire commun."},
            {"nom": "Sans rapport", "description": "Deux phrases sur des sujets totalement différents — score attendu proche de 0."},
            {"nom": "Sensibilité à la langue", "description": "Même phrase en français et dans une langue étrangère — vérifier le comportement (le modèle est-il multilingue ?)."},
        ],
        "metriques": ["Similarité cosinus sur des paires étalons", "Corrélation avec un jugement humain sur un échantillon"],
        "piege_frequent": (
            "Deux phrases qui partagent beaucoup de mots mais un sens opposé à cause d'une négation "
            "peuvent être jugées proches à tort par un modèle d'embeddings peu discriminant. Toujours "
            "inclure explicitement des paires avec négation dans le cahier de test."
        ),
        "cahier_exemple": [
            {"cas": "Synonymes", "entree": "« le chat dort » vs « le félin fait la sieste »", "attendu": "Score élevé (> 0.6)", "constat": "Vérifié sur nomic-embed-text : 0.71."},
            {"cas": "Négation piège", "entree": "« le client est satisfait » vs « le client n'est pas satisfait »", "attendu": "Score bas malgré le vocabulaire quasi identique", "constat": "Cas à tester systématiquement — c'est le piège n°1 des embeddings."},
            {"cas": "Sans rapport", "entree": "« réunion reportée » vs « il pleut en Bretagne »", "attendu": "Score proche de 0", "constat": "Sert de calibrage : si ce score est élevé, le modèle est peu fiable."},
        ],
    },
    {
        "famille": "classification_texte",
        "titre": "Classification de texte",
        "objectif": (
            "Vérifier la précision sur des cas clairs ET la robustesse sur des cas ambigus ou "
            "dont la forme diffère de celle des données d'entraînement."
        ),
        "categories_test": [
            {"nom": "Cas nominal", "description": "Phrases longues et non ambiguës, proches du style des données d'entraînement."},
            {"nom": "Cas mitigé", "description": "Phrases contenant à la fois du positif et du négatif — voir quel signal domine."},
            {"nom": "Hors distribution", "description": "Fragments courts, sans verbe, très différents en structure des exemples d'entraînement."},
            {"nom": "Biais de formulation", "description": "Même avis exprimé poliment vs abruptement — la classification doit rester stable."},
        ],
        "metriques": ["Précision / rappel / F1 par classe", "Matrice de confusion"],
        "piege_frequent": (
            "Un modèle entraîné uniquement sur des phrases complètes généralise mal à des fragments "
            "courts sans verbe. Vécu en direct sur ce site : après un entraînement pourtant réussi "
            "(10/10 sur le jeu de test), l'entrée libre « bonne réactivité » a été classée « négatif » "
            "— parce que ce type de fragment très court n'existait dans aucun exemple d'entraînement. "
            "Toujours faire varier la LONGUEUR et la STRUCTURE des phrases de test, pas seulement leur sentiment."
        ),
        "cahier_exemple": [
            {"cas": "Positif clair", "entree": "Le technicien a été très professionnel et à l'écoute.", "attendu": "positif", "constat": "10/10 sur ce type de cas après le fix du taux d'apprentissage."},
            {"cas": "Fragment hors distribution", "entree": "bonne réactivité", "attendu": "positif", "constat": "Obtenu : négatif (61%) — limite réelle observée, documentée ci-dessus."},
            {"cas": "Mitigé", "entree": "Prix correct mais le délai était vraiment long.", "attendu": "Négatif (le regret domine)", "constat": "À surveiller : la partie positive de la phrase peut faire pencher le score."},
        ],
    },
    {
        "famille": "traduction",
        "titre": "Traduction",
        "objectif": "Vérifier la fidélité du sens, la fluidité, et la gestion du vocabulaire technique métier.",
        "categories_test": [
            {"nom": "Phrase simple", "description": "Une phrase courante sans ambiguïté."},
            {"nom": "Jargon métier", "description": "Vocabulaire technique spécifique au secteur (BTP, juridique...)."},
            {"nom": "Expression idiomatique", "description": "Une tournure imagée qui ne se traduit pas mot à mot."},
            {"nom": "Phrase longue", "description": "Plusieurs propositions subordonnées, pour tester la cohérence sur la longueur."},
        ],
        "metriques": ["Score BLEU/chrF si une traduction de référence existe", "Relecture humaine bilingue sur un échantillon"],
        "piege_frequent": (
            "Un modèle de traduction généraliste gère souvent mal le jargon très spécifique à un "
            "métier (ex: termes du bâtiment). Toujours tester avec du vocabulaire métier réel, pas "
            "seulement des phrases génériques de manuel de langue."
        ),
        "cahier_exemple": [
            {"cas": "Phrase professionnelle", "entree": "Veuillez trouver ci-joint le devis signé.", "attendu": "Please find attached the signed estimate.", "constat": "Vérifié sur Helsinki-NLP opus-mt-fr-en, correct."},
            {"cas": "Jargon BTP", "entree": "La garantie décennale couvre le gros œuvre.", "attendu": "Traduction fidèle du terme 'gros œuvre' (structural work), pas une traduction littérale absurde", "constat": "À tester systématiquement sur le vocabulaire métier réel de l'entreprise."},
        ],
    },
    {
        "famille": "resume_automatique",
        "titre": "Résumé automatique",
        "objectif": "Vérifier la fidélité (pas d'invention), la concision, et la conservation des éléments factuels précis.",
        "categories_test": [
            {"nom": "Texte court", "description": "Un paragraphe simple à résumer en une phrase."},
            {"nom": "Texte avec chiffres/dates", "description": "Vérifier que les valeurs précises ne sont pas déformées dans le résumé."},
            {"nom": "Texte multi-sujets", "description": "Plusieurs informations distinctes — le résumé doit couvrir les points clés, pas un seul."},
            {"nom": "Texte long", "description": "Proche de la limite de contexte du modèle."},
        ],
        "metriques": ["Score ROUGE si un résumé de référence existe", "Vérification manuelle de la fidélité factuelle"],
        "piege_frequent": (
            "Les modèles de résumé peuvent légèrement déformer un chiffre, une date ou un pourcentage "
            "sans que cela saute aux yeux à la lecture. Toujours vérifier les éléments factuels précis "
            "un par un, pas seulement le sens général du résumé."
        ),
        "cahier_exemple": [
            {"cas": "Chiffres précis", "entree": "Hausse de 12% du CA, 5 nouveaux points de vente prévus.", "attendu": "Le résumé doit conserver '12%' et '5' exactement", "constat": "Vérifié sur le modèle T5 résumé FR : chiffres conservés."},
            {"cas": "Multi-sujets", "entree": "Compte-rendu couvrant 3 chantiers différents", "attendu": "Le résumé mentionne les 3 chantiers, pas seulement le premier", "constat": "Risque connu : les modèles de résumé ont tendance à privilégier le début du texte."},
        ],
    },
    {
        "famille": "extraction_entites",
        "titre": "Extraction d'entités (NER)",
        "objectif": "Vérifier le rappel (ne rien manquer) et la précision (ne pas inventer d'entités) sur les catégories définies.",
        "categories_test": [
            {"nom": "Entité standard", "description": "Nom de personne, lieu ou organisation bien formé."},
            {"nom": "Ambiguïté de catégorie", "description": "Une entreprise nommée d'après une personne (ex: 'Dupont SARL') — PER ou ORG ?"},
            {"nom": "Texte sans entité", "description": "Un texte neutre sans aucune entité — vérifier l'absence de faux positifs."},
            {"nom": "Entités proches", "description": "Plusieurs entités différentes dans la même phrase."},
        ],
        "metriques": ["Précision / rappel par type d'entité (PER / LOC / ORG)"],
        "piege_frequent": (
            "Les catégories proches se confondent facilement : une entreprise nommée d'après une "
            "personne peut être étiquetée PER au lieu d'ORG. Toujours inclure ces cas ambigus dans "
            "le cahier de test, pas seulement des entités évidentes."
        ),
        "cahier_exemple": [
            {"cas": "Entités multiples", "entree": "Martin Dubois, domicilié à Lyon, représente Artisans du Bâtiment SARL.", "attendu": "PER: Martin Dubois, LOC: Lyon, ORG: Artisans du Bâtiment SARL", "constat": "Vérifié correct sur CamemBERT NER."},
            {"cas": "Ambiguïté ORG/PER", "entree": "Toiture Plus, dirigée par Karim Benali", "attendu": "'Toiture Plus' = ORG malgré la structure proche d'un nom propre", "constat": "Cas à surveiller systématiquement."},
        ],
    },
    {
        "famille": "question_reponse",
        "titre": "Question-réponse extractive",
        "objectif": "Vérifier que la réponse est un extrait EXACT et correct du contexte fourni — jamais inventée.",
        "categories_test": [
            {"nom": "Réponse explicite", "description": "L'information est écrite noir sur blanc dans le contexte."},
            {"nom": "Question sans réponse", "description": "La question porte sur une info absente du contexte — le modèle doit-il le signaler ?"},
            {"nom": "Réponse composite", "description": "La réponse nécessite de combiner deux informations séparées du texte."},
        ],
        "metriques": ["Exact match / F1 sur les tokens de la réponse"],
        "piege_frequent": (
            "Face à une question dont la réponse n'existe PAS dans le contexte, un modèle extractif "
            "renvoie souvent quand même le passage le plus proche lexicalement, au lieu de signaler "
            "l'absence de réponse. Toujours tester ce cas explicitement — c'est le test le plus révélateur."
        ),
        "cahier_exemple": [
            {"cas": "Réponse explicite", "entree": "Contexte : la garantie dure 2 ans. Question : combien de temps dure la garantie ?", "attendu": "2 ans", "constat": "Vérifié correct sur CamemBERT QA."},
            {"cas": "Sans réponse", "entree": "Contexte : la garantie dure 2 ans. Question : quel est le prix du produit ?", "attendu": "Le modèle devrait signaler l'absence de réponse", "constat": "À tester : beaucoup de modèles extractifs renvoient un passage au hasard plutôt que d'admettre l'absence de réponse."},
        ],
    },
    {
        "famille": "detection_langue",
        "titre": "Détection de langue",
        "objectif": "Vérifier la robustesse sur les textes courts et les langues proches.",
        "categories_test": [
            {"nom": "Texte long", "description": "Un paragraphe entier dans une langue — cas facile."},
            {"nom": "Texte très court", "description": "Quelques mots seulement — la fiabilité chute fortement."},
            {"nom": "Langues proches", "description": "Espagnol/portugais, danois/norvégien — risque de confusion élevé."},
            {"nom": "Mélange de langues", "description": "Une phrase contenant deux langues différentes."},
        ],
        "metriques": ["Précision par langue", "Matrice de confusion entre langues proches"],
        "piege_frequent": (
            "Sur un texte très court (1-2 mots), presque tous les détecteurs de langue perdent en "
            "fiabilité. Toujours afficher un score de confiance à l'utilisateur, et tester "
            "explicitement la longueur minimale à partir de laquelle le modèle reste fiable."
        ),
        "cahier_exemple": [
            {"cas": "Texte clair", "entree": "Hola, quisiera saber el estado de mi pedido.", "attendu": "es (espagnol)", "constat": "Vérifié correct sur py3langid, confiance 100%."},
            {"cas": "Texte très court", "entree": "Sí", "attendu": "Confiance faible attendue (mot trop court)", "constat": "À tester : un mot unique peut exister dans plusieurs langues."},
        ],
    },
    {
        "famille": "vision_detection",
        "titre": "Détection d'objets (vision)",
        "objectif": (
            "Détecter tous les objets pertinents (rappel) sans en inventer (précision), et rester "
            "robuste aux conditions réelles (angle, luminosité, occlusion)."
        ),
        "categories_test": [
            {"nom": "Image nette", "description": "Objets bien visibles, bon éclairage — cas de référence."},
            {"nom": "Occlusion", "description": "Objets partiellement masqués par un autre élément."},
            {"nom": "Petits objets / loin", "description": "Objets de petite taille dans l'image."},
            {"nom": "Mauvaise qualité", "description": "Image floue, mal éclairée, ou avec un angle inhabituel."},
            {"nom": "Absence d'objet cible", "description": "Image ne contenant aucun objet de la catégorie recherchée."},
        ],
        "metriques": ["Précision / rappel par classe", "mAP (mean Average Precision)", "IoU des boîtes englobantes"],
        "piege_frequent": (
            "Un modèle entraîné sur des photos prises au sol généralise souvent mal à une vue "
            "aérienne (drone) — l'angle change radicalement l'apparence des objets. Toujours tester "
            "avec des images qui reflètent le VRAI contexte d'usage final, pas seulement des images "
            "génériques du jeu d'entraînement d'origine du modèle."
        ),
        "cahier_exemple": [
            {"cas": "Image de référence", "entree": "Photo générique avec bus et piétons", "attendu": "Détection du bus + des personnes", "constat": "Vérifié sur YOLOv8n : bus et personnes détectés avec confiance > 0.85."},
            {"cas": "Vue aérienne (cas d'usage réel)", "entree": "Photo prise par un drone en hauteur", "attendu": "À vérifier spécifiquement — modèle générique non entraîné sur ce type de vue", "constat": "Non testé sur ce catalogue — modèle générique, à valider avant tout usage drone réel."},
        ],
    },
    {
        "famille": "vision_classification",
        "titre": "Classification d'image",
        "objectif": "Vérifier si la bonne catégorie ressort en top-1, ou au moins dans le top-5.",
        "categories_test": [
            {"nom": "Image typique", "description": "Une image représentative et sans ambiguïté de la classe recherchée."},
            {"nom": "Classes proches", "description": "Deux catégories visuellement similaires (ex: deux variétés de plantes malades)."},
            {"nom": "Hors catégories connues", "description": "Une image dont la vraie classe n'existe pas dans le modèle."},
        ],
        "metriques": ["Précision top-1", "Précision top-5"],
        "piege_frequent": (
            "Un modèle générique (entraîné sur ImageNet) classera une maladie de plante spécifique "
            "dans une catégorie générique proche mais fausse, car cette maladie n'existe simplement "
            "pas dans ses catégories d'origine. Toujours vérifier que les catégories cibles existent "
            "VRAIMENT dans le modèle avant de l'utiliser en production."
        ),
        "cahier_exemple": [
            {"cas": "Image générique", "entree": "Photo d'exemple bundlée", "attendu": "Catégorie ImageNet plausible en top-5", "constat": "Vérifié sur YOLOv8n-cls."},
            {"cas": "Cas d'usage réel (agriculture)", "entree": "Photo d'une feuille malade spécifique", "attendu": "Catégorie précise de maladie", "constat": "Non couvert par ce modèle générique — nécessiterait un modèle spécialisé type PlantVillage."},
        ],
    },
    {
        "famille": "audio_transcription",
        "titre": "Transcription audio",
        "objectif": "Vérifier l'exactitude du texte transcrit (taux d'erreur de mots) et la robustesse au bruit et à l'accent.",
        "categories_test": [
            {"nom": "Voix claire", "description": "Enregistrement studio, sans bruit — cas de référence."},
            {"nom": "Bruit de fond", "description": "Environnement bruyant (chantier, rue, open-space)."},
            {"nom": "Accent régional", "description": "Locuteurs avec des accents différents du français standard."},
            {"nom": "Vocabulaire technique", "description": "Termes métier spécifiques, noms propres."},
        ],
        "metriques": ["Word Error Rate (WER) — taux d'erreur de mots"],
        "piege_frequent": (
            "Un même modèle transcrit très différemment selon la qualité du micro et le bruit "
            "ambiant. Toujours tester avec un enregistrement réel du contexte final d'usage (ex: un "
            "appel client sur chantier bruyant), pas seulement un enregistrement studio propre."
        ),
        "cahier_exemple": [
            {"cas": "Échantillon standard", "entree": "Échantillon audio anglais du jeu de test Whisper", "attendu": "Transcription fidèle", "constat": "Vérifié sur Whisper tiny : transcription correcte."},
            {"cas": "Cas d'usage réel", "entree": "Message vocal client sur fond de chantier", "attendu": "À tester spécifiquement avant tout déploiement", "constat": "Non couvert par l'échantillon de démonstration — à valider avec de vrais enregistrements terrain."},
        ],
    },
    {
        "famille": "series_temporelles",
        "titre": "Prévision de séries temporelles",
        "objectif": "Vérifier la qualité de la prévision et la fiabilité de l'intervalle de confiance associé.",
        "categories_test": [
            {"nom": "Court terme", "description": "Prévoir le mois suivant — cas le plus fiable."},
            {"nom": "Long terme", "description": "Prévoir loin dans le futur — l'incertitude doit grandir visiblement."},
            {"nom": "Rupture de tendance", "description": "Le modèle s'adapte-t-il à un changement brutal, ou reste-t-il bloqué sur l'ancienne tendance ?"},
            {"nom": "Comparaison à une baseline naïve", "description": "Comparer à une simple moyenne ou dernière valeur connue."},
        ],
        "metriques": ["MAE / RMSE (erreur moyenne)", "Couverture de l'intervalle de confiance"],
        "piege_frequent": (
            "Sans historique suffisant, un modèle de prévision peut se contenter de prédire la "
            "moyenne globale — ce qu'on observe littéralement dans la colonne « avant entraînement » "
            "du module Entraînement de ce site. Toujours comparer la prévision du modèle à cette "
            "baseline naïve pour vérifier qu'il apporte vraiment quelque chose de plus."
        ),
        "cahier_exemple": [
            {"cas": "Baseline naïve", "entree": "Prévoir le mois 19 sans aucun apprentissage", "attendu": "Moyenne globale (~11 081 €)", "constat": "Observé en direct sur ce site — confirme le comportement attendu d'un modèle non entraîné."},
            {"cas": "Modèle entraîné", "entree": "Prévoir le mois 19 après entraînement", "attendu": "Suit la tendance réelle (~14 000 €)", "constat": "Vérifié : 14 051 € obtenu, cohérent avec la tendance +320€/mois."},
        ],
    },
    {
        "famille": "anomalie",
        "titre": "Détection d'anomalie",
        "objectif": "Détecter les vraies anomalies (rappel) sans générer trop de fausses alertes (précision).",
        "categories_test": [
            {"nom": "Anomalie évidente", "description": "Valeur extrême, très éloignée de la normale."},
            {"nom": "Anomalie subtile", "description": "Valeur légèrement hors norme, plus difficile à détecter."},
            {"nom": "Donnée normale mais rare", "description": "Une valeur normale mais peu fréquente — ne doit pas être signalée à tort."},
            {"nom": "Dérive progressive", "description": "Un changement lent dans le temps, pas un pic isolé."},
        ],
        "metriques": ["Précision / rappel", "Taux de faux positifs (coût d'une fausse alerte)"],
        "piege_frequent": (
            "Le seuil de sensibilité (paramètre 'contamination') change radicalement le nombre "
            "d'alertes générées. Toujours tester PLUSIEURS seuils et discuter avec le métier le bon "
            "compromis entre rater une vraie panne et multiplier les fausses alertes."
        ),
        "cahier_exemple": [
            {"cas": "Anomalie évidente", "entree": "Mesure vibratoire à 1.4 (normale ~0.5)", "attendu": "Détectée comme anomalie", "constat": "Vérifié sur Isolation Forest maintenance."},
            {"cas": "Fraude transactionnelle", "entree": "Transaction de 2450€ (moyenne ~45€)", "attendu": "Détectée comme anomalie", "constat": "Vérifié sur Isolation Forest fraude bancaire."},
        ],
    },
    {
        "famille": "classification_classique",
        "titre": "Classification classique (algorithmes traditionnels)",
        "objectif": "Vérifier la précision globale, mais aussi l'explicabilité (quelle variable pèse dans la décision).",
        "categories_test": [
            {"nom": "Cas clair", "description": "Dossier nettement bon ou nettement à risque."},
            {"nom": "Cas limite", "description": "Dossier proche de la frontière de décision."},
            {"nom": "Variable manquante/aberrante", "description": "Une donnée d'entrée absente ou incohérente."},
            {"nom": "Performance par sous-groupe", "description": "Vérifier que la précision ne cache pas un biais sur une catégorie de dossiers."},
        ],
        "metriques": ["Précision / rappel", "AUC-ROC", "Importance des variables"],
        "piege_frequent": (
            "Un modèle peut avoir une bonne précision globale tout en se trompant systématiquement "
            "sur un sous-groupe particulier (biais caché par la moyenne). Toujours vérifier la "
            "performance PAR sous-catégorie, jamais seulement en moyenne globale."
        ),
        "cahier_exemple": [
            {"cas": "Dossier à risque", "entree": "Revenu 1900€, endettement 45%, 2 incidents", "attendu": "Probabilité de risque élevée", "constat": "Vérifié sur le scoring crédit."},
            {"cas": "Cas limite", "entree": "Dossier proche du seuil de décision", "attendu": "Probabilité proche de 50%", "constat": "À tester systématiquement — c'est là que les erreurs sont les plus fréquentes."},
        ],
    },
    {
        "famille": "recommandation",
        "titre": "Recommandation",
        "objectif": "Vérifier la pertinence des recommandations, leur diversité, et la gestion des nouveaux utilisateurs/produits sans historique.",
        "categories_test": [
            {"nom": "Utilisateur avec historique", "description": "Beaucoup de notes passées — cas le plus favorable."},
            {"nom": "Cold start", "description": "Nouvel utilisateur ou nouveau produit sans aucun historique."},
            {"nom": "Diversité", "description": "Le système ne recommande-t-il que la même catégorie encore et encore ?"},
        ],
        "metriques": ["Précision@k / Rappel@k", "Diversité des recommandations"],
        "piege_frequent": (
            "Un système de recommandation peut s'enfermer dans une « bulle de filtre » — toujours "
            "recommander la même catégorie déjà appréciée, sans jamais proposer de découverte. "
            "Toujours mesurer la diversité, pas seulement la pertinence brute des recommandations."
        ),
        "cahier_exemple": [
            {"cas": "Utilisateur avec historique", "entree": "Utilisateur ayant noté 3 films d'action", "attendu": "Recommandation cohérente avec ses goûts", "constat": "Vérifié sur le modèle NMF recommandation."},
            {"cas": "Cold start", "entree": "Nouvel utilisateur sans aucune note", "attendu": "Recommandation par défaut (les plus populaires)", "constat": "Non géré explicitement dans ce catalogue — limite connue des systèmes par factorisation de matrice."},
        ],
    },
]


def get_strategies() -> list[dict]:
    return STRATEGIES
