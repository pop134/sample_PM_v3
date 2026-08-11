"""Tests for metrics registry & endpoint (WBS 1.7.4, part 1/2)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.metrics import MetricsRegistry, registry
from app.main import create_app


def test_registry_counts_status_classes():
    reg = MetricsRegistry()
    reg.observe_status(200)
    reg.observe_status(404)
    reg.observe_status(503)
    snap = reg.snapshot()
    assert snap["http_requests_total"] == 3
    assert snap["http_responses_2xx_total"] == 1
    assert snap["http_responses_4xx_total"] == 1
    assert snap["http_responses_5xx_total"] == 1
    assert snap["http_errors_total"] == 1


@pytest.fixture()
def client():
    registry.reset()
    with TestClient(create_app()) as c:
        yield c


def test_metrics_endpoint_reflects_traffic(client):
    client.get("/api/health")
    client.get("/api/nonexistent-route")  # 404 from routing (no DB needed)
    snap = client.get("/api/metrics").json()
    assert snap["http_requests_total"] >= 2
    assert snap["http_responses_2xx_total"] >= 1
    assert snap["http_responses_4xx_total"] >= 1
