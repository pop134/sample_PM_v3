"""Location endpoints (WBS 1.2.2, part 2/2)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.location import LocationOut
from app.services.location_store import LocationRepository

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationOut])
def list_locations(db: Session = Depends(get_db)) -> list[LocationOut]:
    return [LocationOut.model_validate(loc) for loc in LocationRepository(db).list_all()]


@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db)) -> LocationOut:
    loc = LocationRepository(db).get(location_id)
    if loc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return loc
