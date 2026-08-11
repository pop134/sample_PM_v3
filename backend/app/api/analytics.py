"""Analytics endpoints (WBS 1.3.1, part 2/2)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AggregateBucket, Period, TrendPoint
from app.services.analytics import aggregate, fetch_readings, rolling_average

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/aggregate", response_model=list[AggregateBucket])
def aggregate_endpoint(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    period: Period = Query(Period.DAILY),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    provider: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[AggregateBucket]:
    readings = fetch_readings(db, lat, lon, start=start, end=end, provider=provider)
    return aggregate(readings, period)


@router.get("/trends", response_model=list[TrendPoint])
def trends_endpoint(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    period: Period = Query(Period.DAILY),
    window: int = Query(3, ge=1, le=90),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    provider: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[TrendPoint]:
    readings = fetch_readings(db, lat, lon, start=start, end=end, provider=provider)
    return rolling_average(aggregate(readings, period), window)
