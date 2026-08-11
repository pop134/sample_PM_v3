"""Preferences API schemas (WBS 1.6.1)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PreferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    temperature_unit: str
    wind_unit: str


class PreferenceUpdate(BaseModel):
    temperature_unit: Literal["c", "f"] | None = None
    wind_unit: Literal["ms", "mph"] | None = None


class SavedLocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    latitude: float
    longitude: float


class SavedLocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ThresholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    metric: str
    minimum: float | None
    maximum: float | None
    severity: str


class ThresholdUpsert(BaseModel):
    metric: str = Field(min_length=1, max_length=60)
    minimum: float | None = None
    maximum: float | None = None
    severity: Literal["info", "warning", "critical"] = "warning"
