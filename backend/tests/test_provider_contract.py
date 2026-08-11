"""Provider contract tests (WBS 1.7.1, part 2/2).

Exercise the OpenWeatherMap HTTP paths end-to-end with respx so a change in the
request shape or parsing is caught, without hitting the network.
"""
from __future__ import annotations

import httpx
import pytest
import respx

from app.providers.base import ProviderConfig
from app.providers.models import GeoPoint
from app.providers.openweather import OpenWeatherProvider

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")

FORECAST_PAYLOAD = {
    "city": {"name": "London", "coord": {"lat": 51.5074, "lon": -0.1278}},
    "list": [
        {"dt": 1_700_003_600, "main": {"temp": 12.0, "humidity": 80}, "wind": {"speed": 3.6},
         "weather": [{"description": "broken clouds"}], "pop": 0.4, "rain": {"3h": 1.2}},
        {"dt": 1_700_014_400, "main": {"temp": 10.5, "humidity": 88}, "wind": {"speed": 5.0},
         "weather": [{"description": "light snow"}], "pop": 0.6, "snow": {"3h": 0.5}},
    ],
}


def _provider() -> OpenWeatherProvider:
    return OpenWeatherProvider(ProviderConfig(api_key="k", base_url="https://api.openweathermap.org"))


@pytest.mark.asyncio
@respx.mock
async def test_get_forecast_http_contract():
    route = respx.get("https://api.openweathermap.org/data/2.5/forecast").mock(
        return_value=httpx.Response(200, json=FORECAST_PAYLOAD)
    )
    forecast = await _provider().get_forecast(POINT)
    assert route.called
    # request carries appid + metric units
    url = str(route.calls.last.request.url)
    assert "appid=k" in url and "units=metric" in url
    # response mapped to canonical entries
    assert len(forecast.entries) == 2
    assert forecast.entries[0].precipitation_mm == 1.2
    assert forecast.entries[1].condition == "light snow"


@pytest.mark.asyncio
@respx.mock
async def test_get_forecast_server_error_wrapped():
    from app.providers.base import ProviderResponseError

    respx.get("https://api.openweathermap.org/data/2.5/forecast").mock(
        return_value=httpx.Response(503, json={"message": "unavailable"})
    )
    with pytest.raises(ProviderResponseError):
        await _provider().get_forecast(POINT)
