"""Resume as reproducoes de scripts/replay_event.py (datum do Gasometro).

Duas tabelas:
  1. por evento e versao: erro do pico central contra o maximo observado nas
     72 h seguintes ao corte, separando cortes com subida pela frente;
  2. por pico observado: o pico previsto pelo v1 em cortes 72/48/24/12 h antes.

Uso:
  python scripts/summarize_replays.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from waters.calibrate.run import load_calibration_series
from waters.config import settings

RESULTS = Path("docs/resultados")
VERSIONS = ("v1", "v2", "v3", "v4")
RISE_AHEAD_M = 0.10  # corte "com subida pela frente": maximo a frente > nivel + 10 cm
LEADS_H = (72, 48, 24, 12)

# janelas que isolam cada pico local no nivel horario do Gasometro
EVENTS = {
    "2024-05": [("2024-05-10", "2024-05-19"), ("2024-05-23", "2024-05-27"),
                ("2024-06-01", "2024-06-05")],
    "2026-07": [("2026-07-22", "2026-07-27"), ("2026-07-28", "2026-08-03")],
    "2026-09": [("2026-09-20", "2026-09-27"), ("2026-09-28", "2026-10-06"),
                ("2026-10-07", "2026-10-14")],
}


def _load(event: str) -> pd.DataFrame:
    table = pd.read_csv(RESULTS / f"reproducao_{event}_gasometro.csv")
    table["cut"] = pd.to_datetime(table["cut"]).dt.tz_localize(settings.TZ)
    return table.dropna(subset=["obs_max_horizon_m"])


def _version_rows(event: str, table: pd.DataFrame) -> list[dict]:
    rising = table["obs_max_horizon_m"] > table["observed_m"] + RISE_AHEAD_M
    rows = []
    for v in VERSIONS:
        err = table[f"{v}_peak_m"] - table["obs_max_horizon_m"]
        inside = table["obs_max_horizon_m"].between(table[f"{v}_low_m"], table[f"{v}_high_m"])
        rows.append({
            "evento": event, "versao": v, "cortes": len(table),
            "EAM": round(err.abs().mean(), 2), "vies": round(err.mean(), 2),
            "EAM_subida": round(err[rising].abs().mean(), 2),
            "vies_subida": round(err[rising].mean(), 2),
            "pior_erro": round(err.max(), 2),
            "vies_sem_subida": round(err[~rising].mean(), 2),
            "faixa_contem": f"{inside.mean():.0%}",
            "pico_no_fim": f"{table[f'{v}_at_horizon'].astype(bool).mean():.0%}",
        })
    return rows


def _peak_rows(event: str, table: pd.DataFrame, poa: pd.Series) -> list[dict]:
    rows = []
    for start, end in EVENTS[event]:
        window = poa.loc[start:end].dropna()
        peak_time, peak = window.idxmax(), float(window.max())
        row = {"evento": event, "pico": peak_time.strftime("%d/%m/%Y %Hh"), "observado": round(peak, 2)}
        for lead in LEADS_H:
            before = table[table["cut"] <= peak_time - pd.Timedelta(hours=lead)]
            row[f"v1_-{lead}h"] = round(float(before["v1_peak_m"].iloc[-1]), 2) if len(before) else None
        rows.append(row)
    return rows


def main() -> None:
    logging.basicConfig(level=logging.ERROR)
    _, poa, _ = load_calibration_series()
    by_version, by_peak = [], []
    for event in EVENTS:
        table = _load(event)
        by_version += _version_rows(event, table)
        by_peak += _peak_rows(event, table, poa)
    pd.set_option("display.width", 200)
    print(pd.DataFrame(by_version).to_string(index=False))
    print()
    print(pd.DataFrame(by_peak).to_string(index=False))


if __name__ == "__main__":
    main()
