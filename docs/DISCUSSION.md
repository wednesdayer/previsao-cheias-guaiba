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

Even after the Taquari crest had passed (cut 24/07 00h), v1 still predicted 2.87 m at Cais Mauá against 2.15 m observed. The hindcasts of June 2024 and June 2025 show the same +0.5 m bias. A likely cause is that the model sends the full Taquari wave into a single 470 km² storage, shifted in time but not attenuated. In reality much of it spreads over the Jacuí delta and its floodplains first. Laipelt et al. [2026] show that the Jacuí floodplains govern the duration of Guaíba floods. A lumped level-pool model calibrated on the extreme May 2024 event has no such buffer for smaller events.

### 2.3 The level-pool assumption

The model treats the Guaíba as a reservoir with a flat surface. During May 2024, ADCP measurements near downtown Porto Alegre recorded velocities of about 4 m/s, and the IPH team describes the event as "predominantly fluvial… with high velocities and well-defined flow direction" [Medeiros 2025]. A storage model cannot represent the water-surface slope between the delta and Porto Alegre. That slope is also why the inundation map misses by about 1.5 m of stage in Eldorado do Sul ([METHODOLOGY §6.3](METHODOLOGY.md#63-caveats)).

### 2.4 An effective, not physical, outflow curve

The rating Qout(h) is fitted to close the water balance, so it absorbs every error in inflow, storage and wind. Its exponent sits at the upper bound (b = 4.0) and the fit RMSE is about 2,000 m³/s. Without an independent discharge measurement in Porto Alegre, storage area and outflow are not separately identifiable ([METHODOLOGY §3.4](METHODOLOGY.md#34-identifiability)).

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
- **July 2026.** Prof. Fernando Meirelles (IPH) said the rise happened within "uma faixa de incerteza". He said the main difficulty was estimating tributary discharge, because the gauge network damaged in 2024 had not been maintained at several points [Sul21 2026].

## 4. Gaps shared by every model of the Guaíba

### 4.1 Bathymetry from the 1960s

The hydrodynamic models of the IPH describe the bed of the Guaíba and the Patos Lagoon with **Brazilian Navy nautical charts from surveys of 1961–1966** [Medeiros 2025; also Possa 2022; Laipelt 2026]. On the Taquari there was not enough data, and the channel was lowered by about 4 m by hand [Laipelt 2026]. Laipelt et al. state that the results "are depended on the DTM model data and bathymetry accuracy".

The May 2024 flood moved a large amount of sediment, so it is reasonable to ask whether that 60-year-old bathymetry still holds. The evidence so far is mixed and partial:

| Source | Finding |
|---|---|
| Technical note by Portos RS and IPH/UFRGS, survey of 26 Dec 2024 compared with nautical charts [O Sul 2025] | No generalised siltation in the Guaíba or the Jacuí, but "remoção de sedimentos e exposição do substrato rochoso em alguns trechos". The profile near the Usina do Gasômetro shows erosion. |
| State government bathymetry, 2025/2026, compared with surveys from 2013 and 2015 at a few control points [Sema 2026] | "não foram identificadas… alterações significativas nos pontos de amostragem". Partial results. |
| Projeto Guaíba (Unisinos, UFRGS, FEPAM), seismic survey compared with FEPAM 2018 [Unisinos 2026] | "processos localizados de erosão, transporte e deposição de sedimentos… especialmente na região do Delta do Jacuí e em corredores preferenciais de fluxo". Extent and link to 2024 still under evaluation; final synthesis due July 2028. |
| Sand bank between the Centro Histórico and Eldorado do Sul [Nova ilha] | Already on maps from the 1961–1964 surveys; grew after May 2024 to about 1.4 km × 250 m. The state government says it does not affect floods. |

In short, there is no evidence of large-scale siltation. There is evidence of **local erosion near the Gasômetro and deposition in the delta**, which are exactly the areas that control the stage–discharge relation at the gauge this model uses. The reference bathymetry predates both the 2024 flood and these changes.

**How this affects this model.** It uses no bathymetry directly. Its outflow curve is fitted on data from May 2024 onwards, so it already reflects the post-flood channel, but it mixes the geometry during the flood with the geometry after it. If the bed near the Gasômetro keeps evolving, the curve will drift, and so will the datum offset between the two gauges (§4.4). Its stage–area curve and inundation map come from a 2011–2015 surface model (GLO-30), which predates the flood as well.

### 4.2 Extrapolated discharges at the tributaries

Every model of the Guaíba takes tributary discharge from ANA/SGB rating curves. Those curves are extrapolated in large floods (§3) and may have shifted after the 2024 bed changes on the Taquari. This model has no way to detect a shifted curve: the error goes straight into Qin and is absorbed by the outflow fit.

### 4.3 No discharge measurement on the Guaíba

Outflow to the Patos Lagoon is not measured routinely. The ADCP campaigns of May 2024 near the Cais Mauá (Ponta da Cadeia and Ponta do Dionísio sections; Andrade et al. 2024, as cited in [Laipelt 2026]) are the only independent discharge data for the Guaíba. They are what would break the area–outflow trade-off in this model (§2.4).

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
| ADCP measurements as independent validation [Laipelt 2026] | Identified as the missing data to make outflow identifiable |

The **zero-rainfall comparison** is the most telling. In the IPH evaluation of May 2024, zero-rainfall forecasts *underestimated* levels beyond 24 h, because new rain kept adding water [Medeiros 2025]. This model, which is effectively zero-rainfall, *overestimated* in July 2026. So its error does not come from missing rain. It comes from the crest extrapolation and the missing delta storage (§2.1–2.2).

## 6. What would reduce the error

In rough order of expected gain:

1. **Cap or replace the crest extrapolation.** Use upstream gauges (Muçum, Encantado) or an MGB-like rainfall–runoff model to bound how high a tributary can still rise.
2. **Add delta / floodplain storage between the tributaries and the Guaíba**, for example one more storage element for the Jacuí delta.
3. **Calibrate the outflow against independent discharge** (the 2024 ADCP campaigns) instead of only closing the balance.
4. **Use a stage-dependent datum offset** between Gasômetro and Cais Mauá.
5. **Add wind** as a predictor of the Patos Lagoon backwater.
6. **Flag horizon-truncated peaks** and log every live forecast, so the next event can be evaluated without re-running.
7. **Revisit the topography once post-2024 bathymetry is published.** Use a terrain model without buildings (FABDEM, or ANADEM as in [Laipelt 2026]) for the map.
