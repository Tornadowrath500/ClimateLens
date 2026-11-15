from typing import Optional

from fastapi import APIRouter, Depends, File, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from backend import services as svc
from backend.api.deps import ERRORS, session_header
from backend.errors import ServiceError
from backend.schemas import ByomAuditRequest, SettingsRequest
from backend.services.byom import MAX_UPLOAD_BYTES

router = APIRouter(prefix="/byom", tags=["audit your model"], responses={**ERRORS, 413: ERRORS[422]})


@router.post("/upload", summary="Upload a CSV of decisions (kept in memory for this session only)")
async def upload(request: Request, file: UploadFile = File(...), session: Optional[str] = Depends(session_header)):
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_UPLOAD_BYTES + 64 * 1024:
        raise ServiceError(413, "file_too_large", f"The file is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    return await run_in_threadpool(svc.byom_upload, session, file.filename, content)


@router.post("/sample", summary="Use FairLens's own validation predictions as a sample upload")
def sample(body: SettingsRequest, session: Optional[str] = Depends(session_header)):
    return svc.byom_sample(session, **body.model_dump())


@router.post("/audit", summary="Group comparison for an uploaded file")
def audit(body: ByomAuditRequest, session: Optional[str] = Depends(session_header)):
    return svc.byom_audit(session, **body.model_dump())