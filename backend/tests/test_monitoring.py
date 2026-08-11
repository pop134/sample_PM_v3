"""Tests for logging, alerting & readiness (WBS 1.7.4, part 2/2)."""
from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.alerting import check_and_log, error_rate, should_page
from app.core.logging import configure_logging, get_logger
from app.db.session import Base, get_db
from app.main import create_app


def test_error_rate_and_paging():
    snap = {"http_requests_total": 100, "http_errors_total": 60}
    assert error_rate(snap) == pytest.approx(0.6)
    assert should_page(snap) is True
    # not enough traffic
    assert should_page({"http_requests_total": 5, "http_errors_total": 5}) is False
    # low rate
    assert should_page({"http_requests_total": 100, "http_errors_total": 1}) is False


def test_check_and_log_emits_error(caplog):
    with caplog.at_level(logging.ERROR):
        tripped = check_and_log({"http_requests_total": 50, "http_errors_total": 40})
    assert tripped is True
    assert any("ALERT api_error_rate" in r.message for r in caplog.records)


def test_configure_logging_idempotent():
    configure_logging()
    configure_logging()  # second call is a no-op
    assert get_logger("x") is not None


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


def test_readiness_ok_and_request_id_header(client):
    resp = client.get("/api/health/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
    # request-logging middleware attaches a correlation id
    assert "X-Request-ID" in resp.headers
