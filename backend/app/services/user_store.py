"""User repository & authentication (WBS 1.2.3)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


class EmailAlreadyExists(Exception):
    """Raised when registering an email that is already taken."""


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.execute(
            select(User).where(User.email == email.lower())
        ).scalar_one_or_none()

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def create(self, email: str, password: str, *, is_admin: bool = False) -> User:
        email = email.lower()
        if self.get_by_email(email) is not None:
            raise EmailAlreadyExists(email)
        user = User(
            email=email, hashed_password=hash_password(password), is_admin=is_admin
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
