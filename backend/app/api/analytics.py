"""Analytics endpoints (WBS 1.3.1, part 2/2)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.accuracy import AccuracyResult
from app.schemas.analytics import AggregateBucket, Period, TrendPoint
from app.services.analytics import aggregate, fetch_readings, rolling_average
from app.services.forecast_accuracy import compare
from app.services.forecast_store import ForecastRepository

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


@router.get("/accuracy", response_model=AccuracyResult)
def accuracy_endpoint(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    provider: str | None = Query(None),
    tolerance_minutes: int = Query(90, ge=5, le=720),
    db: Session = Depends(get_db),
) -> AccuracyResult:
    """Compare stored forecasts against observed readings for a location."""
    forecasts = ForecastRepository(db).list_for(lat, lon, provider=provider)
    actuals = fetch_readings(db, lat, lon, provider=provider)
    return compare(
        forecasts, actuals, tolerance_minutes=tolerance_minutes, provider=provider
    )
