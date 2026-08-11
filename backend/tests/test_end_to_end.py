"""End-to-end integration: ingest -> normalise -> store -> query API (WBS 1.7.1).

Exercises the full backend pipeline with a fake provider (no network): the
ingestion job writes through the DB sink, then the REST + analytics endpoints
read the same database.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app
from app.providers.base import WeatherProvider
from app.providers.models import Forecast, GeoPoint, WeatherObservation
from app.services.ingestion import IngestionJob
from app.services.observation_store import make_db_sink

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")


class SequenceProvider(WeatherProvider):
    """Returns a scripted temperature per call so we can assert stored history."""

    name = "sequence"

    def __init__(self, temps: list[float]) -> None:
        self._temps = temps
        self._i = 0

    async def get_current(self, point: GeoPoint) -> WeatherObservation:
        temp = self._temps[min(self._i, len(self._temps) - 1)]
        self._i += 1
        return WeatherObservation(
            location=point,
            observed_at=datetime(2026, 8, 1, self._i, tzinfo=timezone.utc),
            temperature_c=temp, provider=self.name,
        )

    async def get_forecast(self, point: GeoPoint) -> Forecast:  # pragma: no cover
        raise NotImplementedError


@pytest.fixture()
def app_and_db():
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
    return app, TestSession


@pytest.mark.asyncio
async def test_ingest_then_query_via_api(app_and_db):
    app, TestSession = app_and_db
    provider = SequenceProvider([10.0, 20.0, 30.0])
    job = IngestionJob(provider, lambda: [POINT], make_db_sink(TestSession))

    # three polling passes populate the time series
    for _ in range(3):
        await job.poll_once()

    with TestClient(app) as client:
        current = client.get("/api/weather/current", params={"lat": 51.5074, "lon": -0.1278})
        assert current.status_code == 200
        assert current.json()["temperature_c"] == 30.0  # newest

        history = client.get("/api/weather/history", params={"lat": 51.5074, "lon": -0.1278})
        assert history.json()["page"]["total"] == 3

        agg = client.get("/api/analytics/aggregate", params={"lat": 51.5074, "lon": -0.1278})
        buckets = agg.json()
        assert buckets[0]["temp_min"] == 10.0
        assert buckets[0]["temp_max"] == 30.0
