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


import time
import uuid

from app.core.logging import get_logger

_request_logger = get_logger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach a request id, time the request, and log a structured line."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = uuid.uuid4().hex[:12]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        _request_logger.info(
            "request id=%s method=%s path=%s status=%d duration_ms=%.1f",
            request_id, request.method, request.url.path, response.status_code, duration_ms,
        )
        return response
