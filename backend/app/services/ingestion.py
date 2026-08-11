"""Weather ingestion job (WBS 1.1.2, part 2/2).

Polls a weather provider for a set of locations and hands each observation to a
`sink`. The sink is an injected callback so this module stays independent of
storage: in tests it's an in-memory list, and the time-series persistence layer
(WBS 1.1.3) provides a database-backed sink. Wrap `poll_once` in the
`PeriodicScheduler` (part 1) to run it on an interval.
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field

from app.providers.base import WeatherProvider
from app.providers.models import GeoPoint, WeatherObservation

logger = logging.getLogger(__name__)

LocationsSource = Callable[[], Iterable[GeoPoint]]
ObservationSink = Callable[[WeatherObservation], Awaitable[None]]


@dataclass
class IngestionResult:
    """Outcome of a single polling pass."""

    succeeded: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.succeeded + self.failed


class IngestionJob:
    """Poll a provider for each location and forward observations to a sink."""

    def __init__(
        self,
        provider: WeatherProvider,
        locations_source: LocationsSource,
        sink: ObservationSink,
    ) -> None:
        self._provider = provider
        self._locations_source = locations_source
        self._sink = sink

    async def poll_once(self) -> IngestionResult:
        """Fetch current conditions for every location, forwarding each reading.

        A failure for one location (provider or sink error) is recorded and the
        pass continues with the next location.
        """
        result = IngestionResult()
        for point in self._locations_source():
            try:
                observation = await self._provider.get_current(point)
                await self._sink(observation)
                result.succeeded += 1
            except Exception as exc:  # noqa: BLE001 - one bad location must not stop the pass
                result.failed += 1
                label = point.name or f"({point.latitude},{point.longitude})"
                result.errors.append(f"{label}: {exc}")
                logger.warning("Ingestion failed for %s: %s", label, exc)
        logger.info(
            "Ingestion pass complete: %d ok, %d failed",
            result.succeeded,
            result.failed,
        )
        return result

    def as_job(self) -> Callable[[], Awaitable[None]]:
        """Adapt to the scheduler's zero-arg, None-returning job signature."""

        async def _job() -> None:
            await self.poll_once()

        return _job
