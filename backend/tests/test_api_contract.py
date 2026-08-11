"""API contract tests (WBS 1.7.1, part 2/2).

Assert the published OpenAPI contract documents the shapes the frontend depends
on, so an accidental response-model change is caught in CI.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def spec():
    with TestClient(create_app()) as client:
        return client.get("/openapi.json").json()


def test_documents_core_paths_and_methods(spec):
    paths = spec["paths"]
    assert "get" in paths["/api/weather/current"]
    assert "get" in paths["/api/weather/history"]
    assert "post" in paths["/api/auth/login"]
    assert "put" in paths["/api/preferences"]
    assert "post" in paths["/api/alerts/scan"]


def test_current_response_schema_shape(spec):
    schemas = spec["components"]["schemas"]
    assert "ObservationOut" in schemas
    props = schemas["ObservationOut"]["properties"]
    for field in ("temperature_c", "observed_at", "provider", "latitude", "longitude"):
        assert field in props


def test_token_schema_present(spec):
    schemas = spec["components"]["schemas"]
    assert "Token" in schemas
    assert "access_token" in schemas["Token"]["properties"]
