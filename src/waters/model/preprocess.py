"""Preparo das series: grade horaria, lacunas, controle de qualidade."""

from __future__ import annotations

import numpy as np
import pandas as pd

from waters.config import settings

SPIKE_LEVEL_M_PER_H = 2.0      # subida/queda de nivel fisicamente implausivel
FLATLINE_MIN_HOURS = 12        # valor identico por tanto tempo = sensor travado


def to_hourly_grid(frame: pd.DataFrame, max_gap_hours: float | None = None) -> pd.DataFrame:
    """Reamostra para grade horaria com interpolacao temporal limitada.

    Lacunas maiores que max_gap_hours permanecem NaN (nao inventamos dados).
    """
    if frame.empty:
        return frame.copy()
    limit = int(max_gap_hours if max_gap_hours is not None else settings.MAX_GAP_INTERP_HOURS)
    hourly = frame.resample("1h").mean()
    return hourly.interpolate(method="time", limit=limit, limit_area="inside")


def qc_series(series: pd.Series) -> pd.Series:
    """Remove spikes e flatlines de uma serie de nivel; devolve copia limpa."""
    if series.empty:
        return series.copy()
    clean = series.copy()

    # Spikes: variacao horaria implausivel — corta o ponto, interpolacao decide depois
    hours = clean.index.to_series().diff().dt.total_seconds() / 3600.0
    rate = clean.diff().abs() / hours.replace(0, np.nan)
    clean[rate > SPIKE_LEVEL_M_PER_H] = np.nan

    # Flatlines longas: sensor travado
    unchanged = clean.diff() == 0
    groups = (~unchanged).cumsum()
    run_hours = clean.groupby(groups).transform(
        lambda g: (g.index[-1] - g.index[0]).total_seconds() / 3600.0
    )
    clean[unchanged & (run_hours >= FLATLINE_MIN_HOURS)] = np.nan
    return clean


def rate_of_change(series: pd.Series) -> pd.Series:
    """Derivada temporal (unidade/h) numa serie ja em grade regular."""
    if len(series) < 2:
        return pd.Series(dtype=float, index=series.index)
    hours = series.index.to_series().diff().dt.total_seconds() / 3600.0
    return series.diff() / hours


def coverage_fraction(series: pd.Series) -> float:
    """Fracao de pontos validos — util para decidir se a serie presta."""
    return 0.0 if series.empty else float(series.notna().mean())
