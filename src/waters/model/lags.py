"""Estimativa de defasagem (lag) afluente -> Porto Alegre por correlacao cruzada.

Fisica do reservatorio: A*dh/dt = Qin(t-lag) - Qout(h). Logo o sinal que
chega defasado ao Guaiba e o VALOR da vazao a montante, e ele aparece na
TAXA de variacao do nivel em POA — correlacionamos Q(t) com dh/dt(t+lag).
Usar dh/dt do lado de POA tambem elimina datum e tendencia lenta.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from waters.config import settings
from waters.domain.errors import InsufficientDataError
from waters.model.preprocess import rate_of_change

MIN_VALID_HOURS = 48


def estimate_lag_hours(
    upstream: pd.Series,
    downstream: pd.Series,
    max_lag_hours: float = 72.0,
    downstream_kind: str = "level",
) -> float:
    """Lag (h) que maximiza a correlacao upstream -> downstream.

    downstream_kind="level": correlaciona Q com dh/dt (primeira passada,
    tem vies porque o fluxo liquido inclui -Qout). downstream_kind="flux":
    correlaciona Q com o fluxo de entrada reconstruido A*dh/dt + Qout(h)
    (segunda passada, sem vies). Series em grade horaria no mesmo fuso.
    """
    du = upstream.rename("du")
    dp = (
        rate_of_change(downstream) if downstream_kind == "level" else downstream
    ).rename("dp")
    joined = pd.concat([du, dp], axis=1, join="inner").dropna()
    if len(joined) < MIN_VALID_HOURS:
        raise InsufficientDataError(
            f"So {len(joined)} horas validas em comum; minimo {MIN_VALID_HOURS}."
        )

    du_values = joined["du"].to_numpy()
    dp_values = joined["dp"].to_numpy()
    max_shift = int(max_lag_hours)

    best_lag, best_corr = 0, -np.inf
    for shift in range(0, max_shift + 1):
        if shift >= len(joined) - MIN_VALID_HOURS // 2:
            break
        upstream_part = du_values[: len(du_values) - shift] if shift else du_values
        poa_part = dp_values[shift:]
        if np.std(upstream_part) == 0 or np.std(poa_part) == 0:
            continue
        corr = float(np.corrcoef(upstream_part, poa_part)[0, 1])
        if corr > best_corr:
            best_lag, best_corr = shift, corr

    if not np.isfinite(best_corr):
        raise InsufficientDataError("Series sem variancia suficiente para correlacao.")
    return float(best_lag)


def clamp_to_bounds(lag_hours: float, river_group: str) -> tuple[float, bool]:
    """Aplica a faixa de plausibilidade fisica; devolve (lag, foi_ajustado)."""
    bounds = settings.LAG_BOUNDS_HOURS.get(river_group)
    if bounds is None:
        return lag_hours, False
    low, high = bounds
    if lag_hours < low:
        return low, True
    if lag_hours > high:
        return high, True
    return lag_hours, False
