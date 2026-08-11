"""Provider registry (WBS 1.1.1).

Maps provider names to their client classes and constructs configured instances
from application settings. Concrete providers register themselves here so
ingestion jobs (WBS 1.1.2) can look one up by name without importing it directly.
"""
from __future__ import annotations

from app.core.config import Settings, get_settings
from app.providers.base import (
    ProviderConfig,
    ProviderConfigError,
    WeatherProvider,
)

# name -> provider class
_REGISTRY: dict[str, type[WeatherProvider]] = {}


def register_provider(cls: type[WeatherProvider]) -> type[WeatherProvider]:
    """Class decorator that registers a provider under its `name`."""
    name = cls.name.lower()
    if not name or name == "base":
        raise ValueError(f"Provider {cls!r} must define a unique 'name'")
    if name in _REGISTRY and _REGISTRY[name] is not cls:
        raise ValueError(f"Provider name '{name}' is already registered")
    _REGISTRY[name] = cls
    return cls


def available_providers() -> list[str]:
    """Names of all registered providers, sorted for stable output."""
    return sorted(_REGISTRY)


def _config_for(name: str, settings: Settings) -> ProviderConfig:
    """Build a ProviderConfig for a known provider from settings."""
    if name == "openweather":
        return ProviderConfig(
            api_key=settings.openweather_api_key,
            base_url=settings.openweather_base_url,
        )
    raise ProviderConfigError(f"No configuration mapping for provider '{name}'")


def get_provider(name: str, settings: Settings | None = None) -> WeatherProvider:
    """Instantiate a registered provider by name with settings-derived config."""
    key = name.lower()
    cls = _REGISTRY.get(key)
    if cls is None:
        raise ProviderConfigError(
            f"Unknown provider '{name}'. Available: {available_providers()}"
        )
    settings = settings or get_settings()
    return cls(_config_for(key, settings))
