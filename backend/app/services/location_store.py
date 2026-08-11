"""Location metadata repository (WBS 1.2.1, part 2/2).

CRUD for the tracked-locations metadata table. Ingestion's `locations_source`
and the API's location endpoints resolve places through this, keeping the set of
polled locations in one authoritative place.
"""
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.location import Location
from app.providers.models import GeoPoint

# Precision for treating two coordinates as the same place (~11 m).
_COORD_DP = 4


class LocationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create(self, name: str, latitude: float, longitude: float) -> Location:
        lat, lon = round(latitude, _COORD_DP), round(longitude, _COORD_DP)
        existing = self.session.execute(
            select(Location).where(
                func.round(Location.latitude, _COORD_DP) == lat,
                func.round(Location.longitude, _COORD_DP) == lon,
            )
        ).scalars().first()
        if existing is not None:
            return existing
        location = Location(name=name, latitude=lat, longitude=lon)
        self.session.add(location)
        self.session.commit()
        self.session.refresh(location)
        return location

    def list_all(self) -> Sequence[Location]:
        return self.session.execute(
            select(Location).order_by(Location.name)
        ).scalars().all()

    def get(self, location_id: int) -> Location | None:
        return self.session.get(Location, location_id)

    def as_points(self) -> list[GeoPoint]:
        """Expose tracked locations as GeoPoints for the ingestion job."""
        return [
            GeoPoint(latitude=loc.latitude, longitude=loc.longitude, name=loc.name)
            for loc in self.list_all()
        ]
