"""Calibracao: deteccao de eventos, ajuste de lags/crista, params IO e hindcast."""

from datetime import datetime

import pandas as pd
import pytest

from conftest import make_hourly_index, triangular_wave
from waters.config import settings
from waters.calibrate.events import all_events, detect_events
from waters.calibrate.fit_crest import fit_station_crest
from waters.calibrate.fit_lags import fit_station_lag
from waters.calibrate.hindcast import hindcast_event
from waters.calibrate.run import calibrate
from waters.config.params_io import load_latest_params, save_params
from waters.domain.errors import CalibrationError
from waters.domain.models import (
    CalibrationParams,
    CrestParams,
    LagParams,
    RatingParams,
    ScenarioName,
    Station,
)


def _station(code: str, role: str, group: str) -> Station:
    return Station(
        code=code, name=f"est-{code}", slug=f"est-{code}", river=group,
        river_group=group, role=role, has_vazao=role == "inflow",
        cota_inundacao_m=3.0,
    )


def _params(version: str = "v1") -> CalibrationParams:
    return CalibrationParams(
        version=version,
        generated_at=datetime(2026, 7, 1, tzinfo=settings.TZ),
        events=["sintetico"],
        lags={"11111111": LagParams(station_code="11111111", lag_hours=24.0)},
        rating=RatingParams(a=800.0, h0=-2.0, b=1.5, area_km2=470.0),
        crests={
            "11111111": CrestParams(
                station_code="11111111", tau_rise_hours=18.0, tau_recession_hours=48.0
            )
        },
    )


def test_detect_events_finds_high_water_window():
    index = make_hourly_index("2025-05-01", 24 * 30)
    level = pd.Series(1.0, index=index)
    level.iloc[240:480] = 2.5  # 10 dias de agua alta
    events = detect_events(level)
    assert len(events) == 1


def test_all_events_drops_detected_overlapping_known():
    index = make_hourly_index("2024-04-20", 24 * 60)
    level = pd.Series(1.0, index=index)
    level.iloc[300:600] = 3.0  # dentro da janela conhecida mai-2024
    events = all_events(level)
    assert "mai-2024" in events
    assert len(events) == 1


def test_quiet_series_has_no_events():
    index = make_hourly_index("2025-05-01", 24 * 30)
    assert detect_events(pd.Series(0.8, index=index)) == {}


def test_params_roundtrip(tmp_path):
    path = save_params(_params(), tmp_path)
    assert path.exists()
    loaded = load_latest_params(tmp_path)
    assert loaded.rating.a == 800.0
    assert loaded.lags["11111111"].lag_hours == 24.0


def test_latest_params_picks_highest_version(tmp_path):
    save_params(_params("v1"), tmp_path)
    save_params(_params("v2"), tmp_path)
    assert load_latest_params(tmp_path).version == "v2"


def test_missing_params_raises(tmp_path):
    with pytest.raises(CalibrationError):
        load_latest_params(tmp_path)


def test_fit_station_lag_flux_mode_recovers_true_lag(synthetic_flood):
    from waters.model.rating import reconstructed_inflow

    station = _station("11111111", "inflow", "taquari")
    poa = synthetic_flood["poa_level"]
    window = (
        poa.index[0].strftime("%Y-%m-%d"),
        poa.index[-1].strftime("%Y-%m-%d"),
    )
    # Segunda passada: fluxo reconstruido com o rating verdadeiro
    flux = reconstructed_inflow(poa, synthetic_flood["rating"])
    lag = fit_station_lag(
        station, synthetic_flood["upstream"], flux, {"sintetico": window},
        downstream_kind="flux",
    )
    # lag verdadeiro 24 h, dentro da faixa do taquari (18-36)
    assert lag.lag_hours == pytest.approx(24.0, abs=3.0)


def test_fit_station_lag_without_events_raises(synthetic_flood):
    station = _station("11111111", "inflow", "taquari")
    with pytest.raises(CalibrationError):
        fit_station_lag(station, synthetic_flood["upstream"],
                        synthetic_flood["poa_level"], {})


def test_fit_station_crest_returns_bounded_taus(synthetic_flood):
    station = _station("11111111", "inflow", "taquari")
    poa = synthetic_flood["poa_level"]
    window = (poa.index[0].strftime("%Y-%m-%d"), poa.index[-1].strftime("%Y-%m-%d"))
    crest = fit_station_crest(station, synthetic_flood["upstream"], {"ev": window})
    assert 6.0 <= crest.tau_rise_hours <= 120.0
    assert 6.0 <= crest.tau_recession_hours <= 120.0


def test_fit_station_crest_defaults_on_short_series():
    station = _station("11111111", "inflow", "taquari")
    short = triangular_wave("2025-06-01", 10, base=1.0, peak=2.0, peak_hour=5)
    crest = fit_station_crest(station, short, {"ev": ("2025-06-01", "2025-06-02")})
    assert crest.tau_rise_hours == 24.0
    assert crest.tau_recession_hours == 48.0


def test_calibrate_end_to_end_on_synthetic(synthetic_flood):
    registry = {
        "11111111": _station("11111111", "inflow", "taquari"),
        "87450020": _station("87450020", "target", "guaiba"),
    }
    flows = {"11111111": synthetic_flood["upstream"]}
    params, scores = calibrate(flows, synthetic_flood["poa_level"], registry)
    assert "11111111" in params.lags
    assert params.rating.a > 0
    # hindcast do proprio evento sintetico deve chegar perto do pico real
    assert scores, "esperado ao menos um hindcast"
    assert abs(scores[0].level_error_m) < 0.6


def test_hindcast_event_scores(synthetic_flood):
    registry = {
        "11111111": _station("11111111", "inflow", "taquari"),
        "87450020": _station("87450020", "target", "guaiba"),
    }
    poa = synthetic_flood["poa_level"]
    window = (poa.index[0].strftime("%Y-%m-%d"), poa.index[-1].strftime("%Y-%m-%d"))
    score = hindcast_event(
        "sintetico", window,
        {"11111111": synthetic_flood["upstream"]},
        poa, _params(), registry,
    )
    assert score.observed_peak_m > 0
    assert abs(score.timing_error_h) <= 24.0
