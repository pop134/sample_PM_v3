"""Tests for the weather query service (WBS 1.2.2, part 1/2)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.providers.models import GeoPoint, WeatherObservation
from app.services.observation_store import ObservationRepository
from app.services.weather_query import get_current, get_history

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def _seed(session, hours):
    repo = ObservationRepository(session)
    for h in hours:
        repo.save(WeatherObservation(
            location=POINT,
            observed_at=datetime(2026, 8, 1, h, 0, tzinfo=timezone.utc),
            temperature_c=float(h), provider="openweather",
        ))


def test_get_current_returns_newest(session):
    _seed(session, [6, 12, 18])
    current = get_current(session, POINT.latitude, POINT.longitude)
    assert current is not None
    assert current.temperature_c == 18.0


def test_get_current_none_when_empty(session):
    assert get_current(session, 0.0, 0.0) is None


def test_history_time_range_and_total(session):
    _seed(session, [0, 6, 12, 18])
    rows, total = get_history(
        session, POINT.latitude, POINT.longitude,
        start=datetime(2026, 8, 1, 6, tzinfo=timezone.utc),
        end=datetime(2026, 8, 1, 12, tzinfo=timezone.utc),
    )
    assert total == 2
    assert [r.temperature_c for r in rows] == [12.0, 6.0]  # newest first


def test_history_pagination(session):
    _seed(session, list(range(0, 10)))
    page1, total = get_history(session, POINT.latitude, POINT.longitude, limit=3, offset=0)
    page2, _ = get_history(session, POINT.latitude, POINT.longitude, limit=3, offset=3)
    assert total == 10
    assert len(page1) == 3
    assert page1[-1].temperature_c != page2[0].temperature_c


def test_history_limit_clamped(session):
    _seed(session, [1, 2, 3])
    rows, _ = get_history(session, POINT.latitude, POINT.longitude, limit=99999)
    assert len(rows) == 3
