"""Forecast-accuracy schemas (WBS 1.3.3)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AccuracyPair(BaseModel):
    target_time: datetime
    forecast_temp_c: float
    actual_temp_c: float
    error_c: float


class AccuracyResult(BaseModel):
    provider: str | None = None
    matched: int
    mae_c: float | None = None   # mean absolute error
    bias_c: float | None = None  # mean signed error (forecast - actual)
    rmse_c: float | None = None  # root mean squared error
    pairs: list[AccuracyPair] = []
