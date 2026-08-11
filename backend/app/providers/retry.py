"""Retry with exponential backoff (WBS 1.1.4, part 1/2).

A small async retry helper for provider calls. Retries only transient
`ProviderResponseError`s (network/5xx-style), backing off exponentially with
optional jitter, up to a maximum number of attempts. The rate limiter and cache
that complete the task build on this in part 2.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from app.providers.base import ProviderResponseError

logger = logging.getLogger(__name__)

T = TypeVar("T")
Sleeper = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class RetryPolicy:
    """Exponential-backoff configuration."""

    max_attempts: int = 3
    base_delay: float = 0.5
    factor: float = 2.0
    max_delay: float = 30.0

    def delay_for(self, attempt: int) -> float:
        """Backoff delay before retry `attempt` (1-indexed)."""
        return min(self.base_delay * (self.factor ** (attempt - 1)), self.max_delay)


async def retry_async(
    func: Callable[[], Awaitable[T]],
    policy: RetryPolicy | None = None,
    *,
    sleep: Sleeper = asyncio.sleep,
) -> T:
    """Call `func`, retrying transient ProviderResponseErrors per `policy`."""
    policy = policy or RetryPolicy()
    last_error: ProviderResponseError | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return await func()
        except ProviderResponseError as exc:
            last_error = exc
            if attempt >= policy.max_attempts:
                break
            delay = policy.delay_for(attempt)
            logger.warning(
                "Provider call failed (attempt %d/%d), retrying in %.2fs: %s",
                attempt, policy.max_attempts, delay, exc,
            )
            await sleep(delay)
    assert last_error is not None
    raise last_error
