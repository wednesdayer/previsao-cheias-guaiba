"""Pre-computa o raster de "nivel-de-chegada" da inundacao do Guaiba.

Para cada pixel de terra, o menor nivel da regua do Gasometro (m) em que ele
fica alagado E conectado ao corpo d'agua (modelo bathtub com conectividade).
Assim o dashboard so faz `arrival <= h` para inundar instantaneamente.

Fonte topografica: DEM Copernicus GLO-30 ja baixado em data/dem/ por
scripts/build_area_curve.py. Rodar uma vez:
    python scripts/build_inundation.py
Saida: data/inundation/region.npz (dem, arrival, metadados).
"""

from __future__ import annotations

import json
import logging

import numpy as np
from scipy import ndimage

from waters.config import settings
from waters.model import topo

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("build_inundation")

# Recorte cobrindo Porto Alegre + Eldorado do Sul + Delta do Jacui
BBOX = (-51.68, -30.36, -51.05, -29.85)   # lon_w, lat_s, lon_e, lat_n
TILES = ["Copernicus_DSM_COG_10_S31_00_W052_00_DEM",
         "Copernicus_DSM_COG_10_S30_00_W052_00_DEM"]
NORMAL_AREA_KM2 = settings.GUAIBA_AREA_KM2

GAUGE_MIN, GAUGE_MAX, GAUGE_STEP = 0.0, 6.0, 0.05

# Presets de zoom (lon_w, lat_s, lon_e, lat_n) para a UI
PRESETS = {
    "regiao": list(BBOX),
    "poa": [-51.30, -30.09, -51.16, -29.97],
    "eldorado": [-51.68, -30.12, -51.54, -30.00],
}


def build() -> None:
    tile_paths = [settings.DEM_DIR / f"{t}.tif" for t in TILES]
    missing = [p for p in tile_paths if not p.exists()]
    if missing:
        raise SystemExit(f"Tiles ausentes: {missing}. Rode scripts/build_area_curve.py antes.")

    dem, transform = topo.read_dem_clip(BBOX, tile_paths)
    logger.info("Recorte: %s px, elevacao %.1f a %.1f m",
                dem.shape, np.nanmin(dem), np.nanmax(dem))
    area_m2 = topo.pixel_area_m2(transform, dem.shape)
    e_ref = topo.find_e_ref(dem, area_m2, NORMAL_AREA_KM2)
    logger.info("E_ref (area=%.0f km2) = %.2f m no datum do DEM (regua %.1f m)",
                NORMAL_AREA_KM2, e_ref, settings.NORMAL_GAUGE_M)

    # Semente = maior componente conexo da agua em nivel normal (Guaiba+Jacui)
    normal_wet = np.isfinite(dem) & (dem <= e_ref)
    labels, n = ndimage.label(normal_wet)
    if n == 0:
        raise SystemExit("Nenhuma agua no nivel normal — verificar E_ref/recorte.")
    sizes = ndimage.sum(np.ones_like(labels), labels, index=np.arange(1, n + 1))
    seed_label = int(np.argmax(sizes)) + 1
    seed = labels == seed_label
    logger.info("Semente de agua: %d px (%.0f km2)", seed.sum(), area_m2[seed].sum() / 1e6)

    arrival = np.full(dem.shape, np.inf, dtype="float64")
    gauges = np.round(np.arange(GAUGE_MIN, GAUGE_MAX + 1e-9, GAUGE_STEP), 3)
    for g in gauges:
        water_elev = topo.gauge_to_dem_elev(g, e_ref)
        wet = np.isfinite(dem) & (dem <= water_elev)
        lab, _ = ndimage.label(wet)
        seed_labels = np.unique(lab[seed & (lab > 0)])
        connected = np.isin(lab, seed_labels) & wet
        newly = connected & ~np.isfinite(arrival)
        arrival[newly] = g

    # Sanidade: area alagada de terra (acima do normal) a 3 m e 5 m
    for g in (3.0, 5.0):
        land_flooded = (arrival <= g) & (dem > e_ref)
        logger.info("Cota %.1f m -> terra alagada %.0f km2 (area total ~%.0f km2)",
                    g, area_m2[land_flooded].sum() / 1e6,
                    area_m2[(arrival <= g)].sum() / 1e6)

    settings.INUNDATION_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "bbox": list(BBOX),
        "transform": [transform.a, transform.b, transform.c,
                      transform.d, transform.e, transform.f],
        "e_ref": e_ref,
        "normal_gauge_m": settings.NORMAL_GAUGE_M,
        "gauge_min": GAUGE_MIN, "gauge_max": GAUGE_MAX, "gauge_step": GAUGE_STEP,
        "presets": PRESETS,
        "source": "DEM Copernicus GLO-30 (AWS Open Data); bathtub + conectividade",
    }
    np.savez_compressed(
        settings.INUNDATION_FILE,
        dem=dem.astype("float32"),
        arrival=arrival.astype("float32"),
        meta=json.dumps(meta),
    )
    logger.info("Gravado %s (%.1f MB)",
                settings.INUNDATION_FILE,
                settings.INUNDATION_FILE.stat().st_size / 1e6)


if __name__ == "__main__":
    build()
