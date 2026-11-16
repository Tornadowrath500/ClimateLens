from fastapi import APIRouter

from backend import services as svc
from backend.api.deps import ERRORS
from backend.schemas import Source

router = APIRouter(tags=["system"], responses=ERRORS)


@router.get("/health", summary="Liveness check")
def health():
    return svc.health()


@router.get("/meta", summary="Constants, data dictionary, plain-language definitions")
def meta():
    return svc.meta()


@router.get("/methodology", summary="Cost matrix, limitations and (if data exists) split sizes")
def methodology(source: Source = "real"):
    return svc.methodology(source=source)
