"""Tests for OpenAPI documentation metadata (WBS 1.2.4, part 1/2)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client():
    with TestClient(create_app()) as c:
        yield c


def test_openapi_has_rich_metadata(client):
    spec = client.get("/openapi.json").json()
    assert spec["info"]["description"].strip()
    assert spec["info"]["contact"]["name"]
    assert spec["info"]["license"]["name"] == "MIT"
    tag_names = {t["name"] for t in spec["tags"]}
    assert {"weather", "locations", "auth", "system"} <= tag_names


def test_openapi_documents_key_paths(client):
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    for path in ("/api/weather/current", "/api/weather/history", "/api/auth/login"):
        assert path in paths


def test_swagger_ui_served(client):
    assert client.get("/docs").status_code == 200
