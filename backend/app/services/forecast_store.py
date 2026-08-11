"""Forecast persistence (WBS 1.3.3, part 1/2).

Upserts provider forecast points into `forecasts` so predictions can later be
compared against observed readings. Newer generations overwrite the row for the
same (location, target_time, provider).
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.forecast import ForecastRecord
from app.providers.models import Forecast

_DP = 4


class ForecastRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_forecast(self, forecast: Forecast) -> int:
        """Upsert every entry of a provider Forecast. Returns rows written."""
        written = 0
        for entry in forecast.entries:
            lat, lon = round(entry.location.latitude, _DP), round(entry.location.longitude, _DP)
            existing = self.session.execute(
                select(ForecastRecord).where(
                    ForecastRecord.latitude == lat,
                    ForecastRecord.longitude == lon,
                    ForecastRecord.target_time == entry.observed_at,
                    ForecastRecord.provider == forecast.provider,
                )
            ).scalar_one_or_none()
            if existing is None:
                existing = ForecastRecord(
                    latitude=lat, longitude=lon,
                    target_time=entry.observed_at, provider=forecast.provider,
                    generated_at=forecast.generated_at, temperature_c=entry.temperature_c,
                )
                self.session.add(existing)
            existing.generated_at = forecast.generated_at
            existing.location_name = entry.location.name
            existing.temperature_c = entry.temperature_c
            existing.humidity_pct = entry.humidity_pct
            existing.wind_speed_ms = entry.wind_speed_ms
            existing.precipitation_mm = entry.precipitation_mm
            existing.precipitation_probability = entry.precipitation_probability
            existing.condition = entry.condition
            written += 1
        self.session.commit()
        return written
