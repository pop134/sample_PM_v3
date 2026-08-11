"""Tests for historical aggregation & trends (WBS 1.3.1, part 1/2)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.schemas.analytics import Period
from app.services.analytics import aggregate, bucket_start, rolling_average


@dataclass
class R:
    observed_at: datetime
    temperature_c: float
    humidity_pct: float | None = None
    wind_speed_ms: float | None = None


def dt(month, day, hour=0):
    return datetime(2026, month, day, hour, tzinfo=timezone.utc)


def test_bucket_start_periods():
    assert bucket_start(dt(8, 5, 15), Period.DAILY) == dt(8, 5)
    # 2026-08-05 is a Wednesday -> week starts Monday 2026-08-03
    assert bucket_start(dt(8, 5, 15), Period.WEEKLY) == dt(8, 3)
    assert bucket_start(dt(8, 20), Period.MONTHLY) == dt(8, 1)


def test_daily_aggregate_avg_min_max():
    readings = [
        R(dt(8, 1, 6), 10.0, 80, 3.0),
        R(dt(8, 1, 18), 20.0, 60, 5.0),
        R(dt(8, 2, 12), 15.0, 70, 4.0),
    ]
    buckets = aggregate(readings, Period.DAILY)
    assert len(buckets) == 2
    day1 = buckets[0]
    assert day1.count == 2
    assert day1.temp_avg == 15.0
    assert day1.temp_min == 10.0
    assert day1.temp_max == 20.0
    assert day1.humidity_avg == 70.0
    assert day1.wind_avg == 4.0


def test_aggregate_sorted_by_period():
    readings = [R(dt(8, 3), 5.0), R(dt(8, 1), 1.0), R(dt(8, 2), 3.0)]
    buckets = aggregate(readings, Period.DAILY)
    assert [b.period_start for b in buckets] == [dt(8, 1), dt(8, 2), dt(8, 3)]


def test_rolling_average_window():
    readings = [R(dt(8, d), float(d)) for d in range(1, 6)]
    buckets = aggregate(readings, Period.DAILY)
    trend = rolling_average(buckets, window=3)
    assert trend[0].rolling_avg is None
    assert trend[1].rolling_avg is None
    assert trend[2].rolling_avg == 2.0  # (1+2+3)/3
    assert trend[4].rolling_avg == 4.0  # (3+4+5)/3


def test_empty_input_yields_empty():
    assert aggregate([], Period.DAILY) == []
