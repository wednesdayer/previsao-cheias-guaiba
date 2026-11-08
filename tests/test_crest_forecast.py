"""Extrapolacao de crista e previsao fim-a-fim sobre cheia sintetica."""

import pandas as pd
import pytest

from conftest import triangular_wave
from waters.domain.models import (
    CalibrationParams,
    CrestParams,
    LagParams,
    ScenarioName,
    Station,
)
from waters.model import crest as crest_mod
from waters.model.forecast import run_forecast


def _station(code: str, role: str, group: str, cota: float = 3.0) -> Station:
    return Station(
        code=code, name=f"est-{code}", slug=f"est-{code}", river=group,
        river_group=group, role=role, has_vazao=role == "inflow",
        cota_inundacao_m=cota,
    )


def test_rising_series_crests_above_last_value():
    wave = triangular_wave("2025-06-01", 60, base=100.0, peak=5000.0, peak_hour=90)
    crest = CrestParams(station_code="x", tau_rise_hours=12.0, tau_recession_hours=48.0)
    future = crest_mod.extrapolate(wave, crest, ScenarioName.CENTRAL, horizon_hours=72.0)
    assert future.max() > float(wave.iloc[-1])
    assert future.index[0] > wave.index[-1]


def test_pessimistic_crest_higher_than_optimistic():
    wave = triangular_wave("2025-06-01", 60, base=100.0, peak=5000.0, peak_hour=90)
    crest = CrestParams(station_code="x", tau_rise_hours=12.0, tau_recession_hours=48.0)
    peaks = {
        s: crest_mod.extrapolate(wave, crest, s, 72.0).max()
        for s in ScenarioName
    }
    assert peaks[ScenarioName.PESSIMISTA] > peaks[ScenarioName.CENTRAL]
    assert peaks[ScenarioName.CENTRAL] > peaks[ScenarioName.OTIMISTA]


def test_falling_series_recedes():
    # corta a onda no meio da descida (hora 84 de 120, pico na 48)
    wave = triangular_wave("2025-06-01", 120, base=100.0, peak=5000.0, peak_hour=48)
    partial = wave.iloc[:84]
    crest = CrestParams(station_code="x", tau_rise_hours=12.0, tau_recession_hours=24.0)
    future = crest_mod.extrapolate(partial, crest, ScenarioName.CENTRAL, horizon_hours=72.0)
    assert future.iloc[-1] < future.iloc[0]
    assert future.max() <= float(partial.iloc[-1]) + 1e-6


def test_end_to_end_forecast_finds_peak(synthetic_flood):
    """Corta a cheia sintetica no meio da subida e confere o pico previsto."""
    poa = synthetic_flood["poa_level"]
    upstream = synthetic_flood["upstream"]
    lag = synthetic_flood["lag_hours"]

    observed_peak = float(poa.max())
    observed_peak_time = poa.idxmax()

    # "agora" = 36 h antes do pico observado no Guaiba
    as_of = observed_peak_time - pd.Timedelta(hours=36)
    stations = {
        "11111111": _station("11111111", "inflow", "taquari"),
        "87450020": _station("87450020", "target", "guaiba"),
    }
    params = CalibrationParams(
        version="test",
        generated_at=as_of.to_pydatetime(),
        events=["sintetico"],
        lags={"11111111": LagParams(station_code="11111111", lag_hours=lag)},
        rating=synthetic_flood["rating"],
        crests={
            "11111111": CrestParams(
                station_code="11111111", tau_rise_hours=18.0, tau_recession_hours=48.0
            )
        },
    )

    result, trajectories = run_forecast(
        flows_by_station={"11111111": upstream[upstream.index <= as_of]},
        poa_level=poa[poa.index <= as_of],
        params=params,
        stations=stations,
        now=as_of.to_pydatetime(),
    )

    central = result.peaks[ScenarioName.CENTRAL]
    # Pico previsto na janela certa (±12 h) e nivel na ordem certa (±20%)
    timing_error_h = abs(
        (pd.Timestamp(central.peak_time) - observed_peak_time).total_seconds() / 3600.0
    )
    assert timing_error_h <= 12.0
    assert central.peak_level_m == pytest.approx(observed_peak, rel=0.2)
    assert result.inflow_total_m3s > 0
    assert result.outflow_now_m3s > 0
    assert set(trajectories) == set(ScenarioName)
