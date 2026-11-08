"""Ajuste dos parametros de crista (tau de subida e de recessao) por estacao.

tau_rise: nos trechos de subida dos eventos, a taxa dQ/dt decai ~exponencial;
regressao log-linear da taxa da o tau. tau_recession: log-linear de
(Q - baseflow) no trecho de descida.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from waters.domain.models import CrestParams, Station
from waters.model.preprocess import rate_of_change

logger = logging.getLogger(__name__)

DEFAULT_TAU_RISE_H = 24.0
DEFAULT_TAU_RECESSION_H = 48.0
TAU_BOUNDS_H = (6.0, 120.0)
MIN_LIMB_POINTS = 12


def _fit_exponential_tau(hours: np.ndarray, values: np.ndarray) -> float | None:
    """tau de y = y0*exp(-t/tau) por regressao em log(y); None se nao der."""
    mask = values > 0
    if mask.sum() < MIN_LIMB_POINTS:
        return None
    slope, _ = np.polyfit(hours[mask], np.log(values[mask]), 1)
    if slope >= 0:
        return None
    tau = -1.0 / slope
    low, high = TAU_BOUNDS_H
    return float(np.clip(tau, low, high))


def _event_taus(series: pd.Series) -> tuple[float | None, float | None]:
    """(tau_rise, tau_recession) de um evento na estacao, se ajustaveis."""
    valid = series.dropna()
    if len(valid) < MIN_LIMB_POINTS * 2:
        return None, None
    peak_time = valid.idxmax()
    rising = valid[:peak_time]
    falling = valid[peak_time:]

    tau_rise = None
    rates = rate_of_change(rising).dropna()
    rates = rates[rates > 0]
    if len(rates) >= MIN_LIMB_POINTS:
        hours = (rates.index - rates.index[0]).total_seconds() / 3600.0
        tau_rise = _fit_exponential_tau(hours.to_numpy(), rates.to_numpy())

    tau_recession = None
    if len(falling) >= MIN_LIMB_POINTS:
        baseflow = float(valid.quantile(0.25))
        excess = (falling - baseflow).dropna()
        hours = (excess.index - excess.index[0]).total_seconds() / 3600.0
        tau_recession = _fit_exponential_tau(hours.to_numpy(), excess.to_numpy())

    return tau_rise, tau_recession


def fit_station_crest(
    station: Station,
    flow: pd.Series,
    events: dict[str, tuple[str, str]],
) -> CrestParams:
    """Mediana dos taus por evento; sem ajuste possivel, usa defaults."""
    rises, recessions = [], []
    for name, (start, end) in events.items():
        tau_rise, tau_recession = _event_taus(flow.loc[start:end])
        if tau_rise is not None:
            rises.append(tau_rise)
        if tau_recession is not None:
            recessions.append(tau_recession)
        logger.debug(
            "crest %s evento %s: rise=%s recession=%s",
            station.code, name, tau_rise, tau_recession,
        )

    return CrestParams(
        station_code=station.code,
        tau_rise_hours=float(np.median(rises)) if rises else DEFAULT_TAU_RISE_H,
        tau_recession_hours=(
            float(np.median(recessions)) if recessions else DEFAULT_TAU_RECESSION_H
        ),
    )
