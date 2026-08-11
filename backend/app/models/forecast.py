"""Persisted forecast entry (WBS 1.2.1).

Stores individual forecast points so the dashboard and the forecast-vs-actual
analytics (WBS 1.3.3) can compare predictions against later observations. A
unique constraint keeps one row per (location, target time, provider); a newer
generation overwrites via upsert in the repository layer.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ForecastRecord(Base):
    __tablename__ = "forecasts"
    __table_args__ = (
        UniqueConstraint(
            "latitude", "longitude", "target_time", "provider",
            name="uq_forecast_point_target_provider",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    location_name: Mapped[str | None] = mapped_column(String(120), index=True)
    latitude: Mapped[float] = mapped_column(Float, index=True)
    longitude: Mapped[float] = mapped_column(Float, index=True)
    target_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    temperature_c: Mapped[float] = mapped_column(Float)
    humidity_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    condition: Mapped[str | None] = mapped_column(String(120), nullable=True)
    provider: Mapped[str] = mapped_column(String(60), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
