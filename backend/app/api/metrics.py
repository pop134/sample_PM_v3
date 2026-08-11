"""Metrics endpoint (WBS 1.7.4)."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.metrics import registry

router = APIRouter(tags=["system"])


@router.get("/metrics")
def metrics() -> dict[str, int]:
    """Current in-process counters (requests, per-class responses, errors)."""
    return registry.snapshot()
