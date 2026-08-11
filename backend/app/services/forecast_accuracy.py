"""Forecast vs. actual comparison (WBS 1.3.3, part 1/2).

Pure computations that match forecast points to the nearest observation within a
time tolerance and produce accuracy metrics (MAE, bias, RMSE). No I/O, so it is
unit-testable; the endpoint that feeds it from storage lands in part 2.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import sqrt
from typing import Protocol

from app.schemas.accuracy import AccuracyPair, AccuracyResult


class _Forecast(Protocol):
    target_time: datetime
    temperature_c: float


class _Actual(Protocol):
    observed_at: datetime
    temperature_c: float


def _utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _nearest(actuals: list[_Actual], target: datetime, tolerance: timedelta) -> _Actual | None:
    best, best_gap = None, None
    for a in actuals:
        gap = abs(_utc(a.observed_at) - target)
        if gap <= tolerance and (best_gap is None or gap < best_gap):
            best, best_gap = a, gap
    return best


def compare(
    forecasts: list[_Forecast],
    actuals: list[_Actual],
    *,
    tolerance_minutes: int = 90,
    provider: str | None = None,
) -> AccuracyResult:
    """Match forecasts to nearest actuals and compute error metrics."""
    tolerance = timedelta(minutes=tolerance_minutes)
    pairs: list[AccuracyPair] = []
    for f in forecasts:
        target = _utc(f.target_time)
        actual = _nearest(actuals, target, tolerance)
        if actual is None:
            continue
        error = round(f.temperature_c - actual.temperature_c, 2)
        pairs.append(AccuracyPair(
            target_time=target, forecast_temp_c=f.temperature_c,
            actual_temp_c=actual.temperature_c, error_c=error,
        ))
    if not pairs:
        return AccuracyResult(provider=provider, matched=0)
    errors = [p.error_c for p in pairs]
    n = len(errors)
    return AccuracyResult(
        provider=provider,
        matched=n,
        mae_c=round(sum(abs(e) for e in errors) / n, 2),
        bias_c=round(sum(errors) / n, 2),
        rmse_c=round(sqrt(sum(e * e for e in errors) / n), 2),
        pairs=pairs,
    )
