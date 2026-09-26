import os


class Settings:
    ollama_url: str = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
    data_dir: str = os.environ.get("IAEASY_DATA_DIR", "/data")
    hf_cache_dir: str = os.environ.get("HF_HOME", "/data/hf_cache")
    # Pas de valeur par défaut en dur ici : ce dépôt est public, le mot de passe ne vit que dans
    # un fichier .env non versionné sur le serveur. Vide = panneau admin inaccessible.
    admin_password: str = os.environ.get("IAEASY_ADMIN_PASSWORD", "")
    # URL interne (réseau docker proxy-net, pas le tunnel Cloudflare public) du formulaire n8n
    # "TKonsulting - Post Instagram via prompt" — passer par le réseau docker plutôt que par le
    # tunnel évite le timeout ~10s déjà rencontré côté Cloudflare sur d'autres appels longs (voir
    # l'assistant CE Haiku), alors que cet appel (Ollama + Instagram) prend couramment 30-90s.
    n8n_instagram_url: str = os.environ.get(
        "N8N_INSTAGRAM_URL", "http://n8n:5678/form/cb743df1-9c97-4617-beca-221321dfc0f5"
    )
    # Workflow n8n séparé (lecture seule) qui récupère les indicateurs d'engagement d'un post
    # déjà publié — voir backend/app/instagram/router.py /insights.
    n8n_instagram_insights_url: str = os.environ.get(
        "N8N_INSTAGRAM_INSIGHTS_URL", "http://n8n:5678/webhook/instagram-insights"
    )
    # Workflow n8n (carrousel) : chaque enfant du carrousel est une URL d'image publique que les
    # serveurs de Meta doivent pouvoir récupérer — réseau docker interne pour l'appeler depuis
    # iaeasy, mais les URLs d'images elles-mêmes doivent être le domaine public (voir
    # public_base_url), pas ce réseau interne.
    n8n_instagram_carrousel_url: str = os.environ.get(
        "N8N_INSTAGRAM_CARROUSEL_URL", "http://n8n:5678/webhook/instagram-carrousel"
    )
    # Domaine public par lequel les serveurs de Meta atteignent les images de slides générées à
    # la volée (contrairement à la banque de templates, hébergée sur tkonsulting.fr).
    public_base_url: str = os.environ.get("IAEASY_PUBLIC_BASE_URL", "https://iaeasy.noschoixpourvous.com")
    # Workflow n8n (story) — pas de légende côté API Instagram pour une story, juste une image.
    n8n_instagram_story_url: str = os.environ.get(
        "N8N_INSTAGRAM_STORY_URL", "http://n8n:5678/webhook/instagram-story"
    )
    # Workflow n8n (reel) — 3 webhooks séparés car le traitement vidéo par Meta est asynchrone :
    # créer le conteneur, vérifier son état (à interroger plusieurs fois), publier une fois prêt.
    # Le token d'accès reste uniquement côté n8n (jamais dans iaeasy), comme pour les autres formats.
    n8n_instagram_reel_creer_url: str = os.environ.get(
        "N8N_INSTAGRAM_REEL_CREER_URL", "http://n8n:5678/webhook/instagram-reel-creer"
    )
    n8n_instagram_reel_statut_url: str = os.environ.get(
        "N8N_INSTAGRAM_REEL_STATUT_URL", "http://n8n:5678/webhook/instagram-reel-statut"
    )
    n8n_instagram_reel_publier_url: str = os.environ.get(
        "N8N_INSTAGRAM_REEL_PUBLIER_URL", "http://n8n:5678/webhook/instagram-reel-publier"
    )
    # Workflow n8n (lecture seule) qui récupère les commentaires réels d'un post déjà publié —
    # capter les réactions des visiteurs, pas seulement les compteurs agrégés de /insights.
    n8n_instagram_commentaires_url: str = os.environ.get(
        "N8N_INSTAGRAM_COMMENTAIRES_URL", "http://n8n:5678/webhook/instagram-commentaires"
    )
    # Workflow n8n (messages privés) — 3 webhooks : lister les conversations, lire les messages
    # d'une conversation, envoyer une réponse. Toujours déclenché par un humain qui lit et écrit
    # chaque réponse depuis l'IHM — jamais de réponse automatique envoyée par l'IA elle-même.
    n8n_instagram_dm_conversations_url: str = os.environ.get(
        "N8N_INSTAGRAM_DM_CONVERSATIONS_URL", "http://n8n:5678/webhook/instagram-dm-conversations"
    )
    n8n_instagram_dm_messages_url: str = os.environ.get(
        "N8N_INSTAGRAM_DM_MESSAGES_URL", "http://n8n:5678/webhook/instagram-dm-messages"
    )
    n8n_instagram_dm_envoyer_url: str = os.environ.get(
        "N8N_INSTAGRAM_DM_ENVOYER_URL", "http://n8n:5678/webhook/instagram-dm-envoyer"
    )
    # Workflow n8n (instantané du compte) — abonnés, portée et visites de profil du jour ;
    # capturé et archivé une fois par jour pour construire une vraie courbe de croissance dans le
    # temps (Instagram ne conserve pas cet historique de façon interrogeable directement).
    n8n_instagram_compte_url: str = os.environ.get(
        "N8N_INSTAGRAM_COMPTE_URL", "http://n8n:5678/webhook/instagram-compte"
    )
    # Destinations réelles des liens "en bio" — Instagram autorise plusieurs liens externes sur un
    # compte pro/créateur (jusqu'à 5), donc chacun a sa propre route trackée /lien-bio/<cle> :
    # comparer combien de clics va vers tkonsulting.fr vs lesensia.com, pas juste un total global.
    lien_bio_url_tkonsulting: str = os.environ.get("LIEN_BIO_URL_TKONSULTING", "https://tkonsulting.fr")
    lien_bio_url_lesensia: str = os.environ.get("LIEN_BIO_URL_LESENSIA", "https://lesensia.com")
    lien_bio_url_iaeasy: str = os.environ.get("LIEN_BIO_URL_IAEASY", "https://iaeasy.noschoixpourvous.com")
    # Utilisée uniquement pour les textes Instagram (légendes, accroches, plans de carrousel) —
    # un vrai modèle de copywriting rend un texte nettement moins générique qu'un petit 7B local
    # sur ce genre de format court, pour un coût marginal (quelques centimes par génération).
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    # Workflow n8n (lecture seule) — derniers médias publiés, pour l'aperçu embarqué sur
    # tkonsulting.fr (section dédiée) plutôt qu'un lien externe qui peut casser (identifiant
    # erroné, compte renommé...). Résultat mis en cache et rafraîchi en fond (voir
    # router.py:_boucle_derniers_posts_auto), jamais interrogé en direct par le site public.
    n8n_instagram_derniers_posts_url: str = os.environ.get(
        "N8N_INSTAGRAM_DERNIERS_POSTS_URL", "http://n8n:5678/webhook/instagram-derniers-posts"
    )


settings = Settings()

os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.hf_cache_dir, exist_ok=True)
os.environ.setdefault("HF_HOME", settings.hf_cache_dir)
