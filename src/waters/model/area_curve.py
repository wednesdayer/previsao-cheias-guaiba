"""Interpolacao da curva cota-area A(h) do Guaiba.

A banheira de paredes retas (area constante) subestima o armazenamento em
cota alta: ao subir, a lamina se espraia sobre o Delta do Jacui e as varzeas
metropolitanas, entao precisa de muito mais volume para subir 1 cm. Esta
curva tabela A(h) e o balanco de massa a interpola a cada passo.

A tabela padrao (config/stage_area.yaml) e uma curva hipsometrica aproximada,
ancorada em fatos conhecidos (Guaiba ~470 km2 em cota normal; recorde de
5,35 m em mai/2024 com inundacao metropolitana extensa). Deve ser refinada
com uma curva extraida de DEM (Copernicus GLO-30 / MERIT) do delta.
"""

from __future__ import annotations

import numpy as np

from waters.domain.models import StageAreaCurve

M2_PER_KM2 = 1_000_000.0


def area_km2_at(h_m: float, curve: StageAreaCurve) -> float:
    """Area (km2) no estagio h; fora da tabela, mantem o valor da borda."""
    return float(np.interp(h_m, curve.levels_m, curve.areas_km2))


def area_m2_at(h_m: float, curve: StageAreaCurve) -> float:
    """Area (m2) no estagio h."""
    return area_km2_at(h_m, curve) * M2_PER_KM2
