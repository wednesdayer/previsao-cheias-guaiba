"""Curva cota-area A(h): interpolacao, validacao e efeito no balanco."""

import numpy as np
import pandas as pd
import pytest

from conftest import make_hourly_index
from waters.config.registry import load_stage_area_curve
from waters.domain.models import RatingParams, StageAreaCurve
from waters.model.area_curve import area_km2_at, area_m2_at
from waters.model.balance import integrate_level, make_qin_function
from waters.model.rating import predict_qout
from waters.model.storage import area_m2_at_stage


def _curve() -> StageAreaCurve:
    return StageAreaCurve(
        levels_m=[0.0, 1.0, 3.0, 5.0], areas_km2=[470.0, 500.0, 830.0, 1400.0]
    )


def test_interpolates_between_points():
    c = _curve()
    assert area_km2_at(0.0, c) == pytest.approx(470.0)
    assert area_km2_at(2.0, c) == pytest.approx(665.0)   # meio de 500..830
    assert area_m2_at(2.0, c) == pytest.approx(665.0 * 1e6)


def test_clamps_outside_range():
    c = _curve()
    assert area_km2_at(-3.0, c) == pytest.approx(470.0)   # borda inferior
    assert area_km2_at(9.0, c) == pytest.approx(1400.0)   # borda superior


def test_rejects_non_monotonic_area():
    with pytest.raises(ValueError):
        StageAreaCurve(levels_m=[0.0, 1.0, 2.0], areas_km2=[500.0, 400.0, 600.0])


def test_rejects_unsorted_levels():
    with pytest.raises(ValueError):
        StageAreaCurve(levels_m=[0.0, 2.0, 1.0], areas_km2=[500.0, 600.0, 700.0])


def test_config_curve_loads_and_is_increasing():
    c = load_stage_area_curve()
    assert c.areas_km2[0] == pytest.approx(470.0)
    assert c.areas_km2[-1] > c.areas_km2[0]           # cresce com a cota
    assert list(c.levels_m) == sorted(c.levels_m)


def test_storage_uses_curve_when_given():
    rating = RatingParams(a=800.0, h0=-2.0, b=1.5, area_km2=470.0)
    c = _curve()
    # com curva: A(5m)=1400 km2; sem curva (linear k=0): 470 km2
    assert area_m2_at_stage(5.0, rating, c) == pytest.approx(1400.0 * 1e6)
    assert area_m2_at_stage(5.0, rating, None) == pytest.approx(470.0 * 1e6)


def test_larger_area_slows_level_rise():
    """Mais area => mesmo superavit de vazao sobe menos o nivel."""
    rating = RatingParams(a=800.0, h0=-2.0, b=1.5, area_km2=470.0)
    idx = make_hourly_index("2025-06-01", 48)
    qin = pd.Series(predict_qout(2.0, rating) + 8000.0, index=idx)
    fn = make_qin_function(qin)

    small = integrate_level(2.0, idx[0].to_pydatetime(), fn, rating, horizon_hours=47.0)
    big_curve = StageAreaCurve(levels_m=[0.0, 6.0], areas_km2=[2000.0, 2000.0])
    big = integrate_level(
        2.0, idx[0].to_pydatetime(), fn, rating, horizon_hours=47.0, area_curve=big_curve
    )
    assert big.iloc[-1] < small.iloc[-1]   # area maior => subiu menos
