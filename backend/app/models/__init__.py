"""ORM models. Import each model here so metadata is fully registered."""
from app.models.alert import AlertRecord  # noqa: F401
from app.models.forecast import ForecastRecord  # noqa: F401
from app.models.location import Location  # noqa: F401
from app.models.observation import Observation  # noqa: F401
from app.models.preferences import (  # noqa: F401
    AlertThreshold,
    SavedLocation,
    UserPreference,
)
from app.models.user import User  # noqa: F401

__all__ = [
    "Location", "Observation", "ForecastRecord", "User", "AlertRecord",
    "SavedLocation", "UserPreference", "AlertThreshold",
]
