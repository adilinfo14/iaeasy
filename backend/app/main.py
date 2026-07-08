from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agents.router import router as agents_router
from .catalogue.router import router as catalogue_router
from .progress.router import router as progress_router
from .stats.router import router as stats_router
from .strategie_test.router import router as strategie_test_router
from .training.router import router as training_router

app = FastAPI(title="iaeasy — plateforme pédagogique IA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalogue_router, prefix="/api")
app.include_router(training_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(strategie_test_router, prefix="/api")


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
