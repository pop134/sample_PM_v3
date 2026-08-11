"""Integration tests for analytics endpoints (WBS 1.3.1, part 2/2)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app
from app.providers.models import GeoPoint, WeatherObservation
from app.services.observation_store import ObservationRepository

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")


@pytest.fixture()
def client_and_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, future=True)
    app = create_app()

    def override():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as client:
        yield client, TestSession


def _seed(TestSession):
    session = TestSession()
    repo = ObservationRepository(session)
    for day in range(1, 6):
        for hour, temp in ((6, day * 2.0), (18, day * 2.0 + 4)):
            repo.save(WeatherObservation(
                location=POINT,
                observed_at=datetime(2026, 8, day, hour, tzinfo=timezone.utc),
                temperature_c=temp, provider="openweather",
            ))
    session.close()


def test_aggregate_daily(client_and_session):
    client, TestSession = client_and_session
    _seed(TestSession)
    r = client.get("/api/analytics/aggregate", params={"lat": 51.5074, "lon": -0.1278, "period": "daily"})
    assert r.status_code == 200
    buckets = r.json()
    assert len(buckets) == 5
    assert buckets[0]["count"] == 2


def test_trends_rolling(client_and_session):
    client, TestSession = client_and_session
    _seed(TestSession)
    r = client.get("/api/analytics/trends", params={"lat": 51.5074, "lon": -0.1278, "window": 2})
    assert r.status_code == 200
    points = r.json()
    assert points[0]["rolling_avg"] is None
    assert points[1]["rolling_avg"] is not None


def test_aggregate_empty_ok(client_and_session):
    client, _ = client_and_session
    r = client.get("/api/analytics/aggregate", params={"lat": 0, "lon": 0})
    assert r.status_code == 200
    assert r.json() == []
