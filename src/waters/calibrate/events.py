"""Eventos de cheia para calibracao: janelas conhecidas + deteccao automatica."""

from __future__ import annotations

import pandas as pd

# Janelas fechadas conhecidas (nome -> inicio/fim, horario local).
# Mai/2024: maior cheia da historia do Guaiba (5,37 m na regua Cais Maua em 05/05/2024;
# 4,17 m na telemetria do Gasometro, datum diferente).
KNOWN_EVENTS: dict[str, tuple[str, str]] = {
    "mai-2024": ("2024-04-26", "2024-06-08"),
}

DETECT_LEVEL_M = 1.8       # POA acima disso caracteriza evento
MIN_EVENT_HOURS = 48
MERGE_GAP_HOURS = 72


def detect_events(poa_level: pd.Series) -> dict[str, tuple[str, str]]:
    """Encontra janelas de agua alta no historico de POA e as nomeia por mes."""
    valid = poa_level.dropna()
    if valid.empty:
        return {}
    high = valid[valid >= DETECT_LEVEL_M]
    if high.empty:
        return {}

    events: dict[str, tuple[str, str]] = {}
    block_start = prev = high.index[0]
    blocks: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    for ts in high.index[1:]:
        if (ts - prev) > pd.Timedelta(hours=MERGE_GAP_HOURS):
            blocks.append((block_start, prev))
            block_start = ts
        prev = ts
    blocks.append((block_start, prev))

    for start, end in blocks:
        if (end - start) < pd.Timedelta(hours=MIN_EVENT_HOURS):
            continue
        # Expande margens para pegar subida e recessao completas
        window = (
            (start - pd.Timedelta(days=7)).strftime("%Y-%m-%d"),
            (end + pd.Timedelta(days=10)).strftime("%Y-%m-%d"),
        )
        events[start.strftime("%b-%Y").lower()] = window
    return events


def _overlaps(a: tuple[str, str], b: tuple[str, str]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def all_events(poa_level: pd.Series) -> dict[str, tuple[str, str]]:
    """Conhecidos + detectados; janela detectada que sobrepoe conhecida e descartada."""
    merged = dict(KNOWN_EVENTS)
    for name, window in detect_events(poa_level).items():
        if not any(_overlaps(window, known) for known in KNOWN_EVENTS.values()):
            merged[name] = window
    return merged
