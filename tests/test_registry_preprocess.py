"""Registro de estacoes e preprocessamento/QC."""

import numpy as np
import pandas as pd
import pytest

from conftest import make_hourly_index
from waters.config.registry import (
    get_registry,
    inflow_stations,
    target_station,
    target_stations,
)
from waters.domain.errors import WatersError
from waters.model.preprocess import coverage_fraction, qc_series, to_hourly_grid


def test_registry_loads_all_stations():
    registry = get_registry()
    assert len(registry) == 15
    assert {s.river_group for s in registry.values()} == {
        "jacui", "taquari", "cai", "sinos", "gravatai", "guaiba",
    }


def test_inflow_covers_five_rivers():
    groups = {s.river_group for s in inflow_stations()}
    assert groups == {"jacui", "taquari", "cai", "sinos", "gravatai"}


def test_default_target_is_porto_alegre():
    target = target_station()
    assert target.code == "87450020"
    assert target.cota_inundacao_m == 3.00
    assert target.mirror_of is None


def test_target_stations_base_comes_first():
    targets = target_stations()
    # base (mirror_of None) primeiro; derivadas depois em ordem alfabetica
    assert targets[0].code == "87450020"
    assert targets[0].mirror_of is None
    codes = {t.code for t in targets}
    assert codes == {"87450020", "87450004", "87450030"}
    for t in targets[1:]:
        assert t.mirror_of == "87450020"


def test_cais_maua_has_own_telemetry():
    cais = target_station(code="87450004")
    assert cais.own_telemetry is True
    assert cais.datum_offset_m == 0.44
    assert cais.cota_inundacao_m == 3.44


def test_target_station_by_code_and_unknown():
    assert target_station(code="87450030").name.startswith("Eldorado")
    with pytest.raises(WatersError):
        target_station(code="00000000")


def test_hourly_grid_interpolates_small_gaps_only():
    index = make_hourly_index("2025-06-01", 48)
    values = pd.Series(np.linspace(1.0, 2.0, 48), index=index)
    values.iloc[10:13] = np.nan   # lacuna de 3 h -> interpola
    values.iloc[20:40] = np.nan   # lacuna de 20 h -> mantem NaN
    frame = pd.DataFrame({"nivel_m": values, "vazao_m3s": np.nan, "chuva_mm": 0.0})
    hourly = to_hourly_grid(frame, max_gap_hours=6)
    assert hourly["nivel_m"].iloc[11] == pytest.approx(values.iloc[9], abs=0.2)
    assert hourly["nivel_m"].iloc[30:35].isna().all()


def test_qc_removes_spikes():
    index = make_hourly_index("2025-06-01", 24)
    series = pd.Series(1.0, index=index)
    series.iloc[12] = 8.0  # salto de 7 m em 1 h: impossivel
    clean = qc_series(series)
    assert pd.isna(clean.iloc[12])
    assert coverage_fraction(clean) < 1.0


def test_qc_removes_long_flatline():
    index = make_hourly_index("2025-06-01", 48)
    values = np.linspace(1.0, 3.0, 48)
    values[20:40] = values[20]  # 20 h identicas: sensor travado
    clean = qc_series(pd.Series(values, index=index))
    assert clean.iloc[25:39].isna().all()
