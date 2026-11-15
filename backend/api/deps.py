"""Shared HTTP response metadata and browser session header validation."""

from typing import Optional

from fastapi import Header

from backend.errors import ServiceError
from backend.state import SESSION_RE

ERRORS = {400: {"description": "Invalid request"}, 404: {"description": "Not found"},
          409: {"description": "Unavailable or already completed"}, 422: {"description": "Invalid input"},
          500: {"description": "Internal server error"}}


def session_header(value: Optional[str] = Header(None, alias="X-FairLens-Session")) -> Optional[str]:
    if value is not None and not SESSION_RE.fullmatch(value):
        raise ServiceError(400, "invalid_session", "The browser session identifier is invalid.")
    return value
