"""Painel de previsao: trajetorias por cenario, pico anotado e cota de inundacao."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from waters.config import settings
from waters.domain.models import ForecastResult, ScenarioName, Station

SCENARIO_STYLE = {
    ScenarioName.OTIMISTA: {"color": "#2ca02c", "dash": "dot", "label": "Otimista"},
    ScenarioName.CENTRAL: {"color": "#1f77b4", "dash": "solid", "label": "Central"},
    ScenarioName.PESSIMISTA: {"color": "#d62728", "dash": "dot", "label": "Pessimista"},
}
OBSERVED_DAYS = 7


def _peak_summary(result: ForecastResult, cota_m: float) -> None:
    central = result.peaks[ScenarioName.CENTRAL]
    peak_local = pd.Timestamp(central.peak_time).tz_convert(settings.TZ)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pico previsto (central)", f"{central.peak_level_m:.2f} m")
    col2.metric("Quando", f"{peak_local:%d/%m às %H}h")
    col3.metric(
        "Entrada total agora", f"{result.inflow_total_m3s:,.0f} m³/s".replace(",", ".")
    )
    col4.metric(
        "Saída estimada agora", f"{result.outflow_now_m3s:,.0f} m³/s".replace(",", ".")
    )
    if central.above_cota:
        st.error(
            f"⚠️ Pico previsto ACIMA da cota de inundação ({cota_m:.2f} m) "
            f"— cenário central passa {central.hours_above_cota:.0f} h acima da cota."
        )
    else:
        pess = result.peaks[ScenarioName.PESSIMISTA]
        if pess.above_cota:
            st.warning(
                f"Cenário central abaixo da cota, mas o pessimista atinge "
                f"{pess.peak_level_m:.2f} m ({pd.Timestamp(pess.peak_time).tz_convert(settings.TZ):%d/%m %H}h)."
            )
        else:
            st.success("Nenhum cenário atinge a cota de inundação no horizonte de 72 h.")


def render(
    result: ForecastResult,
    trajectories: dict[ScenarioName, pd.Series],
    observed_level: pd.Series,
    target: Station,
) -> None:
    st.subheader(f"Previsão do nível do Guaíba — {target.name} (72 h)")
    cota = target.cota_inundacao_m
    cota_alerta = target.cota_alerta_m or 0.85 * cota
    if target.mirror_of is not None and target.own_telemetry:
        st.info(
            f"Medição própria + previsão espelhada: o **observado** é o nível real "
            f"transmitido por esta régua; a **previsão** vem do modelo no Gasômetro "
            f"deslocado em {target.datum_offset_m:+.2f} m (diferença de datum medida). "
            f"Cotas nesta escala: alerta {cota_alerta:.2f} m, inundação {cota:.2f} m."
        )
    elif target.mirror_of is not None:
        st.info(
            "Régua derivada: esta estação não transmite publicamente — o nível é "
            f"espelhado da régua-base (offset {target.datum_offset_m:+.2f} m) e "
            "comparado à cota local. Ajuste offset/cotas em config/stations.yaml "
            "quando houver referência da Defesa Civil de Eldorado do Sul."
        )
    _peak_summary(result, cota)

    observed = observed_level.dropna()
    cutoff = observed.index[-1] - pd.Timedelta(days=OBSERVED_DAYS)
    observed = observed[observed.index >= cutoff]

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(x=observed.index, y=observed, name="Observado",
                   line={"color": "#333333", "width": 2.5})
    )
    for scenario, trajectory in trajectories.items():
        style = SCENARIO_STYLE[scenario]
        figure.add_trace(
            go.Scatter(
                x=trajectory.index, y=trajectory, name=style["label"],
                line={"color": style["color"], "dash": style["dash"], "width": 2},
            )
        )

    central = result.peaks[ScenarioName.CENTRAL]
    peak_ts = pd.Timestamp(central.peak_time).tz_convert(settings.TZ)
    figure.add_annotation(
        x=peak_ts, y=central.peak_level_m,
        text=f"Pico {central.peak_level_m:.2f} m<br>{peak_ts:%d/%m %H}h",
        showarrow=True, arrowhead=2, ax=40, ay=-40,
    )
    figure.add_hline(
        y=cota, line={"color": "#d62728", "dash": "dash"},
        annotation_text=f"Cota de inundação {cota:.2f} m",
    )
    figure.add_hline(
        y=cota_alerta, line={"color": "#ff7f0e", "dash": "dot"},
        annotation_text=f"Alerta {cota_alerta:.2f} m",
    )
    figure.update_layout(
        yaxis_title="Nível (m)", hovermode="x unified", height=460,
        legend={"orientation": "h", "y": 1.1},
        margin={"t": 10, "b": 10},
    )
    st.plotly_chart(figure, width="stretch")

    st.caption(
        f"Vazão de entrada agora por rio: "
        + " · ".join(
            f"{river}: {value:,.0f} m³/s".replace(",", ".")
            for river, value in sorted(result.inflow_now_m3s.items())
        )
        + f" | correção de viés aplicada: {result.bias_offset_m:+.2f} m"
        + f" | parâmetros {result.params_version}"
    )
