"""Tests for anomaly detection (WBS 1.3.2, part 1/2)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.schemas.alerts import AlertKind, AlertSeverity
from app.services.anomaly import (
    DEFAULT_RULES,
    ThresholdRule,
    detect_outliers,
    detect_threshold,
)


@dataclass
class R:
    observed_at: datetime
    temperature_c: float | None = None
    wind_speed_ms: float | None = None
    humidity_pct: float | None = None


def dt(h):
    return datetime(2026, 8, 1, h, tzinfo=timezone.utc)


def test_threshold_flags_temperature_spike():
    events = detect_threshold(R(dt(0), temperature_c=50.0), DEFAULT_RULES)
    assert len(events) == 1
    e = events[0]
    assert e.metric == "temperature_c"
    assert e.kind == AlertKind.THRESHOLD
    assert e.severity == AlertSeverity.CRITICAL
    assert "above maximum" in e.message


def test_threshold_flags_below_minimum():
    events = detect_threshold(R(dt(0), temperature_c=-40.0), DEFAULT_RULES)
    assert events[0].value == -40.0
    assert "below minimum" in events[0].message


def test_threshold_ignores_missing_metric():
    assert detect_threshold(R(dt(0)), DEFAULT_RULES) == []


def test_threshold_within_bounds_no_events():
    assert detect_threshold(R(dt(0), temperature_c=20.0, wind_speed_ms=5.0), DEFAULT_RULES) == []


def test_outlier_detection_flags_spike():
    readings = [R(dt(h), temperature_c=20.0) for h in range(10)]
    readings.append(R(dt(10), temperature_c=80.0))  # clear outlier
    events = detect_outliers(readings, "temperature_c", z=3.0)
    assert len(events) == 1
    assert events[0].value == 80.0
    assert events[0].kind == AlertKind.OUTLIER


def test_outlier_needs_minimum_samples():
    assert detect_outliers([R(dt(0), temperature_c=1.0)], "temperature_c") == []


def test_outlier_zero_variance_no_events():
    readings = [R(dt(h), temperature_c=20.0) for h in range(5)]
    assert detect_outliers(readings, "temperature_c") == []


def test_custom_rule():
    rule = ThresholdRule("humidity_pct", maximum=90.0, severity=AlertSeverity.WARNING)
    events = detect_threshold(R(dt(0), humidity_pct=95.0), [rule])
    assert events[0].severity == AlertSeverity.WARNING
