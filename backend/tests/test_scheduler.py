"""Tests for the periodic scheduler (WBS 1.1.2, part 1/2)."""
from __future__ import annotations

import pytest

from app.services.scheduler import PeriodicScheduler


async def _noop_sleep(_seconds: float) -> None:
    return None


@pytest.mark.asyncio
async def test_runs_bounded_number_of_times():
    calls = []

    async def job() -> None:
        calls.append(1)

    sched = PeriodicScheduler(job, interval_seconds=0.01, sleep=_noop_sleep)
    await sched.run(max_iterations=3)
    assert len(calls) == 3
    assert sched.runs == 3
    assert sched.errors == 0


@pytest.mark.asyncio
async def test_job_error_does_not_stop_loop():
    async def job() -> None:
        raise RuntimeError("boom")

    sched = PeriodicScheduler(job, interval_seconds=0.01, sleep=_noop_sleep)
    await sched.run(max_iterations=2)
    assert sched.runs == 2
    assert sched.errors == 2


@pytest.mark.asyncio
async def test_stop_breaks_loop():
    calls = []

    sched = PeriodicScheduler(
        lambda: _record(calls, sched), interval_seconds=0.01, sleep=_noop_sleep
    )
    await sched.run(max_iterations=10)
    # _record stops after the first call
    assert len(calls) == 1


async def _record(calls: list, sched: PeriodicScheduler) -> None:
    calls.append(1)
    sched.stop()


def test_rejects_non_positive_interval():
    async def job() -> None:
        return None

    with pytest.raises(ValueError):
        PeriodicScheduler(job, interval_seconds=0)
