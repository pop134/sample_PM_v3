"""Tests for the provider abstraction layer (WBS 1.1.1, part 1)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.providers import (
    Forecast,
    GeoPoint,
    ProviderConfig,
    ProviderConfigError,
    WeatherObservation,
    WeatherProvider,
    available_providers,
    get_provider,
    register_provider,
)
from app.providers.models import ForecastEntry


def _obs(point: GeoPoint) -> WeatherObservation:
    return WeatherObservation(
        location=point,
        observed_at=datetime.now(timezone.utc),
        temperature_c=20.0,
        provider="dummy",
    )


@register_provider
class DummyProvider(WeatherProvider):
    name = "dummy"

    async def get_current(self, point: GeoPoint) -> WeatherObservation:
        return _obs(point)

    async def get_forecast(self, point: GeoPoint) -> Forecast:
        return Forecast(
            location=point,
            provider=self.name,
            generated_at=datetime.now(timezone.utc),
            entries=[
                ForecastEntry(
                    location=point,
                    observed_at=datetime.now(timezone.utc),
                    temperature_c=21.0,
                    provider=self.name,
                    precipitation_probability=0.3,
                )
            ],
        )


def test_registry_lists_registered_provider():
    assert "dummy" in available_providers()


def test_get_provider_without_config_mapping_raises():
    # 'dummy' is registered but has no entry in the settings->config mapping,
    # so the registry surfaces a clear ProviderConfigError rather than crashing.
    with pytest.raises(ProviderConfigError):
        get_provider("dummy")


def test_get_unknown_provider_raises():
    with pytest.raises(ProviderConfigError):
        get_provider("does-not-exist")


@pytest.mark.asyncio
async def test_dummy_provider_returns_canonical_dtos():
    cfg = ProviderConfig(api_key="k", base_url="http://x")
    provider = DummyProvider(cfg)
    point = GeoPoint(latitude=51.5, longitude=-0.12, name="London")

    current = await provider.get_current(point)
    assert current.temperature_c == 20.0
    assert current.location.name == "London"

    forecast = await provider.get_forecast(point)
    assert forecast.provider == "dummy"
    assert forecast.entries[0].precipitation_probability == 0.3


def test_require_key_raises_when_missing():
    cfg = ProviderConfig(api_key="", base_url="http://x")
    with pytest.raises(ProviderConfigError):
        cfg.require_key()


def test_geopoint_rejects_out_of_range():
    with pytest.raises(ValueError):
        GeoPoint(latitude=200, longitude=0)
