"""Tests for security primitives & user store (WBS 1.2.3, part 1/2)."""
from __future__ import annotations

import time

import jwt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.session import Base
from app.services.user_store import EmailAlreadyExists, UserRepository


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_password_hash_roundtrip():
    h = hash_password("s3cret!")
    assert h != "s3cret!"
    assert verify_password("s3cret!", h) is True
    assert verify_password("wrong", h) is False


def test_verify_password_bad_hash_is_false():
    assert verify_password("x", "not-a-bcrypt-hash") is False


def test_access_token_roundtrip():
    token = create_access_token("42")
    claims = decode_access_token(token)
    assert claims["sub"] == "42"
    assert "exp" in claims


def test_expired_token_rejected():
    token = create_access_token("1", expires_minutes=-1)
    time.sleep(0.01)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_user_create_and_authenticate(session):
    repo = UserRepository(session)
    user = repo.create("User@Example.com", "pw12345")
    assert user.email == "user@example.com"  # normalised
    assert repo.authenticate("user@example.com", "pw12345") is not None
    assert repo.authenticate("user@example.com", "bad") is None


def test_duplicate_email_rejected(session):
    repo = UserRepository(session)
    repo.create("a@x.com", "pw")
    with pytest.raises(EmailAlreadyExists):
        repo.create("a@x.com", "pw2")


def test_inactive_user_cannot_auth(session):
    repo = UserRepository(session)
    user = repo.create("z@x.com", "pw")
    user.is_active = False
    session.commit()
    assert repo.authenticate("z@x.com", "pw") is None
