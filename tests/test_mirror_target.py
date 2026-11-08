"""Regua derivada (Eldorado do Sul): espelho na ingestao e alvo na previsao."""

import httpx
import pandas as pd
import pytest
import respx

from conftest import triangular_wave
from waters.config import settings
from waters.domain.models import (
    CalibrationParams,
    CrestParams,
    LagParams,
    RatingParams,
    ScenarioName,
    Station,
)
from waters.ingest.cache import ParquetCache
from waters.ingest.service import refresh_station
from waters.model.forecast import run_forecast

ELDORADO = "87450030"
CAIS = "87450004"
POA = "87450020"


@respx.mock
def test_own_telemetry_station_fetches_own_data_not_mirror(tmp_path, ana_xml):
    """Cais Maua tem telemetria propria: deve buscar da ANA, nao derivar da base."""
    respx.get(url__startswith=settings.ANA_BASE_URL).mock(
        return_value=httpx.Response(200, text=ana_xml)
    )
    result = refresh_station(CAIS, cache=ParquetCache(tmp_path))
    assert result.source == "ana"          # dados proprios, nao "espelho:..."
    assert not result.frame.empty


@respx.mock
def test_mirror_station_reflects_base_with_offset(tmp_path, ana_xml, monkeypatch):
    respx.get(url__startswith=settings.ANA_BASE_URL).mock(
        return_value=httpx.Response(200, text=ana_xml)
    )
    cache = ParquetCache(tmp_path)
    base = refresh_station(POA, cache=cache)
    mirror = refresh_station(ELDORADO, cache=cache)

    assert mirror.source == f"espelho:{POA}"
    offset = mirror.station.datum_offset_m
    expected = base.frame["nivel_m"] + offset
    pd.testing.assert_series_equal(mirror.frame["nivel_m"], expected)
    assert mirror.frame["vazao_m3s"].isna().all()


def _stations(offset: float, cota_eldorado: float) -> dict[str, Station]:
    return {
        "11111111": Station(
            code="11111111", name="afluente", slug="afl", river="taquari",
            river_group="taquari", role="inflow", has_vazao=True,
            cota_inundacao_m=18.0,
        ),
        POA: Station(
            code=POA, name="POA", slug="poa", river="Guaíba",
            river_group="guaiba", role="target", has_vazao=False,
            cota_inundacao_m=3.0,
        ),
        ELDORADO: Station(
            code=ELDORADO, name="Eldorado", slug="eldorado", river="Guaíba",
            river_group="guaiba", role="target", has_vazao=False,
            cota_inundacao_m=cota_eldorado, mirror_of=POA, datum_offset_m=offset,
        ),
    }


def test_forecast_for_mirror_target_shifts_trajectory(synthetic_flood):
    offset = 0.30
    stations = _stations(offset, cota_eldorado=3.0)
    poa = synthetic_flood["poa_level"]
    as_of = poa.idxmax() - pd.Timedelta(hours=36)
    params = CalibrationParams(
        version="test",
        generated_at=as_of.to_pydatetime(),
        events=["sintetico"],
        lags={"11111111": LagParams(station_code="11111111",
                                    lag_hours=synthetic_flood["lag_hours"])},
        rating=synthetic_flood["rating"],
        crests={"11111111": CrestParams(station_code="11111111",
                                        tau_rise_hours=18.0,
                                        tau_recession_hours=48.0)},
    )
    flows = {"11111111": synthetic_flood["upstream"][synthetic_flood["upstream"].index <= as_of]}
    poa_cut = poa[poa.index <= as_of]

    result_poa, traj_poa = run_forecast(
        flows, poa_cut, params, stations, now=as_of.to_pydatetime(), target_code=POA
    )
    result_eld, traj_eld = run_forecast(
        flows, poa_cut, params, stations, now=as_of.to_pydatetime(), target_code=ELDORADO
    )

    assert result_eld.target_code == ELDORADO
    central_poa = traj_poa[ScenarioName.CENTRAL]
    central_eld = traj_eld[ScenarioName.CENTRAL]
    pd.testing.assert_series_equal(central_eld, central_poa + offset)
    assert result_eld.h0_m == pytest.approx(result_poa.h0_m + offset, abs=0.01)
    assert result_eld.peaks[ScenarioName.CENTRAL].peak_level_m == pytest.approx(
        result_poa.peaks[ScenarioName.CENTRAL].peak_level_m + offset, abs=0.01
    )


def test_default_target_resolves_to_base(synthetic_flood):
    stations = _stations(0.5, cota_eldorado=3.0)
    poa = synthetic_flood["poa_level"]
    as_of = poa.idxmax() - pd.Timedelta(hours=36)
    params = CalibrationParams(
        version="test",
        generated_at=as_of.to_pydatetime(),
        events=["sintetico"],
        lags={"11111111": LagParams(station_code="11111111", lag_hours=24.0)},
        rating=synthetic_flood["rating"],
        crests={"11111111": CrestParams(station_code="11111111",
                                        tau_rise_hours=18.0,
                                        tau_recession_hours=48.0)},
    )
    flows = {"11111111": synthetic_flood["upstream"][synthetic_flood["upstream"].index <= as_of]}
    result, _ = run_forecast(
        flows, poa[poa.index <= as_of], params, stations, now=as_of.to_pydatetime()
    )
    assert result.target_code == POA
