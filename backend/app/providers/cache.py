"""In-memory TTL cache (WBS 1.1.4, part 2/2).

Caches provider responses for a short TTL to cut latency and quota use. Simple
size-bounded dict keyed by a caller-supplied string; the clock is injectable for
deterministic expiry tests.
"""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Generic, TypeVar

V = TypeVar("V")


class TTLCache(Generic[V]):
    def __init__(
        self,
        ttl_seconds: float,
        *,
        max_size: int = 512,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._clock = clock
        self._store: dict[str, tuple[float, V]] = {}

    def get(self, key: str) -> V | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if self._clock() >= expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: V) -> None:
        if len(self._store) >= self.max_size and key not in self._store:
            # Evict the soonest-to-expire entry.
            oldest = min(self._store, key=lambda k: self._store[k][0])
            del self._store[oldest]
        self._store[key] = (self._clock() + self.ttl, value)

    def __len__(self) -> int:
        return len(self._store)
