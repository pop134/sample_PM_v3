"""Tests for the location metadata repository (WBS 1.2.1, part 2/2)."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.services.location_store import LocationRepository


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_get_or_create_is_idempotent(session):
    repo = LocationRepository(session)
    a = repo.get_or_create("London", 51.50741, -0.12781)
    b = repo.get_or_create("London", 51.50742, -0.12779)  # ~same coords
    assert a.id == b.id
    assert len(repo.list_all()) == 1


def test_list_all_sorted_by_name(session):
    repo = LocationRepository(session)
    repo.get_or_create("Paris", 48.85, 2.35)
    repo.get_or_create("Amsterdam", 52.37, 4.90)
    names = [loc.name for loc in repo.list_all()]
    assert names == ["Amsterdam", "Paris"]


def test_as_points_feeds_ingestion(session):
    repo = LocationRepository(session)
    repo.get_or_create("Berlin", 52.52, 13.40)
    points = repo.as_points()
    assert len(points) == 1
    assert points[0].name == "Berlin"


def test_get_by_id(session):
    repo = LocationRepository(session)
    loc = repo.get_or_create("Rome", 41.9, 12.5)
    assert repo.get(loc.id) is not None
    assert repo.get(9999) is None
