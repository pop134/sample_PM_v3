"""Tests for the OpenWeatherMap provider (WBS 1.1.1, part 2/2).

Parsing is tested directly against representative payloads; the HTTP path is
exercised with respx so no real network calls are made.
"""
from __future__ import annotations

import httpx
import pytest
import respx

from app.providers import available_providers, get_provider
from app.providers.base import ProviderConfig, ProviderResponseError
from app.providers.models import GeoPoint
from app.providers.openweather import (
    OpenWeatherProvider,
    parse_current,
    parse_forecast,
)
from app.core.config import Settings

LONDON = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")

CURRENT_PAYLOAD = {
    "coord": {"lon": -0.1278, "lat": 51.5074},
    "weather": [{"description": "light rain"}],
    "main": {"temp": 12.4, "feels_like": 11.8, "humidity": 82, "pressure": 1009},
    "wind": {"speed": 4.1, "deg": 210},
    "dt": 1_700_000_000,
    "name": "London",
}

FORECAST_PAYLOAD = {
    "city": {"name": "London", "coord": {"lat": 51.5074, "lon": -0.1278}},
    "list": [
        {
            "dt": 1_700_003_600,
            "main": {"temp": 12.0, "feels_like": 11.0, "humidity": 80, "pressure": 1008},
            "wind": {"speed": 3.6, "deg": 200},
            "weather": [{"description": "broken clouds"}],
            "pop": 0.4,
            "rain": {"3h": 1.2},
        },
        {
            "dt": 1_700_014_400,
            "main": {"temp": 10.5, "feels_like": 9.0, "humidity": 88, "pressure": 1007},
            "wind": {"speed": 5.0, "deg": 220},
            "weather": [{"description": "light snow"}],
            "pop": 0.6,
            "snow": {"3h": 0.5},
        },
    ],
}


def test_provider_is_registered():
    assert "openweather" in available_providers()


def test_parse_current_maps_all_fields():
    obs = parse_current(CURRENT_PAYLOAD, LONDON)
    assert obs.provider == "openweather"
    assert obs.temperature_c == 12.4
    assert obs.humidity_pct == 82
    assert obs.wind_speed_ms == 4.1
    assert obs.condition == "light rain"
    assert obs.location.name == "London"


def test_parse_forecast_maps_entries_and_precip():
    fc = parse_forecast(FORECAST_PAYLOAD, LONDON)
    assert len(fc.entries) == 2
    first, second = fc.entries
    assert first.precipitation_mm == 1.2
    assert first.precipitation_probability == 0.4
    assert second.precipitation_mm == 0.5
    assert second.condition == "light snow"


def test_parse_current_missing_field_raises():
    bad = {"main": {}, "dt": 1_700_000_000}
    with pytest.raises(ProviderResponseError):
        parse_current(bad, LONDON)


def test_get_provider_builds_openweather_from_settings():
    settings = Settings(openweather_api_key="test-key")
    provider = get_provider("openweather", settings=settings)
    assert isinstance(provider, OpenWeatherProvider)
    assert provider.config.api_key == "test-key"


@pytest.mark.asyncio
@respx.mock
async def test_get_current_http_flow():
    route = respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
        return_value=httpx.Response(200, json=CURRENT_PAYLOAD)
    )
    provider = OpenWeatherProvider(
        ProviderConfig(api_key="k", base_url="https://api.openweathermap.org")
    )
    obs = await provider.get_current(LONDON)
    assert route.called
    assert obs.temperature_c == 12.4
    # units=metric and appid are always sent
    request = route.calls.last.request
    assert "units=metric" in str(request.url)
    assert "appid=k" in str(request.url)


@pytest.mark.asyncio
@respx.mock
async def test_get_current_http_error_wrapped():
    respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
        return_value=httpx.Response(401, json={"message": "bad key"})
    )
    provider = OpenWeatherProvider(
        ProviderConfig(api_key="bad", base_url="https://api.openweathermap.org")
    )
    with pytest.raises(ProviderResponseError):
        await provider.get_current(LONDON)
