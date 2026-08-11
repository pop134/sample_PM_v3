"""Anomaly detection (WBS 1.3.2, part 1/2).

Two complementary, pure detectors that flag suspicious weather readings:
- threshold rules — a metric outside configured bounds (e.g. temperature spike,
  heavy precipitation);
- statistical outliers — a value far from the recent mean (z-score).
Both yield `AlertEvent`s. Persistence + an alerts endpoint follow in part 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean, pstdev
from typing import Protocol

from app.schemas.alerts import AlertEvent, AlertKind, AlertSeverity


class _Reading(Protocol):
    observed_at: datetime


@dataclass(frozen=True)
class ThresholdRule:
    """Bounds for one metric; None means unbounded on that side."""

    metric: str
    minimum: float | None = None
    maximum: float | None = None
    severity: AlertSeverity = AlertSeverity.WARNING


# Sensible defaults; per-user overrides arrive with preferences (WBS 1.6.1).
DEFAULT_RULES = [
    ThresholdRule("temperature_c", minimum=-30.0, maximum=45.0, severity=AlertSeverity.CRITICAL),
    ThresholdRule("wind_speed_ms", maximum=25.0, severity=AlertSeverity.WARNING),
    ThresholdRule("humidity_pct", minimum=0.0, maximum=100.0, severity=AlertSeverity.INFO),
]


def detect_threshold(reading: _Reading, rules: list[ThresholdRule]) -> list[AlertEvent]:
    """Flag metrics on `reading` that fall outside their rule bounds."""
    events: list[AlertEvent] = []
    for rule in rules:
        value = getattr(reading, rule.metric, None)
        if value is None:
            continue
        if rule.minimum is not None and value < rule.minimum:
            events.append(_event(rule, value, reading, f"below minimum {rule.minimum}"))
        elif rule.maximum is not None and value > rule.maximum:
            events.append(_event(rule, value, reading, f"above maximum {rule.maximum}"))
    return events


def detect_outliers(
    readings: list[_Reading], metric: str, *, z: float = 3.0
) -> list[AlertEvent]:
    """Flag readings whose `metric` is more than `z` std devs from the mean."""
    values = [getattr(r, metric, None) for r in readings]
    present = [v for v in values if v is not None]
    if len(present) < 3:
        return []
    mu, sigma = mean(present), pstdev(present)
    if sigma == 0:
        return []
    events: list[AlertEvent] = []
    for reading, value in zip(readings, values):
        if value is None:
            continue
        score = abs(value - mu) / sigma
        if score > z:
            events.append(
                AlertEvent(
                    metric=metric,
                    value=float(value),
                    kind=AlertKind.OUTLIER,
                    severity=AlertSeverity.WARNING,
                    message=f"{metric}={value} is {score:.1f}σ from mean {mu:.1f}",
                    observed_at=reading.observed_at,
                )
            )
    return events


def _event(rule: ThresholdRule, value: float, reading: _Reading, why: str) -> AlertEvent:
    return AlertEvent(
        metric=rule.metric,
        value=float(value),
        kind=AlertKind.THRESHOLD,
        severity=rule.severity,
        message=f"{rule.metric}={value} {why}",
        observed_at=reading.observed_at,
    )
