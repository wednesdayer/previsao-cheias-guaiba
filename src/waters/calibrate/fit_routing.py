"""Calibracao dos trechos de roteamento (Muskingum) da rede.

Para cada par regua-a-regua (montante->jusante) com vazao nos dois, ajusta K,X
minimizando o erro entre o hidrograma roteado do montante e o medido no jusante,
nas janelas de evento. Depois monta os trechos de PREVISAO (regua-fonte -> delta)
por rio, encadeando o K validado com a defasagem da regua de entrada ate POA.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from waters.config.registry import haversine_km
from waters.domain.models import LagParams, ReachParams
from waters.model.routing import muskingum_route

logger = logging.getLogger(__name__)

DEFAULT_X = 0.2
DEFAULT_CELERITY_KMH = 3.0     # fallback: ~3 km/h de celeridade de onda
MIN_POINTS = 48
# regua de entrada (ate POA) por rio, cuja defasagem completa a perna fonte->delta
INFLOW_GAUGE = {"taquari": "86879300", "jacui": "85900000",
                "cai": "87170000", "sinos": "87382000", "gravatai": "87399000"}


def _event_pair(up: pd.Series, down: pd.Series, events: dict) -> pd.DataFrame:
    parts_u, parts_d = [], []
    for _name, (s, e) in events.items():
        parts_u.append(up.loc[s:e])
        parts_d.append(down.loc[s:e])
    u = pd.concat(parts_u).resample("1h").mean()
    d = pd.concat(parts_d).resample("1h").mean()
    u = u[~u.index.duplicated()]
    d = d[~d.index.duplicated()]
    return pd.concat([u.rename("u"), d.rename("d")], axis=1).dropna()


def fit_reach(up: pd.Series, down: pd.Series, events: dict, length_km: float):
    """Ajusta (K,X) e devolve (k, x, nse) ou None se dados insuficientes."""
    joined = _event_pair(up.dropna(), down.dropna(), events)
    if len(joined) < MIN_POINTS:
        return None

    def resid(theta):
        k, x = theta
        routed = muskingum_route(joined["u"], k, x)
        return (routed - joined["d"]).to_numpy()

    k0 = max(2.0, length_km / DEFAULT_CELERITY_KMH)
    res = least_squares(resid, [k0, DEFAULT_X], bounds=([1.0, 0.0], [120.0, 0.5]),
                        max_nfev=300)
    k, x = float(res.x[0]), float(res.x[1])
    sim = muskingum_route(joined["u"], k, x)
    obs = joined["d"]
    ss_res = float(((obs - sim) ** 2).sum())
    ss_tot = float(((obs - obs.mean()) ** 2).sum())
    nse = (1.0 - ss_res / ss_tot) if ss_tot > 0 else None
    return k, x, nse


def calibrate_reaches(
    flows_all: dict[str, pd.Series],
    lags: dict[str, LagParams],
    events: dict,
    network: dict,
) -> tuple[dict[str, ReachParams], list[dict]]:
    """Devolve (reaches por rio [fonte->delta], relatorio de validacao)."""
    coords = network["coords"]
    delta = network["delta_code"]

    # 1) trechos de validacao regua-a-regua -> K,X,NSE e celeridade por rio
    valid: dict[tuple[str, str], dict] = {}
    report: list[dict] = []
    for pair in network["validation_pairs"]:
        up_c, down_c, rg = pair["upstream"], pair["downstream"], pair["river_group"]
        if up_c not in flows_all or down_c not in flows_all:
            continue
        length = haversine_km(coords[up_c], coords[down_c])
        fit = fit_reach(flows_all[up_c], flows_all[down_c], events, length)
        if fit is None:
            logger.warning("validacao %s->%s: dados insuficientes", up_c, down_c)
            continue
        k, x, nse = fit
        valid[(up_c, down_c)] = {"k": k, "x": x, "nse": nse, "length": length,
                                 "celerity": length / k if k > 0 else DEFAULT_CELERITY_KMH,
                                 "river_group": rg}
        report.append({"reach": f"{up_c}->{down_c}", "river_group": rg,
                       "length_km": round(length, 1), "k_hours": round(k, 1),
                       "x": round(x, 3), "nse": round(nse, 2) if nse is not None else None})
        logger.info("validacao %s->%s (%s): L=%.0f km  K=%.1f h  X=%.2f  NSE=%.2f  c=%.1f km/h",
                    up_c, down_c, rg, length, k, x, nse or float("nan"),
                    length / k if k > 0 else 0)

    # 2) trechos de previsao fonte->delta, por rio
    reaches: dict[str, ReachParams] = {}
    for rg, src in network["sources"].items():
        length = haversine_km(coords[src], coords[delta])
        k, x, nse = _source_to_delta(rg, src, valid, lags, length)
        reaches[rg] = ReachParams(reach_id=f"{rg}->delta", source_code=src,
                                  river_group=rg, length_km=round(length, 1),
                                  k_hours=round(k, 1), x=round(x, 3), nse=nse)
        logger.info("trecho de previsao %s: fonte %s -> delta  L=%.0f km  K=%.1f h  X=%.2f",
                    rg, src, length, k, x)
    return reaches, report


def _source_to_delta(rg, src, valid, lags, length):
    """K,X da perna fonte->delta: encadeia K validado + lag da regua de entrada."""
    # trecho validado que parte da propria fonte (ex.: Encantado->Lajeado)
    inter = next((v for (u, _d), v in valid.items() if u == src), None)
    inflow_code = INFLOW_GAUGE.get(rg)
    lag_final = lags[inflow_code].lag_hours if inflow_code in lags else 0.0
    if inter is not None:
        # K = viagem fonte->regua-de-entrada (validada) + regua-de-entrada->POA (lag)
        return inter["k"] + lag_final, inter["x"], inter["nse"]
    # sem validacao a partir da fonte: usa celeridade de qualquer trecho do rio
    river_valid = [v for v in valid.values() if v["river_group"] == rg]
    if river_valid:
        c = float(np.median([v["celerity"] for v in river_valid]))
        x = float(np.median([v["x"] for v in river_valid]))
        return max(length / c, 1.0), x, None
    # fonte == regua de entrada (Cai/Sinos/Gravatai): K = lag ate POA
    if lag_final > 0:
        return lag_final, DEFAULT_X, None
    return max(length / DEFAULT_CELERITY_KMH, 1.0), DEFAULT_X, None
