from fastapi import APIRouter

from .strategies import get_strategies

router = APIRouter(prefix="/strategie-test", tags=["strategie_test"])


@router.get("")
def strategies():
    return get_strategies()
