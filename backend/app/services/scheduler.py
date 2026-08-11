"""Periodic scheduler (WBS 1.1.2, part 1/2).

A small, dependency-free async scheduler that runs a coroutine on a fixed
interval until stopped. Ingestion polling jobs (part 2) are driven by this. It
is deliberately generic and unit-testable: `run` accepts a `max_iterations`
bound and a swappable `sleep` so tests never wait real wall-clock time.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

# A job is any zero-arg coroutine function.
Job = Callable[[], Awaitable[None]]
Sleeper = Callable[[float], Awaitable[None]]


class PeriodicScheduler:
    """Run an async job every `interval_seconds` until stopped."""

    def __init__(
        self,
        job: Job,
        interval_seconds: float,
        *,
        name: str = "job",
        sleep: Sleeper = asyncio.sleep,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self._job = job
        self._interval = interval_seconds
        self._name = name
        self._sleep = sleep
        self._stop = asyncio.Event()
        self.runs = 0
        self.errors = 0

    def stop(self) -> None:
        """Signal the run loop to exit after the current iteration."""
        self._stop.set()

    async def run(self, max_iterations: int | None = None) -> None:
        """Execute the job repeatedly.

        Runs until `stop()` is called or, when provided, `max_iterations` have
        completed. A failing job is logged and counted but does not stop the
        loop — polling should survive a transient provider error.
        """
        while not self._stop.is_set():
            if max_iterations is not None and self.runs >= max_iterations:
                break
            try:
                await self._job()
            except Exception:  # noqa: BLE001 - resilience is the point
                self.errors += 1
                logger.exception("Scheduled job %r failed", self._name)
            finally:
                self.runs += 1
            if max_iterations is not None and self.runs >= max_iterations:
                break
            await self._sleep(self._interval)
