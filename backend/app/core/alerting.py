"""Alerting hooks (WBS 1.7.4).

Pure predicates over the metrics snapshot that a scheduler/monitor can poll to
decide whether to page (e.g. sustained API error rate). Kept pure so alerting
policy is unit-tested; wiring to a pager/webhook is deployment-specific.
"""
from __future__ import annotations

import logging

logger = logging.getLogger("alerting")


def error_rate(snapshot: dict[str, int]) -> float:
    total = snapshot.get("http_requests_total", 0)
    errors = snapshot.get("http_errors_total", 0)
    return errors / total if total else 0.0


def should_page(snapshot: dict[str, int], *, threshold: float = 0.5, min_requests: int = 20) -> bool:
    """Page when enough traffic has a 5xx rate at/above the threshold."""
    if snapshot.get("http_requests_total", 0) < min_requests:
        return False
    return error_rate(snapshot) >= threshold


def check_and_log(snapshot: dict[str, int], **kwargs) -> bool:
    """Evaluate the paging condition, emitting an ERROR log when tripped."""
    paging = should_page(snapshot, **kwargs)
    if paging:
        logger.error(
            "ALERT api_error_rate rate=%.2f requests=%d",
            error_rate(snapshot), snapshot.get("http_requests_total", 0),
        )
    return paging
