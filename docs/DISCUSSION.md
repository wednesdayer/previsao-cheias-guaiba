# Discussion

This document covers four things: where the model failed, what the IPH/UFRGS team reported about its own forecasts of the same floods, and which gaps affect both. The last section lists what would actually reduce the error.

Reference keys point to [papers/README.md](../papers/README.md). Levels are in metres. When a level is compared with public forecasts, the gauge is named, because the two Porto Alegre gauges are on different datums (see [§4.4](#44-two-gauges-two-datums)).

**Contents**

1. [July 2026: a real-time test](#1-july-2026-a-real-time-test)
2. [Problems we found in this model](#2-problems-we-found-in-this-model)
3. [Problems reported by IPH/UFRGS](#3-problems-reported-by-iphufrgs)
4. [Gaps shared by every model of the Guaíba](#4-gaps-shared-by-every-model-of-the-guaíba)
5. [Where this model follows the IPH approach](#5-where-this-model-follows-the-iph-approach)
6. [What would reduce the error](#6-what-would-reduce-the-error)
7. [Documents consulted](#7-documents-consulted)

---

## 1. July 2026: a real-time test

The model was built on 22 July 2026, during a flood of the Taquari, and was used live over the following days. Tributary discharge at Lajeado peaked at about 11,100 m³/s in the early hours of 23 July. The Guaíba rose in two waves.

| Wave | Observed peak, Cais Mauá (C6) | Observed peak, Gasômetro |
|---|---|---|
| 1st | **2.15 m**, 24/07 15h | 1.53 m, 24/07 20h |
| 2nd | **2.59 m**, 31/07 20h | 1.89 m, 31/07 21h |

The table below replays every model version as if it were live. For each cut, only the data available at that moment is used (`scripts/replay_event.py`; output in [`results/replay_2026-07_cais-maua.csv`](results/replay_2026-07_cais-maua.csv)). Values are the central-scenario peak converted to the Cais Mauá gauge (+0.44 m) so they can be compared with the public forecasts, which use that gauge.

| Cut | v1 | v2 | v3 | v4 | Public forecasts around the same time |
|---|---|---|---|---|---|
| 21/07 12h | 1.54 | 1.51 | 1.52 | 1.49 | MetSul: "near or above 2 m" |
| 22/07 00h | 2.96 | 2.84 | 2.98 | 4.78 | |
| 22/07 12h | 4.97 | 4.52 | 4.80 | 6.61 | |
| 22/07 20h | 4.77 | 4.37 | 4.61 | 4.75 | SGB + IPH + Catavento (22/07 19h50): Cais Mauá "pode atingir 2,50 m"; IPH: "2,50 a 2,60 m prováveis" |
| 23/07 10h | 3.97 | 3.53 | 3.67 | 3.82 | SGB/IPH: alert level 2.5 m, 3 m "não há previsão de que seja alcançada". Dmae, citing scenarios available when its request was drafted: Guaíba "poderia ultrapassar a cota dos 3 metros" |
| 23/07 16h | 3.70 | 3.31 | 3.40 | 3.38 | IPH via press: up to 2.70 m at Cais Mauá on Saturday 25/07 |
| 24/07 00h | 2.87 | 2.48 | 2.50 | 2.38 | |
| 24/07 08h | 2.35 | 2.16 | 2.15 | 2.03 | MetSul: 2.3–2.5 m in 48 h |
| 24/07 12h | 2.13 | 2.04 | 2.02 | 2.01 | Dmae closes six floodgates at noon on a 2.50–2.70 m forecast |
| 28/07 12h | 2.44 | 2.15 | 2.21 | 2.51 | |
| 29/07 10h | 4.92 | 4.46 | 4.74 | 4.97 | SGB/IPH bulletin (29/07): could exceed 3 m by 01/08; most adverse scenario about 3.50 m |
| 30/07 08h | 3.93 | 3.47 | 3.57 | 3.98 | MetSul: up to 2.5 m |
| 30/07 12h | 3.77 | 3.32 | 3.39 | 3.70 | SGB/IPH (revised): between 2.60 and 3.00 m |
| 31/07 00h | 3.04 | 2.81 | 2.81 | 3.14 | |
| 31/07 10h | 2.58 | 2.56 | 2.54 | 2.89 | IPH (Meirelles): should stay below 3 m |

Sources for the public forecasts are listed in [papers/README.md](../papers/README.md#news-and-bulletins-july-2026).

What the replay shows:

- **Every version overestimated both waves while the tributaries were still rising**, by 2.3–2.8 m (v4 by up to 4.5 m) about 2.5 days ahead. They converged within 0–0.15 m only once the upstream crest had passed (24/07 08h and 31/07 10h), a few hours before the peak.
- **The official forecasts overestimated too, but much less.** For the 1st wave they said 2.50–2.70 m, after scenarios above 3 m that were dropped. The real peak was 2.15 m, so the error was +0.35 to +0.55 m. For the 2nd wave they went from "may exceed 3 m, worst case ~3.50 m" to 2.60–3.00 m, and the peak was 2.59 m.
- **At the moments of greatest uncertainty, our forecasts sat in the same range as the official high scenarios.** On 23/07 our versions gave 3.3–4.0 m against the >3 m scenarios the Dmae cited. On 29–30/07 they gave 3.3–4.0 m against the "exceeds 3 m / ~3.50 m" bulletin. Once the public forecast settled, ours stayed far above it until the crest passed.
- **v2 was the least bad on the rise in July 2026.** It was not the best on the May 2024 hindcast, where v1 won. No version is consistently better, which is a sign of over-fitting to the few calibration events (§2.6).
- **Many of these peaks are truncated at the end of the 72 h horizon.** In most cells of the table the model was still rising when it stopped integrating, so the true model peak would be higher. The dashboard does not flag this yet (§2.5).

## 2. Problems we found in this model

### 2.1 Crest extrapolation runs away on the rise

The forecast has to guess how high each tributary will go before propagating it ([METHODOLOGY §4.1](METHODOLOGY.md#41-crest-extrapolation-project-heuristic)). At midday on 22/07, Lajeado was still rising at about 400 m³/s per hour (700 m³/s per hour a few hours earlier). Fed with that rate, the exponential-decay assumption projected a crest far above the 11,078 m³/s actually reached at 01h on 23/07. This explains most of the early error and all of the volatility. There is no physical limit on the extrapolated crest: no rainfall information and no upstream routing caps it.

### 2.2 Structural overestimation of medium floods

Even after the Taquari crest had passed (cut 24/07 00h), v1 still predicted 2.87 m at Cais Mauá against 2.15 m observed. The hindcasts of June 2024 and June 2025 show the same +0.5 m bias. Two causes contribute. The main one is the outflow bias in §2.4. The other is that the model sends the full Taquari wave into a single 470 km² storage, shifted in time but not attenuated. In reality much of it spreads over the Jacuí delta and its floodplains first. Laipelt et al. [2026] show that the Jacuí floodplains govern the duration of Guaíba floods. A lumped level-pool model calibrated on the extreme May 2024 event has no such buffer for smaller events.

### 2.3 The level-pool assumption

The model treats the Guaíba as a reservoir with a flat surface. The IPH team describes the May 2024 flood as "predominantly fluvial", with the wave propagating as a riverine flow of high velocity [Medeiros 2025]. The ADCP campaign of 05/05/2024 at the Usina do Gasômetro measured a maximum current of 4.2 m/s [Toldo 2024]. In June 2025, the level at Cais Navegantes was about 30 cm higher than at Cais Mauá, a few kilometres downstream [IPH 2025]. A storage model cannot represent this water-surface slope between the delta and Porto Alegre. That slope is also why the inundation map misses by about 1.5 m of stage in Eldorado do Sul ([METHODOLOGY §6.3](METHODOLOGY.md#63-caveats)).

### 2.4 The outflow curve gives about half the measured outflow

The rating Qout(h) is fitted to close the water balance, so it absorbs every error in inflow, storage and wind. Its exponent sits at the upper bound (b = 4.0) and the fit RMSE is about 2,000 m³/s.

There are three ADCP discharge measurements on the Guaíba, made by the PGA POA/UFRGS team [Toldo 2024; IPH 2025]. They are independent of everything the model was fitted on. Each version's curve, evaluated at the Gasômetro telemetry level at the time of each measurement, gives:

| Measurement | Measured (ADCP) | Gasômetro level | v1 | v2 | v3 | v4 |
|---|---|---|---|---|---|---|
| 05/05/2024 17h45 (Gasômetro section, corrected for overflow) | 35,736 m³/s | 4.10 m | 16,432 (46 %) | 17,178 (48 %) | 16,635 (47 %) | 6,249 (17 %) |
| 15/05/2024 09h50 (Ponta do Dionísio) | 22,070 m³/s | 4.02 m | 15,879 (72 %) | 16,599 (75 %) | 16,077 (73 %) | 6,145 (28 %) |
| 25/06/2025 ~11h50 (Usina do Gasômetro) | 12,941 m³/s | 2.26 m | 6,265 (48 %) | 6,528 (50 %) | 6,361 (49 %) | 3,897 (30 %) |

**The fitted outflow is roughly half of the real outflow at flood stages** (v4 much less). The balance still closed during calibration because the **inflow was underestimated by a similar amount**. The inflow gauges have long gaps (§2.7), and the drainage area downstream of them is not measured at all: Rio Pardo, for example, covers about 71,000 of the 84,763 km² upstream of Porto Alegre. With two compensating errors the hindcasts look acceptable. When the inflow is complete, as in July 2026 when Lajeado was transmitting continuously, the too-small outflow makes the level rise too much. This is probably the main structural cause of the overestimation in §1, beyond the crest extrapolation.

It also confirms the identifiability problem ([METHODOLOGY §3.4](METHODOLOGY.md#34-identifiability)) and shows the way out: fit the outflow curve to the ADCP points (§6).

### 2.5 Horizon truncation

When the predicted peak falls on the last step of the 72 h horizon, it is a lower bound, not a peak. `scripts/replay_event.py` flags this (`*_at_horizon`). The dashboard should do the same, and should either extend the horizon or say "still rising at +72 h".

### 2.6 Few events, one extreme

Calibration uses three events, and one of them (May 2024) is far outside the range of the others. Parameters fitted mostly to that event (v1) do best on it and overshoot smaller floods. A version that does slightly worse on May 2024 (v2) does best in July 2026.

### 2.7 Inflow gauges with holes

Over the record, Lajeado (Taquari) has discharge in only 7 % of hours and Rio Pardo (Jacuí) in 41 % ([DATA.md](DATA.md#data-quirks-that-shape-the-model)). Each gap silently removes a major tributary from the inflow, and the rating then compensates during calibration.

## 3. Problems reported by IPH/UFRGS

The IPH/UFRGS team ran the operational forecasts of the Guaíba in May 2024 and, with the SGB, in July 2026. Their published work describes several of the same difficulties.

- **Damaged gauges and no data assimilation.** The MGB model has a streamflow data-assimilation scheme, but it "was not used during the forecast's elaboration since several gauging stations… [were] damaged or not properly operating" [Medeiros 2025]. The SGB reports that gauges on the Taquari and Caí were swept away or had their level sensors damaged, and that the operation of the Taquari and Caí alert systems was "seriamente comprometido" [SGB 2024].
- **Rating-curve extrapolation at the key gauges.** At Estrela/Lajeado (station 86879300, the Taquari gauge this model uses) the 2024 peak stage was 33.66 m, but discharge measurements only reach about 25 m. The 23,472 m³/s peak is therefore an extrapolation with "high" uncertainty [Collischonn 2025]. At Muçum the rating was defined with measurements up to 8,380 m³/s for an estimated peak of 13,241 m³/s [Collischonn 2025]. Laipelt et al. [2026] cite a report by Paiva et al. (2025) on rating-extrapolation uncertainty "particularly in locations such as Rio Pardo on the Jacuí River and at points along the Taquari River". These are the same two gauges that drive most of this model's inflow error.
- **Missing upstream boundaries.** The 2D model's "upstream boundary conditions… do not cover all the tributaries… due to lack of in situ observations, which may lead to local underestimations" [Laipelt 2026]. This model has the same issue when routing only upstream gauges (v4).
- **Sensitivity to the Guaíba's hydraulics.** Changing only Manning's roughness in the Guaíba between 0.025 and 0.045 moves the simulated peak at Cais Mauá by −0.91 to +0.32 m [Laipelt 2026]. That is the physical counterpart of this model's uncertain outflow curve.
- **Wind.** South-westerly wind over the Patos Lagoon restricts outflow and can raise the Guaíba by up to about 50 cm [Laipelt 2026; Possa 2022]. Medeiros et al. [2025] report forecast misses in June 2024 tied to wind: levels were forecast to fall below the alert level, but they reached 3.22 m.
- **Interpretation matters as much as the model.** "Signals of rising or falling water levels, in time horizons greater than 72 hours, were interpreted and discussed among the forecasters", with models recalibrated during the event [Medeiros 2025]. The published numbers are model output filtered by expert judgement.
- **The June 2025 flood.** The IPH ran hydrodynamic forecasts for this flood. They used the **old bathymetry**, because the new state survey was not yet available, and reported scenario uncertainty of 10–20 cm. They anticipated the rise, the alert level and the approach to the flood level about 3 days ahead. The IPH saw no anomaly that would suggest the 2024 bed changes had degraded its forecasts [IPH 2025].
- **Who publishes the forecasts.** The IPH published its own daily Guaíba forecasts on its website in 2024 and during the June 2025 flood. The last one, on 04/07/2025, says it is "a última previsão emitida pela equipe para a cheia de junho de 2025" [IPH site]. There is no IPH-branded forecast on that site for July 2026. Forecasts for the Guaíba are now issued in **SGB bulletins "utilizando as técnicas desenvolvidas no projeto"**, a cooperation agreement between SGB and IPH (TED) that runs to November 2026, with an extension to June 2027 in progress. A joint workshop in September 2026 discussed forecasting procedures, bulletin issuance and "propostas de interpretação e comunicação de resultados" [IPH 2026]. So the IPH did stop publishing forecasts under its own name, but the documented reason is this institutional change. **No source attributes it to overestimation.**
- **July 2026.** On 31/07/2026, Prof. Fernando Meirelles (IPH) said the Guaíba rose "no tempo esperado" but within "uma banda de incerteza". He said the main difficulty was estimating the discharge of the tributaries, which were falling by then, because the gauge network damaged in 2024 had not been maintained at several points. Measurement "feita ainda longe da Capital" adds to the uncertainty: "Se instalasse [pontos de observação] onde deveria ter, já se poderia saber com maior precisão" [Sul21 2026a].

## 4. Gaps shared by every model of the Guaíba

### 4.1 Bathymetry from the 1960s

The hydrodynamic models of the IPH describe the bed of the Guaíba and the Patos Lagoon with **Brazilian Navy nautical charts** [Possa 2022; Laipelt 2026]. The operational model of 2024 states that those charts come from **surveys of 1961–1966** [Medeiros 2025]. On the Taquari there was not enough data, and the channel was lowered by about 4 m by hand [Laipelt 2026]. Laipelt et al. state that the results "are depended on the DTM model data and bathymetry accuracy".

The May 2024 flood moved a large amount of sediment, so it is reasonable to ask whether that 60-year-old bathymetry still holds. The evidence so far is mixed and partial:

| Source | Finding |
|---|---|
| IPH/UFRGS and PGA POA technical note: dual-beam and side-scan survey of 26 Dec 2024, three profiles compared with the pre-2022 nautical-chart base [IPH 2025; O Sul 2025] | Lowering by erosion of the main channel and thalweg at the Usina do Gasômetro section and in the two Jacuí channels upstream. Sediment removed and bedrock exposed in places (sediment sampling hit rock). No generalised siltation. The IPH recommends "mapeamentos periódicos e mais abrangentes de batimetria". |
| State government bathymetry, 2025/2026, compared with surveys from 2013 and 2015 at a few control points [Sema 2026] | "não foram identificadas… alterações significativas nos pontos de amostragem". Partial results. |
| Projeto Guaíba (Unisinos, UFRGS, FEPAM), seismic survey compared with FEPAM 2018 [Unisinos 2026] | "processos localizados de erosão, transporte e deposição de sedimentos… especialmente na região do Delta do Jacuí e em corredores preferenciais de fluxo". Extent and link to 2024 still under evaluation; final synthesis due July 2028. |
| Sand bank between the Centro Histórico and Eldorado do Sul [Nova ilha] | Already on maps from the 1961–1964 surveys; grew after May 2024 to about 1.4 km × 250 m. The state government says it does not affect floods. |

In short, there is no evidence of large-scale siltation. There is evidence of **erosion of the channel at the Gasômetro section and in the Jacuí channels, and of deposition in parts of the delta**. Those are exactly the areas that control the stage–discharge relation at the gauge this model uses. The bathymetry in the hydrodynamic models predates both the 2024 flood and these changes. The IPH notes that its June 2025 forecasts, run on the old bathymetry, did not lose accuracy [IPH 2025]. The deepened channel is therefore not a demonstrated source of forecast error, but it remains unrepresented.

**How this affects this model.** It uses no bathymetry directly. Its outflow curve is fitted on data from May 2024 onwards, so it already reflects the post-flood channel, but it mixes the geometry during the flood with the geometry after it. If the bed near the Gasômetro keeps evolving, the curve will drift, and so will the datum offset between the two gauges (§4.4). Its stage–area curve and inundation map come from a 2011–2015 surface model (GLO-30), which predates the flood as well.

### 4.2 Extrapolated discharges at the tributaries

Every model of the Guaíba takes tributary discharge from ANA/SGB rating curves. Those curves are extrapolated in large floods (§3) and may have shifted after the 2024 bed changes on the Taquari. This model has no way to detect a shifted curve: the error goes straight into Qin and is absorbed by the outflow fit.

### 4.3 No discharge measurement on the Guaíba

Outflow to the Patos Lagoon is not measured routinely. The PGA POA/UFRGS ADCP campaigns are the only independent discharge data for the Guaíba:

- 35,736 m³/s on 05/05/2024 (Usina do Gasômetro section, corrected for overflow across the Ilha da Pintada);
- 22,070 m³/s on 15/05/2024 (Ponta do Dionísio);
- 12,941 m³/s on 25/06/2025 (Usina do Gasômetro).

[Toldo 2024; IPH 2025; also used by Laipelt 2026.] For reference, normal outflow is 1,000–2,000 m³/s, and the IPH estimates peak discharge at 14.9, 16.0, 28.2 and 15.1 thousand m³/s for the floods of Sept 2023, Nov 2023, May 2024 and June 2025 [IPH 2025]. These measurements are what exposed this model's outflow bias (§2.4).

### 4.4 Two gauges, two datums

Public forecasts and alert levels refer to the Cais Mauá (C6) gauge. The model works on the Gasômetro telemetry. Their difference is not constant:

| Condition | Cais Mauá − Gasômetro |
|---|---|
| Whole record, median | 0.42 m |
| July 2026 flood, median | 0.52 m |
| Peak of 24/07/2026 | 0.62 m |
| Peak of 31/07/2026 | 0.70 m |

The model uses a fixed +0.44 m, so converted forecasts **understate** the Cais Mauá level during floods. The overestimation in §1 is therefore, if anything, slightly larger than shown. The relation between the two gauges at the May 2024 peak was studied by the SGB [Germano 2024]. A stage-dependent offset would be more correct.

### 4.5 Wind is not in the model

The IPH models include wind; this one does not. Up to about 50 cm of Guaíba level can come from wind over the Patos Lagoon (§3), which this model absorbs into its bias term with a delay.

## 5. Where this model follows the IPH approach

Several design choices in this project follow, or match, the published IPH methodology:

| IPH/UFRGS | This model |
|---|---|
| "Simple offset corrections… ensured that each forecast started from a level consistent with the most recent observed data" [Medeiros 2025] | Bias correction from the last 24 h, applied as a ramp so the forecast starts at the observed level ([METHODOLOGY §4.3](METHODOLOGY.md#43-bias-correction-project-heuristic)) |
| Scenario ensembles, including a "zero rainfall and zero wind" benchmark [Medeiros 2025] | Three crest scenarios; with no rainfall input, the whole model is the analogue of the zero-rainfall benchmark |
| Contribution of each tributary and the timing of its peak; Taquari sets the peak, Jacuí the duration; synchronised peaks would add 0.82 m [Laipelt 2026; Medeiros 2025] | Inflow split by river, with per-river travel times |
| Wind scenarios for the Patos Lagoon backwater [Medeiros 2025; Possa 2022] | Not modelled: listed as a limitation |
| ADCP measurements as independent validation [Laipelt 2026; Toldo 2024] | Used here to test the outflow curve (§2.4); next step is to fit it to them |

The **zero-rainfall comparison** is the most telling. In the IPH evaluation of May 2024, zero-rainfall forecasts *underestimated* levels beyond 24 h, because new rain kept adding water [Medeiros 2025]. This model, which is effectively zero-rainfall, *overestimated* in July 2026. So its error does not come from missing rain. It comes from the crest extrapolation, an outflow curve about half the measured value, and the missing delta storage (§2.1, §2.4, §2.2).

## 6. What would reduce the error

In rough order of expected gain:

1. **Anchor the outflow curve to the ADCP measurements** (§2.4, §4.3), for example as a constrained fit or a penalty term, and let the inflow side absorb the remaining imbalance as an ungauged-area factor. This addresses the largest structural error found.
2. **Cap or replace the crest extrapolation.** Use upstream gauges (Muçum, Encantado) or an MGB-like rainfall–runoff model to bound how high a tributary can still rise.
3. **Add delta / floodplain storage between the tributaries and the Guaíba**, for example one more storage element for the Jacuí delta.
4. **Use a stage-dependent datum offset** between Gasômetro and Cais Mauá.
5. **Add wind** as a predictor of the Patos Lagoon backwater.
6. **Flag horizon-truncated peaks** and log every live forecast, so the next event can be evaluated without re-running.
7. **Revisit the topography once post-2024 bathymetry is published.** Use a terrain model without buildings (FABDEM, or ANADEM as in [Laipelt 2026]) for the map.

## 7. Documents consulted

Every PDF read for this discussion, with where it came from and its SHA-256, so anyone can check they are looking at the same file. All files were retrieved on **08 Nov 2026**. The ones bundled in this repository are also listed in [`papers/SHA256SUMS`](../papers/SHA256SUMS); verify with `sha256sum -c SHA256SUMS` from inside `papers/`.

### 7.1 Bundled in `papers/` (open licence)

| Key | Link | Size (bytes) | SHA-256 |
|---|---|---|---|
| [Medeiros 2025] | [papers/2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf](../papers/2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf) · https://doi.org/10.1590/2318-0331.302520250025 | 4,624,444 | `1adeb4b9b373d215b9ec8e29991c4661ffa46a2806ebff7d0be4e6b5695ff212` |
| [Laipelt 2026] | [papers/2026_Laipelt_HESS_2024_flood_mechanisms.pdf](../papers/2026_Laipelt_HESS_2024_flood_mechanisms.pdf) · https://doi.org/10.5194/hess-30-573-2026 | 14,034,473 | `07456865174e3d2cc0293584fe31973db26aca86201065b92ee7e51047d6858e` |
| [Collischonn 2025] | [papers/2025_Collischonn_RBRH_2024_disaster.pdf](../papers/2025_Collischonn_RBRH_2024_disaster.pdf) · https://doi.org/10.1590/2318-0331.302520240119 | 6,788,699 | `53f671ed1e0976f84f830aba3868b6f73d57fb0304828b2f107cef4dfb9ade33` |
| [Possa 2022] | [papers/2022_Possa_RBRH_1941_flood_wind.pdf](../papers/2022_Possa_RBRH_1941_flood_wind.pdf) · https://doi.org/10.1590/2318-0331.272220220028 | 5,003,409 | `ed8b3b5a043d9f3cbadfddfe17bad37607d7819abc9469bd79ea630d6fc7d298` |
| [Hawker 2022] | [papers/2022_Hawker_FABDEM.pdf](../papers/2022_Hawker_FABDEM.pdf) · https://doi.org/10.1088/1748-9326/ac4d4f | 2,516,007 | `683ac0dd52233a10ddb2293ebe59e1763aacb6def2323af244aac1559be24321` |
| [Rantz 1982] vol. 2 | [papers/1982_Rantz_WSP2175_vol2.pdf](../papers/1982_Rantz_WSP2175_vol2.pdf) · https://doi.org/10.3133/wsp2175 | 22,486,605 | `18f758d2cd3d5b136db559bbf2fc46dd9e3327a252393823f5518f8ad6f53eb4` |
| [Yevjevich 1964] | [papers/1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf](../papers/1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf) · https://doi.org/10.3133/wsp1690 | 5,412,959 | `1fcabaaabf06f65d3f67bd646b5b3f257818a316b7178ff4ff81f25bc090762a` |

### 7.2 Consulted online, not redistributed (licence not stated)

| Key | PDF link | Size (bytes) | SHA-256 |
|---|---|---|---|
| [Toldo 2024] Vazões no Rio Guaíba durante os picos da enchente de maio de 2024 (PGA POA/UFRGS, 24 Jul 2024) | https://www.ufrgs.br/iph/wp-content/uploads/2024/07/05_Nota-Vazoes-no-Rio-Guaiba-durante-os-picos-da-enchente-de-maio-de-2024.pdf | 209,861 | `41ef47d53725ec6d83b55aa7e69f0161dbbf5ac83cdf7779cc98c2155531d027` |
| [IPH 2025] Monitoramento ambiental e cheia no Guaíba e Delta do Jacuí em junho de 2025 (IPH/UFRGS and PGA POA, Jul 2025) | https://www.ufrgs.br/iph/wp-content/uploads/2025/07/Nota-Tecnica_Cheia-no-Guaiba-.pdf | 14,972,315 | `3f4b79716ec6816669fc0bd8fb1dab1f08da647913ac641382161041e5a590a7` |
| [SGB 2024] Levantamento dos níveis das marcas da grande cheia de maio de 2024 no RS (Nota Técnica, 3ª versão, 10 Sep 2024) | https://rigeo.sgb.gov.br/bitstream/doc/24939.5/3/nota_tecnica_levantamento_cheia_2024_v.3.pdf | 4,103,092 | `93364c95e92576068be8800d1d9b14f580f25baa4a21bd36fe5e70bcbf440f50` |
| Soares, D. M. & Marcuzzo, F. F. N. *Grandes cheias de 2023 e 2024 do rio Taquari: estudo preliminar das áreas inundadas em Encantado e Muçum* (SGB, poster). Read; not cited above | https://rigeo.sgb.gov.br/server/api/core/bitstreams/f620f9f9-1cbb-4b14-8c3c-a8eda53d47c2/content | 2,712,521 | `db0a7ee768afc46a4c047b45aca5a8948e5678a075b55b629d71121f1a64d0d7` |

Web pages (not PDFs) read in full: the three Sul21 articles [Sul21 2026a–c], the IPH news pages [IPH site; IPH 2026], and the state, O Sul, Unisinos and Jornal do Comércio pages on bathymetry. Their links are in [papers/README.md](../papers/README.md).

### 7.3 Tried but not obtained

| Document | Link | What happened |
|---|---|---|
| SGB/IPH bulletins of the July 2026 flood (SAH Guaíba, 22, 23, 24, 26, 29 and 30 Jul) | e.g. https://www.sgb.gov.br/sace/boletins/Guaiba/20260723_12-20260723%20-%20115622.pdf | HTTP 404 on 08 Nov 2026; content known only through the press |
| Paper on rating curves and the 2023/2024 floods (XXVI SBRH) | https://lume.ufrgs.br/bitstream/handle/10183/303638/001299077.pdf | Connection dropped / HTTP 504; not used |
| Jornal do Comércio, 23/07/2026, "Guaíba pode chegar a 2,70m… diz IPH" | https://www.jornaldocomercio.com/geral/2026/07/1257312-guaiba-pode-chegar-a-270m-em-porto-alegre-no-fim-de-semana-diz-iph.html | Paywall after the first paragraph. The 2.70 m figure (Cais Mauá, IPH) is confirmed by Sul21 [2026c], Rádio Pampa and Serra e Litoral |
