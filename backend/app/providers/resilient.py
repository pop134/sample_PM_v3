"""Resilient provider wrapper (WBS 1.1.4, part 2/2).

Decorates any `WeatherProvider` with the reliability concerns of task 1.1.4:
per-provider rate limiting, exponential-backoff retries, and short-TTL response
caching — composed in one place so ingestion and API code use a single,
quota-friendly client. Completes task 1.1.4.
"""
from __future__ import annotations

from app.providers.base import WeatherProvider
from app.providers.cache import TTLCache
from app.providers.models import Forecast, GeoPoint, WeatherObservation
from app.providers.ratelimit import RateLimiter
from app.providers.retry import RetryPolicy, retry_async


class ResilientProvider(WeatherProvider):
    """Adds rate limiting, retries and caching around an inner provider."""

    def __init__(
        self,
        inner: WeatherProvider,
        *,
        limiter: RateLimiter | None = None,
        retry_policy: RetryPolicy | None = None,
        cache: TTLCache | None = None,
    ) -> None:
        self.inner = inner
        self.name = inner.name
        self.config = inner.config
        self._limiter = limiter
        self._retry = retry_policy or RetryPolicy()
        self._cache: TTLCache = cache or TTLCache(ttl_seconds=300)

    def _key(self, kind: str, point: GeoPoint) -> str:
        return f"{self.name}:{kind}:{round(point.latitude, 4)}:{round(point.longitude, 4)}"

    async def get_current(self, point: GeoPoint) -> WeatherObservation:
        return await self._cached(self._key("current", point), self.inner.get_current, point)

    async def get_forecast(self, point: GeoPoint) -> Forecast:
        return await self._cached(self._key("forecast", point), self.inner.get_forecast, point)

    async def _cached(self, key, call, point):
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        if self._limiter is not None:
            await self._limiter.acquire()
        result = await retry_async(lambda: call(point), self._retry)
        self._cache.set(key, result)
        return result
