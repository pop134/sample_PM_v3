"""Tests for metadata schema models (WBS 1.2.1)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models import ForecastRecord, User


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_user_email_unique(session):
    session.add(User(email="a@x.com", hashed_password="h"))
    session.commit()
    session.add(User(email="a@x.com", hashed_password="h2"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_user_defaults(session):
    u = User(email="b@x.com", hashed_password="h")
    session.add(u)
    session.commit()
    assert u.is_active is True
    assert u.is_admin is False


def test_forecast_unique_per_point_target_provider(session):
    when = datetime(2026, 8, 2, 9, 0, tzinfo=timezone.utc)
    common = dict(
        latitude=51.5, longitude=-0.12, target_time=when,
        generated_at=when, temperature_c=14.0, provider="openweather",
    )
    session.add(ForecastRecord(**common))
    session.commit()
    session.add(ForecastRecord(**common))
    with pytest.raises(IntegrityError):
        session.commit()


def test_forecast_query_by_target(session):
    when = datetime(2026, 8, 2, 9, 0, tzinfo=timezone.utc)
    session.add(ForecastRecord(
        latitude=51.5, longitude=-0.12, target_time=when, generated_at=when,
        temperature_c=14.0, provider="openweather",
    ))
    session.commit()
    rows = session.execute(select(ForecastRecord).where(ForecastRecord.target_time == when)).scalars().all()
    assert len(rows) == 1
