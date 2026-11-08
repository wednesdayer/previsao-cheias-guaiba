"""Orquestra a previsao: series -> cenarios -> integracao -> pico.

Passos:
1. Vazoes observadas dos afluentes + nivel de POA (ja em grade horaria, QC ok).
2. Por cenario, extrapola a crista de cada afluente e defasa pelo lag calibrado.
3. Integra o balanco A(h)dh/dt = Qin - Qout(h) por 72 h a partir do nivel atual.
4. Correcao de vies: offset mediano entre hindcast recente e observado.
5. Extrai pico (valor, instante) e tempo acima da cota de inundacao.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from waters.config import settings
from waters.domain.errors import InsufficientDataError
from waters.domain.models import (
    CalibrationParams,
    ForecastResult,
    PeakEstimate,
    ScenarioName,
    Station,
)
from waters.model import crest as crest_mod
from waters.model.balance import integrate_level, make_qin_function
from waters.model.inflow import current_inflow_by_river, total_inflow
from waters.model.rating import predict_qout
from waters.model.routing import routed_inflow

MIN_H0_POINTS = 4


def _scenario_qin(
    flows: dict[str, pd.Series],
    params: CalibrationParams,
    scenario: ScenarioName,
    horizon_hours: float,
) -> pd.Series:
    """Qin(t) total do cenario: observado + crista extrapolada.

    v4 (params.reaches): roteia cada regua-fonte de montante ate o delta por
    Muskingum. Senao: desloca cada regua de entrada pelo lag fixo (v1-v3).
    Nos dois casos a crista e extrapolada antes de propagar.
    """
    if params.reaches:
        extended: dict[str, pd.Series] = {}
        for reach in params.reaches.values():
            series = flows.get(reach.source_code)
            if series is None or series.dropna().empty:
                continue
            crest_params = params.crests.get(reach.source_code)
            if crest_params is not None:
                series = crest_mod.with_forecast(
                    series, crest_params, scenario, horizon_hours + reach.k_hours
                )
            extended[reach.source_code] = series
        frame = routed_inflow(extended, params)
        return frame["total"] if "total" in frame else pd.Series(dtype=float)

    extended = {}
    for code, series in flows.items():
        if code not in params.lags:
            continue
        crest_params = params.crests.get(code)
        if crest_params is None:
            extended[code] = series
            continue
        lag = params.lags[code].lag_hours
        # Extrapola alem do horizonte para cobrir o deslocamento pelo lag
        extended[code] = crest_mod.with_forecast(
            series, crest_params, scenario, horizon_hours + lag
        )
    frame = total_inflow(extended, params.lags)
    return frame["total"] if "total" in frame else pd.Series(dtype=float)


def _find_peak(
    trajectory: pd.Series, scenario: ScenarioName, cota_m: float
) -> PeakEstimate:
    peak_level = float(trajectory.max())
    peak_time = trajectory.idxmax().to_pydatetime()
    above = trajectory[trajectory >= cota_m]
    step_hours = (
        (trajectory.index[1] - trajectory.index[0]).total_seconds() / 3600.0
        if len(trajectory) > 1
        else 0.0
    )
    return PeakEstimate(
        scenario=scenario,
        peak_level_m=round(peak_level, 2),
        peak_time=peak_time,
        above_cota=peak_level >= cota_m,
        hours_above_cota=round(len(above) * step_hours, 1),
    )


def _bias_offset(
    poa_level: pd.Series,
    flows: dict[str, pd.Series],
    params: CalibrationParams,
) -> float:
    """Offset (m) = mediana(observado - hindcast) nas ultimas BIAS_WINDOW_HOURS."""
    valid = poa_level.dropna()
    window_start = valid.index[-1] - pd.Timedelta(hours=settings.BIAS_WINDOW_HOURS)
    observed = valid[valid.index >= window_start]
    if len(observed) < MIN_H0_POINTS:
        return 0.0
    qin_frame = routed_inflow(flows, params) if params.reaches else total_inflow(flows, params.lags)
    qin = qin_frame.get("total", pd.Series(dtype=float)).dropna()
    qin = qin[qin.index >= window_start - pd.Timedelta(hours=1)]
    if qin.empty:
        return 0.0
    try:
        hindcast = integrate_level(
            h0_m=float(observed.iloc[0]),
            start=observed.index[0].to_pydatetime(),
            qin_fn=make_qin_function(qin),
            rating=params.rating,
            horizon_hours=settings.BIAS_WINDOW_HOURS,
            dt_minutes=settings.FORECAST_DT_MINUTES,
            area_curve=params.area_curve,
        )
    except ValueError:
        return 0.0
    aligned = hindcast.reindex(observed.index, method="nearest")
    return float((observed - aligned).median())


def _resolve_target(stations: dict[str, Station], target_code: str | None) -> Station:
    targets = [s for s in stations.values() if s.role == "target"]
    if not targets:
        raise InsufficientDataError("Nenhuma estacao target informada.")
    if target_code is not None:
        for station in targets:
            if station.code == target_code:
                return station
        raise InsufficientDataError(f"Estacao target {target_code} desconhecida.")
    base = [s for s in targets if s.mirror_of is None]
    return base[0] if base else targets[0]


def run_forecast(
    flows_by_station: dict[str, pd.Series],
    poa_level: pd.Series,
    params: CalibrationParams,
    stations: dict[str, Station],
    now: datetime | None = None,
    degraded_stations: list[str] | None = None,
    target_code: str | None = None,
) -> tuple[ForecastResult, dict[ScenarioName, pd.Series]]:
    """Roda a previsao completa; devolve o resultado e as trajetorias h(t).

    poa_level e sempre a serie da regua-base (Gasometro). Se o alvo for uma
    regua derivada (mirror_of), a trajetoria e deslocada pelo offset de datum
    e o pico e comparado a cota de inundacao do alvo.
    """
    valid_poa = poa_level.dropna()
    if len(valid_poa) < MIN_H0_POINTS:
        raise InsufficientDataError("Nivel de Porto Alegre sem leituras suficientes.")

    target = _resolve_target(stations, target_code)
    datum_shift = target.datum_offset_m if target.mirror_of is not None else 0.0

    moment = now or datetime.now(settings.TZ)
    h0 = float(valid_poa.iloc[-1])
    start = valid_poa.index[-1].to_pydatetime()
    cota = target.cota_inundacao_m

    bias = _bias_offset(poa_level, flows_by_station, params)

    trajectories: dict[ScenarioName, pd.Series] = {}
    peaks: dict[ScenarioName, PeakEstimate] = {}
    for scenario in ScenarioName:
        qin = _scenario_qin(
            flows_by_station, params, scenario, settings.FORECAST_HORIZON_HOURS
        ).dropna()
        qin = qin[qin.index >= pd.Timestamp(start) - pd.Timedelta(hours=6)]
        if qin.empty:
            raise InsufficientDataError(f"Cenario {scenario.value} sem Qin utilizavel.")
        raw = integrate_level(
            h0_m=h0,
            start=start,
            qin_fn=make_qin_function(qin),
            rating=params.rating,
            area_curve=params.area_curve,
        )
        # Vies em rampa: 0 no instante inicial (a curva conecta no nivel
        # observado) crescendo ate o valor cheio em BIAS_RAMP_HOURS. Evita o
        # "degrau" e reflete que a deriva do modelo se acumula com o tempo.
        hours = ((raw.index - raw.index[0]) / pd.Timedelta(hours=1)).to_numpy()
        ramp = (hours / settings.BIAS_RAMP_HOURS).clip(max=1.0)
        trajectory = raw + bias * ramp + datum_shift
        trajectories[scenario] = trajectory
        peaks[scenario] = _find_peak(trajectory, scenario, cota)

    active_codes = (
        {r.source_code for r in params.reaches.values()}
        if params.reaches else set(params.lags)
    )
    inflow_by_river = current_inflow_by_river(flows_by_station, stations, codes=active_codes)
    result = ForecastResult(
        generated_at=moment,
        params_version=params.version,
        target_code=target.code,
        h0_m=round(h0 + datum_shift, 2),
        bias_offset_m=round(bias, 3),
        inflow_now_m3s={k: round(v, 0) for k, v in inflow_by_river.items()},
        inflow_total_m3s=round(sum(inflow_by_river.values()), 0),
        outflow_now_m3s=round(predict_qout(h0, params.rating), 0),
        peaks=peaks,
        degraded_stations=degraded_stations or [],
    )
    return result, trajectories
