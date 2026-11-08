"""Mapa interativo de inundacao: slider (client-side) da cota -> mancha vermelha.

Modelo bathtub com conectividade sobre o DEM GLO-30 (pre-computado em
data/inundation/region.npz). Ilustrativo, nao e previsao oficial.

A troca de nivel usa um slider NATIVO do Plotly com frames: acontece toda no
navegador, sem rerun do Streamlit. Assim o zoom/pan que o usuario deu no mapa
NAO reseta ao mudar o nivel. Basemap OpenStreetMap (sem token).
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from waters.config import settings
from waters.dashboard import data_access

PRESET_LABELS = {
    "regiao": "Região (POA + Eldorado)",
    "poa": "Porto Alegre",
    "eldorado": "Eldorado do Sul",
}
PRESET_ZOOM = {"regiao": 8.7, "poa": 11.0, "eldorado": 11.0}
LANDMARKS = {"Gasômetro (POA)": (-30.034, -51.233), "Eldorado do Sul": (-30.084, -51.618)}


def _image_layer(uri: str, bounds: list[float]) -> dict:
    w, s, e, n = bounds
    return {
        "sourcetype": "image",
        "source": uri,
        "coordinates": [[w, n], [e, n], [e, s], [w, s]],
        "opacity": 0.75,
        "below": "traces",
    }


def _title(level: float, area_km2: float) -> str:
    status = "acima da cota" if level >= settings.COTA_INUNDACAO_POA_M else "abaixo da cota"
    return (f"Cota {level:.2f} m ({status}, inundação {settings.COTA_INUNDACAO_POA_M:.2f} m)"
            f"  ·  terra alagada ≈ {area_km2:.0f} km²")


def _nearest_index(frames: list[dict], level: float | None) -> int:
    if level is None:
        return 0
    return min(range(len(frames)), key=lambda i: abs(frames[i]["level"] - level))


def render(inund, current_level_m: float | None, forecast_peak_m: float | None) -> None:
    st.subheader("🗺️ Mapa de inundação — até onde a água chega")
    st.caption(
        "Arraste o nível da régua **no controle abaixo do mapa** e veja em vermelho "
        "o território de terra que a água invade (tom mais forte = lâmina mais funda). "
        "O zoom/posição do mapa não reseta ao mudar o nível."
    )

    preset = st.selectbox(
        "Zoom", options=list(PRESET_LABELS), format_func=lambda k: PRESET_LABELS[k]
    )
    refs = []
    if current_level_m is not None:
        refs.append(f"nível atual **{current_level_m:.2f} m**")
    if forecast_peak_m is not None:
        refs.append(f"pico previsto **{forecast_peak_m:.2f} m**")
    if refs:
        st.caption("Referências: " + " · ".join(refs) + " (marcados no slider).")

    frames_data, bounds = data_access.inundation_frames()
    start = _nearest_index(frames_data, current_level_m)
    peak_idx = _nearest_index(frames_data, forecast_peak_m) if forecast_peak_m else None
    preset_bbox = inund.presets[preset]
    center = {"lat": (preset_bbox[1] + preset_bbox[3]) / 2,
              "lon": (preset_bbox[0] + preset_bbox[2]) / 2}

    frames = [
        go.Frame(
            name=f"{f['level']:.2f}",
            layout=go.Layout(
                mapbox={"layers": [_image_layer(f["uri"], bounds)]},
                title={"text": _title(f["level"], f["area_km2"]), "x": 0.01,
                       "font": {"size": 13}},
            ),
        )
        for f in frames_data
    ]

    def _step_label(i: int, f: dict) -> str:
        tag = ""
        if i == start:
            tag = " ▲atual"
        elif peak_idx is not None and i == peak_idx:
            tag = " ◆pico"
        # rotulo apenas em cotas inteiras (+ marcas) para nao poluir
        base = f"{f['level']:.1f}" if abs(f["level"] - round(f["level"])) < 1e-6 else ""
        return (base + tag).strip()

    slider = {
        "active": start,
        "y": 0, "x": 0, "len": 1.0, "pad": {"t": 40, "b": 10},
        "currentvalue": {"prefix": "Nível da régua: ", "suffix": " m",
                         "font": {"size": 15}},
        "steps": [
            {"method": "animate", "label": _step_label(i, f),
             "args": [[f"{f['level']:.2f}"],
                      {"mode": "immediate", "frame": {"duration": 0, "redraw": True},
                       "transition": {"duration": 0}}]}
            for i, f in enumerate(frames_data)
        ],
    }

    fig = go.Figure(
        data=[go.Scattermapbox(
            lat=[c[0] for c in LANDMARKS.values()],
            lon=[c[1] for c in LANDMARKS.values()],
            mode="markers+text", marker={"size": 9, "color": "#111"},
            text=list(LANDMARKS), textposition="top right",
            textfont={"size": 12, "color": "#111"}, hoverinfo="text",
        )],
        frames=frames,
    )
    fig.update_layout(
        mapbox={
            "style": "open-street-map", "center": center, "zoom": PRESET_ZOOM[preset],
            "uirevision": preset,           # camera preservada enquanto o preset nao muda
            "layers": [_image_layer(frames_data[start]["uri"], bounds)],
        },
        title={"text": _title(frames_data[start]["level"], frames_data[start]["area_km2"]),
               "x": 0.01, "font": {"size": 13}},
        sliders=[slider],
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
        height=600, showlegend=False,
    )
    st.plotly_chart(fig, width="stretch", key="flood_map_chart")

    with st.expander("⚠️ Como ler este mapa (limitações)"):
        st.markdown(
            "- **Modelo \"bathtub\"**: assume uma superfície d'água plana e instantânea "
            "na cota da régua. Ignora a declividade do rio (Eldorado/Jacuí fica mais alto "
            "que POA nas cheias), vento e a dinâmica do escoamento. É um mapa **ilustrativo "
            "de inundação potencial**, não uma previsão oficial.\n"
            "- **Topografia**: DEM Copernicus GLO-30 (~2011–2015), modelo de *superfície* — "
            "prédios e vegetação bloqueiam a água e fazem **subestimar** a inundação urbana. "
            "Resolução de 30 m perde canais e bueiros.\n"
            "- **Datum aproximado** (linha d'água normal ≈ 0,9 m na régua). "
            "**Não use para decisão de risco** — siga a Defesa Civil.\n"
            f"- Fonte: {inund.source}.\n"
            "- Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus "
            "Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European "
            "Union and ESA; all rights reserved. Mapa base © OpenStreetMap contributors."
        )
