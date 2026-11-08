"""Extrapolacao de crista: projeta o futuro proximo de um hidrograma.

Se a estacao ainda sobe, a taxa de subida decai exponencialmente
(dQ/dt = r0 * exp(-t/tau)) ate a crista; depois recessao exponencial em
direcao ao patamar pre-cheia. Se ja desce, so recessao.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from waters.domain.models import CrestParams, ScenarioName

RISE_WINDOW_HOURS = 6          # janela para medir a taxa de subida atual
BASEFLOW_QUANTILE = 0.25       # patamar de recessao: quantil baixo dos ultimos dias
SCENARIO_TAU_FACTOR: dict[ScenarioName, float] = {
    ScenarioName.OTIMISTA: 0.7,
    ScenarioName.CENTRAL: 1.0,
    ScenarioName.PESSIMISTA: 1.4,
}
PESSIMISTA_CREST_HOLD_HOURS = 6.0


def current_rise_rate(series: pd.Series) -> float:
    """Taxa media (unidade/h) nas ultimas RISE_WINDOW_HOURS; negativa se desce."""
    valid = series.dropna()
    if len(valid) < 2:
        return 0.0
    cutoff = valid.index[-1] - pd.Timedelta(hours=RISE_WINDOW_HOURS)
    window = valid[valid.index >= cutoff]
    if len(window) < 2:
        window = valid.iloc[-2:]
    span_hours = (window.index[-1] - window.index[0]).total_seconds() / 3600.0
    if span_hours <= 0:
        return 0.0
    return float((window.iloc[-1] - window.iloc[0]) / span_hours)


def extrapolate(
    series: pd.Series,
    crest: CrestParams,
    scenario: ScenarioName,
    horizon_hours: float,
    freq_minutes: float = 60.0,
) -> pd.Series:
    """Serie futura (apos a ultima observacao) para o cenario pedido."""
    valid = series.dropna()
    if valid.empty:
        return pd.Series(dtype=float)

    last_time = valid.index[-1]
    last_value = float(valid.iloc[-1])
    rate = current_rise_rate(valid)
    # Alvo da recessao: nunca acima do valor atual (senao a "descida" subiria)
    baseflow = min(float(valid.quantile(BASEFLOW_QUANTILE)), last_value)
    tau_rise = crest.tau_rise_hours * SCENARIO_TAU_FACTOR[scenario]
    hold_hours = (
        PESSIMISTA_CREST_HOLD_HOURS if scenario is ScenarioName.PESSIMISTA else 0.0
    )

    steps = int(horizon_hours * 60.0 / freq_minutes)
    hours = np.arange(1, steps + 1) * (freq_minutes / 60.0)
    future_index = last_time + pd.to_timedelta(hours, unit="h")

    if rate > 0:
        # Subida integrada: v(t) = v0 + r0*tau*(1 - exp(-t/tau)); crista = v0 + r0*tau
        crest_gain = rate * tau_rise
        rising = last_value + crest_gain * (1.0 - np.exp(-hours / tau_rise))
        crest_value = last_value + crest_gain
        # Apos ~4*tau a subida acabou; segura a crista (pessimista) e entra em recessao
        crest_end = 4.0 * tau_rise + hold_hours
        recession_hours = np.clip(hours - crest_end, 0.0, None)
        receding = baseflow + (crest_value - baseflow) * np.exp(
            -recession_hours / crest.tau_recession_hours
        )
        values = np.where(hours <= crest_end, rising, receding)
        values = np.minimum(values, crest_value)
    else:
        values = baseflow + (last_value - baseflow) * np.exp(
            -hours / crest.tau_recession_hours
        )

    return pd.Series(values, index=future_index, name=series.name)


def with_forecast(
    series: pd.Series,
    crest: CrestParams,
    scenario: ScenarioName,
    horizon_hours: float,
) -> pd.Series:
    """Observado + extrapolado, contiguos, sem duplicar o instante da emenda."""
    future = extrapolate(series, crest, scenario, horizon_hours)
    return pd.concat([series.dropna(), future])
