"""Tests for the ingestion job (WBS 1.1.2, part 2/2)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.providers.base import ProviderResponseError, WeatherProvider
from app.providers.models import Forecast, GeoPoint, WeatherObservation
from app.services.ingestion import IngestionJob
from app.services.scheduler import PeriodicScheduler

POINTS = [
    GeoPoint(latitude=51.5, longitude=-0.12, name="London"),
    GeoPoint(latitude=48.85, longitude=2.35, name="Paris"),
]


class FakeProvider(WeatherProvider):
    name = "fake"

    def __init__(self, *, fail_for: set[str] | None = None) -> None:
        self._fail_for = fail_for or set()

    async def get_current(self, point: GeoPoint) -> WeatherObservation:
        if point.name in self._fail_for:
            raise ProviderResponseError(f"no data for {point.name}")
        return WeatherObservation(
            location=point,
            observed_at=datetime.now(timezone.utc),
            temperature_c=15.0,
            provider=self.name,
        )

    async def get_forecast(self, point: GeoPoint) -> Forecast:  # pragma: no cover
        raise NotImplementedError


@pytest.mark.asyncio
async def test_poll_once_collects_all_observations():
    captured: list[WeatherObservation] = []
    job = IngestionJob(FakeProvider(), lambda: POINTS, _sink(captured))
    result = await job.poll_once()
    assert result.succeeded == 2
    assert result.failed == 0
    assert {o.location.name for o in captured} == {"London", "Paris"}


@pytest.mark.asyncio
async def test_poll_once_records_failures_and_continues():
    captured: list[WeatherObservation] = []
    job = IngestionJob(
        FakeProvider(fail_for={"Paris"}), lambda: POINTS, _sink(captured)
    )
    result = await job.poll_once()
    assert result.succeeded == 1
    assert result.failed == 1
    assert result.total == 2
    assert any("Paris" in e for e in result.errors)
    assert [o.location.name for o in captured] == ["London"]


@pytest.mark.asyncio
async def test_ingestion_runs_under_scheduler():
    captured: list[WeatherObservation] = []
    job = IngestionJob(FakeProvider(), lambda: POINTS, _sink(captured))

    async def _no_sleep(_s: float) -> None:
        return None

    sched = PeriodicScheduler(job.as_job(), interval_seconds=0.01, sleep=_no_sleep)
    await sched.run(max_iterations=2)
    assert sched.runs == 2
    assert len(captured) == 4  # 2 locations x 2 passes


def _sink(store: list):
    async def sink(obs: WeatherObservation) -> None:
        store.append(obs)

    return sink
