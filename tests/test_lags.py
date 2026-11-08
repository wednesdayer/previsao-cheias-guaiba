"""Estimador de lag recupera defasagem conhecida em series sinteticas."""

import pytest

from conftest import triangular_wave
from waters.domain.errors import InsufficientDataError
from waters.model.lags import clamp_to_bounds, estimate_lag_hours
from waters.model.inflow import shifted_inflow


def _level_from_flow(flow, lag_hours: float):
    """Nivel de reservatorio puro: dh/dt = Q(t-lag) => h = integral acumulada."""
    arriving = shifted_inflow(flow, lag_hours)
    return arriving.cumsum() / 1e6  # escala nao importa para a correlacao


def test_recovers_known_lag_within_one_hour():
    upstream = triangular_wave("2025-06-01", 240, base=100.0, peak=5000.0, peak_hour=72)
    downstream_level = _level_from_flow(upstream, 18.0)
    lag = estimate_lag_hours(upstream, downstream_level)
    assert lag == pytest.approx(18.0, abs=1.0)


def test_zero_lag_detected():
    wave = triangular_wave("2025-06-01", 200, base=50.0, peak=800.0, peak_hour=60)
    assert estimate_lag_hours(wave, _level_from_flow(wave, 0.0)) == pytest.approx(0.0, abs=1.0)


def test_short_series_raises():
    wave = triangular_wave("2025-06-01", 10, base=1.0, peak=5.0, peak_hour=5)
    with pytest.raises(InsufficientDataError):
        estimate_lag_hours(wave, wave)


def test_clamp_to_bounds():
    assert clamp_to_bounds(50.0, "taquari") == (36.0, True)
    assert clamp_to_bounds(2.0, "taquari") == (18.0, True)
    assert clamp_to_bounds(24.0, "taquari") == (24.0, False)
    assert clamp_to_bounds(99.0, "grupo-desconhecido") == (99.0, False)
