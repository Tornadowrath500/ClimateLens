from fastapi import APIRouter

from backend import services as svc
from backend.api.deps import ERRORS
from backend.schemas import MitigationRequest, ModelRuleRequest, ProxyRequest

router = APIRouter(tags=["fairness tools"], responses=ERRORS)


@router.post("/proxies/report", summary="Can age group be recovered from the other inputs? (cross-validated AUC)")
def proxies_report(body: ProxyRequest):
    return svc.proxies_report(**body.model_dump())


@router.post("/proxies/removal", summary="Does removing age / status change outcomes?")
def proxies_removal(body: ModelRuleRequest):
    return svc.proxies_removal(**body.model_dump())


@router.post("/mitigation/run", summary="Six strategies compared on one validation split (slow)")
def mitigation_run(body: MitigationRequest):
    return svc.mitigation_run(**body.model_dump())
