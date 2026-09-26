# "Le Voyage de l'IA" — un seul récit continu qui traverse toutes les familles de modèles
# réellement présentes sur ce site (Catalogue) et les 5 briques du Constructeur, chapitre par
# chapitre. Contenu écrit à la main (pas généré par un LLM à l'exécution) : contrairement au
# Théâtre (épisodes historiques, où une petite variation factuelle importe peu), ce récit
# explique des concepts techniques précis du site — une hallucination ici induirait vraiment
# le visiteur en erreur sur ce qu'il peut essayer ailleurs sur le site.
#
# Réutilise le moteur du Théâtre (personnages, décors, voix Piper) : mêmes clés "clio"/"marco",
# mêmes décors fermés (voir theatre/episodes.py DECORS), mêmes émotions fermées (EMOTIONS).

CHAPITRES = [
    {
        "id": "ouverture",
        "titre": "Qu'est-ce qu'un modèle ?",
        "decor": "plaine_venteuse",
        "schema": [
            {"icone": "❓", "label": "Qu'est-ce qu'un modèle ?"},
            {"icone": "🧩", "label": "Plusieurs familles, pas une seule"},
            {"icone": "🗺️", "label": "Un voyage, une famille à la fois"},
        ],
        "repliques": [
            {"personnage": "marco", "emotion": "joyeux", "texte": "Bienvenue dans l'atelier de l'intelligence artificielle ! Avant de partir, une question, Clio : c'est quoi, pour toi, un modèle d'IA ?"},
            {"personnage": "clio", "emotion": "surprise", "texte": "Un genre de robot qui discute, non ? Comme un chatbot ?"},
            {"personnage": "marco", "emotion": "neutre", "texte": "C'est le premier réflexe, mais c'est trop étroit ! Un modèle, c'est n'importe quel programme entraîné sur des exemples pour reconnaître un motif — parfois du texte, parfois une image, un son, ou même une simple courbe de chiffres."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Alors il n'existe pas qu'un seul type d'IA ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Exactement ! Suis-moi, on va visiter chaque famille l'une après l'autre — et tu pourras toutes les essayer toi-même dans le Catalogue."},
        ],
    },
    {
        "id": "llm_generatif",
        "titre": "Les modèles génératifs (LLM)",
        "decor": "chantier_urbain",
        "schema": [
            {"icone": "💬", "label": "Tout le texte déjà écrit"},
            {"icone": "🧠", "label": "Le LLM prédit UN mot"},
            {"icone": "➕", "label": "Mot ajouté au texte"},
            {"icone": "🔁", "label": "On recommence"},
            {"icone": "✅", "label": "Réponse complète"},
        ],
        "repliques": [
            {"personnage": "marco", "emotion": "neutre", "texte": "Ici, on construit du texte, mot après mot — comme un maçon pose une brique à la fois. C'est un LLM génératif : Llama, Qwen, Mistral, Gemma, ou encore DeepSeek Coder pour le code."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Il écrit un mot, puis il s'arrête pour réfléchir au suivant ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Précisément ! Il regarde tout ce qui est déjà écrit, prédit le mot le plus probable, l'ajoute, et recommence — encore, et encore, jusqu'à la réponse complète."},
            {"personnage": "clio", "emotion": "inquiet", "texte": "Et un modèle plus gros, comme Llama 8B face à Llama 3.2B, construit toujours mieux ?"},
            {"personnage": "marco", "emotion": "neutre", "texte": "Souvent, oui — plus de mémoire pour raisonner sur plusieurs étapes d'un coup. Mais un petit modèle bien choisi reste très utile pour des tâches simples, et bien plus rapide."},
        ],
    },
    {
        "id": "embeddings",
        "titre": "Les embeddings — une carte du sens",
        "decor": "espace_etoiles",
        "schema": [
            {"icone": "💬", "label": "Phrase A"},
            {"icone": "🔢", "label": "Vecteur A"},
            {"icone": "↔️", "label": "Distance mesurée"},
            {"icone": "🔢", "label": "Vecteur B"},
            {"icone": "💬", "label": "Phrase B"},
        ],
        "repliques": [
            {"personnage": "clio", "emotion": "surprise", "texte": "Pourquoi m'emmener dans les étoiles, Marco ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Parce qu'un embedding, c'est exactement ça : transformer une phrase en un point dans un immense espace — une vraie carte du sens, comme Nomic Embed ou Mxbai Embed."},
            {"personnage": "clio", "emotion": "neutre", "texte": "Une carte du sens ?"},
            {"personnage": "marco", "emotion": "neutre", "texte": "Deux phrases qui veulent dire la même chose, même avec des mots différents, atterrissent comme deux étoiles voisines. Deux phrases sans rapport se retrouvent aux deux bouts du ciel."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Et ça sert à quoi, concrètement ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "C'est la base de la recherche par le sens et du RAG — chercher, dans toute une bibliothèque, la bonne étoile sans relire chaque page une par une."},
        ],
    },
    {
        "id": "encodeurs",
        "titre": "Les encodeurs spécialisés",
        "decor": "temple_antique",
        "schema": [
            {"icone": "📄", "label": "Texte entier"},
            {"icone": "🏛️", "label": "Encodeur spécialisé"},
            {"icone": "🏷️", "label": "Une seule étiquette / un seul extrait"},
        ],
        "repliques": [
            {"personnage": "marco", "emotion": "neutre", "texte": "Ce temple abrite des oracles très différents de moi : les encodeurs. CamemBERT, par exemple, ne rédige jamais un seul mot."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Il ne dit rien du tout ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Il lit un texte en entier, puis rend UNE seule réponse fixe : une note de satisfaction, un nom de personne repéré, ou l'extrait exact qui répond à une question — jamais une phrase inventée."},
            {"personnage": "clio", "emotion": "inquiet", "texte": "Ça semble plus rassurant qu'un LLM qui peut se tromper en racontant..."},
            {"personnage": "marco", "emotion": "neutre", "texte": "C'est exactement pourquoi on les utilise en assurance ou en RH : moins polyvalents qu'un LLM, mais bien plus prévisibles et rapides — et ça vaut aussi pour la traduction ou le résumé automatique, deux autres tâches très ciblées."},
        ],
    },
    {
        "id": "vision_audio",
        "titre": "Voir et entendre",
        "decor": "ocean_exploration",
        "schema": [
            {"icone": "🖼️", "label": "Une image"},
            {"icone": "🔊", "label": "ou un son"},
            {"icone": "👁️", "label": "Modèle spécialisé"},
            {"icone": "📝", "label": "Cadre + étiquette, ou texte transcrit"},
        ],
        "repliques": [
            {"personnage": "clio", "emotion": "joyeux", "texte": "Enfin de l'aventure ! On explore quoi, par ici ?"},
            {"personnage": "marco", "emotion": "surprise", "texte": "Les modèles qui ne lisent pas du texte : YOLO regarde une image et entoure chaque objet trouvé d'un cadre, avec une étiquette — utile sur un drone agricole, par exemple."},
            {"personnage": "clio", "emotion": "neutre", "texte": "Et pour le son ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Whisper transforme une voix enregistrée en texte écrit — pratique pour transcrire un appel client avant de le confier à un autre modèle."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Donc l'IA peut voir ET entendre, pas seulement lire !"},
            {"personnage": "marco", "emotion": "neutre", "texte": "Le texte n'est jamais qu'une des portes d'entrée possibles."},
        ],
    },
    {
        "id": "algorithmes_classiques",
        "titre": "Les petits algorithmes malins",
        "decor": "revolution_industrielle",
        "schema": [
            {"icone": "🔢", "label": "Données chiffrées"},
            {"icone": "⚙️", "label": "Algorithme classique"},
            {"icone": "🚨", "label": "Score, anomalie ou recommandation"},
        ],
        "repliques": [
            {"personnage": "marco", "emotion": "neutre", "texte": "Ici, pas de réseau de neurones géant — juste des machines simples et redoutablement efficaces."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Comme quoi, par exemple ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Isolation Forest repère un point anormal dans des vibrations de machine ou des transactions bancaires. Une régression logistique trace une frontière simple pour un scoring de crédit. Une factorisation de matrice devine les goûts d'un client pour lui recommander un produit."},
            {"personnage": "clio", "emotion": "inquiet", "texte": "Simple, mais fiable ?"},
            {"personnage": "marco", "emotion": "neutre", "texte": "Plus interprétable qu'un LLM, même : on peut dire précisément quelle variable a pesé dans la décision. Toute l'IA n'a pas besoin d'être un immense réseau de neurones."},
        ],
    },
    {
        "id": "entrainement",
        "titre": "L'entraînement et la perte",
        "decor": "siege_medieval",
        "schema": [
            {"icone": "📊", "label": "Exemple d'entraînement"},
            {"icone": "🤖", "label": "Le modèle devine"},
            {"icone": "⚖️", "label": "Comparaison à la vraie réponse"},
            {"icone": "📉", "label": "Erreur mesurée (la loss)"},
            {"icone": "🔧", "label": "Réglages ajustés"},
            {"icone": "🔁", "label": "On répète (une epoch)"},
        ],
        "repliques": [
            {"personnage": "clio", "emotion": "inquiet", "texte": "Un siège ? C'est un peu violent pour parler d'entraînement, non ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "C'est pourtant exactement ça : à chaque assaut, le modèle devine une réponse, on la compare à la bonne, et l'écart s'appelle la perte — la loss."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Et il apprend de ses erreurs ?"},
            {"personnage": "marco", "emotion": "neutre", "texte": "Il ajuste un peu ses réglages internes pour se rapprocher de la bonne réponse la prochaine fois. Un assaut complet sur toutes les données, ça s'appelle une epoch — tu peux regarder cette courbe descendre en direct dans le module Entraînement."},
            {"personnage": "clio", "emotion": "joyeux", "texte": "Alors la muraille finit toujours par tomber !"},
            {"personnage": "marco", "emotion": "inquiet", "texte": "Sauf s'il apprend TROP par cœur les mêmes exemples — l'overfitting, le vrai piège : il gagne cette bataille précise, mais serait perdu face à une muraille légèrement différente."},
        ],
    },
    {
        "id": "constructeur",
        "titre": "La guilde des agents",
        "decor": "ville_medievale_sombre",
        "schema": [
            {"icone": "🧠", "label": "LLM seul"},
            {"icone": "📚", "label": "+ RAG"},
            {"icone": "🛠️", "label": "+ Outil (MCP)"},
            {"icone": "🔁", "label": "Agent (boucle ReAct)"},
            {"icone": "🤝", "label": "Multi-agent"},
        ],
        "repliques": [
            {"personnage": "marco", "emotion": "neutre", "texte": "Cette guilde débloque ses savoirs un par un, jamais tous en même temps — exactement comme le parcours du Constructeur."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Par où commence-t-on ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Un LLM seul, d'abord — il répond avec ce qu'il a appris pendant son entraînement général, rien de plus."},
            {"personnage": "clio", "emotion": "inquiet", "texte": "Mais s'il ne connaît pas les documents internes d'une entreprise ?"},
            {"personnage": "marco", "emotion": "neutre", "texte": "On ajoute le RAG : il cherche d'abord le bon passage grâce aux embeddings qu'on a vus tout à l'heure dans les étoiles, puis répond en s'appuyant dessus."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Et s'il doit calculer un montant précis, pas juste chercher un passage ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "On lui donne un vrai outil — une calculatrice exposée en MCP. Puis on le laisse décider LUI-MÊME quel outil utiliser, en boucle : c'est l'agent ReAct."},
            {"personnage": "clio", "emotion": "joyeux", "texte": "Et pour aller encore plus loin ?"},
            {"personnage": "marco", "emotion": "neutre", "texte": "Deux agents qui se répartissent le travail — un chercheur, un rédacteur — c'est le multi-agent. Chaque brique de cette guilde s'appuie sur la précédente, jamais sur du vide."},
        ],
    },
    {
        "id": "conclusion",
        "titre": "À vous de jouer",
        "decor": "plaine_venteuse",
        "schema": [
            {"icone": "🗂️", "label": "Catalogue : essayer chaque modèle"},
            {"icone": "🧪", "label": "Entraînement : voir la loss en direct"},
            {"icone": "🧱", "label": "Constructeur : assembler ses briques"},
        ],
        "repliques": [
            {"personnage": "clio", "emotion": "joyeux", "texte": "Quel voyage ! Des générateurs de texte, une carte du sens, des oracles spécialisés, des yeux et des oreilles artificiels, de petits algorithmes malins, l'entraînement, et la guilde des agents..."},
            {"personnage": "marco", "emotion": "neutre", "texte": "Et ce n'est qu'un aperçu — chaque famille compte plusieurs modèles à essayer soi-même dans le Catalogue, et chaque brique d'agent se construit pas à pas dans le Constructeur."},
            {"personnage": "clio", "emotion": "surprise", "texte": "Et cette histoire, Marco, qui l'a racontée ?"},
            {"personnage": "marco", "emotion": "joyeux", "texte": "Écrite par Claude (Sonnet 5), qui a aussi dessiné ces petits schémas. Nos voix, elles, viennent de Piper, une voix neuronale hébergée ici même, sur ce serveur — aucun de nous deux n'est un service payant."},
            {"personnage": "clio", "emotion": "joyeux", "texte": "Alors à vous de jouer, maintenant !"},
        ],
    },
]


def get_chapitres() -> list[dict]:
    return CHAPITRES
