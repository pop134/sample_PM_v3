"""Tests for rate limiter, cache and ResilientProvider (WBS 1.1.4, part 2/2)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.providers.base import ProviderResponseError, WeatherProvider
from app.providers.cache import TTLCache
from app.providers.models import Forecast, GeoPoint, WeatherObservation
from app.providers.ratelimit import RateLimiter
from app.providers.resilient import ResilientProvider
from app.providers.retry import RetryPolicy

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def time(self) -> float:
        return self.t

    async def sleep(self, seconds: float) -> None:
        self.t += seconds


class CountingProvider(WeatherProvider):
    name = "counting"

    def __init__(self, *, fail_times: int = 0) -> None:
        self.calls = 0
        self._fail_times = fail_times
        self.config = None  # type: ignore[assignment]

    async def get_current(self, point: GeoPoint) -> WeatherObservation:
        self.calls += 1
        if self.calls <= self._fail_times:
            raise ProviderResponseError("transient")
        return WeatherObservation(
            location=point, observed_at=datetime.now(timezone.utc),
            temperature_c=float(self.calls), provider=self.name,
        )

    async def get_forecast(self, point: GeoPoint) -> Forecast:  # pragma: no cover
        raise NotImplementedError


# ---- RateLimiter ----

@pytest.mark.asyncio
async def test_rate_limiter_waits_when_depleted():
    clock = FakeClock()
    limiter = RateLimiter(rate=10, capacity=2, clock=clock.time, sleep=clock.sleep)
    await limiter.acquire()  # 2 -> 1
    await limiter.acquire()  # 1 -> 0
    await limiter.acquire()  # needs to wait 0.1s for 1 token
    assert clock.t == pytest.approx(0.1)


def test_rate_limiter_rejects_bad_rate():
    with pytest.raises(ValueError):
        RateLimiter(rate=0)


# ---- TTLCache ----

def test_cache_expires_after_ttl():
    clock = FakeClock()
    cache: TTLCache[str] = TTLCache(ttl_seconds=5, clock=clock.time)
    cache.set("k", "v")
    assert cache.get("k") == "v"
    clock.t = 5.0
    assert cache.get("k") is None


def test_cache_evicts_when_full():
    cache: TTLCache[int] = TTLCache(ttl_seconds=100, max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert len(cache) == 2


# ---- ResilientProvider ----

@pytest.mark.asyncio
async def test_resilient_caches_second_call():
    inner = CountingProvider()
    provider = ResilientProvider(inner, cache=TTLCache(ttl_seconds=300))
    first = await provider.get_current(POINT)
    second = await provider.get_current(POINT)
    assert inner.calls == 1  # second served from cache
    assert first.temperature_c == second.temperature_c


@pytest.mark.asyncio
async def test_resilient_retries_transient_errors():
    clock = FakeClock()
    inner = CountingProvider(fail_times=2)
    provider = ResilientProvider(
        inner,
        retry_policy=RetryPolicy(max_attempts=3, base_delay=0.01),
        cache=TTLCache(ttl_seconds=300, clock=clock.time),
    )
    # retry uses its own asyncio.sleep by default; patch via policy small delay
    obs = await provider.get_current(POINT)
    assert inner.calls == 3
    assert obs.provider == "counting"
