"""Historical trend & aggregation (WBS 1.3.1, part 1/2).

Pure computations over weather readings: bucketing into daily/weekly/monthly
periods, per-bucket avg/min/max aggregates, and a rolling average across
buckets. Any object exposing `observed_at`, `temperature_c`, `humidity_pct`,
`wind_speed_ms` works (ORM row or DTO), so this is unit-testable without a DB.
The endpoints that surface it are added in part 2.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Protocol

from app.schemas.analytics import AggregateBucket, Period, TrendPoint


class _Reading(Protocol):
    observed_at: datetime
    temperature_c: float
    humidity_pct: float | None
    wind_speed_ms: float | None


def bucket_start(when: datetime, period: Period) -> datetime:
    """Normalise a timestamp to the start of its period (UTC)."""
    when = when.astimezone(timezone.utc)
    day = when.replace(hour=0, minute=0, second=0, microsecond=0)
    if period is Period.DAILY:
        return day
    if period is Period.WEEKLY:
        return day - timedelta(days=day.weekday())  # Monday
    return day.replace(day=1)  # monthly


def _avg(values: list[float]) -> float | None:
    present = [v for v in values if v is not None]
    return round(sum(present) / len(present), 2) if present else None


def aggregate(readings: list[_Reading], period: Period) -> list[AggregateBucket]:
    """Group readings into period buckets with avg/min/max temperature etc."""
    buckets: dict[datetime, list[_Reading]] = defaultdict(list)
    for r in readings:
        buckets[bucket_start(r.observed_at, period)].append(r)

    result: list[AggregateBucket] = []
    for start in sorted(buckets):
        group = buckets[start]
        temps = [r.temperature_c for r in group]
        result.append(
            AggregateBucket(
                period_start=start,
                count=len(group),
                temp_avg=round(sum(temps) / len(temps), 2),
                temp_min=round(min(temps), 2),
                temp_max=round(max(temps), 2),
                humidity_avg=_avg([r.humidity_pct for r in group]),
                wind_avg=_avg([r.wind_speed_ms for r in group]),
            )
        )
    return result


def rolling_average(buckets: list[AggregateBucket], window: int) -> list[TrendPoint]:
    """Rolling mean of bucket temp_avg over `window` buckets (period-over-period)."""
    if window < 1:
        raise ValueError("window must be >= 1")
    points: list[TrendPoint] = []
    for i, bucket in enumerate(buckets):
        if i + 1 >= window:
            recent = buckets[i + 1 - window : i + 1]
            rolling = round(sum(b.temp_avg for b in recent) / window, 2)
        else:
            rolling = None
        points.append(
            TrendPoint(
                period_start=bucket.period_start,
                temp_avg=bucket.temp_avg,
                rolling_avg=rolling,
            )
        )
    return points
