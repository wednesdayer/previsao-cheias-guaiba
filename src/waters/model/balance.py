"""Integrador do balanco de massa do Guaiba: A(h) * dh/dt = Qin(t) - Qout(h).

RK4 explicito com passo fixo. Qin vem como funcao do tempo (serie prevista
interpolada); Qout vem da curva de descarga calibrada.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from waters.config import settings
from waters.domain.models import RatingParams, StageAreaCurve
from waters.model.rating import predict_qout
from waters.model.storage import area_m2_at_stage

QinFunction = Callable[[datetime], float]


def make_qin_function(qin_series: pd.Series) -> QinFunction:
    """Interpola a serie de Qin no tempo; fora do suporte usa o extremo."""
    valid = qin_series.dropna()
    if valid.empty:
        raise ValueError("Serie de Qin vazia — nada para integrar.")
    # as_unit('ns') fixa a unidade: pandas 2 pode indexar em us e o .value do
    # Timestamp e sempre ns — misturar as escalas quebra a interpolacao
    times = valid.index.as_unit("ns").view("int64").astype(float)
    values = valid.to_numpy(dtype=float)

    def qin_at(moment: datetime) -> float:
        t = float(pd.Timestamp(moment).as_unit("ns").value)
        return float(np.interp(t, times, values))

    return qin_at


def _dh_dt(
    h: float, qin: float, rating: RatingParams, curve: StageAreaCurve | None
) -> float:
    """Taxa de variacao do nivel (m/s) no estagio h."""
    return (qin - predict_qout(h, rating)) / area_m2_at_stage(h, rating, curve)


def integrate_level(
    h0_m: float,
    start: datetime,
    qin_fn: QinFunction,
    rating: RatingParams,
    horizon_hours: float = settings.FORECAST_HORIZON_HOURS,
    dt_minutes: float = settings.FORECAST_DT_MINUTES,
    area_curve: StageAreaCurve | None = None,
) -> pd.Series:
    """Integra h(t) por RK4 e devolve a trajetoria em serie temporal."""
    dt_s = dt_minutes * 60.0
    steps = int(horizon_hours * 60.0 / dt_minutes)

    times = [pd.Timestamp(start)]
    levels = [h0_m]
    h = h0_m
    moment = pd.Timestamp(start)

    for _ in range(steps):
        half = moment + timedelta(seconds=dt_s / 2)
        full = moment + timedelta(seconds=dt_s)
        k1 = _dh_dt(h, qin_fn(moment), rating, area_curve)
        k2 = _dh_dt(h + 0.5 * dt_s * k1, qin_fn(half), rating, area_curve)
        k3 = _dh_dt(h + 0.5 * dt_s * k2, qin_fn(half), rating, area_curve)
        k4 = _dh_dt(h + dt_s * k3, qin_fn(full), rating, area_curve)
        h = h + (dt_s / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        moment = full
        times.append(moment)
        levels.append(h)

    return pd.Series(levels, index=pd.DatetimeIndex(times, name="timestamp"), name="h_m")
