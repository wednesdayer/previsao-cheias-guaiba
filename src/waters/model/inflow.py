"""Composicao da vazao de entrada no Guaiba a partir dos afluentes."""

from __future__ import annotations

import pandas as pd

from waters.domain.models import LagParams, Station


def shifted_inflow(series: pd.Series, lag_hours: float) -> pd.Series:
    """Desloca a vazao do afluente pelo tempo de viagem ate o Guaiba."""
    if series.empty:
        return series.copy()
    shifted = series.copy()
    shifted.index = shifted.index + pd.Timedelta(hours=lag_hours)
    return shifted


def total_inflow(
    flows_by_station: dict[str, pd.Series],
    lags: dict[str, LagParams],
    freq: str = "1h",
) -> pd.DataFrame:
    """Soma as vazoes defasadas numa grade comum.

    Devolve um frame com uma coluna por estacao (ja defasada) e a coluna
    'total'. NaN de uma estacao vira 0 na soma apenas se as demais cobrem o
    instante — instantes sem nenhuma estacao valida ficam NaN.
    """
    if not flows_by_station:
        return pd.DataFrame()

    # soma apenas as estacoes com lag definido (o conjunto de entrada); ignora
    # reguas extras que possam vir em flows (ex.: fontes de roteamento no v4),
    # evitando dupla contagem do mesmo rio.
    shifted: dict[str, pd.Series] = {}
    for code, series in flows_by_station.items():
        if code not in lags:
            continue
        shifted[code] = shifted_inflow(series.dropna(), lags[code].lag_hours).resample(freq).mean()
    if not shifted:
        return pd.DataFrame()

    frame = pd.concat(shifted, axis=1)
    frame.columns = list(shifted)
    valid_any = frame.notna().any(axis=1)
    frame["total"] = frame.fillna(0.0).sum(axis=1).where(valid_any)
    return frame


def current_inflow_by_river(
    flows_by_station: dict[str, pd.Series],
    stations: dict[str, Station],
    codes: set[str] | None = None,
) -> dict[str, float]:
    """Ultima vazao valida de cada afluente, agregada por rio (m3/s).

    Se `codes` for dado, agrega apenas essas estacoes (o conjunto de entrada
    ativo: reguas com lag no v1-v3, ou fontes de roteamento no v4). Evita
    somar duas reguas do mesmo rio quando flows traz reguas extras.
    """
    by_river: dict[str, float] = {}
    for code, series in flows_by_station.items():
        if codes is not None and code not in codes:
            continue
        valid = series.dropna()
        if valid.empty or code not in stations:
            continue
        river = stations[code].river_group
        by_river[river] = by_river.get(river, 0.0) + float(valid.iloc[-1])
    return by_river
