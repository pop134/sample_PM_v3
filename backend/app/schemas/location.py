"""Location API schemas (WBS 1.2.2)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    latitude: float
    longitude: float
    created_at: datetime
