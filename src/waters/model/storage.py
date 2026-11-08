"""Geometria de armazenamento do Guaiba: area em funcao do estagio."""

from __future__ import annotations

from waters.domain.models import RatingParams, StageAreaCurve
from waters.model.area_curve import area_m2_at

M2_PER_KM2 = 1_000_000.0


def area_m2_at_stage(
    h_m: float, rating: RatingParams, curve: StageAreaCurve | None = None
) -> float:
    """Area superficial (m2) no estagio h.

    Se `curve` for dada, interpola a curva cota-area medida (preferido). Senao,
    cai no modelo linear A = A0*(1 + k*h): k=0 vira paredes verticais, k>0
    aproxima o espraiamento. O fallback preserva compatibilidade com dados
    sinteticos e com parametros antigos sem curva.
    """
    if curve is not None:
        return area_m2_at(h_m, curve)
    factor = max(1.0 + rating.area_stage_factor * h_m, 0.5)
    return rating.area_km2 * M2_PER_KM2 * factor
