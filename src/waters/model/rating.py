"""Curva de descarga do Guaiba: Qout(h) = a * (h - h0)^b.

Nao existe medicao de vazao em Porto Alegre, entao a curva e ajustada para
fechar o balanco de massa no historico:
    Qout(t) = Qin(t) - A(h) * dh/dt
e depois regredida contra h com perda robusta (Huber), porque vento/seiche
e remanso da Lagoa dos Patos geram outliers grandes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from waters.domain.errors import CalibrationError
from waters.domain.models import RatingParams, StageAreaCurve
from waters.model.area_curve import area_km2_at
from waters.model.preprocess import rate_of_change
from waters.model.storage import M2_PER_KM2

MIN_POINTS = 100


def _area_km2_series(
    h: pd.Series, area_km2: float, area_stage_factor: float, curve: StageAreaCurve | None
) -> pd.Series:
    """Area (km2) por instante: curva interpolada, ou linear como fallback."""
    if curve is not None:
        return h.map(lambda v: area_km2_at(v, curve))
    return area_km2 * (1.0 + area_stage_factor * h)


def implied_outflow(
    poa_level: pd.Series,
    total_inflow: pd.Series,
    area_km2: float,
    area_stage_factor: float = 0.0,
    curve: StageAreaCurve | None = None,
) -> pd.Series:
    """Qout implicito pelo balanco, em m3/s, na grade horaria comum."""
    joined = pd.concat(
        [poa_level.rename("h"), total_inflow.rename("qin")], axis=1, join="inner"
    ).dropna()
    dh_dt_m_per_s = rate_of_change(joined["h"]) / 3600.0
    area_m2 = _area_km2_series(joined["h"], area_km2, area_stage_factor, curve) * M2_PER_KM2
    qout = joined["qin"] - area_m2 * dh_dt_m_per_s
    return qout.dropna()


def fit_rating(
    poa_level: pd.Series,
    implied_qout: pd.Series,
    area_km2: float,
    area_stage_factor: float = 0.0,
) -> RatingParams:
    """Ajusta Qout = a*(h-h0)^b por minimos quadrados robustos (Huber)."""
    joined = pd.concat(
        [poa_level.rename("h"), implied_qout.rename("qout")], axis=1, join="inner"
    ).dropna()
    joined = joined[joined["qout"] > 0]
    if len(joined) < MIN_POINTS:
        raise CalibrationError(
            f"So {len(joined)} pontos validos para a curva de descarga; minimo {MIN_POINTS}."
        )

    h = joined["h"].to_numpy()
    q = joined["qout"].to_numpy()
    h_min = float(h.min())

    def residuals(theta: np.ndarray) -> np.ndarray:
        a, h0, b = theta
        depth = np.clip(h - h0, 1e-6, None)
        return a * depth**b - q

    q_med = float(np.median(q))
    initial = np.array([q_med, h_min - 1.0, 1.5])
    result = least_squares(
        residuals,
        initial,
        loss="huber",
        f_scale=max(q_med * 0.2, 100.0),
        bounds=([1.0, h_min - 20.0, 0.3], [1e7, h_min - 0.01, 4.0]),
        max_nfev=5000,
    )
    if not result.success:
        raise CalibrationError(f"Ajuste da curva de descarga nao convergiu: {result.message}")

    a, h0, b = (float(v) for v in result.x)
    rmse = float(np.sqrt(np.mean(residuals(result.x) ** 2)))
    return RatingParams(
        a=a, h0=h0, b=b, area_km2=area_km2,
        area_stage_factor=area_stage_factor, rmse_m3s=rmse,
    )


def predict_qout(h_m: float, rating: RatingParams) -> float:
    """Vazao de saida (m3/s) prevista pela curva no estagio h."""
    depth = max(h_m - rating.h0, 0.0)
    return rating.a * depth**rating.b


def reconstructed_inflow(
    poa_level: pd.Series, rating: RatingParams, curve: StageAreaCurve | None = None
) -> pd.Series:
    """Fluxo de entrada implicito: F(t) = A(h)*dh/dt + Qout(h), em m3/s.

    E o inverso do balanco — dado o nivel observado e a curva ajustada,
    recupera quanta agua estava chegando. Serve para re-estimar lags sem o
    vies que o termo -Qout introduz quando se usa so dh/dt.
    """
    valid = poa_level.dropna()
    dh_dt_m_per_s = rate_of_change(valid) / 3600.0
    area_m2 = _area_km2_series(
        valid, rating.area_km2, rating.area_stage_factor, curve
    ) * M2_PER_KM2
    qout = valid.map(lambda h: predict_qout(h, rating))
    return (area_m2 * dh_dt_m_per_s + qout).dropna()
