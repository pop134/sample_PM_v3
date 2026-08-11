"""Integration test for the forecast-accuracy endpoint (WBS 1.3.3, part 2/2)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app
from app.providers.models import Forecast, ForecastEntry, GeoPoint, WeatherObservation
from app.services.forecast_store import ForecastRepository
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


def dt(h):
    return datetime(2026, 8, 1, h, tzinfo=timezone.utc)


def test_accuracy_endpoint(client_and_session):
    client, TestSession = client_and_session
    s = TestSession()
    ObservationRepository(s).save(WeatherObservation(location=POINT, observed_at=dt(12), temperature_c=19.0, provider="openweather"))
    ForecastRepository(s).save_forecast(Forecast(
        location=POINT, provider="openweather", generated_at=dt(0),
        entries=[ForecastEntry(location=POINT, observed_at=dt(12), temperature_c=20.0, provider="openweather")],
    ))
    s.close()

    r = client.get("/api/analytics/accuracy", params={"lat": 51.5074, "lon": -0.1278})
    assert r.status_code == 200
    body = r.json()
    assert body["matched"] == 1
    assert body["bias_c"] == 1.0   # 20 - 19
    assert body["mae_c"] == 1.0


def test_accuracy_empty(client_and_session):
    client, _ = client_and_session
    r = client.get("/api/analytics/accuracy", params={"lat": 0, "lon": 0})
    assert r.status_code == 200
    assert r.json()["matched"] == 0
