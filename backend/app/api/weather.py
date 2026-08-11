"""Weather query endpoints (WBS 1.2.2, part 2/2)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.weather import ObservationOut, ObservationPage, Page
from app.services import weather_query

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=ObservationOut)
def current_conditions(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    provider: str | None = Query(None),
    db: Session = Depends(get_db),
) -> ObservationOut:
    obs = weather_query.get_current(db, lat, lon, provider)
    if obs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No observations for this location",
        )
    return obs


@router.get("/history", response_model=ObservationPage)
def history(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    provider: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> ObservationPage:
    if start and end and start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'start' must be before 'end'",
        )
    rows, total = weather_query.get_history(
        db, lat, lon, start=start, end=end, provider=provider,
        limit=limit, offset=offset,
    )
    return ObservationPage(
        items=[ObservationOut.model_validate(r) for r in rows],
        page=Page(total=total, limit=limit, offset=offset),
    )
