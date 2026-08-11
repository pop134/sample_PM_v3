"""Tests for time-series observation storage (WBS 1.1.3, part 2/2)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.providers.models import GeoPoint, WeatherObservation
from app.services.ingestion import IngestionJob
from app.services.observation_store import ObservationRepository, make_db_sink
from tests.test_ingestion import POINTS, FakeProvider

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")


@pytest.fixture()
def session_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)


def _obs(minute: int, temp: float = 10.0, provider: str = "openweather") -> WeatherObservation:
    return WeatherObservation(
        location=POINT,
        observed_at=datetime(2026, 8, 1, 12, minute, tzinfo=timezone.utc),
        temperature_c=temp,
        provider=provider,
    )


def test_save_inserts_then_dedups(session_factory):
    session = session_factory()
    repo = ObservationRepository(session)
    assert repo.save(_obs(0)) is True
    assert repo.save(_obs(0)) is False  # exact duplicate
    assert repo.count() == 1


def test_save_many_dedups_within_batch(session_factory):
    repo = ObservationRepository(session_factory())
    inserted = repo.save_many([_obs(0), _obs(0), _obs(5), _obs(5, provider="other")])
    assert inserted == 3
    assert repo.count() == 3


def test_latest_returns_newest(session_factory):
    repo = ObservationRepository(session_factory())
    repo.save(_obs(0, temp=10))
    repo.save(_obs(30, temp=20))
    latest = repo.latest(POINT.latitude, POINT.longitude)
    assert latest is not None
    assert latest.temperature_c == 20


@pytest.mark.asyncio
async def test_db_sink_persists_ingested_observations(session_factory):
    sink = make_db_sink(session_factory)
    job = IngestionJob(FakeProvider(), lambda: POINTS, sink)
    result = await job.poll_once()
    assert result.succeeded == 2
    assert ObservationRepository(session_factory()).count() == 2
