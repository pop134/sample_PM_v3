"""Tests for forecast store & accuracy comparison (WBS 1.3.3, part 1/2)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.forecast import ForecastRecord
from app.providers.models import Forecast, ForecastEntry, GeoPoint
from app.services.forecast_accuracy import compare
from app.services.forecast_store import ForecastRepository

POINT = GeoPoint(latitude=51.5074, longitude=-0.1278, name="London")


@dataclass
class F:
    target_time: datetime
    temperature_c: float


@dataclass
class A:
    observed_at: datetime
    temperature_c: float


def dt(h, m=0):
    return datetime(2026, 8, 1, h, m, tzinfo=timezone.utc)


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_compare_metrics():
    forecasts = [F(dt(6), 10.0), F(dt(12), 20.0), F(dt(18), 30.0)]
    actuals = [A(dt(6), 12.0), A(dt(12), 19.0), A(dt(18), 33.0)]
    result = compare(forecasts, actuals)
    assert result.matched == 3
    # errors: -2, +1, -3 -> bias -1.33, mae 2.0, rmse ~2.16
    assert result.bias_c == pytest.approx(-1.33, abs=0.01)
    assert result.mae_c == pytest.approx(2.0, abs=0.01)
    assert result.rmse_c == pytest.approx(2.16, abs=0.02)


def test_compare_respects_tolerance():
    forecasts = [F(dt(6), 10.0)]
    actuals = [A(dt(12), 12.0)]  # 6h away, outside 90m tolerance
    assert compare(forecasts, actuals).matched == 0


def test_compare_picks_nearest_actual():
    forecasts = [F(dt(12), 20.0)]
    actuals = [A(dt(11, 0), 18.0), A(dt(12, 20), 21.0)]
    result = compare(forecasts, actuals)
    assert result.matched == 1
    assert result.pairs[0].actual_temp_c == 21.0  # closer one


def test_forecast_store_upserts(session):
    repo = ForecastRepository(session)
    fc = Forecast(
        location=POINT, provider="openweather", generated_at=dt(0),
        entries=[ForecastEntry(location=POINT, observed_at=dt(12), temperature_c=20.0, provider="openweather")],
    )
    assert repo.save_forecast(fc) == 1
    # re-save with a newer temperature overwrites (unique target/provider)
    fc.entries[0].temperature_c = 22.0
    fc.generated_at = dt(1)
    repo.save_forecast(fc)
    rows = session.execute(select(ForecastRecord)).scalars().all()
    assert len(rows) == 1
    assert rows[0].temperature_c == 22.0
