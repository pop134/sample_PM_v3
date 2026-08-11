"""Weather normalisation (WBS 1.1.3, part 1/2).

Converts provider readings into a single canonical form before storage:
unit conversion helpers (in case a source is imperial), consistent rounding, and
deduplication by (location, timestamp, provider). Pure functions only — no I/O —
so they are trivially testable and reused by the storage layer (part 2).
"""
from __future__ import annotations

from collections.abc import Iterable

from app.providers.models import WeatherObservation

# Rounding precision for stored values (avoids float noise / near-duplicates).
_TEMP_DP = 2
_GENERIC_DP = 2

DedupKey = tuple[float, float, str, str]


def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32.0) * 5.0 / 9.0


def mph_to_ms(mph: float) -> float:
    return mph * 0.44704


def inhg_to_hpa(inhg: float) -> float:
    return inhg * 33.8638866667


def _round(value: float | None, ndigits: int) -> float | None:
    return None if value is None else round(value, ndigits)


def dedup_key(obs: WeatherObservation) -> DedupKey:
    """Stable identity of an observation for deduplication."""
    return (
        round(obs.location.latitude, 4),
        round(obs.location.longitude, 4),
        obs.observed_at.isoformat(),
        obs.provider,
    )


def normalize(obs: WeatherObservation) -> WeatherObservation:
    """Return a copy with canonical rounding applied to all numeric fields."""
    return obs.model_copy(
        update={
            "temperature_c": _round(obs.temperature_c, _TEMP_DP),
            "feels_like_c": _round(obs.feels_like_c, _TEMP_DP),
            "humidity_pct": _round(obs.humidity_pct, _GENERIC_DP),
            "pressure_hpa": _round(obs.pressure_hpa, _GENERIC_DP),
            "wind_speed_ms": _round(obs.wind_speed_ms, _GENERIC_DP),
            "wind_deg": _round(obs.wind_deg, _GENERIC_DP),
        }
    )


def deduplicate(observations: Iterable[WeatherObservation]) -> list[WeatherObservation]:
    """Drop duplicate readings, keeping the first occurrence of each key."""
    seen: set[DedupKey] = set()
    unique: list[WeatherObservation] = []
    for obs in observations:
        key = dedup_key(obs)
        if key in seen:
            continue
        seen.add(key)
        unique.append(obs)
    return unique


def to_record(obs: WeatherObservation) -> dict:
    """Map a canonical DTO to Observation model constructor kwargs."""
    return {
        "location_name": obs.location.name,
        "latitude": obs.location.latitude,
        "longitude": obs.location.longitude,
        "observed_at": obs.observed_at,
        "temperature_c": obs.temperature_c,
        "feels_like_c": obs.feels_like_c,
        "humidity_pct": obs.humidity_pct,
        "pressure_hpa": obs.pressure_hpa,
        "wind_speed_ms": obs.wind_speed_ms,
        "wind_deg": obs.wind_deg,
        "condition": obs.condition,
        "provider": obs.provider,
    }
