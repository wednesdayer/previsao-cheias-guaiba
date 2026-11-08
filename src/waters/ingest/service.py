"""Orquestra a ingestao: cache -> ANA incremental -> fallback nivelguaiba.

Nunca derruba o chamador por causa de uma estacao fora do ar: devolve o que
tem, marcado como defasado quando for o caso.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd

from waters.config import settings
from waters.config.registry import get_registry
from waters.domain.errors import IngestError, StationOfflineError
from waters.domain.models import Station
from waters.ingest.ana_client import date_chunks, fetch_ana_xml
from waters.ingest.ana_parser import parse_ana_xml
from waters.ingest.cache import ParquetCache
from waters.ingest.nivelguaiba_client import fetch_nivelguaiba

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SeriesResult:
    """Serie de uma estacao com metadados de qualidade."""

    station: Station
    frame: pd.DataFrame
    source: str            # "ana" | "fallback" | "cache"
    is_stale: bool
    fetched_at: datetime = field(default_factory=lambda: datetime.now(settings.TZ))

    @property
    def last_timestamp(self) -> pd.Timestamp | None:
        return None if self.frame.empty else self.frame.index[-1]


def _now() -> datetime:
    return datetime.now(settings.TZ)


def _staleness(frame: pd.DataFrame) -> bool:
    if frame.empty:
        return True
    age = _now() - frame.index[-1].to_pydatetime()
    return age > timedelta(hours=settings.STALE_AFTER_HOURS)


def refresh_station(
    code: str,
    start: datetime | None = None,
    cache: ParquetCache | None = None,
) -> SeriesResult:
    """Atualiza a serie de uma estacao ate agora e devolve tudo que ha em cache.

    Busca incremental: da ultima leitura em cache (menos a sobreposicao) ate hoje.
    """
    registry = get_registry()
    if code not in registry:
        raise StationOfflineError(code, "Codigo ausente do registro de estacoes.")
    station = registry[code]
    if station.mirror_of is not None and not station.own_telemetry:
        return _mirror_result(station, start=start, cache=cache)
    store = cache or ParquetCache()

    last = store.last_timestamp(code)
    fetch_start = start or (
        last - timedelta(hours=settings.CACHE_OVERLAP_HOURS)
        if last is not None
        else _now() - timedelta(days=10)
    )

    source = "cache"
    try:
        for chunk_start, chunk_end in date_chunks(fetch_start, _now()):
            xml_text = fetch_ana_xml(code, chunk_start, chunk_end)
            store.upsert(code, parse_ana_xml(xml_text))
        source = "ana"
    except IngestError as exc:
        logger.warning("ANA falhou para %s (%s); tentando fallback", code, exc)
        try:
            store.upsert(code, fetch_nivelguaiba(station.slug, "7days"))
            source = "fallback"
        except IngestError as fallback_exc:
            logger.error("Fallback tambem falhou para %s: %s", code, fallback_exc)

    frame = store.read(code)
    if frame.empty:
        raise StationOfflineError(code, "Sem dados em nenhuma fonte nem em cache.")
    return SeriesResult(station=station, frame=frame, source=source, is_stale=_staleness(frame))


def _mirror_result(
    station: Station,
    start: datetime | None = None,
    cache: ParquetCache | None = None,
) -> SeriesResult:
    """Regua derivada: nivel da estacao-base + offset de datum.

    Usada quando a regua existe oficialmente mas nao transmite (ex.: Eldorado
    do Sul 87450030/DCRS). Vazao e chuva nao sao espelhadas.
    """
    base = refresh_station(station.mirror_of, start=start, cache=cache)
    frame = base.frame.copy()
    frame["nivel_m"] = frame["nivel_m"] + station.datum_offset_m
    frame["vazao_m3s"] = float("nan")
    frame["chuva_mm"] = float("nan")
    return SeriesResult(
        station=station,
        frame=frame,
        source=f"espelho:{base.station.code}",
        is_stale=base.is_stale,
    )


def refresh_all(
    codes: list[str] | None = None,
    cache: ParquetCache | None = None,
) -> dict[str, SeriesResult]:
    """Atualiza varias estacoes; estacao morta vira ausencia, nao excecao."""
    registry = get_registry()
    wanted = codes or list(registry)
    results: dict[str, SeriesResult] = {}
    for code in wanted:
        try:
            results[code] = refresh_station(code, cache=cache)
        except StationOfflineError as exc:
            logger.error("Estacao %s offline: %s", code, exc)
    return results


def backfill_station(
    code: str,
    start: datetime,
    end: datetime | None = None,
    cache: ParquetCache | None = None,
) -> pd.DataFrame:
    """Baixa historico longo em janelas de ANA_CHUNK_DAYS e grava no cache."""
    store = cache or ParquetCache()
    final = end or _now()
    for chunk_start, chunk_end in date_chunks(start, final):
        xml_text = fetch_ana_xml(code, chunk_start, chunk_end)
        parsed = parse_ana_xml(xml_text)
        store.upsert(code, parsed)
        logger.info("backfill %s: %s a %s -> %d linhas", code, chunk_start, chunk_end, len(parsed))
    return store.read(code)
