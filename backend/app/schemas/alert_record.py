"""Persisted alert response schema (WBS 1.3.2)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_name: str | None
    latitude: float
    longitude: float
    metric: str
    value: float
    kind: str
    severity: str
    message: str
    observed_at: datetime
    created_at: datetime
