"""Parser da ANA: contrato de saida, linhas invalidas, unidades."""

import pandas as pd
import pytest

from waters.domain.errors import IngestError
from waters.ingest.ana_parser import COLUMNS, empty_frame, parse_ana_xml


def test_parses_valid_rows_and_converts_cm_to_m(ana_xml):
    frame = parse_ana_xml(ana_xml)
    assert list(frame.columns) == COLUMNS
    assert frame.index.tz is not None
    # linha invalida descartada; timestamp duplicado mantem o mais novo
    assert len(frame) == 2
    assert frame["nivel_m"].iloc[-1] == pytest.approx(1.04)


def test_duplicate_timestamp_keeps_last(ana_xml):
    frame = parse_ana_xml(ana_xml)
    dup = frame.loc[frame.index == pd.Timestamp("2026-07-22 17:00:00", tz=frame.index.tz)]
    assert len(dup) == 1
    assert dup["nivel_m"].iloc[0] == pytest.approx(1.05)  # rowOrder 3 vence a 1


def test_empty_fields_become_nan(ana_xml):
    frame = parse_ana_xml(ana_xml)
    last = frame.iloc[-1]
    assert pd.isna(last["vazao_m3s"])
    assert last["chuva_mm"] == pytest.approx(3.6)


def test_malformed_xml_raises_ingest_error():
    with pytest.raises(IngestError):
        parse_ana_xml("isto nao e xml <<<")


def test_no_rows_returns_empty_contract_frame():
    frame = parse_ana_xml("<?xml version='1.0'?><DataTable></DataTable>")
    assert frame.empty
    assert list(frame.columns) == COLUMNS
    assert list(empty_frame().columns) == COLUMNS
