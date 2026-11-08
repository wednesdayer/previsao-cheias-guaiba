"""Baixa o historico de todas as estacoes do registro para o cache local.

Uso:
    python scripts/backfill.py                 # desde 2024-04-01
    python scripts/backfill.py --start 2023-10-01
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime

from waters.config import settings
from waters.config.registry import get_registry
from waters.domain.errors import IngestError
from waters.ingest.service import backfill_station

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("backfill")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill do historico ANA")
    parser.add_argument("--start", default="2024-04-01", help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("--codes", nargs="*", help="Codigos especificos (default: todos)")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d").replace(tzinfo=settings.TZ)
    registry = get_registry()
    codes = args.codes or list(registry)

    for code in codes:
        station = registry.get(code)
        label = station.name if station else code
        if station is not None and station.mirror_of is not None and not station.own_telemetry:
            logger.info("%s (%s): regua derivada, sem transmissao — pulando", label, code)
            continue
        try:
            frame = backfill_station(code, start)
            logger.info(
                "%s (%s): %d leituras, %s -> %s",
                label, code, len(frame),
                frame.index[0] if not frame.empty else "-",
                frame.index[-1] if not frame.empty else "-",
            )
        except IngestError as exc:
            logger.error("%s (%s): FALHOU — %s", label, code, exc)


if __name__ == "__main__":
    main()
