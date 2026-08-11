"""In-process metrics registry (WBS 1.7.4).

A tiny thread-unsafe-but-adequate counter store for request/error metrics,
exposed via /api/metrics. Swap for Prometheus client in a real deployment.
"""
from __future__ import annotations

from collections import defaultdict


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)

    def inc(self, name: str, amount: int = 1) -> None:
        self._counters[name] += amount

    def observe_status(self, status_code: int) -> None:
        self.inc("http_requests_total")
        self.inc(f"http_responses_{status_code // 100}xx_total")
        if status_code >= 500:
            self.inc("http_errors_total")

    def snapshot(self) -> dict[str, int]:
        return dict(self._counters)

    def reset(self) -> None:
        self._counters.clear()


registry = MetricsRegistry()
