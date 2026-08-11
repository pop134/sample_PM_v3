"""API response schemas for weather queries (WBS 1.2.2)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_name: str | None
    latitude: float
    longitude: float
    observed_at: datetime
    temperature_c: float
    feels_like_c: float | None
    humidity_pct: float | None
    pressure_hpa: float | None
    wind_speed_ms: float | None
    wind_deg: float | None
    condition: str | None
    provider: str


class Page(BaseModel):
    """Pagination envelope for list responses."""

    total: int
    limit: int
    offset: int


class ObservationPage(BaseModel):
    items: list[ObservationOut]
    page: Page
