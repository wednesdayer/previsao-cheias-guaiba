"""Cadeia de fallback da ingestao, com HTTP mockado (respx)."""

import httpx
import pandas as pd
import pytest
import respx

from waters.config import settings
from waters.domain.errors import StationOfflineError
from waters.ingest.cache import ParquetCache
from waters.ingest.service import refresh_station

POA = "87450020"
ANA_URL = settings.ANA_BASE_URL


def _nivelguaiba_payload() -> dict:
    now = pd.Timestamp.now(tz=settings.TZ).floor("15min")
    return {
        "readings": [
            {"timestamp": (now - pd.Timedelta(minutes=15 * i)).isoformat(), "level": 1.0 + i / 100}
            for i in range(8)
        ]
    }


@respx.mock
def test_ana_ok_populates_cache(tmp_path, ana_xml):
    respx.get(url__startswith=ANA_URL).mock(return_value=httpx.Response(200, text=ana_xml))
    result = refresh_station(POA, cache=ParquetCache(tmp_path))
    assert result.source == "ana"
    assert not result.frame.empty


@respx.mock
def test_ana_down_falls_back_to_nivelguaiba(tmp_path):
    respx.get(url__startswith=ANA_URL).mock(return_value=httpx.Response(500))
    respx.get(url__startswith=settings.NIVELGUAIBA_BASE_URL).mock(
        return_value=httpx.Response(200, json=_nivelguaiba_payload())
    )
    result = refresh_station(POA, cache=ParquetCache(tmp_path))
    assert result.source == "fallback"
    assert not result.frame.empty
    assert not result.is_stale


@respx.mock
def test_all_sources_down_and_empty_cache_raises(tmp_path):
    respx.get(url__startswith=ANA_URL).mock(return_value=httpx.Response(500))
    respx.get(url__startswith=settings.NIVELGUAIBA_BASE_URL).mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(StationOfflineError):
        refresh_station(POA, cache=ParquetCache(tmp_path))


@respx.mock
def test_all_sources_down_serves_stale_cache(tmp_path, ana_xml):
    cache = ParquetCache(tmp_path)
    respx.get(url__startswith=ANA_URL).mock(return_value=httpx.Response(200, text=ana_xml))
    refresh_station(POA, cache=cache)

    respx.get(url__startswith=ANA_URL).mock(return_value=httpx.Response(500))
    respx.get(url__startswith=settings.NIVELGUAIBA_BASE_URL).mock(
        return_value=httpx.Response(500)
    )
    result = refresh_station(POA, cache=cache)
    assert result.source == "cache"
    assert not result.frame.empty


def test_unknown_station_raises(tmp_path):
    with pytest.raises(StationOfflineError):
        refresh_station("00000000", cache=ParquetCache(tmp_path))
