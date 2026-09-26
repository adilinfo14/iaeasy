# HANDOFF — iaeasy (plateforme pédagogique IA souveraine)

Rédigé le 2026-09-26 à partir de : mémoire `project_iaeasy.md`, journal de session (2026-07-07 -> 2026-07-24 pour la
partie iaeasy) et vérifications en lecture seule sur `confia-vm` le 2026-09-26.
Ne pas confondre avec **IA Challenge** (app de quiz, autre dossier `/home/adil/ia-challenge`, autre HANDOFF).

**Aucun secret dans ce document.** Identifiants : dans les `.env` du serveur, Vaultwarden, ou à redéfinir.

## 1. But du projet & contexte

- **Pour qui** : Adil Tsouli Kamal (TKonsulting, Lyon). Public visé : apprenants / professionnels qui veulent comprendre
  l'IA en la manipulant, sans jargon. Outil « académique », très graphique, presque no-code.
- **Pourquoi** : montrer que l'on peut faire de l'IA **100 % souveraine** (modèles open source auto-hébergés via Ollama,
- **Démarrage** : 2026-07-07, séparé de ConfIA. Demande initiale : « tester une centaine de modèles selon leur domaine,
  chacun avec description pédagogique + cas d'usage, puis passer à l'entraînement avec courbe de loss, puis un
  constructeur d'agents ».

### En ligne (vérifié aujourd'hui, HTTP 200)
- **https://iaeasy.noschoixpourvous.com** (conteneur `iaeasy`, « Up 3 weeks », redémarré le 2026-09-04) ;
  `/api/health` répond `{"status":"ok"}`.
- Chiffres réels de l'API : **75 modèles** au catalogue (35 le 2026-07-09), **20 templates** de constructeur,
  **13 composants**, **92 termes** de glossaire, **17 métiers**, **3 scénarios** d'entraînement.
- Routes frontend (extraites du bundle compilé) : `/` (Accueil), `/catalogue`, `/entrainement`, `/parcours`,
  `/constructeur`, `/simulateur`, `/strategie-test`, `/securite`, `/glossaire`, `/metiers`, `/videos`, `/theatre`,
  `/voyage`, `/brief-ia`, `/quiz-eclair`, `/mon-parcours`, `/avis`, `/instagram` (protégé), `/agents/chasseur-mission`
  (protégé), `/admin` (protégé, volontairement absent du menu).
- **NocoDB** : https://nocodb.noschoixpourvous.com (200) — pilotage des agents (voir §3.6).
- **Open WebUI** : https://ia.noschoixpourvous.com (200), conteneur `openwebui` « healthy » — **pré-existant**, du stack
  `/home/ia-souveraine` (avec `ollama` et chromadb). Pas construit par ce projet, mais il partage le même Ollama.

### Fonctionnalités LIVRÉES (par ordre chronologique)
- 2026-07-07/08 : Catalogue (19 -> 35 modèles), Entraînement (3 scénarios, avant/après, test du modèle entraîné),
  Parcours (5 briques débloquables, 5 contextes sectoriels), Constructeur (canvas React Flow, 20 templates classés en
  5 catégories, 13 briques, liens conditionnels réels sur Modération, config éditable par nœud, inspecteur d'artefact),
  Stratégie de tests (21 familles, ~1676 cas), Glossaire, « Mon métier », Simulateur (4 familles comparables :
  LLM génératif 7 modèles ~46 critères en 5 catégories, embeddings, classification classique, vision), quiz + badges,
  assistant d'aide flottant (chat ancré sur le glossaire), avis 5 étoiles, thème « doux » par défaut, menu en
  sous-menus, durcissement sécurité, mobile.
- 2026-07-09 : Vidéos, Sécurité IA (OWASP LLM Top 10), résilience mobile (jobs + SSE), panneau `/admin`.
- 2026-07-10 : **Théâtre de l'Histoire** (`/theatre`) : Clio et Marco, personnages SVG animés, 5 épisodes écrits à la
  main + génération à la demande par qwen2.5:7b-instruct (16 sujets réels tirés au sort), voix neuronale **Piper**
  auto-hébergée (voix `fr_FR-siwis-medium` / `fr_FR-tom-medium`, dans `/data/piper_voices`), émotions par réplique.
- 2026-07-10/11 : **Voyage de l'IA** (`/voyage`, 9 chapitres en récit continu Clio/Marco).
- 2026-07-10 -> 13 : **Module Instagram** (`/instagram`, 1461 lignes de router) pour le compte `@tkonsulting` :
  légendes générées (Claude via API pour le texte, garde-fou de ton), aperçu avant publication, historique,
  carrousels, stories, reels (musiques libres, effets), planificateur, tableau de bord d'engagement, commentaires,
  messages privés (réponse toujours humaine), courbe de croissance du compte, liens « en bio » trackés
  (`/api/instagram/lien-bio/<cle>`), aperçu embarqué des derniers posts sur tkonsulting.fr. Tout passe par des
  workflows **n8n** (conteneur `n8n`), le token Meta ne vit que côté n8n.
- 2026-07-12/13 : **Brief IA** (`/brief-ia`) : pipeline de génération de brief d'animation commerciale avec validation
  humaine ; **réécrit sur Ollama** (qwen2.5:7b-instruct) après une première version LangGraph + Vertex AI/Gemini jugée
  disproportionnée (compte GCP facturé). État en attente de validation gardé en mémoire (perdu au redémarrage).
- 2026-07-13 : audit de cohérence du site (8 bugs corrigés, 19 définitions de glossaire réécrites), « Lot 1 » de 6
  fonctions : barre de progression persistante, durées estimées, favoris, `/mon-parcours` (historique perso),
  `/quiz-eclair`, bac à sable libre.
- 2026-07-19/20 : catalogue enrichi de 35 à 75 modèles (nouveautés : génération d'image `sd-turbo`, détecteurs de
  texte/image générés par IA, `deepfake-detector-visage`, OCR manuscrit TrOCR, toxicité, correction grammaticale...),
  « 5 exemples à essayer » par modèle sans texte (limité à 3 modèles : `tesseract-ocr`, `yolo-classification`,
  `yolo-classification-small` — la suite n'a pas été demandée), page d'accueil enrichie (« Notre conviction » sur
  la maîtrise de la connaissance).
- 2026-07-20/21 : **Chasseur de mission** (`/agents/chasseur-mission`) : recherche à la demande via l'API Claude
  (outil serveur `web_search`), stockage des missions dans `/data/chasseur_mission.json`, graphiques (dataviz).
  22 missions réelles saisies au départ. Timeout de l'appel porté à 15 min, 6 recherches web max.
- 2026-07-21 : **Moteur d'agents orchestré par NocoDB** (`agents-engine`, voir §3.6).

### CASSÉ / INCOMPLET / À RISQUE
1. **Code non versionné (le plus grave).** Voir §3.2 : dernier commit `73626d4` le 2026-07-10 ; tout ce qui précède
   (Voyage, Instagram, Brief IA, Chasseur de mission, catalogue 75, etc.) n'existe **que** sur le disque de `confia-vm`.
2. **Instagram : cache « derniers posts » et instantané quotidien du compte en échec** depuis (au moins) le démarrage du
   2026-09-04 (423 lignes `WARNING [instagram] échec du rafraîchissement des derniers posts` dans les logs). Cause
   **non diagnostiquée** — hypothèse la plus probable : token d'accès Meta expiré (créé vers 2026-07-10, durée de vie
   limitée) ; ou workflow n8n désactivé. À vérifier (§6).
3. **Pas de sauvegarde** connue du volume `iaeasy_iaeasy_data` (avis, progression, historiques Instagram, missions,
   réglages, 31 Go de cache HuggingFace). Aucun cron iaeasy dans `crontab -l` (à vérifier côté système).
4. Agents NocoDB : seul le déclenchement manuel (`lancer_maintenant`) est branché ; `planification_cron` existe mais
   n'est pas implémenté. Deux agents sur six (Veille réglementaire facturation électronique, Prospection clients drone)
   n'ont pas de trace de test dans le journal (à vérifier).
5. Le récit des épisodes générés du Théâtre a été durci (validation stricte) mais la fiabilité du tag `emotion` généré
   n'a jamais été re-testée à grande échelle. Rendu visuel (Théâtre, mobile) jamais vérifié à l'écran par Claude.


### 3.1 Vue d'ensemble
```
Internet -> Cloudflare Tunnel (cloudflared, service systemd sur confia-vm)
         -> 127.0.0.1:80 -> conteneur proxy-nginx (vhost iaeasy.conf) -> conteneur iaeasy:8000 (FastAPI + SPA React)
                                                                       -> ollama:11434 (réseau docker proxy-net)
                                                                       -> n8n:5678 (webhooks Instagram)
                                                                       -> API Anthropic (Instagram, Chasseur) — sortie internet
```
- Serveur : **`confia-vm`** (hostname `adil-VMware20-1`, SSH sans mot de passe : `ssh confia-vm`), homelab VMware.
  Toutes les apps y partagent CPU/RAM : un test lourd ralentit tout (voir §5).
- Stack : FastAPI (Python 3.11) + React 18/Vite/TS + `@xyflow/react` + recharts. Un seul process uvicorn mono-worker.

### 3.2 Dépôt git
- Dossier : `/home/adil/iaeasy` (branche `main`). Remotes : `origin` = `https://github.com/adilinfo14/iaeasy.git`
  et `iaeasy2026` = `https://github.com/adilinfo14/iaeasy-2026.git`.
- `git log` : HEAD = `73626d4` (2026-07-10 15:11, « fix(theatre): histoire générée incohérente ») ; **identique** à
  `origin/main` et `iaeasy2026/main` (0 commit d'écart dans les deux sens).
- **Arbre de travail non commité (état 2026-09-26)** : 36 fichiers modifiés (+6337 / -968 lignes) et 94 fichiers non
  suivis. Détail :
  - *Modifiés* : `.gitignore` (ajout `secrets/`, `.claude/settings.local.json`), `backend/Dockerfile` (+`ffmpeg`),
    `backend/requirements.txt` (+`diffusers`, `Pillow`, `langgraph`, `langchain-core`, `langchain-google-vertexai` ;
    les 3 dernières sont **devenues inutiles** depuis la réécriture du Brief IA sur Ollama), `docker-compose.yml`
  - *Non suivis (nouveaux modules)* : `backend/app/{brief_ia,chasseur_mission,instagram,voyage}/`,
    `core/anthropic_client.py`, `catalogue/runners/{handwriting,image_generation}_runner.py`,
    `frontend/src/components/{SketchIcone.tsx,voyage/}`, pages `BriefIA`, `ChasseurMission`, `Instagram`,
    `MonParcours`, `QuizEclair`.
  - **Piège pour le commit** : `backend/app/instagram/musiques/` pèse **335 Mo** de MP3 (avec un `LICENCE.md`) et
    `instagram/polices/` 2 Mo. À traiter avant `git add` (Git LFS, ou exclure et documenter la source des fichiers).
  - Le `.env` du serveur n'a jamais été dans l'historique git (vérifié le 2026-07-09).

### 3.3 Conteneurs et ports (état réel)
| Conteneur | Image / origine | Rôle | Notes |
|---|---|---|---|
| `iaeasy` | `iaeasy-iaeasy` (build local, 5,5 Go, créée 2026-07-21) | App FastAPI + SPA | port 8000 interne uniquement, réseau `proxy-net`, `cap_drop: ALL`, `no-new-privileges`, root |
| `agents-engine` | `agents-engine-agents-engine` | Moteur d'agents piloté par NocoDB | « Up 5 weeks », docker.sock monté en lecture seule |
| `openwebui` | `ghcr.io/open-webui/open-webui:latest` (même stack) | UI de chat sur Ollama | https://ia.noschoixpourvous.com ; pas géré par iaeasy |
| `proxy-nginx` | `nginx:stable` (stack `/home/proxy`) | Reverse proxy | vhosts dans `/home/proxy/nginx/conf.d/` (**hors git**) |
| `n8n` | — | Workflows Instagram (webhooks) | atteint par `http://n8n:5678` |
| `nocodb` + `nocodb_postgres` | `/home/adil/nocodb` | Base « Agents » | vhost `nocodb.conf` |

Modèles Ollama présents (`docker exec ollama ollama list`) : `qwen2.5:7b-instruct` (et alias `qwen2.5:7b`),
`llama3:8b`, `llama3.2:3b`, `mistral:7b-instruct`, `gemma2:2b`, `phi3:mini`, `deepseek-coder:6.7b`,
`nomic-embed-text`, `all-minilm`, `mxbai-embed-large`, plus `llama3.1:70b-instruct-q4_K_M` (42 Go, **volontairement
exclu** de la liste blanche du site).

### 3.4 Structure du code (`/home/adil/iaeasy`)
- `docker-compose.yml` : service `iaeasy`, `OLLAMA_URL=http://ollama:11434`, `IAEASY_DATA_DIR=/data`, `HF_HOME=/data/hf_cache`,
  `IAEASY_ADMIN_PASSWORD` et `ANTHROPIC_API_KEY` lues dans `/home/adil/iaeasy/.env` (non versionné, droits 600). Volume
  `iaeasy_iaeasy_data` sur `/data` ; bind mount **lecture seule** `./backend/app:/app/app`.
- `backend/Dockerfile` : build Vite puis Python 3.11 (`tesseract-ocr-fra`, `espeak-ng`, `ffmpeg`), uvicorn `--reload`.
- `backend/app/` : un dossier par module (`catalogue`+`runners/`, `training`, `agents`, `simulateur`, `aide`, `theatre`,
  `voyage`, `brief_ia`, `chasseur_mission`, `instagram`, `admin`, `glossaire`, `metiers`, `strategie_test`, `avis`,
  `videos`, `securite`, `progress`, `stats`, `core` = config, `jobs.py` JobStore+SSE, `ollama_client`, `reglages`,
  `anthropic_client`). `frontend/src/` : `pages/`, `components/`, `api/client.ts`, `styles.css` (thèmes sombre/« doux »).
- Données dans `/data` : fichiers JSON (`avis`, `badges`, `progression`, `visiteurs`, `reglages`, `chasseur_mission`,
  `instagram_*`), dossiers `instagram_{carrousels,stories,reels}/`, `piper_voices/`, `hf_cache/` (31 Go). **Pas de SQL.**

### 3.5 nginx (hors dépôt !)
Fichier `/home/proxy/nginx/conf.d/iaeasy.conf` : zones `limit_req` (général 10 r/s ; « lourd » 6 r/min ; admin 5 r/min),
`client_max_body_size 2M`, en-têtes de sécurité dont une **CSP stricte** (`script-src 'self' 'unsafe-inline'`,
`img-src 'self' data: https://tkonsulting.fr`, `media-src 'self' data: blob:`, `frame-src` YouTube nocookie),
locations dédiées avec `proxy_buffering off` et timeouts longs pour les flux SSE (`/api/simulateur/comparer/*/stream`
600 s, `/api/brief-ia/*/stream` 600 s), `/api/instagram/publier` (180 s). **Ce fichier n'est dans aucun dépôt git** :
le sauvegarder (voir §6).

### 3.6 Moteur d'agents (`/home/adil/agents-engine`, **pas de dépôt git**)
- Fichiers : `moteur.py` (138 lignes), `Dockerfile` (python 3.12-slim + `httpx` + `docker`), `docker-compose.yml`,
  `.env` (600). Créé le 2026-07-21.
- Fonctionnement : boucle de 60 s ; interroge la table `agents` de NocoDB (`actif = true` **et**
  `lancer_maintenant = true`), exécute l'agent puis écrit une ligne dans la table `executions`
  (`agent_nom`, `statut`, `resultat`, `erreur`, `horodatage`), puis remet `lancer_maintenant` à faux.
- 3 types : `veille_web` (API Claude + outil `web_search`, max 8 recherches), `monitoring_homelab` (lit l'état des
  conteneurs via le SDK docker, ne remonte que les anormaux), `contenu_tkonsulting` (texte sans recherche). Le modèle
  est codé en dur dans `moteur.py` (`MODELE`).
- 6 agents en base : Veille concurrentielle SaaS BTP, Veille réglementaire facturation électronique, Prospection
  clients drone, Veille technique personnelle, Monitoring homelab intelligent, Générateur de contenu TKonsulting.
  Chaque déclenchement = un vrai appel API payant (centimes à ~20 centimes selon recherche web).
- Variables du `.env` d'agents-engine (noms seulement) : `ANTHROPIC_API_KEY`, `NOCODB_URL`, `NOCODB_TOKEN`, `NOCODB_BASE_ID`,
  `NOCODB_TABLE_AGENTS`, `NOCODB_TABLE_EXECUTIONS`. Valeurs : dans ce `.env` ; compte NocoDB : à redéfinir / Vaultwarden.
- **Cloudflare / NocoDB** : la route `nocodb.noschoixpourvous.com` se gère dans le dashboard Cloudflare Zero Trust
  (Networks -> Tunnels -> Public Hostname) : Type HTTP, URL `127.0.0.1:80`. Voir piège §5.

### 3.7 Intégrations externes
- **API Anthropic** : légendes Instagram (`core/anthropic_client.py`) et recherche de missions ; clé dans
  `/home/adil/iaeasy/.env` et `/home/adil/agents-engine/.env`.
- **n8n -> Meta Graph API** : workflows Instagram (formulaire, carrousel, story, reel créer/statut/publier, insights,
  commentaires, DM x3, compte, derniers-posts). Token Meta : uniquement dans n8n.
- **Nextcloud « Recherche+ »** (`search_hub`) : cron 04:30 sur confia-vm
  (`docker exec --user www-data nextcloud php .../search_hub/iaeasy_index.php`, log `/home/adil/search-hub-iaeasy.log`)
  indexe 8 endpoints iaeasy : `/api/catalogue`, `/api/agents/templates`, `/api/agents/composants`,
  `/api/training/scenarios`, `/api/glossaire`, `/api/metiers`, `/api/securite`, `/api/videos`. **Ne pas renommer/retirer
  leurs champs** (`id`, `nom`, `titre`, `terme`, `description`) sans mettre à jour le connecteur.

## 4. Exploitation

Toutes les commandes se lancent depuis le poste d'Adil via `ssh confia-vm '...'` (pas de sudo possible pour Claude).

**Santé**
```bash
ssh confia-vm 'docker ps --format "{{.Names}} {{.Status}}" | grep -E "iaeasy|agents-engine|ollama|openwebui|n8n|nocodb|proxy-nginx"'
ssh confia-vm 'curl -s localhost/api/health -H "Host: iaeasy.noschoixpourvous.com"'      # {"status":"ok"}
ssh confia-vm 'docker logs --tail 50 iaeasy'
ssh confia-vm 'docker logs --tail 30 agents-engine'
ssh confia-vm 'docker exec ollama ollama list'
```

**Déployer un changement backend Python** (bind mount + `--reload`, pas de rebuild) : copier les fichiers dans
`/home/adil/iaeasy/backend/app/` (ex. `tar czf - -C backend app | ssh confia-vm 'tar xzf - -C /home/adil/iaeasy/backend'`)
puis, en cas de doute, `ssh confia-vm 'docker restart iaeasy'`. **Attention** : ne jamais écraser en bloc un dossier qui
contient du travail non commité (voir incident §5). Comparer d'abord avec `git status` sur le serveur.

**Déployer un changement frontend ou `requirements.txt`/`Dockerfile`** (rebuild obligatoire, 5-10 min ; 20-40 min si
le cache est invalidé) :
```bash
ssh confia-vm 'cd /home/adil/iaeasy && docker compose build iaeasy && docker compose up -d iaeasy'
# vérifier l'artefact réel plutôt que la mention CACHED :
ssh confia-vm 'docker run --rm iaeasy-iaeasy sh -c "grep -c <chaine-litterale> /app/static/assets/*.js"'
```

**nginx** (après modification de `/home/proxy/nginx/conf.d/iaeasy.conf`) :
`ssh confia-vm 'docker exec proxy-nginx nginx -t && docker exec proxy-nginx nginx -s reload'`

**Agents** : `cd /home/adil/agents-engine && docker compose up -d --build`. Déclenchement : cocher `lancer_maintenant`
dans NocoDB (base « Agents », table `agents`), résultat dans la table `executions` sous ~60 s (jusqu'à 1-2 min pour une
veille web).

**Sauvegarde (à mettre en place — n'existe pas)** : exemple d'export du volume sans le cache HF :
```bash
ssh confia-vm 'docker run --rm -v iaeasy_iaeasy_data:/data -v /home/adil/backups:/b alpine \
  tar czf /b/iaeasy_data_$(date +%F).tgz --exclude=data/hf_cache -C / data'
```
Y ajouter `/home/proxy/nginx/conf.d/iaeasy.conf`, `/home/adil/iaeasy/.env`, `/home/adil/agents-engine/` et un dump NocoDB.
Modèle existant à imiter : `/home/adil/nextcloud-backup.sh` (cron 03:45, rsync vers VPS IONOS).

**Panneau admin** : `/admin` (URL tapée à la main), mot de passe = variable `IAEASY_ADMIN_PASSWORD` du `.env` serveur
(le même gate protège aussi `/instagram` et `/agents/chasseur-mission`). Il règle en direct 4 paramètres du chatbot
(`/data/reglages.json`).

## 5. Décisions clés & pièges rencontrés (à ne pas refaire)

**Déploiement / infra**
- **Ne jamais déployer en écrasant `client.ts`, `App.tsx`, `styles.css`** depuis une copie locale : le 2026-07-12 cela a
  écrasé le travail non commité de « Brief IA » construit directement sur la VM (reconstruit ensuite à la main).
  Toujours partir de l'état du serveur (`git status`/`git diff` sur `confia-vm`) et **commiter souvent** : c'est
  pourquoi le retard de commit actuel est dangereux.
- Un `CACHED` de BuildKit ne signifie pas « obsolète » : vérifier le contenu de l'image avant de lancer `--no-cache`
  (20-40 min perdues). Grepper une chaîne littérale (classe CSS, fragment d'URL), pas un nom de fonction
  minifié.
- **Cloudflare Tunnel coupe vers ~10 s d'inactivité** : tout endpoint long (comparaison LLM, chat, génération de
  Théâtre, recherche de missions, Brief IA) doit être un job en tâche de fond (`core/jobs.py`) + SSE ou poll, jamais
  une réponse bloquante. Et nginx : `proxy_buffering off` sur les flux SSE.
- Tunnel : le champ « Service » de la route doit être **HTTP `127.0.0.1:80`** (pas `https://…:443`). Une route en
  **double** pour un même hostname (ancienne + nouvelle) fait que l'ancienne gagne (vécu avec `nocodb`). Changer la
  config dans le dashboard peut exiger `sudo systemctl restart cloudflared` sur la VM (interdit à Claude, à faire par Adil).
- **CSP** : toute ressource embarquée doit être ajoutée explicitement (`media-src ... blob:` pour la voix Piper,
  `data:` pour l'audio Whisper, `frame-src` YouTube, `img-src https://tkonsulting.fr`). Symptôme = contrôles présents,
  rien ne se passe.

**Ollama / modèles**
- **Liste blanche `_MODELES_AUTORISES`** (`agents/engine.py`) : tout modèle ajouté au Simulateur ou au Constructeur
  doit aussi y figurer, sinon repli silencieux sur le défaut. À garder synchronisé avec `_MODELES` (simulateur) et
- CPU pur : toujours plafonner `num_predict` (~300) ; un 7B sans plafond peut durer des minutes.
- **Scripts de test lancés par `docker exec` puis tués côté client peuvent laisser une génération Ollama orpheline**
  (4300 % CPU pendant 30 min ; réglé par `docker restart ollama`). Préférer tester via l'endpoint HTTP avec timeout. Avant
  de conclure « bloqué », vérifier que le CPU cumulé reste FIXE sur un intervalle (un modèle « chaud » a un cumul élevé
  normal).
- Assistant d'aide : ancrer sur le glossaire filtré (max 5 termes, pas les 92 d'un coup) sinon hallucinations ; imposer le français.
- Fiabilité : un endpoint qui répond 200 ne prouve rien ; refaire tourner un entraînement plusieurs fois et vérifier
  les prédictions (fix sentiment : `learning_rate=2e-5`, warmup, `seed=42`, 10 époques).
- Dépendances : `sentencepiece` ET `protobuf` requis ; ne pas installer `torchcodec` (casse l'audio) ; `fasttext`
  incompatible numpy 2 -> `py3langid` ; BARThez cassé -> `plguillou/t5-base-fr-sum-cnndm` ; `requirements.txt` non épinglé
  (torch a déjà bougé, non-régression à revérifier après tout rebuild). Poids HF volumineux parfois bloqués à 0 % sur le
  réseau du homelab (PyTorch Hub a fonctionné à la place) ; TrOCR a été cassé par l'auto-upgrade de transformers 5.14.

**Constructeur**
- Le payload d'exécution doit venir du même état que l'affichage (bug `config: {}` envoyé pour tous les nœuds).
- `verification` régénère son propre brouillon depuis son `prompt` : uniquement en nœud terminal, jamais après un
  générateur (le contexte amont serait ignoré). `base_vectorielle` sans amont retombe sur un petit corpus de démo.
- `fitView` de React Flow ne s'applique qu'au montage : appeler explicitement via `ReactFlowProvider`.
- Les templates sont servis dynamiquement (`/api/agents/templates`) : ajouter un template = sync backend seule.
  Valider par script que chaque `node.type`/`edge`/`exemple.valeurs` est cohérent avant de déployer.

**Sécurité**
- App publique sans authentification : chaque endpoint coûteux est un vecteur d'abus (bornes calculatrice, 3 entraînements
  concurrents max, plafond 20 nœuds/40 arêtes, longueurs max, CORS restreint, `/docs` désactivé, rate-limits nginx).
- Le mot de passe admin ne doit vivre que dans le `.env` serveur (dépôt public). Comparaison à temps constant.

**Contenu / UX / Instagram**
- Piège UX : `<button>` carte -> `color` explicite ; `hidden` + `display` inconditionnel = clics bloqués ; iPhone : pas de `window.confirm()`, police >= 16 px sur les inputs ; valider chaque sortie d'agent générée en masse (JSON, clés, doublons).
- Instagram : ratio d'image 4:5 à 1,91:1 ; compte réel `@tkonsulting` ; appels sur `graph.instagram.com` ; Tailwind de tkonsulting.fr = bundle figé.
- Chasseur : jamais de scraping LinkedIn ; DroneConnect/Rekrute/Indeed en usage ponctuel ; aucune API/RSS n'existe.

## 6. Reste à faire / idées en suspens (priorisé)

1. **[Urgent] Sauvegarder le travail non commité** : décider du sort des 335 Mo de MP3 (LFS / hors dépôt), sortir les
2. **[Urgent] Sauvegarde des données** (`iaeasy_iaeasy_data` hors `hf_cache`, `iaeasy.conf`, `.env`, `agents-engine/`,
   dump NocoDB) sur le modèle du cron Nextcloud.
3. **Diagnostiquer Instagram** : `docker logs iaeasy | grep instagram`, tester un webhook n8n, contrôler l'état/expiration
   du token Meta dans n8n ; le régénérer si expiré ; vérifier que les workflows n8n sont actifs.
5. Nettoyer `requirements.txt` (`langgraph`, `langchain-core`, `langchain-google-vertexai` inutiles) — un rebuild est
   nécessaire ; en profiter pour épingler torch/transformers.
6. Mettre à jour README et docs (75 modèles, 20 templates, modules réels) : rituel d'Adil après chaque fonctionnalité.
7. Agents NocoDB : implémenter `planification_cron` (champ existant, non branché), tester les 2 agents non validés,
   ajouter les 3 idées écartées (sur 10 proposées : 1,3,4,7,8,9 retenues), éventuellement un dépôt git pour le moteur.
8. Divers (chasseur : critères pilotables depuis l'IHM ; « 5 exemples » aux ~30 modèles sans texte restants) : convertir `comparer-embeddings/classification/vision` en job+SSE si leur durée grossit ; vérification visuelle
    réelle du Théâtre/mobile ; 2e vague de catalogue (traduction Helsinki, NER dates) en pause (blocage réseau HF) ;
    conteneur non-root ; 14 des 20 idées du 2026-07-13 non construites (e-mail, export PDF, recherche indexée, modération).

## 7. Reprendre avec Claude

**Prompt d'amorçage (à coller dans une nouvelle session)** :
```
Je reprends le projet « iaeasy » (plateforme pédagogique IA souveraine, https://iaeasy.noschoixpourvous.com), hébergé
sur mon homelab : SSH `ssh confia-vm`, dossier /home/adil/iaeasy, conteneur docker `iaeasy` (FastAPI + React), Ollama
dans le conteneur `ollama`. Lis d'abord HANDOFF/iaeasy.md, puis vérifie en lecture seule : `git status` et `git log`
dans /home/adil/iaeasy (beaucoup de travail n'est PAS commité), `docker ps`, `docker logs --tail 50 iaeasy`.
Ne confonds pas avec IA Challenge (app de quiz, autre dossier). Règles : réponds en français, ne recopie jamais de
secret, ne déploie jamais en écrasant des fichiers sans comparer avec l'état du serveur, teste tout via les vrais
endpoints avant de conclure. Première mission : sécuriser le code non commité (voir section 6, point 1), puis
diagnostiquer les échecs Instagram (cache « derniers posts »).
```

- `agents-engine` et `iaeasy` : clés API Anthropic dans les `.env` du serveur (normal) ; ces clés ont transité par le
  compte de session.
- Journal de session `s2_4690a82e_iaeasy-iachallenge.md`, section `## 2026-07-21`, vers la ligne 12204 : **un mot de
- Même journal, autour des lignes 4321-4400 (2026-07-10) et 6499-6540 (2026-07-10/11) : token/identifiants Instagram-Meta

## 8. Références

- Mémoire : `project_iaeasy.md` (chronologie détaillée jusqu'au 2026-07-14, 216 lignes), `feedback_csp_inline_script_gotcha.md`,
  `feedback_css_hidden_attribute_gotcha.md`, `feedback_ios_input_zoom_gotcha.md`, `feedback_basketvision_window_confirm_gotcha.md`,
  `feedback_rituel_deploiement.md`, `feedback_pas_de_questions_clarification.md`, `project_confia_cloudflare_tunnel.md`,
  `project_confia_cf_tunnel_timeout.md`, `project_confia_git_secrets.md`, `project_nextcloud_tkonsulting.md`
  (connecteur Recherche+), `project_chasseur_mission.md` (étude de faisabilité), `project_homelab_portail_vaultwarden.md`
  (Vaultwarden pour ranger les mots de passe).
- Autres HANDOFF liés : IA Challenge (à ne pas confondre), Nextcloud TKonsulting, tkonsulting.fr, ConfIA (même VM).
- `project_iaeasy.md` est en retard sur Instagram, Voyage, Brief IA, Chasseur, NocoDB/agents-engine, catalogue 75 :
  ce HANDOFF fait foi pour l'état au 2026-09-26.
