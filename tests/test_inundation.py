"""Topografia e inundacao: datum, conectividade, profundidade, overlay."""

import json

import numpy as np
import pytest
from scipy import ndimage

from waters.model import topo
from waters.model.inundation import InundationData, load_inundation, overlay_rgba


def test_gauge_to_dem_elev_uses_normal_anchor():
    # E_ref=0, normal=0.9 => regua 0.9 vira elevacao 0; regua 3 vira 2.1
    assert topo.gauge_to_dem_elev(0.9, e_ref=0.0, normal_gauge_m=0.9) == pytest.approx(0.0)
    assert topo.gauge_to_dem_elev(3.0, e_ref=0.0, normal_gauge_m=0.9) == pytest.approx(2.1)


def _arrival_from_dem(dem, e_ref, gauges):
    """Replica a logica de conectividade do script, em pequena escala."""
    normal_wet = np.isfinite(dem) & (dem <= e_ref)
    labels, n = ndimage.label(normal_wet)
    sizes = ndimage.sum(np.ones_like(labels), labels, index=np.arange(1, n + 1))
    seed = labels == (int(np.argmax(sizes)) + 1)
    arrival = np.full(dem.shape, np.inf)
    for g in gauges:
        elev = topo.gauge_to_dem_elev(g, e_ref, 0.9)
        wet = np.isfinite(dem) & (dem <= elev)
        lab, _ = ndimage.label(wet)
        seed_labels = np.unique(lab[seed & (lab > 0)])
        connected = np.isin(lab, seed_labels) & wet
        arrival[connected & ~np.isfinite(arrival)] = g
    return arrival


def test_connectivity_excludes_isolated_pit():
    # coluna de agua a esquerda (baixa); rampa subindo para a direita;
    # um "poco" isolado (baixo) cercado por terreno alto no meio.
    dem = np.tile(np.linspace(-1.0, 5.0, 12), (6, 1))  # rampa em elevacao
    dem[2:4, 8] = -0.5   # poco isolado abaixo do nivel, cercado por rampa alta
    e_ref = 0.0
    gauges = np.round(np.arange(0.0, 6.01, 0.1), 2)
    arrival = _arrival_from_dem(dem, e_ref, gauges)

    # o poco isolado (col 8, elev -0.5) NAO deve inundar em cota baixa via si
    # mesmo: so quando a agua conectada da esquerda alcanca a coluna 8.
    # A coluna 0 (elev -1) e semente; colunas intermediarias sobem gradualmente.
    left = arrival[3, 0]
    pit = arrival[3, 8]
    assert left <= 0.9                      # semente molhada desde cedo
    # o poco so molha quando a rampa ate ele estiver submersa (cota alta)
    assert pit > left


def test_flood_grows_monotonically_with_level():
    dem = np.tile(np.linspace(-1.0, 5.0, 40), (10, 1))
    e_ref = 0.0
    gauges = np.round(np.arange(0.0, 6.01, 0.1), 2)
    arrival = _arrival_from_dem(dem, e_ref, gauges)
    areas = [(arrival <= g).sum() for g in (1.0, 2.0, 3.0, 4.0)]
    assert areas == sorted(areas)          # nao decrescente
    assert areas[-1] > areas[0]            # cresce


def test_flooded_depth_matches_water_minus_terrain():
    dem = np.array([[-1.0, 0.0, 1.0, 2.0]])
    arrival = np.array([[0.0, 0.0, 3.0, 5.0]])
    e_ref = 0.0
    mask, depth = topo.flooded_depth(dem, arrival, gauge_m=3.0, e_ref=e_ref)
    # cota 3 => elev agua = 0 + (3-0.9) = 2.1
    assert mask.tolist() == [[True, True, True, False]]
    assert depth[0, 2] == pytest.approx(2.1 - 1.0)   # 1.1 m de lamina
    assert depth[0, 3] == pytest.approx(0.0)


def _fake_inund() -> InundationData:
    dem = np.tile(np.linspace(-1.0, 4.0, 20), (10, 1)).astype("float32")
    arrival = np.tile(np.linspace(0.0, 6.0, 20), (10, 1)).astype("float32")
    return InundationData(
        dem=dem, arrival=arrival, e_ref=0.0, normal_gauge_m=0.9,
        bbox=(-51.6, -30.3, -51.1, -29.9), gauge_min=0.0, gauge_max=6.0,
        presets={"regiao": [-51.6, -30.3, -51.1, -29.9]}, source="teste",
    )


def test_overlay_rgba_shapes_and_colors():
    inund = _fake_inund()
    rgba, bounds = overlay_rgba(inund, gauge_m=3.0, depth_gradient=True, max_width=50)
    assert rgba.shape[2] == 4
    assert bounds == [-51.6, -30.3, -51.1, -29.9]
    # ha pixels vermelhos (terra alagada) e azuis (agua baseline)
    red = (rgba[..., 0] > 150) & (rgba[..., 3] > 0)
    blue = (rgba[..., 2] > 120) & (rgba[..., 0] < 120) & (rgba[..., 3] > 0)
    assert red.any()
    assert blue.any()


def test_overlay_depth_gradient_increases_alpha():
    inund = _fake_inund()
    shallow, _ = overlay_rgba(inund, gauge_m=1.5, depth_gradient=True, max_width=50)
    deep, _ = overlay_rgba(inund, gauge_m=5.0, depth_gradient=True, max_width=50)
    # mais cota => lamina mais funda => alfa medio do vermelho maior
    def red_alpha(rgba):
        red = (rgba[..., 0] > 150)
        return rgba[..., 3][red].mean() if red.any() else 0
    assert red_alpha(deep) >= red_alpha(shallow)


def test_load_inundation_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_inundation(tmp_path / "nao_existe.npz")


def test_pixel_area_positive_and_plausible():
    from affine import Affine
    tr = Affine(1 / 3600, 0, -51.5, 0, -1 / 3600, -30.0)  # ~30 m px em lat -30
    area = topo.pixel_area_m2(tr, (5, 5))
    assert area.shape == (5, 5)
    assert (area > 0).all()
    # 1 arc-sec ~30 m; pixel ~ 26 m (lon, cos30) x 31 m (lat) ~ 700-900 m2
    assert 600 < float(area.mean()) < 1000


def test_find_e_ref_at_half_area():
    import numpy as np
    dem = np.linspace(0.0, 10.0, 1000).reshape(1, 1000)
    area = np.ones_like(dem)          # area uniforme por pixel
    e_ref = topo.find_e_ref(dem, area, target_area_km2=(500.0) / 1e6)  # metade dos 1000 px
    assert e_ref == pytest.approx(5.0, abs=0.2)   # mediana da elevacao
