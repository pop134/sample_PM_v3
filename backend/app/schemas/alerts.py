"""Alert schemas (WBS 1.3.2)."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertKind(str, Enum):
    THRESHOLD = "threshold"
    OUTLIER = "outlier"


class AlertEvent(BaseModel):
    metric: str
    value: float
    kind: AlertKind
    severity: AlertSeverity
    message: str
    observed_at: datetime
