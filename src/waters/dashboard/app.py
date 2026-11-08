"""Dashboard do modelo hidrologico do Guaiba.

Rodar: streamlit run src/waters/dashboard/app.py
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from waters.config import settings
from waters.config.registry import target_stations
from waters.domain.errors import WatersError
from waters.domain.models import ScenarioName
from waters.dashboard import data_access
from waters.dashboard.components import (
    flood_map,
    forecast_panel,
    inflow_chart,
    status_cards,
)

st.set_page_config(
    page_title="Nível Guaíba — Modelo de Vazão e Previsão",
    page_icon="🌊",
    layout="wide",
)


def main() -> None:
    st.title("🌊 Guaíba — vazão, distribuição e previsão de pico")
    st.caption(
        "Modelo de balanço de massa: propaga as vazões observadas nos afluentes "
        "(Jacuí, Taquari, Caí, Sinos, Gravataí) com defasagens calibradas e integra "
        "o balanço do Guaíba. Dados: telemetria ANA/SGB, 15 min."
    )

    targets = target_stations()
    models = data_access.list_models()
    with st.sidebar:
        st.header("Controles")
        target = st.radio(
            "Régua de referência",
            options=targets,
            format_func=lambda s: s.name + (" (derivada)" if s.mirror_of else ""),
        )
        model = st.selectbox(
            "Modelo / cenário",
            options=models,
            format_func=lambda m: m["label"],
            help=(
                "Área constante (operacional, melhor magnitude no hindcast) vs. "
                "topografia DEM GLO-30 (cheia mais achatada, melhor timing/duração)."
            ),
        )
        if st.button("🔄 Atualizar agora"):
            data_access.load_series.clear()
            data_access.compute_forecast.clear()
            st.rerun()
        st.caption(
            f"Os dados se renovam automaticamente a cada "
            f"{data_access.REFRESH_TTL_S // 60} min ao recarregar a página."
        )

    try:
        data = data_access.load_series()
    except WatersError as exc:
        st.error(f"Falha ao carregar dados: {exc}")
        st.stop()
        return

    if data["degraded"]:
        st.warning(
            "Estações com dado defasado ou em fonte reserva: "
            + ", ".join(data["degraded"])
        )

    sel_params = None
    try:
        cache_key = datetime.now(settings.TZ).strftime("%Y%m%d%H%M")[:11]  # ~10 min
        result, trajectories, sel_params = data_access.compute_forecast(
            cache_key, target.code, model["key"]
        )
        if target.own_telemetry:
            # Regua com medicao propria (Cais Maua): mostra o nivel real dela
            observed = data["observed_by_target"].get(target.code, data["poa_level"])
        else:
            # Regua derivada pura ou base: observado = base + offset de datum
            observed = data["poa_level"] + (
                target.datum_offset_m if target.mirror_of else 0.0
            )
        forecast_panel.render(result, trajectories, observed, target)
        forecast_peak = result.peaks[ScenarioName.CENTRAL].peak_level_m
    except WatersError as exc:
        st.error(f"Não foi possível rodar a previsão: {exc}")
        forecast_peak = None

    st.divider()
    try:
        # usa o modelo selecionado para a curva de saida do grafico entrada-vs-saida
        params = sel_params or data_access.load_latest_params()
        inflow_chart.render(data["flows"], data["poa_level"], params)
    except WatersError as exc:
        st.error(f"Gráficos de vazão indisponíveis: {exc}")

    st.divider()
    try:
        inund = data_access.load_inundation()
        poa_valid = data["poa_level"].dropna()
        current_level = float(poa_valid.iloc[-1]) if not poa_valid.empty else None
        flood_map.render(inund, current_level, forecast_peak)
    except FileNotFoundError:
        st.info(
            "🗺️ Mapa de inundação indisponível — rode `python scripts/build_inundation.py` "
            "para gerar a topografia pré-computada."
        )

    st.divider()
    status_cards.render(data["levels_now"])

    st.divider()
    st.caption(
        "Fontes: ANA/SGB-CPRM (telemetria) via telemetriaws1.ana.gov.br; "
        "fallback nivelguaiba.com.br. Modelo v1 — propaga apenas água já observada "
        "nos rios (não considera chuva futura). Horizonte confiável: ~48–72 h. "
        "Projeção preliminar, não substitui os avisos oficiais da Defesa Civil."
    )


main()
