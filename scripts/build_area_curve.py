"""Gera a curva cota-area A(h) do Guaiba a partir do DEM Copernicus GLO-30.

Ideia: a area que inunda em cota alta e TERRA, cuja elevacao esta num DEM
topografico. Contando a area de terreno abaixo de cada elevacao dentro do
poligono Guaiba+Delta, obtem-se A(elevacao). Ancoramos essa curva no datum
da regua do Gasometro pela area conhecida em cota normal (~470 km2): a cota
onde a area acumulada = 470 km2 corresponde ao nivel normal da regua.

Fonte: Copernicus GLO-30 (AWS Open Data, CC-BY 4.0). Sem autenticacao.
Uso: python scripts/build_area_curve.py
Saida: config/stage_area.yaml (curva derivada de DEM).
"""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import from_bounds

from waters.config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("build_area_curve")

# Recorte Guaiba + Delta do Jacui + varzea metropolitana de POA.
# Sul em -30.35 (Ponta dos Coatis/Barra do Ribeiro) para NAO capturar a
# Lagoa dos Patos, que armazenaria area alheia a resposta perto de POA.
LON_W, LON_E = -51.55, -51.05
LAT_S, LAT_N = -30.35, -29.85

TILES = ["Copernicus_DSM_COG_10_S31_00_W052_00_DEM",
         "Copernicus_DSM_COG_10_S30_00_W052_00_DEM"]
AWS_BASE = "https://copernicus-dem-30m.s3.amazonaws.com"
DEM_DIR = settings.DATA_DIR / "dem"

# Ancoragem no datum da regua do Gasometro
NORMAL_AREA_KM2 = 470.0     # superficie classica do Guaiba em cota normal
NORMAL_GAUGE_M = 0.9        # nivel normal tipico na regua (m)
GAUGE_LEVELS = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

M_PER_DEG_LAT = 110_540.0
M_PER_DEG_LON = 111_320.0


def download_tiles() -> list[Path]:
    DEM_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in TILES:
        dest = DEM_DIR / f"{name}.tif"
        if not dest.exists():
            url = f"{AWS_BASE}/{name}/{name}.tif"
            logger.info("Baixando %s ...", name)
            urllib.request.urlretrieve(url, dest)
        logger.info("%s: %.1f MB", dest.name, dest.stat().st_size / 1e6)
        paths.append(dest)
    return paths


def collect_elevation_area(paths: list[Path]) -> tuple[np.ndarray, np.ndarray]:
    """Devolve (elevacoes, area_por_pixel_m2) de todos os pixels no recorte."""
    elevs, areas = [], []
    for path in paths:
        with rasterio.open(path) as ds:
            window = from_bounds(LON_W, LAT_S, LON_E, LAT_N, ds.transform)
            arr = ds.read(1, window=window).astype("float64")
            wt = ds.window_transform(window)
            rows, cols = arr.shape
            if rows == 0 or cols == 0:
                continue
            # latitude do centro de cada linha (wt.e e negativo)
            lats = wt.f + (np.arange(rows) + 0.5) * wt.e
            px_lon_deg, px_lat_deg = wt.a, -wt.e
            row_area = (
                px_lon_deg * M_PER_DEG_LON * np.cos(np.radians(lats))
                * px_lat_deg * M_PER_DEG_LAT
            )
            area2d = np.repeat(row_area[:, None], cols, axis=1)
            nodata = ds.nodata
            mask = np.isfinite(arr)
            if nodata is not None:
                mask &= arr != nodata
            elevs.append(arr[mask])
            areas.append(area2d[mask])
    return np.concatenate(elevs), np.concatenate(areas)


def cumulative_area_fn(elevs: np.ndarray, areas: np.ndarray):
    """Funcao area(E) = soma das areas de terreno com elevacao <= E (m2)."""
    order = np.argsort(elevs)
    e_sorted = elevs[order]
    a_cum = np.cumsum(areas[order])

    def area_below(elevation: float) -> float:
        idx = np.searchsorted(e_sorted, elevation, side="right")
        return float(a_cum[idx - 1]) if idx > 0 else 0.0

    return area_below, e_sorted


def build_curve() -> dict:
    paths = download_tiles()
    elevs, areas = collect_elevation_area(paths)
    logger.info("Pixels no recorte: %d | elevacao %.1f a %.1f m",
                len(elevs), elevs.min(), elevs.max())

    area_below, e_sorted = cumulative_area_fn(elevs, areas)
    target_m2 = NORMAL_AREA_KM2 * 1e6

    # E_ref: elevacao (datum DEM) onde a area acumulada iguala a normal
    a_cum = np.cumsum(np.sort(areas)[np.argsort(np.argsort(elevs))]) if False else None
    grid = np.linspace(elevs.min(), elevs.min() + 15.0, 3000)
    cum = np.array([area_below(e) for e in grid])
    e_ref = float(np.interp(target_m2, cum, grid))
    logger.info("E_ref (area=%.0f km2) = %.2f m no datum do DEM = nivel %.1f m na regua",
                NORMAL_AREA_KM2, e_ref, NORMAL_GAUGE_M)

    points = []
    for h in GAUGE_LEVELS:
        elevation = e_ref + (h - NORMAL_GAUGE_M)
        # piso: a lamina nunca e menor que a area normal do lago (o DEM nao
        # enxerga sob a agua, entao subestima a area abaixo da linha d'agua).
        area_km2 = max(area_below(elevation) / 1e6, NORMAL_AREA_KM2)
        points.append((h, round(area_km2)))
        logger.info("regua %.1f m -> DEM %.2f m -> A = %.0f km2", h, elevation, area_km2)

    # garante monotonicidade (a interpolacao exige nao-decrescente)
    for i in range(1, len(points)):
        if points[i][1] < points[i - 1][1]:
            points[i] = (points[i][0], points[i - 1][1])
    return points


def write_yaml(points: list[tuple[float, int]]) -> None:
    lines = [
        "# Curva cota-area A(h) do Guaiba DERIVADA DO DEM Copernicus GLO-30.",
        "# Gerada por scripts/build_area_curve.py. Nivel na regua do Gasometro,",
        f"# ancorado pela area normal {NORMAL_AREA_KM2:.0f} km2 no nivel {NORMAL_GAUGE_M} m.",
        "# Recorte: Guaiba + Delta do Jacui (sem Lagoa dos Patos).",
        "# produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved",
        'source: "DEM Copernicus GLO-30 (AWS Open Data); recorte Guaiba+Delta"',
        "points:",
    ]
    for h, a in points:
        lines.append(f"  - {{nivel_m: {h}, area_km2: {a}}}")
    settings.STAGE_AREA_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Curva gravada em %s", settings.STAGE_AREA_FILE)


if __name__ == "__main__":
    write_yaml(build_curve())
