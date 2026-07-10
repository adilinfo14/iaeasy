from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .admin.router import router as admin_router
from .agents.router import router as agents_router
from .aide.router import router as aide_router
from .avis.router import router as avis_router
from .catalogue.router import router as catalogue_router
from .glossaire.router import router as glossaire_router
from .metiers.router import router as metiers_router
from .progress.router import router as progress_router
from .securite.router import router as securite_router
from .simulateur.router import router as simulateur_router
from .stats.router import router as stats_router
from .strategie_test.router import router as strategie_test_router
from .theatre.router import router as theatre_router
from .training.router import router as training_router
from .videos.router import router as videos_router

# Documentation interactive désactivée en production : le SPA React ne l'utilise jamais et
# elle ne fait qu'élargir la surface de reconnaissance pour un visiteur non prévu.
app = FastAPI(title="iaeasy — plateforme pédagogique IA", docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    # Le frontend est servi par ce même processus (même origine) : cette liste ne sert qu'à
    # d'éventuels appels croisés explicites, jamais au fonctionnement normal du site.
    allow_origins=["https://iaeasy.noschoixpourvous.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(catalogue_router, prefix="/api")
app.include_router(training_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(strategie_test_router, prefix="/api")
app.include_router(glossaire_router, prefix="/api")
app.include_router(metiers_router, prefix="/api")
app.include_router(simulateur_router, prefix="/api")
app.include_router(aide_router, prefix="/api")
app.include_router(avis_router, prefix="/api")
app.include_router(videos_router, prefix="/api")
app.include_router(securite_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(theatre_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


_FRONTEND_DIST = Path(__file__).parent.parent / "static"
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    # Route "catch-all" : sert le fichier statique demandé s'il existe réellement (ex: une
    # police dans /fonts, copiée depuis frontend/public par Vite), sinon retombe sur
    # index.html pour que React Router gère la navigation directe vers une route (ex:
    # /constructeur, F5). Sans cette vérification d'existence, un fichier statique hors
    # /assets (comme les polices) recevait silencieusement index.html à la place.
    # mimetypes ne connaît pas toujours .woff2 (dépend de l'OS/l'image) : sans type MIME
    # correct, X-Content-Type-Options: nosniff peut suffire à faire refuser la police par
    # le navigateur, qui la charge alors silencieusement en fallback vers la police système.
    _TYPES_MIME_SUPPLEMENTAIRES = {".woff2": "font/woff2", ".woff": "font/woff"}

    @app.get("/{chemin_complet:path}")
    def frontend_spa(chemin_complet: str):
        chemin_fichier = _FRONTEND_DIST / chemin_complet
        if chemin_fichier.is_file() and chemin_fichier.resolve().is_relative_to(_FRONTEND_DIST.resolve()):
            media_type = _TYPES_MIME_SUPPLEMENTAIRES.get(chemin_fichier.suffix)
            return FileResponse(chemin_fichier, media_type=media_type)
        return FileResponse(_FRONTEND_DIST / "index.html")
