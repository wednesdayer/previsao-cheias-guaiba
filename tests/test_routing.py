"""Roteamento Muskingum: atenuacao, atraso, conservacao de massa, recuperar K,X."""

import numpy as np
import pandas as pd
import pytest

from conftest import triangular_wave
from waters.model.routing import muskingum_route


def test_routing_delays_and_attenuates_peak():
    wave = triangular_wave("2025-06-01", 240, base=500.0, peak=8000.0, peak_hour=72)
    out = muskingum_route(wave, k_hours=24.0, x=0.2)
    # pico de saida menor (atenuado) e mais tarde (atrasado) que o de entrada
    assert out.max() < wave.max()
    assert out.idxmax() > wave.idxmax()


def test_routing_conserves_mass():
    wave = triangular_wave("2025-06-01", 300, base=400.0, peak=6000.0, peak_hour=80)
    out = muskingum_route(wave, k_hours=18.0, x=0.15)
    # volume (integral) preservado dentro de ~2% (bordas causam pequena perda)
    vin = float(wave.sum()); vout = float(out.sum())
    assert abs(vout - vin) / vin < 0.02


def test_routing_no_negative_flows():
    wave = triangular_wave("2025-06-01", 200, base=100.0, peak=9000.0, peak_hour=40)
    out = muskingum_route(wave, k_hours=30.0, x=0.35)
    assert (out >= 0).all()


def test_zero_k_returns_input():
    wave = triangular_wave("2025-06-01", 100, base=100.0, peak=2000.0, peak_hour=40)
    out = muskingum_route(wave, k_hours=0.0, x=0.2)
    pd.testing.assert_series_equal(out, wave)


def test_recovers_known_k_by_peak_lag():
    """Rotear com K conhecido produz atraso de pico coerente com K."""
    wave = triangular_wave("2025-06-01", 400, base=300.0, peak=7000.0, peak_hour=100)
    for k in (12.0, 24.0, 36.0):
        out = muskingum_route(wave, k_hours=k, x=0.2)
        lag_h = (out.idxmax() - wave.idxmax()).total_seconds() / 3600.0
        # o atraso do pico deve crescer com K e ficar na ordem de K (±50%)
        assert 0.5 * k <= lag_h <= 1.5 * k


def test_routing_beats_pure_lag_on_attenuation():
    """Roteamento reduz o pico; deslocamento puro (lag) mantem o pico."""
    from waters.model.inflow import shifted_inflow
    wave = triangular_wave("2025-06-01", 240, base=500.0, peak=8000.0, peak_hour=72)
    routed = muskingum_route(wave, k_hours=24.0, x=0.2)
    lagged = shifted_inflow(wave, 24.0)
    assert routed.max() < lagged.max() * 0.99   # roteado atenua, lag nao


def _cal_params_with_reaches(reaches):
    from datetime import datetime
    from waters.config import settings
    from waters.domain.models import CalibrationParams, RatingParams
    return CalibrationParams(
        version="t", generated_at=datetime(2026, 1, 1, tzinfo=settings.TZ),
        events=["ev"], lags={}, crests={},
        rating=RatingParams(a=800.0, h0=-2.0, b=1.5, area_km2=470.0),
        reaches=reaches,
    )


def test_routed_inflow_sums_routed_sources():
    from waters.domain.models import ReachParams
    from waters.model.routing import routed_inflow
    up_t = triangular_wave("2025-06-01", 200, base=300.0, peak=5000.0, peak_hour=60)
    up_j = triangular_wave("2025-06-01", 200, base=800.0, peak=3000.0, peak_hour=80)
    reaches = {
        "taquari": ReachParams(reach_id="taquari->delta", source_code="T",
                               river_group="taquari", length_km=100, k_hours=18, x=0.2),
        "jacui": ReachParams(reach_id="jacui->delta", source_code="J",
                             river_group="jacui", length_km=150, k_hours=24, x=0.2),
    }
    params = _cal_params_with_reaches(reaches)
    frame = routed_inflow({"T": up_t, "J": up_j}, params)
    assert set(frame.columns) >= {"taquari", "jacui", "total"}
    # total = soma das colunas de rio, em cada instante
    row = frame.dropna().iloc[100]
    assert row["total"] == pytest.approx(row["taquari"] + row["jacui"], rel=1e-6)


def test_fit_reach_recovers_known_k():
    from waters.calibrate.fit_routing import fit_reach
    up = triangular_wave("2024-05-01", 400, base=300.0, peak=7000.0, peak_hour=120)
    down = muskingum_route(up, k_hours=20.0, x=0.2)   # jusante sintetico
    events = {"ev": ("2024-05-01", "2024-05-17")}
    result = fit_reach(up, down, events, length_km=60.0)
    assert result is not None
    k, x, nse = result
    assert k == pytest.approx(20.0, abs=4.0)   # recupera K
    assert nse > 0.95                          # ajuste quase perfeito
