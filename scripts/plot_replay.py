"""Grafico de uma previsao reproduzida contra o nivel que de fato ocorreu.

Roda a previsao de uma versao num instante de corte passado, usando so os
dados disponiveis ate ali, e desenha os tres cenarios sobre o nivel observado
antes e depois do corte. Gera HTML (Plotly); o PNG do README e um print dele.

Uso:
  python scripts/plot_replay.py --at "2024-05-12 00:00" --version v3 \
      --out docs/img/reproducao_2024-05-12_v3.html
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from waters.calibrate.run import load_calibration_series, load_routing_flows
from waters.config import settings
from waters.config.params_io import discover_param_files, load_params_file
from waters.config.registry import load_reach_network
from waters.domain.models import ScenarioName
from waters.model.forecast import run_forecast

CONTEXT_BEFORE_H = 96
CONTEXT_AFTER_H = 24
STYLE = {
    ScenarioName.OTIMISTA: dict(color="#2ca02c", dash="dot"),
    ScenarioName.CENTRAL: dict(color="#1f77b4", dash="solid"),
    ScenarioName.PESSIMISTA: dict(color="#d62728", dash="dot"),
}


def _params(version: str):
    for path in discover_param_files():
        params = load_params_file(path)
        if params.version == version:
            return params
    raise SystemExit(f"Versao {version} nao encontrada em {settings.PARAMS_DIR}")


def _figure(cut: pd.Timestamp, poa: pd.Series, paths: dict, version: str) -> go.Figure:
    horizon_end = cut + pd.Timedelta(hours=settings.FORECAST_HORIZON_HOURS)
    window = poa.loc[cut - pd.Timedelta(hours=CONTEXT_BEFORE_H):
                     horizon_end + pd.Timedelta(hours=CONTEXT_AFTER_H)].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=window[window.index <= cut].index, y=window[window.index <= cut],
                             name="Observado até o corte", line=dict(color="#444", width=2)))
    fig.add_trace(go.Scatter(x=window[window.index > cut].index, y=window[window.index > cut],
                             name="Observado depois (o que o modelo não via)",
                             line=dict(color="#999", width=2, dash="dash")))
    for scenario, path in paths.items():
        fig.add_trace(go.Scatter(x=path.index, y=path, name=f"Previsão {version}: {scenario.value}",
                                 line=dict(width=2.5 if scenario == ScenarioName.CENTRAL else 1.5,
                                           **STYLE[scenario])))
    fig.add_vline(x=cut, line=dict(color="#888", width=1))
    fig.add_annotation(x=cut, y=1, yref="paper", text="corte da previsão", showarrow=False,
                       xanchor="right", yanchor="bottom")
    observed = window[(window.index > cut) & (window.index <= horizon_end)]
    central = paths[ScenarioName.CENTRAL]
    fig.update_layout(
        title=(f"Reprodução: previsão do {version} emitida em {cut:%d/%m/%Y %Hh}, "
               f"Usina do Gasômetro<br><sup>pico previsto {central.max():.2f} m "
               f"em {central.idxmax():%d/%m %Hh}; observado {observed.max():.2f} m "
               f"em {observed.idxmax():%d/%m %Hh}</sup>"),
        yaxis_title="Nível (m)", template="plotly_white", width=1000, height=520,
        legend=dict(orientation="h", yanchor="top", y=-0.12), margin=dict(l=60, r=30, t=80, b=40),
    )
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description="Grafico de uma previsao reproduzida")
    parser.add_argument("--at", required=True, help="instante de corte, ex.: '2024-05-12 00:00'")
    parser.add_argument("--version", default="v1")
    parser.add_argument("--out", type=Path, required=True, help="arquivo HTML de saida")
    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR)
    cut = pd.Timestamp(args.at, tz=settings.TZ)
    params = _params(args.version)
    flows, poa, registry = load_calibration_series()
    if params.reaches:
        flows = {**flows, **load_routing_flows(load_reach_network())}
    _, paths = run_forecast(
        {code: s[s.index <= cut] for code, s in flows.items()},
        poa[poa.index <= cut], params, registry, now=cut.to_pydatetime(),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _figure(cut, poa, paths, args.version).write_html(args.out, include_plotlyjs=True)
    print(args.out)


if __name__ == "__main__":
    main()
