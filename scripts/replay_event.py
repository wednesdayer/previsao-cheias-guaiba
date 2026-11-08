"""Reproduz previsoes "como se fossem ao vivo" num intervalo de um evento.

Para cada instante de corte, usa apenas os dados disponiveis ate ali e roda a
previsao com cada versao de parametros (v1-v4). Gera uma tabela com o pico
central previsto (opcionalmente convertido para outra regua por offset de
datum) e o nivel observado no corte.

Uso:
  python scripts/replay_event.py --start "2026-07-21 12:00" --end "2026-07-25 00:00" \
      --step-hours 6 --offset 0.44 --out docs/results/replay_2026-07.csv
  python scripts/replay_event.py --at "2026-07-22 12:00" "2026-07-23 10:00"
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

from waters.calibrate.run import load_calibration_series, load_routing_flows
from waters.config import settings
from waters.config.params_io import discover_param_files, load_params_file
from waters.config.registry import load_reach_network
from waters.domain.errors import WatersError
from waters.domain.models import ScenarioName
from waters.model.forecast import run_forecast

logger = logging.getLogger("replay_event")


def _cut_times(args: argparse.Namespace) -> list[pd.Timestamp]:
    if args.at:
        return [pd.Timestamp(t, tz=settings.TZ) for t in args.at]
    start = pd.Timestamp(args.start, tz=settings.TZ)
    end = pd.Timestamp(args.end, tz=settings.TZ)
    return list(pd.date_range(start, end, freq=f"{args.step_hours}h"))


def _replay_row(
    cut: pd.Timestamp,
    poa: pd.Series,
    flows: dict[str, pd.Series],
    routing_flows: dict[str, pd.Series],
    models: dict[str, object],
    registry: dict,
    offset: float,
) -> dict:
    observed = poa[poa.index <= cut].dropna()
    row: dict = {"cut": cut.strftime("%Y-%m-%d %H:%M"), "observed_m": round(float(observed.iloc[-1]), 2)}
    for name, params in models.items():
        source = routing_flows if params.reaches else flows
        cut_flows = {code: s[s.index <= cut] for code, s in source.items()}
        try:
            result, _ = run_forecast(
                cut_flows, poa[poa.index <= cut], params, registry, now=cut.to_pydatetime()
            )
        except WatersError as exc:
            logger.warning("%s em %s: %s", name, cut, exc)
            row[f"{name}_peak_m"] = None
            row[f"{name}_peak_time"] = None
            row[f"{name}_at_horizon"] = None
            continue
        peak = result.peaks[ScenarioName.CENTRAL]
        peak_time = pd.Timestamp(peak.peak_time)
        horizon_end = cut + pd.Timedelta(hours=settings.FORECAST_HORIZON_HOURS)
        row[f"{name}_peak_m"] = round(peak.peak_level_m + offset, 2)
        row[f"{name}_peak_time"] = peak_time.strftime("%Y-%m-%d %H:%M")
        # pico no ultimo passo = ainda subindo no fim do horizonte (valor e um minimo)
        row[f"{name}_at_horizon"] = abs((peak_time - horizon_end).total_seconds()) < 3600
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay de previsoes num evento passado")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--step-hours", type=float, default=6.0)
    parser.add_argument("--at", nargs="*", help="instantes de corte explicitos")
    parser.add_argument("--offset", type=float, default=0.0,
                        help="soma ao pico (ex.: 0.44 para a regua do Cais Maua)")
    parser.add_argument("--out", type=Path, help="CSV de saida")
    args = parser.parse_args()
    if not args.at and not (args.start and args.end):
        parser.error("informe --at ou --start/--end")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    flows, poa, registry = load_calibration_series()
    routing_flows = {**flows, **load_routing_flows(load_reach_network())}
    models = {
        load_params_file(path).version: load_params_file(path)
        for path in discover_param_files()
    }

    rows = [
        _replay_row(cut, poa, flows, routing_flows, models, registry, args.offset)
        for cut in _cut_times(args)
    ]
    table = pd.DataFrame(rows)
    print(table.to_string(index=False))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(args.out, index=False)
        logger.info("Tabela gravada em %s", args.out)


if __name__ == "__main__":
    main()
