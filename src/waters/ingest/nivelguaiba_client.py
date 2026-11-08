"""Fallback: JSON por cidade do nivelguaiba.com.br (somente nivel)."""

from __future__ import annotations

import logging
from typing import Literal

import httpx
import pandas as pd

from waters.config import settings
from waters.domain.errors import IngestError
from waters.ingest.ana_parser import COLUMNS, empty_frame

logger = logging.getLogger(__name__)

Window = Literal["24h", "7days", "30days", "90days"]

_SUFFIX: dict[Window, str] = {
    "24h": ".json",
    "7days": ".7days.json",
    "30days": ".30days.json",
    "90days": ".90days.json",
}


def fetch_nivelguaiba(slug: str, window: Window = "7days") -> pd.DataFrame:
    """Busca a serie de nivel do site e devolve o frame padrao (vazao/chuva NaN)."""
    url = f"{settings.NIVELGUAIBA_BASE_URL}/{slug}{_SUFFIX[window]}"
    try:
        response = httpx.get(url, timeout=settings.NIVELGUAIBA_TIMEOUT_S, follow_redirects=True)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise IngestError(f"nivelguaiba indisponivel para {slug} ({url}): {exc}") from exc

    return _parse_payload(payload, slug)


def _parse_payload(payload: object, slug: str) -> pd.DataFrame:
    """Aceita formatos {readings|data|series|items: [...]} ou lista direta."""
    items: list = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("readings", "data", "series", "items", "levels"):
            if isinstance(payload.get(key), list):
                items = payload[key]
                break

    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        raw_ts = item.get("timestamp") or item.get("datetime") or item.get("date") or item.get("t")
        raw_level = item.get("level") if "level" in item else item.get("nivel", item.get("v"))
        if raw_ts is None or raw_level is None:
            continue
        try:
            timestamp = pd.Timestamp(raw_ts)
            timestamp = (
                timestamp.tz_localize(settings.TZ)
                if timestamp.tzinfo is None
                else timestamp.tz_convert(settings.TZ)
            )
            level = float(str(raw_level).replace(",", "."))
        except (ValueError, TypeError):
            continue
        rows.append({"timestamp": timestamp, "nivel_m": level})

    if not rows:
        logger.warning("nivelguaiba: payload de %s sem leituras reconheciveis", slug)
        return empty_frame()

    frame = pd.DataFrame(rows).set_index("timestamp").sort_index()
    frame = frame[~frame.index.duplicated(keep="last")]
    frame["vazao_m3s"] = float("nan")
    frame["chuva_mm"] = float("nan")
    return frame[COLUMNS].astype(float)
