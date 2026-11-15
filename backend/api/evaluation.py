from fastapi import APIRouter

from backend import services as svc
from backend.api.deps import ERRORS
from backend.schemas import RuleRequest, SettingsRequest, StabilityRequest

router = APIRouter(tags=["evaluation"], responses=ERRORS)


@router.post("/evaluation/validation", summary="Baselines and candidate models on the validation split")
def validation(body: SettingsRequest):
    return svc.evaluation_validation(**body.model_dump())


@router.post("/groups/review", summary="Age-group outcomes (validation split) with intervals and observations")
def review(body: RuleRequest):
    return svc.groups_review(**body.model_dump())


@router.post("/groups/stability", summary="Refit on repeated splits to show how much the gap moves (slow)")
def stability(body: StabilityRequest):
    return svc.groups_stability(**body.model_dump())