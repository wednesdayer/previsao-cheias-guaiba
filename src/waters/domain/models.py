"""Modelos de dominio (pydantic) — validacao nas bordas do sistema."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

RiverGroup = Literal["jacui", "taquari", "cai", "sinos", "gravatai", "guaiba"]
StationRole = Literal["inflow", "upstream", "target"]


class Station(BaseModel):
    """Estacao telemetria da bacia, conforme config/stations.yaml."""

    model_config = {"frozen": True}

    code: str = Field(pattern=r"^\d{7,8}$")
    name: str
    slug: str
    river: str
    river_group: RiverGroup
    role: StationRole
    has_vazao: bool
    cota_inundacao_m: float = Field(gt=0)
    drainage_km2: float | None = Field(default=None, gt=0)
    sparse: bool = False
    datum_offset_m: float = 0.0
    # Regua derivada: previsao vem da estacao-base + offset (mirror_of).
    # own_telemetry=True => a regua transmite seu proprio nivel (exibido como
    # medicao independente), mas a PREVISAO ainda e espelhada da base.
    mirror_of: str | None = Field(default=None, pattern=r"^\d{7,8}$")
    own_telemetry: bool = False
    cota_alerta_m: float | None = Field(default=None, gt=0)


class Reading(BaseModel):
    """Uma leitura telemetrica ja normalizada (nivel em metros)."""

    model_config = {"frozen": True}

    station_code: str
    timestamp: datetime
    nivel_m: float | None = None
    vazao_m3s: float | None = Field(default=None, ge=0)
    chuva_mm: float | None = Field(default=None, ge=0)

    @field_validator("timestamp")
    @classmethod
    def require_tz(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp deve ser timezone-aware")
        return v


class ScenarioName(str, Enum):
    OTIMISTA = "otimista"
    CENTRAL = "central"
    PESSIMISTA = "pessimista"


class LagParams(BaseModel):
    """Defasagem calibrada de um afluente ate Porto Alegre."""

    model_config = {"frozen": True}

    station_code: str
    lag_hours: float = Field(ge=0, le=96)
    lag_spread_hours: float = Field(default=0.0, ge=0)
    per_event_hours: dict[str, float] = Field(default_factory=dict)


class StageAreaCurve(BaseModel):
    """Curva cota-area A(h): area superficial do Guaiba por nivel.

    Substitui a area constante. levels_m crescente; areas_km2 nao-decrescente
    (a lamina so espraia ao subir). Interpolada em model/area_curve.py.
    """

    model_config = {"frozen": True}

    levels_m: list[float]
    areas_km2: list[float]
    source: str = ""

    @model_validator(mode="after")
    def _check(self) -> "StageAreaCurve":
        if len(self.levels_m) != len(self.areas_km2) or len(self.levels_m) < 2:
            raise ValueError("levels_m e areas_km2 precisam do mesmo tamanho >= 2")
        if list(self.levels_m) != sorted(self.levels_m):
            raise ValueError("levels_m deve ser estritamente crescente")
        if any(b < a for a, b in zip(self.areas_km2, self.areas_km2[1:])):
            raise ValueError("areas_km2 deve ser nao-decrescente")
        if any(v <= 0 for v in self.areas_km2):
            raise ValueError("areas_km2 deve ser positivo")
        return self


class RatingParams(BaseModel):
    """Curva de descarga do Guaiba: Qout(h) = a * (h - h0)^b."""

    model_config = {"frozen": True}

    a: float = Field(gt=0)
    h0: float
    b: float = Field(gt=0)
    area_km2: float = Field(gt=0)          # area nominal (h=0); fallback linear
    area_stage_factor: float = Field(default=0.0, ge=0)
    rmse_m3s: float | None = None


class CrestParams(BaseModel):
    """Decaimento da taxa de subida e recessao por estacao."""

    model_config = {"frozen": True}

    station_code: str
    tau_rise_hours: float = Field(gt=0)
    tau_recession_hours: float = Field(gt=0)


class ReachParams(BaseModel):
    """Trecho de canal roteado por Muskingum (do afluente ate o delta).

    K = tempo de viagem (h); X = atenuacao (0..0.5). O trecho de previsao liga
    a regua-fonte (montante confiavel) ao delta; validation_of aponta o par
    regua-a-regua usado para aferir K,X quando existe.
    """

    model_config = {"frozen": True}

    reach_id: str
    source_code: str                       # regua de montante roteada
    river_group: RiverGroup
    length_km: float = Field(ge=0)
    k_hours: float = Field(gt=0, le=120)
    x: float = Field(ge=0, le=0.5)
    nse: float | None = None               # Nash-Sutcliffe na validacao, se houver


class CalibrationParams(BaseModel):
    """Conjunto versionado de parametros calibrados."""

    model_config = {"frozen": True}

    version: str
    generated_at: datetime
    events: list[str]
    lags: dict[str, LagParams]
    rating: RatingParams
    crests: dict[str, CrestParams]
    area_curve: StageAreaCurve | None = None   # None => area linear do rating
    reaches: dict[str, ReachParams] = Field(default_factory=dict)  # vazio => usa lags
    notes: str = ""


class PeakEstimate(BaseModel):
    """Pico previsto do Guaiba em Porto Alegre."""

    model_config = {"frozen": True}

    scenario: ScenarioName
    peak_level_m: float
    peak_time: datetime
    above_cota: bool
    hours_above_cota: float = Field(ge=0)


class ForecastResult(BaseModel):
    """Resultado completo de uma rodada de previsao."""

    model_config = {"frozen": True}

    generated_at: datetime
    params_version: str
    target_code: str = "87450020"
    h0_m: float
    bias_offset_m: float
    inflow_now_m3s: dict[str, float]
    inflow_total_m3s: float
    outflow_now_m3s: float
    peaks: dict[ScenarioName, PeakEstimate]
    degraded_stations: list[str] = Field(default_factory=list)
