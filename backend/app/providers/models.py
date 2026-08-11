"""Canonical, provider-agnostic weather DTOs (WBS 1.1.1).

Every provider client maps its raw response into these normalised shapes so the
rest of the system never depends on a specific vendor's payload format. Units are
canonicalised here: temperatures in Celsius, wind speed in m/s, pressure in hPa.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Units(str, Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"


class GeoPoint(BaseModel):
    """A geographic coordinate a reading belongs to."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    name: str | None = None


class WeatherObservation(BaseModel):
    """A single normalised weather reading (current or historical)."""

    location: GeoPoint
    observed_at: datetime
    temperature_c: float
    feels_like_c: float | None = None
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    pressure_hpa: float | None = None
    wind_speed_ms: float | None = Field(default=None, ge=0)
    wind_deg: float | None = Field(default=None, ge=0, le=360)
    condition: str | None = None
    provider: str


class ForecastEntry(WeatherObservation):
    """A forecasted reading for a future timestamp."""

    precipitation_mm: float | None = Field(default=None, ge=0)
    precipitation_probability: float | None = Field(default=None, ge=0, le=1)


class Forecast(BaseModel):
    """An ordered series of forecast entries for one location."""

    location: GeoPoint
    provider: str
    generated_at: datetime
    entries: list[ForecastEntry] = Field(default_factory=list)
