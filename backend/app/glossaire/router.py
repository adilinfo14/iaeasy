from fastapi import APIRouter

from .termes import get_termes

router = APIRouter(prefix="/glossaire", tags=["glossaire"])


@router.get("")
def termes():
    return get_termes()
