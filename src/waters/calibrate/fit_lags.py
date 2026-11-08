"""Ajuste das defasagens afluente -> POA por evento, com mediana e faixas."""

from __future__ import annotations

import logging
import statistics

import pandas as pd

from waters.domain.errors import CalibrationError, InsufficientDataError
from waters.domain.models import LagParams, Station
from waters.model.lags import clamp_to_bounds, estimate_lag_hours

logger = logging.getLogger(__name__)


def fit_station_lag(
    station: Station,
    upstream_flow: pd.Series,
    downstream: pd.Series,
    events: dict[str, tuple[str, str]],
    downstream_kind: str = "level",
) -> LagParams:
    """Lag por evento -> mediana; valores fora da faixa fisica sao ajustados.

    downstream pode ser o nivel de POA (primeira passada) ou o fluxo de
    entrada reconstruido (segunda passada, downstream_kind="flux").
    """
    per_event: dict[str, float] = {}
    for name, (start, end) in events.items():
        window_up = upstream_flow.loc[start:end]
        window_poa = downstream.loc[start:end]
        try:
            lag = estimate_lag_hours(window_up, window_poa, downstream_kind=downstream_kind)
        except InsufficientDataError as exc:
            logger.warning("lag %s evento %s: %s", station.code, name, exc)
            continue
        clamped, adjusted = clamp_to_bounds(lag, station.river_group)
        if adjusted:
            logger.info(
                "lag %s evento %s: %.0f h fora da faixa, ajustado para %.0f h",
                station.code, name, lag, clamped,
            )
        per_event[name] = clamped

    if not per_event:
        raise CalibrationError(f"Nenhum evento rendeu lag para {station.code}")

    values = list(per_event.values())
    return LagParams(
        station_code=station.code,
        lag_hours=statistics.median(values),
        lag_spread_hours=(max(values) - min(values)) / 2.0 if len(values) > 1 else 3.0,
        per_event_hours=per_event,
    )
