"""Analytics API schemas (WBS 1.3)."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Period(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AggregateBucket(BaseModel):
    period_start: datetime
    count: int
    temp_avg: float
    temp_min: float
    temp_max: float
    humidity_avg: float | None = None
    wind_avg: float | None = None


class TrendPoint(BaseModel):
    period_start: datetime
    temp_avg: float
    rolling_avg: float | None = None
