"""Integration tests for alert endpoints (WBS 1.3.2, part 2/2)."""
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
    # normal readings + one extreme temperature spike (threshold + outlier)
    for h in range(0, 10):
        repo.save(WeatherObservation(
            location=POINT, observed_at=datetime(2026, 8, 1, h, tzinfo=timezone.utc),
            temperature_c=20.0, provider="openweather",
        ))
    repo.save(WeatherObservation(
        location=POINT, observed_at=datetime(2026, 8, 1, 12, tzinfo=timezone.utc),
        temperature_c=55.0, provider="openweather",
    ))
    session.close()


def test_scan_detects_and_persists(client_and_session):
    client, TestSession = client_and_session
    _seed(TestSession)
    r = client.post("/api/alerts/scan", params={"lat": 51.5074, "lon": -0.1278})
    assert r.status_code == 200
    events = r.json()
    assert any(e["metric"] == "temperature_c" for e in events)
    # persisted -> listable
    r2 = client.get("/api/alerts", params={"lat": 51.5074, "lon": -0.1278})
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_scan_no_persist(client_and_session):
    client, TestSession = client_and_session
    _seed(TestSession)
    client.post("/api/alerts/scan", params={"lat": 51.5074, "lon": -0.1278, "persist": False})
    r = client.get("/api/alerts", params={"lat": 51.5074, "lon": -0.1278})
    assert r.json() == []


def test_severity_filter(client_and_session):
    client, TestSession = client_and_session
    _seed(TestSession)
    client.post("/api/alerts/scan", params={"lat": 51.5074, "lon": -0.1278})
    r = client.get("/api/alerts", params={"lat": 51.5074, "lon": -0.1278, "severity": "critical"})
    assert all(a["severity"] == "critical" for a in r.json())
