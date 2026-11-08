# Methodology

This document describes every step of the model, the reference each step rests on, and the places where the method is a **project-specific heuristic** rather than an established technique. Reference keys such as [Chow 1988] point to [papers/README.md](../papers/README.md), which has full citations, DOIs and PDFs where the license allows.

**Contents**

1. [Setting and goal](#1-setting-and-goal)
2. [Inflow](#2-inflow)
3. [Outflow without a discharge gauge](#3-outflow-without-a-discharge-gauge)
4. [Forecast](#4-forecast)
5. [Calibration and validation](#5-calibration-and-validation)
6. [Inundation map](#6-inundation-map)
7. [Model variants and what they showed](#7-model-variants-and-what-they-showed)
8. [Limitations](#8-limitations)
9. [Relation to existing work](#9-relation-to-existing-work)

---

## 1. Setting and goal

The Guaíba is a short, wide water body of about 470 km² at normal stage. It receives the Jacuí, Taquari, Caí, Sinos and Gravataí rivers through the Jacuí delta and drains south into the Lagoa dos Patos [Laipelt 2026]. In May 2024 it reached **5.37 m** on 05 May, beating the 1941 record of 4.76 m [Medeiros 2025; Possa 2022; Collischonn 2025].

Three facts shape the method:

- **The Guaíba has no discharge gauge.** Porto Alegre reports only stage, so outflow has to be inferred.
- **Most of the water passes through gauged rivers first.** ANA telemetry provides stage and discharge every 15 min at the downstream gauge of each tributary (see [DATA.md](DATA.md)).
- **The Guaíba responds slowly.** A large surface area means level changes are an integral of the inflow–outflow imbalance over days.

The goal is a forecast of the stage at the Usina do Gasômetro gauge (ANA 87450020) for the next 72 h, built only from water that has already been measured upstream. There is no rainfall forecast (see [§9](#9-relation-to-existing-work) for how that compares with operational systems).

## 2. Inflow

### 2.1 Composition

Total inflow is the sum of the tributary discharges, each moved forward by its travel time to the delta:

```
Qin(t) = Σ_rivers Q_r(t − L_r)
```

`model/inflow.py` implements this on an hourly grid. The inflow gauges are Rio Pardo (Jacuí), Lajeado (Taquari), São Sebastião do Caí, São Leopoldo (Sinos) and Gravataí. A missing station counts as zero **only** when another station covers that instant; instants with no valid station stay empty. This choice underestimates inflow when a major gauge is silent, as discussed in [§8](#8-limitations).

### 2.2 Travel times (lags), *project heuristic*

The level-pool balance (§3) says that inflow shows up in the **rate of change** of stage, not in the stage itself. The lag of each river is therefore the shift that maximises the Pearson correlation between upstream discharge `Q_r(t)` and downstream `dh/dt(t + L)` (`model/lags.py`). Using dh/dt also removes the gauge datum and slow trends.

That first estimate is biased, because dh/dt reflects the net flow `Qin − Qout`. A second pass (`calibrate/run.py`) correlates `Q_r` with the **reconstructed inflow** `A·dh/dt + Qout(h)` (§3.3), which removes the bias. Lags are estimated per flood event, combined by median, and clamped to physically plausible ranges (`settings.LAG_BOUNDS_HOURS`).

Calibrated lags (v1): Jacuí/Rio Pardo 12 h, Taquari/Lajeado 26 h, Caí 12 h, Sinos 6 h, Gravataí 6 h.

Cross-correlation for lag estimation is standard practice. Applying it to dh/dt and to the reconstructed inflow is this project's adaptation.

### 2.3 Muskingum routing (v4)

v4 replaces the fixed shift with Muskingum routing [McCarthy 1938; Chow 1988, ch. 8]. Each reach relates inflow I and outflow O through storage `S = K[X·I + (1 − X)·O]`, which discretises to

```
O_{t+1} = C0·I_{t+1} + C1·I_t + C2·O_t
C0 = (Δt − 2KX) / D,   C1 = (Δt + 2KX) / D,   C2 = (2K(1 − X) − Δt) / D,   D = 2K(1 − X) + Δt
```

`model/routing.py` implements this with `scipy.signal.lfilter`. K is the travel time and X (0–0.5) controls attenuation. Cunge showed that the scheme approximates the diffusion-wave equation, which ties K to the wave celerity (K ≈ Δx / c) [Cunge 1969]. To keep the coefficients non-negative (no spurious oscillation), a long reach is split into a **cascade of n sub-reaches** with K_sub = K/n ≈ Δt. This is the usual stability condition 2KX ≤ Δt ≤ 2K(1 − X) [Chow 1988].

K and X are fitted per reach by maximising the Nash–Sutcliffe efficiency [Nash 1970] between routed and observed discharge on gauge pairs that both measure flow (`calibrate/fit_routing.py`, `config/reaches.yaml`):

| Validation reach | NSE |
|---|---|
| Muçum → Encantado (Taquari) | 0.88 |
| Encantado → Lajeado (Taquari) | 0.81 |
| Dona Francisca → Cachoeira do Sul → Rio Pardo (Jacuí) | 0.30–0.49 |

The source-to-delta reaches used in the forecast have Taquari K = 21.3 h, X = 0.00 (pure storage attenuation) and Jacuí K = 26.8 h, X = 0.48 (almost pure translation). The other rivers use K equal to their lag and X = 0.2.

On the Taquari the method reproduces the flood wave well (celerity ≈ 8 km/h). On the Jacuí it does not: the reach contains the Dona Francisca hydropower dam, which simple channel routing cannot represent.

## 3. Outflow without a discharge gauge

### 3.1 Level-pool balance

The Guaíba is treated as a single storage element (level-pool or "storage" routing [Puls 1928; Chow 1988; Yevjevich 1964]):

```
A(h) · dh/dt = Qin(t) − Qout(h)
```

Here h is the Gasômetro stage, A(h) the water-surface area (constant 470 km² in v1, see §7) and Qout(h) the outflow to the Lagoa dos Patos. A single storage assumes a horizontal water surface across the Guaíba, so it ignores wind tilt and the slope from the delta to the outlet. §8 lists the consequences.

### 3.2 Outflow as a rating curve

Outflow is written as the standard power-law stage–discharge relation [Rantz 1982, vol. 2; WMO 2010]:

```
Qout(h) = a · (h − h0)^b
```

h0 plays the role of the gauge height of zero flow. In river gauging, a, h0 and b are fitted to measured (h, Q) pairs. **Here there are no measured Q values**, which is the key difference.

### 3.3 Fitting the rating to close the balance

Rearranging the balance gives the outflow implied by the observations at each hour:

```
Qout_implied(t) = Qin(t) − A(h) · dh/dt
```

`model/rating.py` computes this over the whole record (Apr 2024 onwards) and fits a, h0 and b by least squares with a **Huber loss** [Huber 1964] (`scipy.optimize.least_squares(loss="huber")`). The Huber loss is quadratic for small residuals and linear for large ones, so hours dominated by things the model leaves out (wind set-up, backwater from the Lagoa dos Patos, gauge glitches) do not dominate the fit. The scale parameter is 20 % of the median implied outflow, with a floor of 100 m³/s.

Parameters are bounded: b ∈ [0.3, 4.0] and h0 below the minimum observed stage. **In v1–v3 the exponent sits at the upper bound (b = 4.0)** and the RMSE of the fit is about 2,000 m³/s. The rating is an effective curve that absorbs every unmodelled process. It should not be read as a physical discharge measurement.

Inverting the fitted balance gives the **reconstructed inflow** `F(t) = A·dh/dt + Qout(h)`, which is used in the second lag pass (§2.2).

### 3.4 Identifiability

With no independent discharge measurement in Porto Alegre, A(h) and Qout(h) are **not separately identifiable**: any change in the assumed area is compensated by the re-fitted rating. §7 shows this empirically. Breaking the trade-off would need independent outflow data, such as ADCP campaigns on the Guaíba.

## 4. Forecast

`model/forecast.py` orchestrates these steps for each of three scenarios.

### 4.1 Crest extrapolation, *project heuristic*

If a tributary is still rising, its next hours have to be guessed before they can be propagated. `model/crest.py` assumes the current rise rate r0 (measured over the last 6 h) **decays exponentially** with time constant τ:

```
Q(t) = Q0 + r0·τ·(1 − e^(−t/τ))        crest = Q0 + r0·τ
```

After about 4τ the river enters **exponential recession** towards a base level (the 25th percentile of recent flow). τ_rise and τ_recession are fitted per station by log-linear regression on the rising and falling limbs of past events (`calibrate/fit_crest.py`) and clamped to 6–120 h.

The three scenarios scale τ_rise by 0.7 (optimistic), 1.0 (central) and 1.4 (pessimistic, which also holds the crest for 6 h). This extrapolation is the **largest source of forecast volatility** (§7.3). It is a simple parametric assumption, not a hydrological model: a rainfall-runoff model such as MGB [Collischonn 2007; Pontes 2017] is the principled replacement.

### 4.2 Integration

The balance is integrated with the classical fourth-order Runge–Kutta method [Butcher 2016] on a 15-minute step over 72 h (`model/balance.py`). Qin(t) is linearly interpolated between hourly values. RK4 is more than accurate enough for this smooth one-dimensional ODE; the dominant errors are in Qin and Qout, not in the integrator.

### 4.3 Bias correction, *project heuristic*

Before forecasting, the model is re-run over the last 24 h from the observed stage, and the median of `observed − simulated` becomes a bias term. The bias is applied as a **ramp**: zero at the forecast start, full value after 12 h. The forecast therefore starts exactly at the observed level, and the correction grows the way model drift does. An earlier constant offset produced a visible jump at t = 0, which is why it was replaced.

### 4.4 Outputs

For each scenario the model reports the peak stage and its time, whether it exceeds the flood stage (3.00 m at the Gasômetro), and the hours spent above it.

Two more gauges are derived from the Gasômetro forecast by a datum offset: Cais Mauá (+0.44 m, measured from simultaneous telemetry at normal stages) and Eldorado do Sul (offset 0, provisional).

## 5. Calibration and validation

### 5.1 Events

Calibration events are the known May 2024 window (26 Apr – 08 Jun 2024) plus events detected automatically whenever the Gasômetro stage stays above 1.8 m for at least 48 h (`calibrate/events.py`). The v1 calibration used May 2024, June 2024 and June 2025.

### 5.2 Calibration sequence

`calibrate/run.py`:

1. Hourly grid and QC (spikes > 2 m/h, flat lines ≥ 12 h removed; gaps ≤ 6 h interpolated).
2. First-pass lags from Q vs dh/dt.
3. Provisional rating from the implied outflow.
4. Second-pass lags against the reconstructed inflow.
5. Final rating refit.
6. Crest τ per station.
7. Hindcast report. Parameters are written to `config/params/params_vN_<date>.json`.

### 5.3 Hindcast

`calibrate/hindcast.py` cuts all series **48 h before** each observed peak and runs the forecast as if it were live.

| Event | Observed peak | Forecast peak (central) | Error |
|---|---|---|---|
| May 2024 | 4.14 m (06/05 20h) | 3.81 m (06/05 04h) | −0.33 m / −16 h |
| Jun 2024 | 2.37 m (28/06 23h) | 2.93 m (29/06 23h) | +0.56 m / +24 h |
| Jun 2025 | 2.27 m (25/06 15h) | 2.81 m (26/06 15h) | +0.54 m / +24 h |

The model **overestimates small floods**. For the May 2024 rising limb, the mean absolute error over successive blind forecasts was 0.39 m in level and 26 h in timing (v1).

**About the 4.14 m vs 5.37 m difference.** The official 5.37 m refers to the historical Cais Mauá (C6) gauge. The model's series is the ANA telemetry of the Gasômetro gauge, whose record starts on 03 May 2024 and peaks at 4.17 m on 05 May. The two gauges do not share a datum, and the relation between them at the 2024 peak was the subject of a dedicated SGB study [Germano 2024]. The +0.44 m offset this project measured at normal stages does not reconcile the two peaks. All numbers in this repository are in the Gasômetro telemetry datum and should not be compared directly with the official 5.37 m.

## 6. Inundation map

### 6.1 Stage–area curve

`scripts/build_area_curve.py` derives A(h) from the Copernicus DEM GLO-30 (see [DATA.md](DATA.md#2-copernicus-dem-glo-30)). It clips the Guaíba and the Jacuí delta (stopping north of the Lagoa dos Patos), builds the hypsometric curve (area below each elevation) and **anchors** it to the gauge datum. The anchor is the elevation where the cumulative area equals 470 km², taken to correspond to 0.9 m on the gauge. The result goes from 470 km² at 0 m to 961 km² at 6 m (`config/stage_area.yaml`).

### 6.2 Connected bathtub

The map (`scripts/build_inundation.py`, `model/inundation.py`) uses a **bathtub model with hydrological connectivity** [Poulter 2008; Williams 2020]. For a gauge level h, a DEM cell is flooded if its elevation is below the anchored water surface **and** it is connected to the water body (`scipy.ndimage.label`). Without the connectivity test, isolated depressions far from the river would be painted as flooded. The script precomputes an "arrival level" raster, so the dashboard slider only thresholds it, in the browser.

### 6.3 Caveats

- **The DEM is a surface model.** GLO-30 includes buildings and canopy [Copernicus DEM]. Buildings act as walls, so urban flooding is underestimated. FABDEM removes buildings and forests from the same DEM and is the natural upgrade [Hawker 2022].
- **The water surface is flat.** The bathtub ignores the slope of the river and the delta, and any dynamics. Checked against a known point in Eldorado do Sul during the June 2025 flood, the map was off by about 1.5 m of stage there.
- **The datum anchor is approximate** (§6.1).

The map is illustrative, and the dashboard says so.

## 7. Model variants and what they showed

All variants share the balance, rating fit, crest extrapolation and bias correction. They differ in the storage area and in how inflow is propagated. Parameters live in `config/params/` (operational) and `config/params/experimental/`.

| Model | A(h) | Inflow | Rating (a, h0, b) | Status |
|---|---|---|---|---|
| v1 | constant 470 km² | fixed lags | 3.03, −4.48, 4.00 | operational |
| v2 | hand-guessed 470 → 1650 km² | fixed lags | 3.21, −4.46, 4.00 | experimental |
| v3 | DEM curve 470 → 961 km² | fixed lags | 3.03, −4.51, 4.00 | experimental |
| v4 | DEM curve | Muskingum from upstream gauges | 86.3, −4.58, 1.98 | experimental |

### 7.1 Area does not move the peak

May 2024, mean absolute error over the rising limb:

| Model | Level | Timing |
|---|---|---|
| v1 | **0.39 m** | 26 h |
| v3 | 0.59 m | **20 h** |
| v4 | 0.86 m | 39 h |

At the peak dh/dt = 0, so A(h) cancels out of the balance and the peak level is set by Qin = Qout(h). Because the rating is re-fitted for each area assumption (§3.4), a more realistic A(h) changes the shape and timing of the hydrograph but **not the peak magnitude**. v3 has better timing and a flatter, longer flood, but a worse peak level than v1.

### 7.2 Routing works per reach, not end to end

v4's Muskingum reaches validate well on the Taquari (NSE 0.81–0.88), yet the integrated forecast is the worst of the four. Routing only the **upstream** gauge drops the lateral inflow between that gauge and the river mouth, so total inflow is underestimated. The rating fit compensates (the exponent falls from 4 to about 2) and then overestimates the peak. On the Jacuí the dam breaks the routing altogether. The planned use of routing is surgical: fill in the Jacuí from Cachoeira do Sul when Rio Pardo is silent, scaled by drainage area.

### 7.3 Forecast volatility in a live flood

Forecasts re-run with data cut at each moment of the July 2026 Taquari flood:

| Run at | Observed stage | Lajeado Q (m³/s) | v1 peak | v3 peak |
|---|---|---|---|---|
| 22/07 12h | 0.95 m | 9,067 | 4.56 m | 4.39 m |
| 22/07 18h | 1.07 m | 10,485 | 4.42 m | 4.25 m |
| 23/07 00h | 1.34 m | 11,070 | 4.21 m | 4.03 m |
| 23/07 12h | 1.37 m | 9,153 | 3.53 m | 3.15 m |
| 24/07 00h | 1.44 m | 5,631 | 2.74 m | 2.29 m |

**The observed peak at the Gasômetro was 1.53 m** (24/07, about 20h). The forecasts made 2–3 days ahead were therefore 2–3 m too high. [DISCUSSION.md](DISCUSSION.md#1-july-2026-a-real-time-test) compares all four versions with the official SGB/IPH forecasts over both waves of the event.

While the Taquari was rising, crest extrapolation (§4.1) projected it upward. When the real crest passed Lajeado (11,078 m³/s on 23/07 01h), the predicted peak fell with it. Practical reading:

- **Reliable:** inflow over the next ~24 h, which is water already in the rivers inside the travel-time window, and the trend.
- **Not reliable while upstream rivers are still rising:** the absolute peak value, which errs high. That makes the model a conservative alert but a poor number.

## 8. Limitations

1. **No rainfall forecast.** Only observed water is propagated, so the useful horizon is 48–72 h.
2. **Wind and the Lagoa dos Patos are not modelled.** South-westerly wind restricts outflow and can raise the Guaíba by up to about 50 cm; north-easterly wind does the opposite [Laipelt 2026; Possa 2022; Munar 2018]. In this model those effects end up in the rating residuals and the bias term.
3. **Gaps in the inflow gauges.** Rio Pardo (Jacuí) has 41 % discharge coverage and Lajeado (Taquari) 7 %. The Jacuí drains about 85 % of the basin and the Taquari drives the peaks [Laipelt 2026], so these gaps are the main source of inflow error (see [DATA.md](DATA.md#data-quirks-that-shape-the-model)).
4. **Discharges are rating-curve products.** ANA discharges are extrapolated in extreme floods (±10–20 %).
5. **The rating is effective, not physical** (§3.3, §3.4).
6. **The inundation map is a static bathtub on a DSM** (§6.3).

## 9. Relation to existing work

During the May 2024 flood, the IPH/UFRGS team ran daily operational forecasts of the Guaíba. They combined the MGB hydrological model, calibrated for the region, with ECMWF/GEFS rainfall forecasts and wind scenarios. Their system anticipated levels above 5 m with three days of lead time and a second peak eight days ahead [Medeiros 2025]. Laipelt et al. [2026] later built a detailed hydrodynamic model of the event, validated with SWOT satellite data, and showed that the Taquari set the peak in Porto Alegre while the Jacuí set its duration.

This project is deliberately much simpler: a single storage element fed by observed tributary discharge, with an outflow curve inferred from the data instead of hydraulics. Its value is that it runs from public telemetry alone, in seconds, and is transparent about every assumption. The obvious next steps all move towards those operational systems:

- rainfall-runoff upstream (MGB-like, with Open-Meteo forecasts);
- wind forcing on the outlet;
- FABDEM [Hawker 2022] for the map;
- surgical routing for the Jacuí gaps.
