from fastapi import APIRouter

from .chapitres import get_chapitres

router = APIRouter(prefix="/voyage", tags=["voyage"])


@router.get("/chapitres")
def chapitres():
    return get_chapitres()
