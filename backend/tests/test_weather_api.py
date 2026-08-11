"""Integration tests for weather + location endpoints (WBS 1.2.2, part 2/2)."""
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
from app.services.location_store import LocationRepository
from app.services.observation_store import ObservationRepository

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")


@pytest.fixture()
def client_and_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, future=True)

    app = create_app()

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, TestSession


def _seed_obs(TestSession, hours):
    session = TestSession()
    repo = ObservationRepository(session)
    for h in hours:
        repo.save(WeatherObservation(
            location=POINT,
            observed_at=datetime(2026, 8, 1, h, 0, tzinfo=timezone.utc),
            temperature_c=float(h), provider="openweather",
        ))
    session.close()


def test_current_returns_latest(client_and_session):
    client, TestSession = client_and_session
    _seed_obs(TestSession, [6, 12, 18])
    resp = client.get("/api/weather/current", params={"lat": 51.5074, "lon": -0.1278})
    assert resp.status_code == 200
    assert resp.json()["temperature_c"] == 18.0


def test_current_404_when_missing(client_and_session):
    client, _ = client_and_session
    resp = client.get("/api/weather/current", params={"lat": 0, "lon": 0})
    assert resp.status_code == 404


def test_current_validates_coords(client_and_session):
    client, _ = client_and_session
    resp = client.get("/api/weather/current", params={"lat": 200, "lon": 0})
    assert resp.status_code == 422


def test_history_pagination_envelope(client_and_session):
    client, TestSession = client_and_session
    _seed_obs(TestSession, list(range(0, 10)))
    resp = client.get(
        "/api/weather/history",
        params={"lat": 51.5074, "lon": -0.1278, "limit": 4, "offset": 0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["page"]["total"] == 10
    assert len(body["items"]) == 4


def test_history_bad_range_400(client_and_session):
    client, _ = client_and_session
    resp = client.get("/api/weather/history", params={
        "lat": 51.5, "lon": -0.12,
        "start": "2026-08-02T00:00:00Z", "end": "2026-08-01T00:00:00Z",
    })
    assert resp.status_code == 400


def test_locations_list_and_get(client_and_session):
    client, TestSession = client_and_session
    session = TestSession()
    loc = LocationRepository(session).get_or_create("London", 51.5074, -0.1278)
    session.close()
    resp = client.get("/api/locations")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    resp2 = client.get(f"/api/locations/{loc.id}")
    assert resp2.status_code == 200
    assert client.get("/api/locations/9999").status_code == 404
