"""Parser do XML da telemetria ANA -> DataFrame normalizado.

Contrato de saida (todas as fontes convergem para este formato):
    index: DatetimeIndex tz-aware (America/Sao_Paulo), ordenado, sem duplicatas
    colunas: nivel_m (float), vazao_m3s (float), chuva_mm (float)
Campos vazios viram NaN; linha invalida e descartada, nunca fatal.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

import pandas as pd

from waters.config import settings
from waters.domain.errors import IngestError

logger = logging.getLogger(__name__)

COLUMNS = ["nivel_m", "vazao_m3s", "chuva_mm"]


def _text(element: ET.Element, tag: str) -> str:
    child = element.find(tag)
    return (child.text or "").strip() if child is not None else ""


def _to_float(raw: str) -> float | None:
    if not raw:
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def empty_frame() -> pd.DataFrame:
    """Frame vazio no contrato padrao."""
    index = pd.DatetimeIndex([], tz=settings.TZ, name="timestamp")
    return pd.DataFrame(columns=COLUMNS, index=index, dtype=float)


def parse_ana_xml(xml_text: str) -> pd.DataFrame:
    """Converte o XML DataSet da ANA no frame padrao. Nivel chega em cm."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise IngestError(f"XML da ANA ilegivel: {exc}") from exc

    rows = []
    skipped = 0
    for element in root.iter():
        if not element.tag.endswith("DadosHidrometereologicos"):
            continue
        raw_ts = _text(element, "DataHora")
        try:
            timestamp = pd.Timestamp(raw_ts).tz_localize(settings.TZ)
        except (ValueError, TypeError):
            skipped += 1
            continue
        nivel_cm = _to_float(_text(element, "Nivel"))
        rows.append(
            {
                "timestamp": timestamp,
                "nivel_m": nivel_cm / 100.0 if nivel_cm is not None else None,
                "vazao_m3s": _to_float(_text(element, "Vazao")),
                "chuva_mm": _to_float(_text(element, "Chuva")),
            }
        )

    if skipped:
        logger.warning("parse_ana_xml: %d linha(s) descartada(s) por timestamp invalido", skipped)
    if not rows:
        return empty_frame()

    frame = pd.DataFrame(rows).set_index("timestamp").sort_index()
    frame = frame[~frame.index.duplicated(keep="last")]
    return frame[COLUMNS].astype(float)
