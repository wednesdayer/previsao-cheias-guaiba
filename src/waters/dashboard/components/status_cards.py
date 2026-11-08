"""Cards de situacao por estacao: nivel atual, tendencia 24h e status de cheia."""

from __future__ import annotations

import streamlit as st

ROLE_ORDER = {"target": 0, "inflow": 1, "upstream": 2}


def _status(nivel: float | None, cota: float) -> tuple[str, str]:
    if nivel is None:
        return "⚫", "sem dado"
    if nivel >= cota:
        return "🔴", "ALAGADO"
    if nivel >= 0.85 * cota:
        return "🟠", "alerta"
    return "🟢", "normal"


def render(levels_now: dict[str, dict]) -> None:
    st.subheader("Estações da bacia")
    entries = sorted(
        levels_now.values(),
        key=lambda e: (ROLE_ORDER.get(e["role"], 9), -(e["nivel_m"] or 0) / e["cota_m"]),
    )
    columns = st.columns(4)
    for i, entry in enumerate(entries):
        icon, label = _status(entry["nivel_m"], entry["cota_m"])
        delta = None
        if entry["nivel_m"] is not None and entry["nivel_24h_m"] is not None:
            delta = f"{entry['nivel_m'] - entry['nivel_24h_m']:+.2f} m / 24h"
        value = f"{entry['nivel_m']:.2f} m" if entry["nivel_m"] is not None else "—"
        with columns[i % 4]:
            st.metric(
                label=f"{icon} {entry['name']} ({entry['river']})",
                value=value,
                delta=delta,
                help=(
                    f"Status: {label} | cota de inundação {entry['cota_m']:.2f} m | "
                    f"fonte: {entry['source']}"
                    + (" | DADO DEFASADO" if entry["stale"] else "")
                ),
            )
