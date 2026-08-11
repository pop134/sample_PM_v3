"""Token-bucket rate limiter (WBS 1.1.4, part 2/2).

Throttles outbound provider calls to respect per-provider quotas. `acquire`
waits just long enough to stay within `rate` tokens/second (bursting up to
`capacity`). The clock and sleep are injectable so tests are deterministic.
"""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable


class RateLimiter:
    def __init__(
        self,
        rate: float,
        capacity: float | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        self.rate = rate
        self.capacity = capacity if capacity is not None else rate
        self._clock = clock
        self._sleep = sleep
        self._tokens = self.capacity
        self._ts = clock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = now - self._ts
        self._ts = now
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)

    async def acquire(self, tokens: float = 1.0) -> None:
        """Block until `tokens` are available, then consume them."""
        self._refill()
        if self._tokens < tokens:
            wait = (tokens - self._tokens) / self.rate
            await self._sleep(wait)
            self._refill()
        self._tokens -= tokens
