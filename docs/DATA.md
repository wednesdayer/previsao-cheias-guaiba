# Data sources

Everything the model uses is public and free. Nothing is redistributed in this repository: `data/` is git-ignored, and the scripts below rebuild it from the original sources.

| Dataset | Provider | Used for | How to get it |
|---|---|---|---|
| Hydrometeorological telemetry (stage, discharge, rain, 15 min) | ANA, Agência Nacional de Águas e Saneamento Básico (stations operated in the national hydrometric network with SGB/CPRM and state agencies) | Model inputs and calibration | `python scripts/backfill.py --start 2024-04-01` |
| Stage-only JSON feed | nivelguaiba.com.br (unofficial aggregator) | Fallback only, when ANA is down or late | Fetched automatically by `ingest/service.py` |
| Copernicus DEM GLO-30 (two 1°×1° tiles) | ESA / Copernicus, via AWS Open Data | Stage–area curve and inundation map | `python scripts/build_area_curve.py` (downloads tiles) |
| Basemap | © OpenStreetMap contributors | Dashboard map background | Loaded by Plotly at runtime |

Licensing and citation details for each source are in [`papers/README.md`](../papers/README.md#data-sources).

## 1. ANA telemetry

**Endpoint** (open, no authentication, XML):

```
https://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos
    ?codEstacao=<CODE>&dataInicio=DD/MM/YYYY&dataFim=DD/MM/YYYY
```

Fields used: `Nivel` (stage, cm → converted to m), `Vazao` (discharge, m³/s) and `Chuva` (rain, mm). Readings arrive every 15 min and are often late, so each incremental fetch re-reads a 6 h overlap window (`settings.CACHE_OVERLAP_HOURS`). The backfill requests at most 30 days per call.

**The discharge values are not measured directly.** ANA derives them from each station's stage–discharge rating curve. In extreme floods these curves are extrapolated beyond the measured range, so treat peak discharges as ±10–20 % numbers.

### Stations

Coverage is the share of hours with at least one valid reading, from the first record to 08 Nov 2026.

| Code | Station | River | Role in the model | Stage | Discharge |
|---|---|---|---|---|---|
| 85900000 | Rio Pardo | Jacuí | inflow (v1–v3) | 43 % | 41 % |
| 85642000 | Cachoeira do Sul | Jacuí | upstream / routing source (v4) | 96 % | 96 % |
| 85400000 | Dona Francisca | Jacuí | upstream / routing validation | 99 % | 99 % |
| 86879300 | Lajeado | Taquari | inflow (v1–v3) | 95 % | **7 %** |
| 86510000 | Muçum | Upper Taquari | upstream / routing validation | 99 % | 99 % |
| 86720000 | Encantado | Upper Taquari | upstream / routing source (v4) | 90 % | 94 % |
| 86881000 | Bom Retiro do Sul | Taquari | upstream (stage only) | 85 % | — |
| 87170000 | São Sebastião do Caí | Caí | inflow | 92 % | 92 % |
| 87165001 | Feliz | Caí | upstream (stage only) | 83 % | — |
| 87382000 | São Leopoldo | Sinos | inflow | 100 % | 100 % |
| 87376000 | Taquara | Sinos / Paranhana | upstream (stage only) | 63 % | — |
| 87399000 | Gravataí (Passo das Canoas) | Gravataí | inflow | 100 % | 100 % |
| 87450020 | Porto Alegre, Usina do Gasômetro | Guaíba | **target** (calibration base) | 96 % | — |
| 87450004 | Porto Alegre, Cais Mauá (C6) | Guaíba | derived target (+0.44 m datum offset) | 47 % | — |
| 87450030 | Eldorado do Sul (BR-290) | Guaíba | derived target (no public telemetry) | — | — |

Station metadata (coordinates, drainage areas, flood stages) is in [`config/stations.yaml`](../config/stations.yaml). Coordinates come from ANA's HidroInventário.

### Data quirks that shape the model

- **There is no discharge gauge on the Guaíba.** Porto Alegre only reports stage, so the outflow to the Lagoa dos Patos has to be inferred. That is the core of the method (see [METHODOLOGY.md](METHODOLOGY.md#3-outflow-without-a-discharge-gauge)).
- **The Gasômetro gauge starts on 03 May 2024.** It was installed as an emergency gauge during the May 2024 flood, after the historical Cais Mauá gauge failed near the peak. The calibration record therefore begins mid-event.
- **Gauge datums differ.** The official record of the 2024 flood (5.37 m on 05 May 2024 [Medeiros 2025]) refers to the historical Cais Mauá (C6) gauge. The Gasômetro telemetry series used here peaks at 4.17 m (05 May 2024, 05:30 local time). The two gauges are not on the same datum; their relation at the peak is analysed in [Germano 2024]. The +0.44 m offset measured at normal stages does not reconcile the two peaks. All model levels are in the Gasômetro telemetry datum.
- **Rio Pardo, the Jacuí inflow gauge, goes silent often.** It has 41 % discharge coverage and went 41 h without reporting during the July 2026 flood. The Jacuí drains about 85 % of the basin, so a silent Rio Pardo makes the model underestimate inflow. v4 routes Cachoeira do Sul instead to work around this.
- **Lajeado reports stage continuously but discharge only rarely** (7 % of hours). The Taquari is the second-largest tributary, and this gap is one of the main sources of inflow error in v1–v3.
- **QC.** `model/preprocess.py` drops stage jumps above 2 m/h (spikes) and identical values held for 12 h or more (stuck sensors). It interpolates gaps of up to 6 h (12 h for stations flagged `sparse`) and leaves longer gaps empty.

## 2. Copernicus DEM GLO-30

Two tiles cover the Guaíba and the Jacuí delta: `Copernicus_DSM_COG_10_S30_00_W052_00_DEM` and `Copernicus_DSM_COG_10_S31_00_W052_00_DEM`. They are downloaded from the public bucket `https://copernicus-dem-30m.s3.amazonaws.com` (no credentials needed).

- **Resolution:** 1 arc-second, about 30 m.
- **It is a surface model (DSM), not a terrain model.** Buildings and tree canopy count as ground. Urban flooding is therefore underestimated, and the inundation map should be read as illustrative (see [METHODOLOGY.md §6](METHODOLOGY.md#6-inundation-map)).
- **Vertical datum:** EGM2008. The model does not convert it to the gauge datum. Instead it anchors the DEM to the gauge by matching the known normal-stage water area of the Guaíba (470 km² at about 0.9 m on the Gasômetro gauge).

Derived products, regenerated locally and not committed:

| File | Script | Content |
|---|---|---|
| `config/stage_area.yaml` | `scripts/build_area_curve.py` | A(h) curve, 470 → 961 km² between 0 and 6 m (committed, small) |
| `data/inundation/region.npz` | `scripts/build_inundation.py` | Clipped DEM + "arrival stage" raster for the map (13 MB, not committed) |

## 3. Reproducing the data folder

```bash
pip install -e ".[dev,geo]"
python scripts/backfill.py --start 2024-04-01   # ~10 MB of parquet, a few minutes
python scripts/build_area_curve.py              # downloads ~85 MB of DEM tiles
python scripts/build_inundation.py
```

The calibrated parameters in `config/params/` are committed, so the dashboard runs with only the backfill. The DEM step is needed only for the map and for the v2–v4 models.
