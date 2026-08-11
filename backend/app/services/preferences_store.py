"""Repositories for user preferences, saved locations & thresholds (WBS 1.6.1)."""
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.preferences import AlertThreshold, SavedLocation, UserPreference

_DP = 4


class SavedLocationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, user_id: int, name: str, latitude: float, longitude: float) -> SavedLocation:
        lat, lon = round(latitude, _DP), round(longitude, _DP)
        existing = self.session.execute(
            select(SavedLocation).where(
                SavedLocation.user_id == user_id,
                SavedLocation.latitude == lat,
                SavedLocation.longitude == lon,
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing
        loc = SavedLocation(user_id=user_id, name=name, latitude=lat, longitude=lon)
        self.session.add(loc)
        self.session.commit()
        self.session.refresh(loc)
        return loc

    def list(self, user_id: int) -> Sequence[SavedLocation]:
        return self.session.execute(
            select(SavedLocation).where(SavedLocation.user_id == user_id).order_by(SavedLocation.name)
        ).scalars().all()

    def remove(self, user_id: int, location_id: int) -> bool:
        loc = self.session.get(SavedLocation, location_id)
        if loc is None or loc.user_id != user_id:
            return False
        self.session.delete(loc)
        self.session.commit()
        return True


class PreferenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create(self, user_id: int) -> UserPreference:
        pref = self.session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        ).scalar_one_or_none()
        if pref is None:
            pref = UserPreference(user_id=user_id)
            self.session.add(pref)
            self.session.commit()
            self.session.refresh(pref)
        return pref

    def update(
        self, user_id: int, *, temperature_unit: str | None = None, wind_unit: str | None = None,
    ) -> UserPreference:
        pref = self.get_or_create(user_id)
        if temperature_unit is not None:
            pref.temperature_unit = temperature_unit
        if wind_unit is not None:
            pref.wind_unit = wind_unit
        self.session.commit()
        self.session.refresh(pref)
        return pref


class ThresholdRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(
        self, user_id: int, metric: str, *,
        minimum: float | None = None, maximum: float | None = None, severity: str = "warning",
    ) -> AlertThreshold:
        row = self.session.execute(
            select(AlertThreshold).where(
                AlertThreshold.user_id == user_id, AlertThreshold.metric == metric
            )
        ).scalar_one_or_none()
        if row is None:
            row = AlertThreshold(user_id=user_id, metric=metric)
            self.session.add(row)
        row.minimum = minimum
        row.maximum = maximum
        row.severity = severity
        self.session.commit()
        self.session.refresh(row)
        return row

    def list(self, user_id: int) -> Sequence[AlertThreshold]:
        return self.session.execute(
            select(AlertThreshold).where(AlertThreshold.user_id == user_id).order_by(AlertThreshold.metric)
        ).scalars().all()
