"""Helpers de topografia sobre o DEM: area por cota, datum e inundacao.

Puro numpy + (opcionalmente) rasterio para ler os tiles. O import de rasterio
e preguicoso (dentro da funcao de leitura), para que o dashboard possa importar
este modulo sem depender de rasterio.

Datum: o nivel da regua do Gasometro (m) vira elevacao no DEM por
    elev_DEM(h) = E_ref + (h - NORMAL_GAUGE_M)
onde E_ref e a elevacao (no datum do DEM) em que a area acumulada abaixo dela
iguala a area normal do lago (~470 km2), i.e., a linha d'agua no nivel normal.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from waters.config import settings

M_PER_DEG_LAT = 110_540.0
M_PER_DEG_LON = 111_320.0


def read_dem_clip(
    bbox: tuple[float, float, float, float], tile_paths: list[Path]
) -> tuple[np.ndarray, object]:
    """Le e recorta os tiles do DEM ao bbox (lon_w, lat_s, lon_e, lat_n).

    Devolve (dem float64 com NaN no nodata, affine transform do recorte).
    """
    import rasterio
    from rasterio.merge import merge
    from rasterio.windows import from_bounds

    datasets = [rasterio.open(p) for p in tile_paths]
    try:
        mosaic, transform = merge(datasets)
    finally:
        for ds in datasets:
            ds.close()
    band = mosaic[0]
    nodata = datasets[0].nodata if datasets else None

    lon_w, lat_s, lon_e, lat_n = bbox
    window = from_bounds(lon_w, lat_s, lon_e, lat_n, transform)
    r0 = max(int(np.floor(window.row_off)), 0)
    c0 = max(int(np.floor(window.col_off)), 0)
    r1 = min(int(np.ceil(window.row_off + window.height)), band.shape[0])
    c1 = min(int(np.ceil(window.col_off + window.width)), band.shape[1])
    clip = band[r0:r1, c0:c1].astype("float64")

    from rasterio.transform import Affine

    clip_transform = transform * Affine.translation(c0, r0)
    if nodata is not None:
        clip[clip == nodata] = np.nan
    return clip, clip_transform


def pixel_area_m2(transform, shape: tuple[int, int]) -> np.ndarray:
    """Area (m2) de cada pixel, corrigida pela latitude da linha."""
    rows, cols = shape
    px_lon_deg = transform.a
    px_lat_deg = -transform.e
    lats = transform.f + (np.arange(rows) + 0.5) * transform.e
    row_area = (
        px_lon_deg * M_PER_DEG_LON * np.cos(np.radians(lats))
        * px_lat_deg * M_PER_DEG_LAT
    )
    return np.repeat(row_area[:, None], cols, axis=1)


def find_e_ref(dem: np.ndarray, area_m2: np.ndarray, target_area_km2: float) -> float:
    """Elevacao (datum do DEM) onde a area acumulada abaixo dela = target."""
    valid = np.isfinite(dem)
    elev = dem[valid].ravel()
    area = area_m2[valid].ravel()
    order = np.argsort(elev)
    e_sorted = elev[order]
    cum = np.cumsum(area[order])
    return float(np.interp(target_area_km2 * 1e6, cum, e_sorted))


def gauge_to_dem_elev(
    gauge_m: float, e_ref: float, normal_gauge_m: float | None = None
) -> float:
    """Converte nivel da regua (m) em elevacao no datum do DEM (m)."""
    normal = settings.NORMAL_GAUGE_M if normal_gauge_m is None else normal_gauge_m
    return e_ref + (gauge_m - normal)


def flooded_depth(
    dem: np.ndarray,
    arrival_gauge: np.ndarray,
    gauge_m: float,
    e_ref: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Mascara de terra inundada e profundidade (m) na cota `gauge_m`.

    Inundado = pixel cujo nivel-de-chegada (com conectividade) <= gauge_m.
    Profundidade = elev_DEM(gauge) - elev_pixel, saturada em >= 0.
    """
    water_elev = gauge_to_dem_elev(gauge_m, e_ref)
    mask = np.isfinite(arrival_gauge) & (arrival_gauge <= gauge_m)
    depth = np.where(mask, np.clip(water_elev - dem, 0.0, None), 0.0)
    return mask, depth
