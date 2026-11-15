from fastapi import APIRouter

from backend import services as svc
from backend.api.deps import ERRORS
from backend.schemas import MapApplicantRequest, MapRequest, SimulatorEvaluateRequest, Source, SourceRequest

router = APIRouter(tags=["applicants"], responses=ERRORS)


@router.post("/map", summary="Applicant map points and the fairness terrain")
def build_map(body: MapRequest):
    return svc.map_build(**body.model_dump())


@router.post("/map/applicant", summary="Why-this-score, look-alikes and what-if path for one mapped applicant")
def map_applicant(body: MapApplicantRequest):
    return svc.map_applicant(**body.model_dump())


@router.get("/simulator/schema", summary="Form fields (ranges, levels) and a typical starting profile")
def simulator_schema(source: Source = "real"):
    return svc.simulator_schema(source=source)


@router.post("/simulator/random", summary="A randomly drawn training applicant as a starting profile")
def simulator_random(body: SourceRequest):
    return svc.simulator_random(**body.model_dump())


@router.post("/simulator/evaluate", summary="Score, contributions, what-ifs and twin test for a profile")
def simulator_evaluate(body: SimulatorEvaluateRequest):
    return svc.simulator_evaluate(**body.model_dump())