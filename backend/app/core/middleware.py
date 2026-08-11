"""HTTP middleware: metrics counting (WBS 1.7.4)."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import registry


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
        except Exception:
            registry.observe_status(500)
            raise
        registry.observe_status(response.status_code)
        return response
