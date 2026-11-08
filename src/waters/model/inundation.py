"""Carrega o pre-computo de inundacao e gera o overlay RGBA para o mapa.

Sem rasterio nem Streamlit: puro numpy, testavel. O overlay pinta a agua
baseline (azul) e a terra recem-alagada (vermelho graduado por profundidade).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from waters.config import settings
from waters.model import topo


@dataclass(frozen=True)
class InundationData:
    """DEM recortado + raster de nivel-de-chegada + metadados do recorte."""

    dem: np.ndarray
    arrival: np.ndarray
    e_ref: float
    normal_gauge_m: float
    bbox: tuple[float, float, float, float]   # lon_w, lat_s, lon_e, lat_n
    gauge_min: float
    gauge_max: float
    presets: dict[str, list[float]]
    source: str


def load_inundation(path: Path | None = None) -> InundationData:
    """Le region.npz. Levanta FileNotFoundError se o pre-computo nao existe."""
    file = path or settings.INUNDATION_FILE
    if not file.exists():
        raise FileNotFoundError(
            f"Pre-computo de inundacao ausente: {file}. "
            "Rode: python scripts/build_inundation.py"
        )
    npz = np.load(file, allow_pickle=False)
    meta = json.loads(str(npz["meta"]))
    return InundationData(
        dem=npz["dem"],
        arrival=npz["arrival"],
        e_ref=float(meta["e_ref"]),
        normal_gauge_m=float(meta["normal_gauge_m"]),
        bbox=tuple(meta["bbox"]),
        gauge_min=float(meta["gauge_min"]),
        gauge_max=float(meta["gauge_max"]),
        presets={k: list(v) for k, v in meta["presets"].items()},
        source=str(meta["source"]),
    )


def flooded_area_km2(inund: InundationData, gauge_m: float, land_only: bool = True) -> float:
    """Area (km2) alagada na cota. land_only exclui a agua baseline."""
    mask, _ = topo.flooded_depth(inund.dem, inund.arrival, gauge_m, inund.e_ref)
    if land_only:
        mask = mask & (inund.dem > inund.e_ref)
    # area por pixel varia pouco no recorte; usa o pixel do centro (lat media)
    lat_mid = (inund.bbox[1] + inund.bbox[3]) / 2.0
    px_deg = 1.0 / 3600.0
    px_km2 = (px_deg * topo.M_PER_DEG_LON * np.cos(np.radians(lat_mid))
              * px_deg * topo.M_PER_DEG_LAT) / 1e6
    return float(mask.sum() * px_km2)


def _downsample(arr: np.ndarray, max_width: int) -> np.ndarray:
    """Subamostra por fatiamento (rapido) para no maximo max_width colunas."""
    step = max(1, arr.shape[1] // max_width)
    return arr[::step, ::step]


def overlay_rgba(
    inund: InundationData,
    gauge_m: float,
    depth_gradient: bool = True,
    max_width: int = 1200,
) -> tuple[np.ndarray, list[float]]:
    """RGBA (HxWx4 uint8) da inundacao na cota; e os bounds [w,s,e,n].

    - Agua baseline (dem <= E_ref): azul translucido.
    - Terra alagada e conectada: vermelho; alfa cresce com a profundidade se
      depth_gradient, senao alfa fixo.
    """
    dem = _downsample(inund.dem, max_width)
    arrival = _downsample(inund.arrival, max_width)
    mask, depth = topo.flooded_depth(dem, arrival, gauge_m, inund.e_ref)

    baseline_water = np.isfinite(dem) & (dem <= inund.e_ref)
    land_flood = mask & ~baseline_water

    h, w = dem.shape
    rgba = np.zeros((h, w, 4), dtype="uint8")

    # agua baseline: azul (70,130,180) translucido
    rgba[baseline_water] = (70, 130, 180, 90)

    # terra alagada: vermelho, alfa por profundidade
    if depth_gradient:
        norm = np.clip(depth / 4.0, 0.0, 1.0)   # satura em ~4 m de lamina
        alpha = (90 + 150 * norm).astype("uint8")
    else:
        alpha = np.full(dem.shape, 170, dtype="uint8")
    rgba[land_flood, 0] = 220
    rgba[land_flood, 1] = 30
    rgba[land_flood, 2] = 30
    rgba[land_flood, 3] = alpha[land_flood]

    lon_w, lat_s, lon_e, lat_n = inund.bbox
    return rgba, [lon_w, lat_s, lon_e, lat_n]
