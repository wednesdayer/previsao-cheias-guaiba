"""Rating e balanco: fechamento de massa e recuperacao da curva conhecida."""

import numpy as np
import pandas as pd
import pytest

from conftest import make_hourly_index
from waters.domain.models import RatingParams
from waters.model.balance import integrate_level, make_qin_function
from waters.model.rating import fit_rating, implied_outflow, predict_qout


def test_steady_state_holds_level():
    """Com Qin == Qout(h0), o nivel nao se move."""
    rating = RatingParams(a=800.0, h0=-2.0, b=1.5, area_km2=470.0)
    h0 = 1.5
    q_eq = predict_qout(h0, rating)
    index = make_hourly_index("2025-06-01", 48)
    qin = pd.Series(q_eq, index=index)
    trajectory = integrate_level(
        h0_m=h0,
        start=index[0].to_pydatetime(),
        qin_fn=make_qin_function(qin),
        rating=rating,
        horizon_hours=47.0,
    )
    assert trajectory.iloc[-1] == pytest.approx(h0, abs=0.01)


def test_inflow_surplus_raises_level():
    rating = RatingParams(a=800.0, h0=-2.0, b=1.5, area_km2=470.0)
    h0 = 1.0
    index = make_hourly_index("2025-06-01", 48)
    qin = pd.Series(predict_qout(h0, rating) + 5000.0, index=index)
    trajectory = integrate_level(
        h0_m=h0,
        start=index[0].to_pydatetime(),
        qin_fn=make_qin_function(qin),
        rating=rating,
        horizon_hours=47.0,
    )
    assert trajectory.iloc[-1] > h0 + 0.5


def test_fit_rating_recovers_known_curve(synthetic_flood):
    """implied_outflow + fit_rating devem reconstituir a curva geradora."""
    poa = synthetic_flood["poa_level"]
    truth = synthetic_flood["rating"]
    from waters.model.inflow import shifted_inflow

    qin = shifted_inflow(synthetic_flood["upstream"], synthetic_flood["lag_hours"])
    qin_hourly = qin.resample("1h").mean()

    qout = implied_outflow(poa, qin_hourly, truth.area_km2)
    fitted = fit_rating(poa, qout, truth.area_km2)

    # Compara as curvas nos estagios do evento (parametrizacao pode divergir)
    stages = np.linspace(float(poa.min()), float(poa.max()), 20)
    predicted = np.array([predict_qout(h, fitted) for h in stages])
    expected = np.array([predict_qout(h, truth) for h in stages])
    relative_error = np.abs(predicted - expected) / expected
    assert relative_error.max() < 0.15


def test_mass_balance_closure(synthetic_flood):
    """Integral de (Qin - Qout) deve igualar a variacao de volume armazenado."""
    from waters.model.inflow import shifted_inflow
    from waters.model.storage import M2_PER_KM2

    poa = synthetic_flood["poa_level"]
    rating = synthetic_flood["rating"]
    qin = shifted_inflow(synthetic_flood["upstream"], synthetic_flood["lag_hours"])
    qin_hourly = qin.resample("1h").mean().reindex(poa.index).dropna()

    qout = pd.Series(
        [predict_qout(h, rating) for h in poa.reindex(qin_hourly.index)],
        index=qin_hourly.index,
    )
    net_volume = float(((qin_hourly - qout) * 3600.0).sum())
    stored = (
        float(poa.reindex(qin_hourly.index).iloc[-1] - poa.reindex(qin_hourly.index).iloc[0])
        * rating.area_km2 * M2_PER_KM2
    )
    # O residuo liquido e pequeno diante do fluxo bruto; o fechamento deve
    # bater dentro de 2% do volume total que passou pelo sistema
    gross_volume = float((qin_hourly * 3600.0).sum())
    assert abs(net_volume - stored) < 0.02 * gross_volume
