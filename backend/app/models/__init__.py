"""ORM models. Import each model here so metadata is fully registered."""
from app.models.location import Location  # noqa: F401
from app.models.observation import Observation  # noqa: F401

__all__ = ["Location", "Observation"]
