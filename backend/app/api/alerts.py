"""Alert endpoints (WBS 1.3.2, part 2/2)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alert_record import AlertRecordOut
from app.schemas.alerts import AlertEvent
from app.services.alert_store import AlertRepository, generate_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/scan", response_model=list[AlertEvent])
def scan(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    persist: bool = Query(True),
    db: Session = Depends(get_db),
) -> list[AlertEvent]:
    """Detect anomalies over stored observations; optionally persist them."""
    events = generate_alerts(db, lat, lon, start=start, end=end)
    if persist and events:
        AlertRepository(db).save_events(events, lat, lon)
    return events


@router.get("", response_model=list[AlertRecordOut])
def list_alerts(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    severity: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AlertRecordOut]:
    rows = AlertRepository(db).list(lat, lon, severity=severity, limit=limit)
    return [AlertRecordOut.model_validate(r) for r in rows]
