"""Framework-agnostic error type. The HTTP layer (backend/main.py) turns it into the documented error body."""

from __future__ import annotations


class ServiceError(Exception):
    """A client-correctable problem. ``code`` is a stable, machine-readable string (see docs/API.md)."""

    def __init__(self, status: int, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.status, self.code, self.message, self.details = status, code, message, details or {}

    def body(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "details": self.details}}
