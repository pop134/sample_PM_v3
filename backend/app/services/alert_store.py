"""Alert persistence & generation (WBS 1.3.2, part 2/2)."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import AlertRecord
from app.schemas.alerts import AlertEvent
from app.services.analytics import fetch_readings
from app.services.anomaly import (
    DEFAULT_RULES,
    ThresholdRule,
    detect_outliers,
    detect_threshold,
)

# Metrics scanned by the statistical outlier detector.
_OUTLIER_METRICS = ("temperature_c", "wind_speed_ms")


class AlertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_events(
        self, events: Sequence[AlertEvent], latitude: float, longitude: float,
        location_name: str | None = None,
    ) -> int:
        for e in events:
            self.session.add(AlertRecord(
                location_name=location_name,
                latitude=round(latitude, 4),
                longitude=round(longitude, 4),
                metric=e.metric, value=e.value, kind=e.kind.value,
                severity=e.severity.value, message=e.message, observed_at=e.observed_at,
            ))
        self.session.commit()
        return len(events)

    def list(
        self, latitude: float, longitude: float, *,
        severity: str | None = None, limit: int = 100,
    ) -> list[AlertRecord]:
        stmt = select(AlertRecord).where(
            AlertRecord.latitude == round(latitude, 4),
            AlertRecord.longitude == round(longitude, 4),
        )
        if severity:
            stmt = stmt.where(AlertRecord.severity == severity)
        stmt = stmt.order_by(AlertRecord.observed_at.desc()).limit(max(1, min(limit, 500)))
        return list(self.session.execute(stmt).scalars().all())


def generate_alerts(
    session: Session, latitude: float, longitude: float, *,
    start: datetime | None = None, end: datetime | None = None,
    rules: list[ThresholdRule] | None = None,
) -> list[AlertEvent]:
    """Scan stored observations for a location and return detected alert events."""
    rules = rules or DEFAULT_RULES
    readings = fetch_readings(session, latitude, longitude, start=start, end=end)
    events: list[AlertEvent] = []
    for reading in readings:
        events.extend(detect_threshold(reading, rules))
    for metric in _OUTLIER_METRICS:
        events.extend(detect_outliers(readings, metric))
    return events
