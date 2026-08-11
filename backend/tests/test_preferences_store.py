"""Tests for preferences/saved-locations/thresholds repositories (WBS 1.6.1)."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.services.preferences_store import (
    PreferenceRepository,
    SavedLocationRepository,
    ThresholdRepository,
)
from app.services.user_store import UserRepository


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


@pytest.fixture()
def user_id(session):
    return UserRepository(session).create("u@x.com", "pw1234").id


def test_saved_locations_add_dedup_list_remove(session, user_id):
    repo = SavedLocationRepository(session)
    a = repo.add(user_id, "London", 51.5074, -0.1278)
    b = repo.add(user_id, "London", 51.50742, -0.12779)  # ~same
    assert a.id == b.id
    repo.add(user_id, "Paris", 48.85, 2.35)
    assert [l.name for l in repo.list(user_id)] == ["London", "Paris"]
    assert repo.remove(user_id, a.id) is True
    assert repo.remove(user_id, 9999) is False


def test_saved_location_scoped_to_user(session, user_id):
    other = UserRepository(session).create("v@x.com", "pw1234").id
    repo = SavedLocationRepository(session)
    loc = repo.add(user_id, "Berlin", 52.52, 13.4)
    # other user cannot remove it
    assert repo.remove(other, loc.id) is False


def test_preferences_get_or_create_and_update(session, user_id):
    repo = PreferenceRepository(session)
    pref = repo.get_or_create(user_id)
    assert pref.temperature_unit == "c"
    updated = repo.update(user_id, temperature_unit="f")
    assert updated.temperature_unit == "f"
    # idempotent single row
    assert repo.get_or_create(user_id).id == pref.id


def test_threshold_upsert_and_list(session, user_id):
    repo = ThresholdRepository(session)
    repo.upsert(user_id, "temperature_c", minimum=-10, maximum=40, severity="critical")
    repo.upsert(user_id, "temperature_c", maximum=45)  # updates same row
    rows = repo.list(user_id)
    assert len(rows) == 1
    assert rows[0].maximum == 45
    assert rows[0].minimum is None
