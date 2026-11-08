"""Acesso a dados para o dashboard, com cache TTL do Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from waters.config import settings
from pathlib import Path

from waters.config.params_io import (
    describe_params,
    discover_param_files,
    load_latest_params,
    load_params_file,
)
from waters.config.registry import (
    get_registry,
    inflow_stations,
    target_station,
    target_stations,
)
from waters.domain.models import CalibrationParams, ForecastResult, ScenarioName
from waters.ingest.service import refresh_all
from waters.model.forecast import run_forecast
from waters.model.preprocess import qc_series, to_hourly_grid

REFRESH_TTL_S = 300


@st.cache_data(ttl=REFRESH_TTL_S, show_spinner="Buscando telemetria ANA...")
def load_series() -> dict:
    """Atualiza todas as estacoes e devolve series prontas para o modelo.

    Retorna dict picklavel: frames horarios, niveis atuais e metadados.
    """
    registry = get_registry()
    results = refresh_all(list(registry))

    flows: dict[str, pd.Series] = {}
    levels_now: dict[str, dict] = {}
    degraded: list[str] = []

    for code, result in results.items():
        station = result.station
        hourly = to_hourly_grid(
            result.frame,
            max_gap_hours=settings.SPARSE_MAX_GAP_HOURS if station.sparse else None,
        )
        nivel = result.frame["nivel_m"].dropna()
        levels_now[code] = {
            "name": station.name,
            "river": station.river,
            "role": station.role,
            "nivel_m": float(nivel.iloc[-1]) if not nivel.empty else None,
            "nivel_24h_m": (
                float(nivel[nivel.index <= nivel.index[-1] - pd.Timedelta(hours=24)].iloc[-1])
                if len(nivel[nivel.index <= nivel.index[-1] - pd.Timedelta(hours=24)]) > 0
                else None
            ),
            "cota_m": station.cota_inundacao_m,
            "updated": nivel.index[-1].isoformat() if not nivel.empty else None,
            "stale": result.is_stale,
            "source": result.source,
        }
        is_mirror = result.source.startswith("espelho")
        if result.is_stale or (result.source != "ana" and not is_mirror):
            degraded.append(station.name)
        # inclui qualquer regua com vazao (entrada + montante), pois o v4
        # roteia as reguas-fonte de montante. total_inflow/routed_inflow
        # selecionam so as suas estacoes, sem dupla contagem.
        if station.has_vazao and not hourly["vazao_m3s"].dropna().empty:
            flows[code] = hourly["vazao_m3s"]

    def clean_level(code: str) -> pd.Series:
        if code not in results:
            return pd.Series(dtype=float)
        frame = to_hourly_grid(results[code].frame)
        return qc_series(frame["nivel_m"]).interpolate(
            method="time", limit=settings.MAX_GAP_INTERP_HOURS, limit_area="inside"
        )

    target = target_station(registry)
    poa_level = clean_level(target.code)

    # Reguas-alvo com telemetria propria (ex.: Cais Maua) exibem a serie real
    # delas; a base ancora tudo. Reguas puramente derivadas nao entram aqui.
    observed_by_target = {target.code: poa_level}
    for station in target_stations(registry):
        if station.own_telemetry:
            observed_by_target[station.code] = clean_level(station.code)

    missing_inflows = [
        s.name for s in inflow_stations(registry) if s.code not in flows
    ]
    return {
        "flows": flows,
        "poa_level": poa_level,
        "observed_by_target": observed_by_target,
        "levels_now": levels_now,
        "degraded": sorted(set(degraded + missing_inflows)),
    }


@st.cache_resource(show_spinner="Carregando topografia...")
def load_inundation():
    """Carrega o pre-computo de inundacao (uma vez por processo)."""
    from waters.model.inundation import load_inundation as _load
    return _load()


@st.cache_data(ttl=3600, show_spinner="Preparando mapa de inundação...")
def inundation_frames(
    step_m: float = 0.25, max_width: int = 800
) -> tuple[list[dict], list[float]]:
    """Overlays PNG (data URI) por cota, para o slider client-side do Plotly.

    Cada frame: {level, uri, area_km2}. Pre-computado uma vez (cacheado) para
    a troca de nivel ser instantanea no navegador, sem rerun do Streamlit.
    """
    import base64
    from io import BytesIO

    import numpy as np
    from PIL import Image

    from waters.model.inundation import flooded_area_km2, overlay_rgba

    inund = load_inundation()
    levels = [round(float(x), 2)
              for x in np.arange(inund.gauge_min, inund.gauge_max + 1e-9, step_m)]
    frames, bounds = [], None
    for g in levels:
        rgba, bounds = overlay_rgba(inund, g, depth_gradient=True, max_width=max_width)
        buf = BytesIO()
        Image.fromarray(rgba, mode="RGBA").save(buf, format="PNG")
        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        frames.append({"level": g, "uri": uri, "area_km2": round(flooded_area_km2(inund, g))})
    return frames, bounds


@st.cache_data(ttl=REFRESH_TTL_S)
def list_models() -> list[dict]:
    """Modelos selecionaveis (operacional + experimentais), operacional 1o."""
    models = []
    for path in discover_param_files():
        params = load_params_file(path)
        operational = path.parent.name != "experimental"
        models.append(
            {"key": str(path), "label": describe_params(params, path), "operational": operational}
        )
    models.sort(key=lambda m: (not m["operational"], m["label"]))
    return models


@st.cache_data(ttl=REFRESH_TTL_S, show_spinner="Rodando o modelo...")
def compute_forecast(
    _cache_key: str,
    target_code: str,
    model_key: str,
) -> tuple[ForecastResult, dict[ScenarioName, pd.Series], CalibrationParams]:
    """Roda a previsao sobre os dados mais recentes, para a regua e modelo pedidos."""
    data = load_series()
    params = load_params_file(Path(model_key))
    registry = get_registry()
    result, trajectories = run_forecast(
        flows_by_station=data["flows"],
        poa_level=data["poa_level"],
        params=params,
        stations=registry,
        degraded_stations=data["degraded"],
        target_code=target_code,
    )
    return result, trajectories, params
