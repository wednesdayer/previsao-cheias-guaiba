"""Graficos de vazao: entrada empilhada por rio e entrada vs saida do Guaiba."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from waters.config.registry import get_registry
from waters.domain.models import CalibrationParams
from waters.model.inflow import total_inflow
from waters.model.rating import predict_qout

RIVER_LABEL = {
    "jacui": "Jacuí",
    "taquari": "Taquari",
    "cai": "Caí",
    "sinos": "Sinos",
    "gravatai": "Gravataí",
}
RIVER_COLOR = {
    "jacui": "#1f77b4",
    "taquari": "#d62728",
    "cai": "#2ca02c",
    "sinos": "#9467bd",
    "gravatai": "#ff7f0e",
}
WINDOW_DAYS = 10


def _inflow_frame(
    flows: dict[str, pd.Series], params: CalibrationParams
) -> pd.DataFrame:
    """Vazoes defasadas (chegando ao Guaiba), agregadas por rio."""
    registry = get_registry()
    frame = total_inflow(flows, params.lags)
    if frame.empty:
        return frame
    by_river: dict[str, pd.Series] = {}
    for code in flows:
        group = registry[code].river_group
        if code in frame.columns:
            series = frame[code].fillna(0.0)
            by_river[group] = by_river.get(group, 0.0) + series
    result = pd.DataFrame(by_river)
    result["total"] = frame["total"]
    cutoff = result.index[-1] - pd.Timedelta(days=WINDOW_DAYS)
    return result[result.index >= cutoff]


def render(
    flows: dict[str, pd.Series],
    poa_level: pd.Series,
    params: CalibrationParams,
) -> None:
    st.subheader("Vazão chegando ao Guaíba, por rio")
    frame = _inflow_frame(flows, params)
    if frame.empty:
        st.warning("Sem séries de vazão disponíveis para o gráfico.")
        return

    stacked = go.Figure()
    for group, label in RIVER_LABEL.items():
        if group not in frame.columns:
            continue
        stacked.add_trace(
            go.Scatter(
                x=frame.index, y=frame[group], name=label,
                stackgroup="inflow", mode="none",
                fillcolor=RIVER_COLOR[group], line={"width": 0},
            )
        )
    stacked.update_layout(
        yaxis_title="m³/s", hovermode="x unified", height=380,
        legend={"orientation": "h", "y": 1.12},
        margin={"t": 10, "b": 10},
    )
    st.plotly_chart(stacked, width="stretch")

    st.subheader("Entrada vs. saída do Guaíba")
    qout = pd.Series(
        [predict_qout(h, params.rating) for h in poa_level],
        index=poa_level.index,
        name="saida",
    )
    cutoff = frame.index[-1] - pd.Timedelta(days=WINDOW_DAYS)
    qout = qout[qout.index >= cutoff]

    balance = go.Figure()
    balance.add_trace(
        go.Scatter(x=frame.index, y=frame["total"], name="Entrada (Σ afluentes)",
                   line={"color": "#1f77b4", "width": 2})
    )
    balance.add_trace(
        go.Scatter(x=qout.index, y=qout, name="Saída (curva de descarga)",
                   line={"color": "#d62728", "width": 2, "dash": "dash"})
    )
    balance.update_layout(
        yaxis_title="m³/s", hovermode="x unified", height=340,
        legend={"orientation": "h", "y": 1.15},
        margin={"t": 10, "b": 10},
    )
    st.plotly_chart(balance, width="stretch")
    st.caption(
        "Quando a entrada supera a saída, o Guaíba acumula volume e o nível sobe. "
        "A saída é estimada pela curva de descarga calibrada (balanço de massa)."
    )
