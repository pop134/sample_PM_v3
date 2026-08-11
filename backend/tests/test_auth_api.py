"""Integration tests for auth endpoints (WBS 1.2.3, part 2/2)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app
from app.services.user_store import UserRepository


@pytest.fixture()
def client_and_session():
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
    with TestClient(app) as client:
        yield client, TestSession


def test_register_then_login_then_me(client_and_session):
    client, _ = client_and_session
    r = client.post("/api/auth/register", json={"email": "a@x.com", "password": "pw1234"})
    assert r.status_code == 201
    assert r.json()["email"] == "a@x.com"

    r = client.post("/api/auth/login", json={"email": "a@x.com", "password": "pw1234"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@x.com"


def test_duplicate_register_conflict(client_and_session):
    client, _ = client_and_session
    client.post("/api/auth/register", json={"email": "b@x.com", "password": "pw1234"})
    r = client.post("/api/auth/register", json={"email": "b@x.com", "password": "pw1234"})
    assert r.status_code == 409


def test_login_bad_credentials(client_and_session):
    client, _ = client_and_session
    client.post("/api/auth/register", json={"email": "c@x.com", "password": "pw1234"})
    r = client.post("/api/auth/login", json={"email": "c@x.com", "password": "nope"})
    assert r.status_code == 401


def test_me_requires_token(client_and_session):
    client, _ = client_and_session
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer bad"}).status_code == 401


def test_register_validates_password_length(client_and_session):
    client, _ = client_and_session
    r = client.post("/api/auth/register", json={"email": "d@x.com", "password": "x"})
    assert r.status_code == 422


def test_admin_route_authorization(client_and_session):
    client, TestSession = client_and_session
    # normal user -> 403
    client.post("/api/auth/register", json={"email": "u@x.com", "password": "pw1234"})
    tok = client.post("/api/auth/login", json={"email": "u@x.com", "password": "pw1234"}).json()["access_token"]
    assert client.get("/api/auth/admin/ping", headers={"Authorization": f"Bearer {tok}"}).status_code == 403

    # admin user -> 200
    s = TestSession()
    UserRepository(s).create("admin@x.com", "pw1234", is_admin=True)
    s.close()
    atok = client.post("/api/auth/login", json={"email": "admin@x.com", "password": "pw1234"}).json()["access_token"]
    assert client.get("/api/auth/admin/ping", headers={"Authorization": f"Bearer {atok}"}).status_code == 200
