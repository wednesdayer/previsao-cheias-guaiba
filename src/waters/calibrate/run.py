"""Orquestra a calibracao offline e grava os parametros versionados.

Pre-requisito: cache preenchido (python scripts/backfill.py).
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime

import pandas as pd

from waters.config import settings
from waters.config.params_io import save_params
from waters.config.registry import (
    get_registry,
    inflow_stations,
    load_reach_network,
    load_stage_area_curve,
    target_station,
)
from waters.domain.errors import CalibrationError
from waters.domain.models import CalibrationParams, LagParams, RatingParams, Station
from waters.calibrate.events import all_events
from waters.calibrate.fit_crest import fit_station_crest
from waters.calibrate.fit_lags import fit_station_lag
from waters.calibrate.fit_routing import calibrate_reaches
from waters.calibrate.hindcast import HindcastScore, hindcast_event
from waters.ingest.cache import ParquetCache
from waters.model.inflow import total_inflow
from waters.model.routing import routed_inflow
from waters.model.lags import clamp_to_bounds
from waters.model.preprocess import qc_series, to_hourly_grid
from waters.model.rating import fit_rating, implied_outflow, reconstructed_inflow

logger = logging.getLogger(__name__)

FALLBACK_LAG_HOURS = {  # centro da faixa fisica, usado se a correlacao falhar
    group: (low + high) / 2.0 for group, (low, high) in settings.LAG_BOUNDS_HOURS.items()
}


def load_calibration_series(
    cache: ParquetCache | None = None,
) -> tuple[dict[str, pd.Series], pd.Series, dict[str, Station]]:
    """Series horarias QC'd: vazoes dos afluentes e nivel de POA."""
    store = cache or ParquetCache()
    registry = get_registry()
    target = target_station(registry)

    poa_frame = to_hourly_grid(store.read(target.code))
    if poa_frame.empty:
        raise CalibrationError("Cache vazio para Porto Alegre. Rode scripts/backfill.py.")
    poa_level = qc_series(poa_frame["nivel_m"]).interpolate(
        method="time", limit=settings.MAX_GAP_INTERP_HOURS, limit_area="inside"
    )

    flows: dict[str, pd.Series] = {}
    for station in inflow_stations(registry):
        frame = to_hourly_grid(
            store.read(station.code),
            max_gap_hours=settings.SPARSE_MAX_GAP_HOURS if station.sparse else None,
        )
        if frame.empty or frame["vazao_m3s"].dropna().empty:
            logger.warning("Sem vazao em cache para %s (%s)", station.name, station.code)
            continue
        flows[station.code] = frame["vazao_m3s"]
    if not flows:
        raise CalibrationError("Nenhum afluente com vazao em cache.")
    return flows, poa_level, registry


def load_routing_flows(network: dict, cache: ParquetCache | None = None) -> dict[str, pd.Series]:
    """Vazoes horarias de TODAS as reguas da rede (fontes + pares de validacao)."""
    store = cache or ParquetCache()
    codes = set(network["sources"].values())
    for pair in network["validation_pairs"]:
        codes.add(pair["upstream"])
        codes.add(pair["downstream"])
    flows: dict[str, pd.Series] = {}
    for code in codes:
        frame = to_hourly_grid(store.read(code))
        if not frame.empty and not frame["vazao_m3s"].dropna().empty:
            flows[code] = frame["vazao_m3s"]
    return flows


def calibrate(
    flows: dict[str, pd.Series],
    poa_level: pd.Series,
    registry: dict[str, Station],
    version: str = "v1",
    use_area_curve: bool = False,
    area_curve=None,
    use_routing: bool = False,
    routing_flows: dict | None = None,
) -> tuple[CalibrationParams, list[HindcastScore]]:
    events = all_events(poa_level)
    if not events:
        raise CalibrationError("Nenhum evento de cheia identificado no historico.")
    logger.info("Eventos de calibracao: %s", {k: v for k, v in events.items()})

    # Curva cota-area e opt-in: o A/B de mai/2024 mostrou que a curva
    # APROXIMADA nao supera a area constante (o refit do Qout compensa a area,
    # trade-off de identificabilidade). So vale a pena com curva vinda de DEM.
    if use_area_curve and area_curve is None:
        area_curve = load_stage_area_curve()
    if area_curve is not None:
        logger.info(
            "Curva cota-area: %d pontos, A(%.1f)=%.0f -> A(%.1f)=%.0f km2 (%s)",
            len(area_curve.levels_m), area_curve.levels_m[0], area_curve.areas_km2[0],
            area_curve.levels_m[-1], area_curve.areas_km2[-1], area_curve.source,
        )
    else:
        logger.info("Area constante (%.0f km2) — curva cota-area desativada.",
                    settings.GUAIBA_AREA_KM2)

    def fit_all_lags(downstream: pd.Series, kind: str) -> dict[str, LagParams]:
        fitted: dict[str, LagParams] = {}
        for code, flow in flows.items():
            station = registry[code]
            try:
                fitted[code] = fit_station_lag(
                    station, flow, downstream, events, downstream_kind=kind
                )
            except CalibrationError as exc:
                fallback = FALLBACK_LAG_HOURS.get(station.river_group, 18.0)
                fallback, _ = clamp_to_bounds(fallback, station.river_group)
                logger.warning("%s; usando lag padrao %.0f h", exc, fallback)
                fitted[code] = LagParams(
                    station_code=code, lag_hours=fallback, lag_spread_hours=6.0
                )
        return fitted

    def fit_rating_for(lags: dict[str, LagParams]) -> RatingParams:
        qin = total_inflow(flows, lags)["total"]
        qout = implied_outflow(poa_level, qin, settings.GUAIBA_AREA_KM2, curve=area_curve)
        return fit_rating(poa_level, qout, settings.GUAIBA_AREA_KM2)

    # Passada 1: lags via dh/dt (com vies) -> rating provisorio
    lags = fit_all_lags(poa_level, "level")
    rating = fit_rating_for(lags)

    # Passada 2: fluxo de entrada reconstruido elimina o vies do -Qout;
    # re-estima os lags e refaz o rating com eles
    inflow_flux = reconstructed_inflow(poa_level, rating, curve=area_curve)
    lags = fit_all_lags(inflow_flux, "flux")
    rating = fit_rating_for(lags)

    crests = {}
    for code, flow in flows.items():
        station = registry[code]
        crests[code] = fit_station_crest(station, flow, events)
        logger.info(
            "%s: lag=%.0fh (±%.0fh) tau_rise=%.0fh tau_rec=%.0fh",
            station.name, lags[code].lag_hours, lags[code].lag_spread_hours,
            crests[code].tau_rise_hours, crests[code].tau_recession_hours,
        )
    # Roteamento (v4): calibra trechos, adiciona cristas das reguas-fonte e
    # refaz o rating com o Qin ROTEADO (consistencia do balanco).
    reaches: dict = {}
    if use_routing:
        network = load_reach_network()
        rflows = routing_flows if routing_flows is not None else load_routing_flows(network)
        reaches, report = calibrate_reaches(rflows, lags, events, network)
        for src in {r.source_code for r in reaches.values()}:
            if src not in crests and src in rflows:
                crests[src] = fit_station_crest(registry[src], rflows[src], events)
        provisional = CalibrationParams(
            version=version, generated_at=datetime.now(settings.TZ),
            events=sorted(events), lags=lags, rating=rating, crests=crests,
            area_curve=area_curve, reaches=reaches,
        )
        qin_routed = routed_inflow(rflows, provisional).get("total", pd.Series(dtype=float))
        if not qin_routed.dropna().empty:
            qout = implied_outflow(poa_level, qin_routed, settings.GUAIBA_AREA_KM2, curve=area_curve)
            rating = fit_rating(poa_level, qout, settings.GUAIBA_AREA_KM2)
        logger.info("Roteamento: %d trechos; NSE validacao: %s", len(reaches),
                    {r["reach"]: r["nse"] for r in report})

    logger.info(
        "Rating: Qout = %.1f*(h-%.2f)^%.2f  rmse=%.0f m3/s",
        rating.a, rating.h0, rating.b, rating.rmse_m3s or 0.0,
    )

    params = CalibrationParams(
        version=version,
        generated_at=datetime.now(settings.TZ),
        events=sorted(events),
        lags=lags,
        rating=rating,
        crests=crests,
        area_curve=area_curve,
        reaches=reaches,
        notes="Calibrado sobre telemetria ANA; rating fecha o balanco sobre a curva cota-area.",
    )

    # no v4 o hindcast precisa das reguas-fonte de montante em flows
    hindcast_flows = dict(flows)
    if use_routing and routing_flows is not None:
        hindcast_flows.update(routing_flows)
    elif use_routing:
        hindcast_flows.update(load_routing_flows(load_reach_network()))

    scores = []
    for name, window in events.items():
        try:
            scores.append(
                hindcast_event(name, window, hindcast_flows, poa_level, params, registry)
            )
        except Exception as exc:  # hindcast nunca deve abortar a calibracao
            logger.warning("Hindcast do evento %s falhou: %s", name, exc)
    return params, scores


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibracao do modelo do Guaiba")
    parser.add_argument("--version", default=None)
    parser.add_argument(
        "--area-curve", action="store_true",
        help="usa a curva cota-area (experimental; requer curva de DEM p/ valer a pena)",
    )
    parser.add_argument(
        "--routing", action="store_true",
        help="usa roteamento Muskingum na rede (v4)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if args.version:
        version = args.version
    elif args.routing:
        version = "v4"
    elif args.area_curve:
        version = "v2"
    else:
        version = "v1"
    flows, poa_level, registry = load_calibration_series()
    routing_flows = load_routing_flows(load_reach_network()) if args.routing else None
    params, scores = calibrate(
        flows, poa_level, registry, version=version, use_area_curve=args.area_curve,
        use_routing=args.routing, routing_flows=routing_flows,
    )
    path = save_params(params)
    logger.info("Parametros gravados em %s", path)

    print("\n=== RELATORIO DE HINDCAST ===")
    if not scores:
        print("Nenhum hindcast concluido — verificar cobertura dos dados.")
    for score in scores:
        print(
            f"{score.event}: pico obs {score.observed_peak_m:.2f} m em "
            f"{score.observed_peak_time:%d/%m %Hh} | previsto {score.predicted_peak_m:.2f} m "
            f"em {score.predicted_peak_time:%d/%m %Hh} | erro nivel "
            f"{score.level_error_m:+.2f} m, tempo {score.timing_error_h:+.1f} h"
        )


if __name__ == "__main__":
    main()
