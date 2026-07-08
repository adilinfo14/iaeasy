from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agents.router import router as agents_router
from .catalogue.router import router as catalogue_router
from .glossaire.router import router as glossaire_router
from .progress.router import router as progress_router
from .stats.router import router as stats_router
from .strategie_test.router import router as strategie_test_router
from .training.router import router as training_router

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


@app.get("/api/health")
def health():
    return {"status": "ok"}


_FRONTEND_DIST = Path(__file__).parent.parent / "static"
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    # Route "catch-all" : toute URL qui n'est ni /api/* ni /assets/* sert index.html, pour que
    # React Router puisse gérer la navigation directe vers une route (ex: /constructeur, F5).
    @app.get("/{chemin_complet:path}")
    def frontend_spa(chemin_complet: str):
        return FileResponse(_FRONTEND_DIST / "index.html")
