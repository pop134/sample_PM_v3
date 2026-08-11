"""Time-series observation storage (WBS 1.1.3, part 2/2).

Persists normalised observations and enforces deduplication, and provides a
database-backed `sink` that plugs into the ingestion job (WBS 1.1.2) so polled
readings flow straight into storage.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.observation import Observation
from app.providers.models import WeatherObservation
from app.services.normalization import deduplicate, normalize, to_record


class ObservationRepository:
    """CRUD + dedup for stored weather observations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _exists(self, record: dict) -> bool:
        stmt = select(Observation.id).where(
            Observation.latitude == record["latitude"],
            Observation.longitude == record["longitude"],
            Observation.observed_at == record["observed_at"],
            Observation.provider == record["provider"],
        )
        return self.session.execute(stmt).first() is not None

    def save(self, obs: WeatherObservation) -> bool:
        """Persist one observation. Returns False if it was a duplicate."""
        record = to_record(normalize(obs))
        if self._exists(record):
            return False
        self.session.add(Observation(**record))
        try:
            self.session.commit()
        except IntegrityError:
            # Lost a race on the unique constraint — treat as duplicate.
            self.session.rollback()
            return False
        return True

    def save_many(self, observations: Iterable[WeatherObservation]) -> int:
        """Persist a batch (deduped within the batch). Returns rows inserted."""
        inserted = 0
        for obs in deduplicate(observations):
            if self.save(obs):
                inserted += 1
        return inserted

    def latest(
        self, latitude: float, longitude: float, provider: str | None = None
    ) -> Observation | None:
        stmt = select(Observation).where(
            Observation.latitude == round(latitude, 4),
            Observation.longitude == round(longitude, 4),
        )
        if provider is not None:
            stmt = stmt.where(Observation.provider == provider)
        stmt = stmt.order_by(Observation.observed_at.desc()).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()

    def count(self) -> int:
        return self.session.execute(select(func.count(Observation.id))).scalar_one()


def make_db_sink(
    session_factory: Callable[[], Session] = SessionLocal,
) -> Callable[[WeatherObservation], Awaitable[None]]:
    """An ingestion sink that writes each observation to the database."""

    async def sink(obs: WeatherObservation) -> None:
        session = session_factory()
        try:
            ObservationRepository(session).save(obs)
        finally:
            session.close()

    return sink
