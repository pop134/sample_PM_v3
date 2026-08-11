"""Tests for weather normalisation (WBS 1.1.3, part 1/2)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.providers.models import GeoPoint, WeatherObservation
from app.services.normalization import (
    deduplicate,
    dedup_key,
    fahrenheit_to_celsius,
    inhg_to_hpa,
    mph_to_ms,
    normalize,
    to_record,
)

POINT = GeoPoint(latitude=51.50741, longitude=-0.12781, name="London")
WHEN = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _obs(temp: float = 12.3456, provider: str = "openweather") -> WeatherObservation:
    return WeatherObservation(
        location=POINT, observed_at=WHEN, temperature_c=temp,
        humidity_pct=80.129, provider=provider,
    )


def test_unit_conversions():
    assert round(fahrenheit_to_celsius(32), 4) == 0.0
    assert round(fahrenheit_to_celsius(212), 4) == 100.0
    assert round(mph_to_ms(10), 4) == 4.4704
    assert round(inhg_to_hpa(29.92), 1) == 1013.2


def test_normalize_rounds_fields():
    n = normalize(_obs())
    assert n.temperature_c == 12.35
    assert n.humidity_pct == 80.13


def test_dedup_key_is_stable_and_precise():
    a = _obs()
    b = _obs()
    assert dedup_key(a) == dedup_key(b)
    c = _obs(provider="other")
    assert dedup_key(a) != dedup_key(c)


def test_deduplicate_keeps_first():
    dupes = [_obs(temp=1.0), _obs(temp=2.0), _obs(temp=3.0, provider="other")]
    result = deduplicate(dupes)
    assert len(result) == 2
    assert result[0].temperature_c == 1.0


def test_to_record_maps_all_columns():
    rec = to_record(normalize(_obs()))
    assert rec["latitude"] == POINT.latitude
    assert rec["location_name"] == "London"
    assert rec["provider"] == "openweather"
    assert rec["temperature_c"] == 12.35
