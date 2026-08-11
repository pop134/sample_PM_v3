"""Provider abstraction (WBS 1.1.1).

`WeatherProvider` is the contract every external-source client implements.
Concrete clients (e.g. OpenWeatherMap) are added in later PRs; this module only
defines the interface, the shared config/credential shape and the error types so
callers can depend on a stable surface.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass

from app.providers.models import Forecast, GeoPoint, WeatherObservation


class ProviderError(Exception):
    """Base class for all provider-related failures."""


class ProviderConfigError(ProviderError):
    """Raised when a provider is missing required configuration (e.g. API key)."""


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an unexpected or unparseable response."""


@dataclass(frozen=True)
class ProviderConfig:
    """Credentials and connection settings for a single provider."""

    api_key: str
    base_url: str
    timeout_seconds: float = 10.0

    def require_key(self) -> str:
        if not self.api_key:
            raise ProviderConfigError("Provider API key is not configured")
        return self.api_key


class WeatherProvider(abc.ABC):
    """Interface implemented by every external weather data source."""

    #: Stable, lowercase identifier used in config, DTOs and the registry.
    name: str = "base"

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @abc.abstractmethod
    async def get_current(self, point: GeoPoint) -> WeatherObservation:
        """Return the current conditions for a location."""

    @abc.abstractmethod
    async def get_forecast(self, point: GeoPoint) -> Forecast:
        """Return the upcoming forecast series for a location."""

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<{type(self).__name__} name={self.name!r}>"
