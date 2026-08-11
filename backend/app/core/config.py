"""Application configuration loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Weather Tracking & Analysis Dashboard"
    environment: str = "development"
    database_url: str = "sqlite:///./weather.db"

    # External providers (WBS 1.1.1)
    openweather_api_key: str = ""
    openweather_base_url: str = "https://api.openweathermap.org"

    # Ingestion / polling (WBS 1.1.2)
    poll_interval_seconds: int = 900


@lru_cache
def get_settings() -> Settings:
    return Settings()
