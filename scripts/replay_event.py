"""Reproduz previsoes "como se fossem ao vivo" num intervalo de um evento.

Para cada instante de corte, usa apenas os dados disponiveis ate ali e roda a
previsao com cada versao de parametros (v1-v4). Gera uma tabela com o pico
previsto em cada cenario (opcionalmente convertido para outra regua por offset
de datum), o nivel observado no corte e o maximo observado dentro do horizonte
de previsao, para verificacao.

Uso:
  python scripts/replay_event.py --start "2026-07-21 12:00" --end "2026-07-25 00:00" \
      --step-hours 6 --offset 0.44 --out docs/resultados/reproducao_2026-07_cais-maua.csv
  python scripts/replay_event.py --at "2026-07-22 12:00" "2026-07-23 10:00"
  # maio de 2024: a regua do Gasometro so comeca em 03/05; antes disso usa o
  # Cais Maua convertido pelo offset de datum (aproximacao, ver DISCUSSAO)
  python scripts/replay_event.py --start "2024-04-29 00:00" --end "2024-05-20 00:00"       --prepend-station 87450004 --prepend-offset -0.44
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
from waters.ingest.cache import ParquetCache
from waters.model.forecast import run_forecast
from waters.model.preprocess import qc_series, to_hourly_grid

logger = logging.getLogger("replay_event")


def _cut_times(args: argparse.Namespace) -> list[pd.Timestamp]:
    if args.at:
        return [pd.Timestamp(t, tz=settings.TZ) for t in args.at]
    start = pd.Timestamp(args.start, tz=settings.TZ)
    end = pd.Timestamp(args.end, tz=settings.TZ)
    return list(pd.date_range(start, end, freq=f"{args.step_hours}h"))


def _prepend_level(poa: pd.Series, code: str, offset: float) -> pd.Series:
    """Preenche o nivel antes da primeira leitura do alvo com outra regua + offset."""
    first = poa.first_valid_index()
    other = qc_series(to_hourly_grid(ParquetCache().read(code))["nivel_m"]) + offset
    before = other[other.index < first].dropna()
    logger.info("Nivel de %s usado antes de %s (%d horas)", code, first, len(before))
    return pd.concat([before, poa[poa.index >= first]]).sort_index()


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
    horizon_end = cut + pd.Timedelta(hours=settings.FORECAST_HORIZON_HOURS)
    ahead = poa[(poa.index > cut) & (poa.index <= horizon_end)].dropna()
    row: dict = {
        "cut": cut.strftime("%Y-%m-%d %H:%M"),
        "observed_m": round(float(observed.iloc[-1]) + offset, 2),
        "obs_max_horizon_m": round(float(ahead.max()) + offset, 2) if len(ahead) else None,
        "obs_max_horizon_time": ahead.idxmax().strftime("%Y-%m-%d %H:%M") if len(ahead) else None,
    }
    for name, params in models.items():
        source = routing_flows if params.reaches else flows
        cut_flows = {code: s[s.index <= cut] for code, s in source.items()}
        try:
            result, _ = run_forecast(
                cut_flows, poa[poa.index <= cut], params, registry, now=cut.to_pydatetime()
            )
        except WatersError as exc:
            logger.warning("%s em %s: %s", name, cut, exc)
            for col in ("peak_m", "peak_time", "at_horizon", "low_m", "high_m"):
                row[f"{name}_{col}"] = None
            continue
        peak = result.peaks[ScenarioName.CENTRAL]
        peak_time = pd.Timestamp(peak.peak_time)
        row[f"{name}_peak_m"] = round(peak.peak_level_m + offset, 2)
        row[f"{name}_low_m"] = round(result.peaks[ScenarioName.OTIMISTA].peak_level_m + offset, 2)
        row[f"{name}_high_m"] = round(result.peaks[ScenarioName.PESSIMISTA].peak_level_m + offset, 2)
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
    parser.add_argument("--prepend-station",
                        help="regua usada antes da primeira leitura do alvo (ex.: 87450004)")
    parser.add_argument("--prepend-offset", type=float, default=0.0,
                        help="soma a regua anterior para leva-la ao datum do alvo (ex.: -0.44)")
    parser.add_argument("--out", type=Path, help="CSV de saida")
    args = parser.parse_args()
    if not args.at and not (args.start and args.end):
        parser.error("informe --at ou --start/--end")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    flows, poa, registry = load_calibration_series()
    if args.prepend_station:
        poa = _prepend_level(poa, args.prepend_station, args.prepend_offset)
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
