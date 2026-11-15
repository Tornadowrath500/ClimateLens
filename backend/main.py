"""FairLens API.  Run from the repository root:   uvicorn backend.main:app --reload

* API:      /api/...        (interactive docs at /api/docs, schema at /api/openapi.json)
* Frontend: served from ../frontend at "/" unless FAIRLENS_SERVE_FRONTEND=0 (then run any static server for it).
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api import routers
from backend.errors import ServiceError
from backend.services.system import API_VERSION

log = logging.getLogger("fairlens")
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"

app = FastAPI(
    title="FairLens API",
    version=API_VERSION,
    description=(
        "Backend for the FairLens model-auditing prototype. Educational benchmark only: never a lending system. "
        "Errors always use {\"error\": {\"code\", \"message\", \"details\"}}. See docs/API.md."
    ),
    docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ.get("FAIRLENS_CORS_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()],
    allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-FairLens-Session"],
    expose_headers=["Content-Disposition"],
)
for router in routers:
    app.include_router(router, prefix="/api")


def _error(status: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status, content=ServiceError(status, code, message, details).body())


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError):
    return JSONResponse(status_code=exc.status, content=exc.body())


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    errors = [{"loc": [str(p) for p in e.get("loc", [])], "msg": str(e.get("msg", "")), "type": str(e.get("type", ""))}
              for e in exc.errors()]
    return _error(422, "validation_error", "The request is not valid.", {"errors": errors})


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(_: Request, exc: StarletteHTTPException):
    return _error(exc.status_code, "http_error", str(exc.detail))


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)  # details stay in the server log
    return _error(500, "internal_error", "Something went wrong on the server. Check the server log.")


if FRONTEND_DIR.is_dir() and os.environ.get("FAIRLENS_SERVE_FRONTEND", "1") != "0":
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")  # must stay last