from fastapi import APIRouter

from backend import services as svc
from backend.api.deps import ERRORS
from backend.schemas import Source

router = APIRouter(prefix="/data", tags=["data"], responses=ERRORS)


@router.get("/status", summary="Is the real benchmark available on the server?")
def status():
    return svc.data_status()


@router.post("/download", summary="Explicitly download the UCI benchmark to the server (never automatic)")
def download():
    return svc.data_download()


@router.get("/overview", summary="Data page: counts, age groups, raw preview, provenance")
def overview(source: Source = "real"):
    return svc.data_overview(source=source)