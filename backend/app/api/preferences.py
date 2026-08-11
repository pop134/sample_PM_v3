"""User preferences, saved locations & thresholds endpoints (WBS 1.6.1, part 2/2).

All routes require authentication and are scoped to the current user.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.preferences import (
    PreferenceOut,
    PreferenceUpdate,
    SavedLocationCreate,
    SavedLocationOut,
    ThresholdOut,
    ThresholdUpsert,
)
from app.services.preferences_store import (
    PreferenceRepository,
    SavedLocationRepository,
    ThresholdRepository,
)

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=PreferenceOut)
def get_preferences(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PreferenceOut:
    return PreferenceRepository(db).get_or_create(user.id)


@router.put("", response_model=PreferenceOut)
def update_preferences(
    payload: PreferenceUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> PreferenceOut:
    return PreferenceRepository(db).update(
        user.id, temperature_unit=payload.temperature_unit, wind_unit=payload.wind_unit
    )


@router.get("/locations", response_model=list[SavedLocationOut])
def list_saved(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SavedLocationOut]:
    return [SavedLocationOut.model_validate(l) for l in SavedLocationRepository(db).list(user.id)]


@router.post("/locations", response_model=SavedLocationOut, status_code=status.HTTP_201_CREATED)
def add_saved(
    payload: SavedLocationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> SavedLocationOut:
    return SavedLocationRepository(db).add(user.id, payload.name, payload.latitude, payload.longitude)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def remove_saved(
    location_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> Response:
    if not SavedLocationRepository(db).remove(user.id, location_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved location not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/thresholds", response_model=list[ThresholdOut])
def list_thresholds(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ThresholdOut]:
    return [ThresholdOut.model_validate(t) for t in ThresholdRepository(db).list(user.id)]


@router.put("/thresholds", response_model=ThresholdOut)
def upsert_threshold(
    payload: ThresholdUpsert, user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> ThresholdOut:
    return ThresholdRepository(db).upsert(
        user.id, payload.metric, minimum=payload.minimum, maximum=payload.maximum, severity=payload.severity,
    )
