"""Weather query service (WBS 1.2.2, part 1/2).

Read-side business logic over stored observations: current conditions and
historical ranges with filtering and pagination. Kept separate from the HTTP
layer (part 2) so it is unit-testable without a running app.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.observation import Observation

_COORD_DP = 4
MAX_LIMIT = 500


def _point_filter(stmt: Select, latitude: float, longitude: float) -> Select:
    return stmt.where(
        func.round(Observation.latitude, _COORD_DP) == round(latitude, _COORD_DP),
        func.round(Observation.longitude, _COORD_DP) == round(longitude, _COORD_DP),
    )


def get_current(
    session: Session, latitude: float, longitude: float, provider: str | None = None
) -> Observation | None:
    """Most recent observation for a location (optionally provider-scoped)."""
    stmt = _point_filter(select(Observation), latitude, longitude)
    if provider:
        stmt = stmt.where(Observation.provider == provider)
    stmt = stmt.order_by(Observation.observed_at.desc()).limit(1)
    return session.execute(stmt).scalar_one_or_none()


def get_history(
    session: Session,
    latitude: float,
    longitude: float,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    provider: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[Observation], int]:
    """A page of observations for a location within an optional time range.

    Returns (rows newest-first, total matching count). `limit` is clamped to
    MAX_LIMIT and `offset` floored at 0.
    """
    limit = max(1, min(limit, MAX_LIMIT))
    offset = max(0, offset)

    base = _point_filter(select(Observation), latitude, longitude)
    if provider:
        base = base.where(Observation.provider == provider)
    if start is not None:
        base = base.where(Observation.observed_at >= start)
    if end is not None:
        base = base.where(Observation.observed_at <= end)

    total = session.execute(
        select(func.count()).select_from(base.subquery())
    ).scalar_one()

    rows = session.execute(
        base.order_by(Observation.observed_at.desc()).limit(limit).offset(offset)
    ).scalars().all()
    return list(rows), int(total)
