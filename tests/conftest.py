"""Fixtures compartilhadas: series sinteticas com fisica conhecida."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from waters.config import settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def ana_xml() -> str:
    return (FIXTURES_DIR / "ana_sample.xml").read_text(encoding="utf-8")


def make_hourly_index(start: str, hours: int) -> pd.DatetimeIndex:
    return pd.date_range(start=start, periods=hours, freq="1h", tz=settings.TZ)


def triangular_wave(
    start: str,
    hours: int,
    base: float,
    peak: float,
    peak_hour: int,
) -> pd.Series:
    """Hidrograma triangular: sobe linear ate peak_hour, desce linear ate o fim."""
    index = make_hourly_index(start, hours)
    values = np.interp(
        np.arange(hours), [0, peak_hour, hours - 1], [base, peak, base]
    )
    return pd.Series(values, index=index)


@pytest.fixture
def synthetic_flood() -> dict:
    """Cheia sintetica: onda no afluente + nivel de POA consistente com o balanco.

    Rating conhecido: Qout = 800*(h+2)^1.5, area 470 km2 constante.
    O nivel de POA e gerado integrando o balanco com a onda ja defasada 24 h.
    """
    from waters.domain.models import RatingParams
    from waters.model.balance import integrate_level, make_qin_function
    from waters.model.inflow import shifted_inflow

    rating = RatingParams(a=800.0, h0=-2.0, b=1.5, area_km2=470.0)
    lag_hours = 24.0
    hours = 240
    upstream = triangular_wave("2025-06-01", hours, base=1500.0, peak=9000.0, peak_hour=72)
    qin_at_guaiba = shifted_inflow(upstream, lag_hours)

    h_start = 1.0
    poa_level = integrate_level(
        h0_m=h_start,
        start=qin_at_guaiba.index[0].to_pydatetime(),
        qin_fn=make_qin_function(qin_at_guaiba),
        rating=rating,
        horizon_hours=float(hours - 1),
        dt_minutes=60.0,
    )
    return {
        "upstream": upstream,
        "poa_level": poa_level,
        "rating": rating,
        "lag_hours": lag_hours,
    }
