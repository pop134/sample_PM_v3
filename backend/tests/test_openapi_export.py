"""Tests for OpenAPI export tooling (WBS 1.2.4, part 2/2)."""
from __future__ import annotations

import json

from scripts.export_openapi import generate_openapi, main


def test_generate_openapi_has_paths():
    spec = generate_openapi()
    assert spec["openapi"].startswith("3.")
    assert "/api/weather/current" in spec["paths"]


def test_main_writes_file(tmp_path):
    out = tmp_path / "openapi.json"
    main([str(out)])
    written = json.loads(out.read_text())
    assert "paths" in written
    assert written["info"]["title"]
