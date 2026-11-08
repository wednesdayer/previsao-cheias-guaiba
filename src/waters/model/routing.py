"""Roteamento de onda de cheia por Muskingum (canal aberto).

Substitui o deslocamento por lag fixo: propaga um hidrograma de montante para
jusante com tempo de viagem (K) e atenuacao (X), trabalhando em vazao (m3/s) —
imune ao datum. Um trecho longo e roteado como uma cascata de sub-trechos para
estabilidade numerica (coeficientes de Muskingum bem-comportados quando
K_sub ~ dt).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import lfilter, lfilter_zi

from waters.domain.models import CalibrationParams, ReachParams


def _median_dt_hours(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 1.0
    secs = pd.Series(index).diff().dropna().dt.total_seconds()
    return float(secs.median() / 3600.0) if not secs.empty else 1.0


def muskingum_route(
    inflow: pd.Series,
    k_hours: float,
    x: float,
    dt_hours: float | None = None,
    n_sub: int | None = None,
) -> pd.Series:
    """Roteia o hidrograma de entrada por um trecho (K,X). Devolve o de saida.

    A serie de saida fica na mesma grade temporal da entrada — o pico aparece
    mais tarde e mais baixo (atrasado e atenuado). Conserva massa.
    """
    valid = inflow.dropna()
    if len(valid) < 3 or k_hours <= 0:
        return inflow.copy()

    dt = dt_hours if dt_hours is not None else _median_dt_hours(valid.index)
    if dt <= 0:
        return inflow.copy()
    # cascata: cada sub-trecho com K_sub ~ dt mantem C0,C2 >= 0 (sem oscilacao)
    n = n_sub if n_sub is not None else max(1, int(round(k_hours / dt)))
    k_sub = k_hours / n

    denom = 2.0 * k_sub * (1.0 - x) + dt
    c0 = (dt - 2.0 * k_sub * x) / denom
    c1 = (dt + 2.0 * k_sub * x) / denom
    c2 = (2.0 * k_sub * (1.0 - x) - dt) / denom

    b = [c0, c1]
    a = [1.0, -c2]
    arr = valid.to_numpy(dtype=float)
    zi = lfilter_zi(b, a) * arr[0]
    for _ in range(n):
        arr, _ = lfilter(b, a, arr, zi=zi)
        zi = lfilter_zi(b, a) * arr[0]
        arr = np.clip(arr, 0.0, None)
    return pd.Series(arr, index=valid.index, name=inflow.name)


def route_source(series: pd.Series, reach: ReachParams, freq: str = "1h") -> pd.Series:
    """Reamostra e roteia a regua-fonte pelo trecho ate o delta."""
    grid = series.dropna().resample(freq).mean().interpolate(
        method="time", limit=6, limit_area="inside"
    )
    return muskingum_route(grid, reach.k_hours, reach.x)


def routed_inflow(
    flows_by_station: dict[str, pd.Series],
    params: CalibrationParams,
    freq: str = "1h",
) -> pd.DataFrame:
    """Soma as vazoes roteadas ate o delta, uma coluna por rio + 'total'.

    Usa uma regua-fonte por rio (a de montante confiavel), definida em
    params.reaches. Rios sem trecho de roteamento sao ignorados aqui (o
    chamador cai no total_inflow por lag).
    """
    routed: dict[str, pd.Series] = {}
    for reach in params.reaches.values():
        src = flows_by_station.get(reach.source_code)
        if src is None or src.dropna().empty:
            continue
        routed[reach.river_group] = route_source(src, reach, freq=freq)
    if not routed:
        return pd.DataFrame()
    frame = pd.concat(routed, axis=1)
    frame.columns = list(routed)
    valid_any = frame.notna().any(axis=1)
    frame["total"] = frame.fillna(0.0).sum(axis=1).where(valid_any)
    return frame
