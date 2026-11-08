"""Cache parquet: upsert, dedupe, leitura com timezone."""

import numpy as np
import pandas as pd

from waters.config import settings
from waters.ingest.cache import ParquetCache


def _frame(start: str, hours: int, level: float) -> pd.DataFrame:
    index = pd.date_range(start, periods=hours, freq="1h", tz=settings.TZ, name="timestamp")
    return pd.DataFrame(
        {"nivel_m": level, "vazao_m3s": np.nan, "chuva_mm": 0.0}, index=index
    )


def test_read_missing_station_returns_empty(tmp_path):
    cache = ParquetCache(tmp_path)
    assert cache.read("99999999").empty
    assert cache.last_timestamp("99999999") is None


def test_upsert_merges_and_newer_wins(tmp_path):
    cache = ParquetCache(tmp_path)
    cache.upsert("87450020", _frame("2026-07-01", 24, 1.0))
    # sobreposicao de 6 h com valores revisados
    merged = cache.upsert("87450020", _frame("2026-07-01 18:00", 24, 2.0))
    assert len(merged) == 42  # 24 + 24 - 6 duplicadas
    assert merged.loc["2026-07-01 20:00", "nivel_m"] == 2.0  # revisado venceu
    assert merged.loc["2026-07-01 10:00", "nivel_m"] == 1.0


def test_last_timestamp_tracks_newest(tmp_path):
    cache = ParquetCache(tmp_path)
    cache.upsert("87450020", _frame("2026-07-01", 24, 1.0))
    last = cache.last_timestamp("87450020")
    assert last == pd.Timestamp("2026-07-01 23:00", tz=settings.TZ)
