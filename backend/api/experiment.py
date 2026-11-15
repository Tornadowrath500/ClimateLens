from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from backend import services as svc
from backend.api.deps import ERRORS, session_header
from backend.schemas import RuleRequest

router = APIRouter(tags=["experiment"], responses=ERRORS)


@router.post("/experiment/sweep", summary="Threshold sweep, best threshold and current-rule metrics (validation)")
def sweep(body: RuleRequest):
    return svc.experiment_sweep(**body.model_dump())


@router.post("/experiment/pin", summary="Pin a configuration and run the single final test review (once per session)")
def pin(body: RuleRequest, session: Optional[str] = Depends(session_header)):
    return svc.experiment_pin(session, **body.model_dump())


@router.get("/experiment/pin", summary="The pinned review for this session, if any")
def pinned(session: Optional[str] = Depends(session_header)):
    return svc.experiment_pinned(session)


@router.get("/report/findings", summary="Frozen findings of the pinned review (404 if none)")
def findings(session: Optional[str] = Depends(session_header)):
    return svc.report_findings(session)


@router.get("/report/markdown", summary="Downloadable Markdown report of the pinned review", response_class=PlainTextResponse)
def markdown(session: Optional[str] = Depends(session_header)):
    text = svc.report_markdown(session)
    return PlainTextResponse(text, media_type="text/markdown; charset=utf-8",
                             headers={"Content-Disposition": 'attachment; filename="fairlens_report.md"'})
