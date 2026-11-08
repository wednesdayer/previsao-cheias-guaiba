"""Cliente HTTP da API aberta de telemetria da ANA (XML)."""

from __future__ import annotations

import time
from datetime import date, datetime, timedelta

import httpx

from waters.config import settings
from waters.domain.errors import IngestError


def _as_date(value: datetime | date) -> date:
    return value.date() if isinstance(value, datetime) else value


def fetch_ana_xml(
    code: str,
    start: datetime | date,
    end: datetime | date,
    client: httpx.Client | None = None,
) -> str:
    """Busca o XML bruto da estacao no intervalo pedido, com retries.

    A API aceita no maximo janelas moderadas; o service fatia janelas longas.
    """
    params = {
        "codEstacao": code,
        "dataInicio": _as_date(start).strftime("%d/%m/%Y"),
        "dataFim": _as_date(end).strftime("%d/%m/%Y"),
    }
    owns_client = client is None
    http = client or httpx.Client(timeout=settings.ANA_TIMEOUT_S)
    last_error: Exception | None = None
    try:
        for attempt in range(settings.ANA_MAX_RETRIES):
            try:
                response = http.get(settings.ANA_BASE_URL, params=params)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt < settings.ANA_MAX_RETRIES - 1:
                    time.sleep(2.0 * (attempt + 1))
        raise IngestError(
            f"ANA indisponivel para estacao {code} "
            f"({params['dataInicio']}–{params['dataFim']}): {last_error}"
        ) from last_error
    finally:
        if owns_client:
            http.close()


def date_chunks(
    start: datetime | date, end: datetime | date, chunk_days: int = settings.ANA_CHUNK_DAYS
) -> list[tuple[date, date]]:
    """Divide [start, end] em janelas de ate chunk_days para o backfill."""
    first, last = _as_date(start), _as_date(end)
    if first > last:
        raise ValueError(f"Intervalo invalido: {first} > {last}")
    chunks = []
    cursor = first
    while cursor <= last:
        chunk_end = min(cursor + timedelta(days=chunk_days - 1), last)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end + timedelta(days=1)
    return chunks
