"""Validacao por hindcast: roda a previsao 'como se fosse' antes de um pico
historico e mede o erro de nivel e de tempo do pico previsto."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from waters.domain.errors import InsufficientDataError
from waters.domain.models import CalibrationParams, ScenarioName, Station
from waters.model.forecast import run_forecast

LEAD_HOURS = 48


@dataclass(frozen=True)
class HindcastScore:
    event: str
    observed_peak_m: float
    observed_peak_time: pd.Timestamp
    predicted_peak_m: float
    predicted_peak_time: pd.Timestamp
    level_error_m: float
    timing_error_h: float


def hindcast_event(
    event_name: str,
    window: tuple[str, str],
    flows_by_station: dict[str, pd.Series],
    poa_level: pd.Series,
    params: CalibrationParams,
    stations: dict[str, Station],
) -> HindcastScore:
    """Corta as series LEAD_HOURS antes do pico observado e preve o pico."""
    start, end = window
    observed = poa_level.loc[start:end].dropna()
    if observed.empty:
        raise InsufficientDataError(f"Evento {event_name} sem nivel de POA observado.")
    peak_time = observed.idxmax()
    peak_value = float(observed.max())
    as_of = peak_time - pd.Timedelta(hours=LEAD_HOURS)

    flows_cut = {c: s[s.index <= as_of] for c, s in flows_by_station.items()}
    poa_cut = observed[observed.index <= as_of]

    result, _ = run_forecast(
        flows_by_station=flows_cut,
        poa_level=poa_cut,
        params=params,
        stations=stations,
        now=as_of.to_pydatetime(),
    )
    central = result.peaks[ScenarioName.CENTRAL]
    predicted_time = pd.Timestamp(central.peak_time)

    return HindcastScore(
        event=event_name,
        observed_peak_m=round(peak_value, 2),
        observed_peak_time=peak_time,
        predicted_peak_m=central.peak_level_m,
        predicted_peak_time=predicted_time,
        level_error_m=round(central.peak_level_m - peak_value, 2),
        timing_error_h=round((predicted_time - peak_time).total_seconds() / 3600.0, 1),
    )
