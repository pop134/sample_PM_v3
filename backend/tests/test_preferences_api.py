"""Integration tests for preferences endpoints (WBS 1.6.1, part 2/2)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, future=True)
    app = create_app()

    def override():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c


def _auth(client, email="a@x.com"):
    client.post("/api/auth/register", json={"email": email, "password": "pw1234"})
    tok = client.post("/api/auth/login", json={"email": email, "password": "pw1234"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_requires_auth(client):
    assert client.get("/api/preferences").status_code == 401


def test_preferences_get_and_update(client):
    h = _auth(client)
    r = client.get("/api/preferences", headers=h)
    assert r.status_code == 200
    assert r.json()["temperature_unit"] == "c"
    r = client.put("/api/preferences", json={"temperature_unit": "f"}, headers=h)
    assert r.json()["temperature_unit"] == "f"


def test_preferences_update_validates(client):
    h = _auth(client)
    assert client.put("/api/preferences", json={"temperature_unit": "kelvin"}, headers=h).status_code == 422


def test_saved_locations_crud(client):
    h = _auth(client)
    r = client.post("/api/preferences/locations", json={"name": "London", "latitude": 51.5, "longitude": -0.12}, headers=h)
    assert r.status_code == 201
    loc_id = r.json()["id"]
    assert len(client.get("/api/preferences/locations", headers=h).json()) == 1
    assert client.delete(f"/api/preferences/locations/{loc_id}", headers=h).status_code == 204
    assert client.delete(f"/api/preferences/locations/{loc_id}", headers=h).status_code == 404


def test_saved_locations_isolated_between_users(client):
    h1 = _auth(client, "one@x.com")
    h2 = _auth(client, "two@x.com")
    r = client.post("/api/preferences/locations", json={"name": "Paris", "latitude": 48.85, "longitude": 2.35}, headers=h1)
    loc_id = r.json()["id"]
    # user two sees none and cannot delete user one's location
    assert client.get("/api/preferences/locations", headers=h2).json() == []
    assert client.delete(f"/api/preferences/locations/{loc_id}", headers=h2).status_code == 404


def test_thresholds_upsert_and_list(client):
    h = _auth(client)
    r = client.put("/api/preferences/thresholds", json={"metric": "temperature_c", "maximum": 40, "severity": "critical"}, headers=h)
    assert r.status_code == 200
    assert r.json()["maximum"] == 40
    assert len(client.get("/api/preferences/thresholds", headers=h).json()) == 1
