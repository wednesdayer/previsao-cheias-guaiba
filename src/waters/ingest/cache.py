"""Cache local em parquet, um arquivo por estacao, com upsert incremental."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from waters.config import settings
from waters.ingest.ana_parser import COLUMNS, empty_frame


class ParquetCache:
    """Persistencia simples: data/cache/{code}.parquet no contrato padrao."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or settings.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, code: str) -> Path:
        return self.cache_dir / f"{code}.parquet"

    def read(self, code: str) -> pd.DataFrame:
        path = self._path(code)
        if not path.exists():
            return empty_frame()
        frame = pd.read_parquet(path)
        if frame.index.tz is None:
            frame.index = frame.index.tz_localize(settings.TZ)
        else:
            frame.index = frame.index.tz_convert(settings.TZ)
        return frame[COLUMNS]

    def upsert(self, code: str, new_data: pd.DataFrame) -> pd.DataFrame:
        """Mescla dados novos com os existentes; o mais novo vence no empate."""
        if new_data.empty:
            return self.read(code)
        existing = self.read(code)
        merged = pd.concat([existing, new_data[COLUMNS]])
        merged = merged.sort_index()
        merged = merged[~merged.index.duplicated(keep="last")]
        merged.to_parquet(self._path(code))
        return merged

    def last_timestamp(self, code: str) -> pd.Timestamp | None:
        frame = self.read(code)
        return None if frame.empty else frame.index[-1]
