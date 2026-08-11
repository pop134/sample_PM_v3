"""OpenWeatherMap provider client (WBS 1.1.1, part 2/2).

Concrete implementation of the `WeatherProvider` contract. Handles the HTTP
calls to OpenWeatherMap's current-weather and 5-day/3-hour forecast endpoints
and maps their raw JSON into the canonical DTOs. Parsing is isolated in pure
functions (`parse_current`, `parse_forecast`) so it can be unit-tested without
network access.

API reference: https://openweathermap.org/current , https://openweathermap.org/forecast5
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.providers.base import (
    ProviderResponseError,
    WeatherProvider,
)
from app.providers.models import (
    Forecast,
    ForecastEntry,
    GeoPoint,
    WeatherObservation,
)
from app.providers.registry import register_provider

PROVIDER_NAME = "openweather"


def _to_dt(epoch: Any) -> datetime:
    try:
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise ProviderResponseError(f"Invalid timestamp: {epoch!r}") from exc


def _point_from(payload: dict[str, Any], fallback: GeoPoint) -> GeoPoint:
    coord = payload.get("coord") or {}
    return GeoPoint(
        latitude=coord.get("lat", fallback.latitude),
        longitude=coord.get("lon", fallback.longitude),
        name=payload.get("name") or fallback.name,
    )


def _condition(entry: dict[str, Any]) -> str | None:
    weather = entry.get("weather") or []
    if weather and isinstance(weather, list):
        return weather[0].get("description")
    return None


def parse_current(payload: dict[str, Any], point: GeoPoint) -> WeatherObservation:
    """Map an OpenWeatherMap current-weather response to a WeatherObservation.

    Assumes units=metric (Celsius, m/s), which the client always requests.
    """
    try:
        main = payload["main"]
        wind = payload.get("wind") or {}
        return WeatherObservation(
            location=_point_from(payload, point),
            observed_at=_to_dt(payload.get("dt")),
            temperature_c=float(main["temp"]),
            feels_like_c=_opt_float(main.get("feels_like")),
            humidity_pct=_opt_float(main.get("humidity")),
            pressure_hpa=_opt_float(main.get("pressure")),
            wind_speed_ms=_opt_float(wind.get("speed")),
            wind_deg=_opt_float(wind.get("deg")),
            condition=_condition(payload),
            provider=PROVIDER_NAME,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderResponseError(
            f"Unexpected OpenWeatherMap current payload: {exc}"
        ) from exc


def parse_forecast(payload: dict[str, Any], point: GeoPoint) -> Forecast:
    """Map an OpenWeatherMap 5-day/3-hour forecast response to a Forecast."""
    try:
        city = payload.get("city") or {}
        loc = GeoPoint(
            latitude=(city.get("coord") or {}).get("lat", point.latitude),
            longitude=(city.get("coord") or {}).get("lon", point.longitude),
            name=city.get("name") or point.name,
        )
        entries: list[ForecastEntry] = []
        for item in payload.get("list", []):
            main = item.get("main") or {}
            wind = item.get("wind") or {}
            entries.append(
                ForecastEntry(
                    location=loc,
                    observed_at=_to_dt(item.get("dt")),
                    temperature_c=float(main["temp"]),
                    feels_like_c=_opt_float(main.get("feels_like")),
                    humidity_pct=_opt_float(main.get("humidity")),
                    pressure_hpa=_opt_float(main.get("pressure")),
                    wind_speed_ms=_opt_float(wind.get("speed")),
                    wind_deg=_opt_float(wind.get("deg")),
                    condition=_condition(item),
                    provider=PROVIDER_NAME,
                    precipitation_mm=_precip_mm(item),
                    precipitation_probability=_opt_float(item.get("pop")),
                )
            )
        return Forecast(
            location=loc,
            provider=PROVIDER_NAME,
            generated_at=datetime.now(timezone.utc),
            entries=entries,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderResponseError(
            f"Unexpected OpenWeatherMap forecast payload: {exc}"
        ) from exc


def _opt_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _precip_mm(item: dict[str, Any]) -> float | None:
    rain = item.get("rain") or {}
    snow = item.get("snow") or {}
    total = 0.0
    found = False
    for bucket in (rain, snow):
        if "3h" in bucket:
            total += float(bucket["3h"])
            found = True
    return total if found else None


@register_provider
class OpenWeatherProvider(WeatherProvider):
    """Client for the OpenWeatherMap REST API."""

    name = PROVIDER_NAME

    async def get_current(self, point: GeoPoint) -> WeatherObservation:
        payload = await self._get(
            "/data/2.5/weather",
            {"lat": point.latitude, "lon": point.longitude},
        )
        return parse_current(payload, point)

    async def get_forecast(self, point: GeoPoint) -> Forecast:
        payload = await self._get(
            "/data/2.5/forecast",
            {"lat": point.latitude, "lon": point.longitude},
        )
        return parse_forecast(payload, point)

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = {
            **params,
            "appid": self.config.require_key(),
            "units": "metric",
        }
        url = f"{self.config.base_url.rstrip('/')}{path}"
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            try:
                resp = await client.get(url, params=query)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                raise ProviderResponseError(
                    f"OpenWeatherMap returned {exc.response.status_code} for {path}"
                ) from exc
            except httpx.HTTPError as exc:
                raise ProviderResponseError(
                    f"OpenWeatherMap request to {path} failed: {exc}"
                ) from exc
