"""Carrega e valida o registro de estacoes (config/stations.yaml)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from waters.config import settings
from waters.domain.errors import WatersError
from waters.domain.models import StageAreaCurve, Station


def load_stations(path: Path | None = None) -> dict[str, Station]:
    """Le o YAML e devolve {codigo: Station}, validado via pydantic."""
    file = path or settings.STATIONS_FILE
    if not file.exists():
        raise WatersError(f"Registro de estacoes nao encontrado: {file}")

    raw = yaml.safe_load(file.read_text(encoding="utf-8"))
    entries = raw.get("stations") if isinstance(raw, dict) else None
    if not entries:
        raise WatersError(f"Arquivo {file} sem chave 'stations' ou vazio")

    stations = {}
    for entry in entries:
        station = Station.model_validate(entry)
        if station.code in stations:
            raise WatersError(f"Codigo duplicado no registro: {station.code}")
        stations[station.code] = station
    return stations


@lru_cache(maxsize=1)
def get_registry() -> dict[str, Station]:
    """Registro padrao, cacheado por processo."""
    return load_stations()


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia em km entre (lat,lon) a e b."""
    import math
    r = 6371.0
    dlat = math.radians(b[0] - a[0])
    dlon = math.radians(b[1] - a[1])
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    h = (math.sin(dlat / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin(dlon / 2) ** 2)
    return r * 2 * math.asin(math.sqrt(h))


def load_reach_network(path: Path | None = None) -> dict:
    """Le config/reaches.yaml: fontes por rio, pares de validacao, coords."""
    file = path or settings.REACHES_FILE
    if not file.exists():
        raise WatersError(f"Rede de trechos nao encontrada: {file}")
    raw = yaml.safe_load(file.read_text(encoding="utf-8"))
    return {
        "delta_code": raw["delta_code"],
        "sources": dict(raw["sources"]),
        "validation_pairs": list(raw.get("validation_pairs", [])),
        "coords": {k: tuple(v) for k, v in raw.get("coords", {}).items()},
    }


def load_stage_area_curve(path: Path | None = None) -> StageAreaCurve:
    """Le config/stage_area.yaml -> StageAreaCurve (validada)."""
    file = path or settings.STAGE_AREA_FILE
    if not file.exists():
        raise WatersError(f"Curva cota-area nao encontrada: {file}")
    raw = yaml.safe_load(file.read_text(encoding="utf-8"))
    points = raw.get("points") if isinstance(raw, dict) else None
    if not points:
        raise WatersError(f"Arquivo {file} sem chave 'points' ou vazio")
    return StageAreaCurve(
        levels_m=[float(p["nivel_m"]) for p in points],
        areas_km2=[float(p["area_km2"]) for p in points],
        source=str(raw.get("source", "")),
    )


def inflow_stations(registry: dict[str, Station] | None = None) -> list[Station]:
    reg = registry if registry is not None else get_registry()
    return [s for s in reg.values() if s.role == "inflow"]


def target_stations(registry: dict[str, Station] | None = None) -> list[Station]:
    """Reguas-alvo disponiveis; a base (com dados proprios) vem primeiro."""
    reg = registry if registry is not None else get_registry()
    targets = [s for s in reg.values() if s.role == "target"]
    return sorted(targets, key=lambda s: (s.mirror_of is not None, s.name))


def target_station(
    registry: dict[str, Station] | None = None, code: str | None = None
) -> Station:
    """Regua-alvo pedida, ou a base (nao-derivada) por padrao."""
    targets = target_stations(registry)
    if not targets:
        raise WatersError("Nenhuma estacao target no registro")
    if code is not None:
        for station in targets:
            if station.code == code:
                return station
        raise WatersError(f"Estacao target {code} nao encontrada no registro")
    base = [s for s in targets if s.mirror_of is None]
    if len(base) != 1:
        raise WatersError(f"Esperada exatamente 1 regua-base, ha {len(base)}")
    return base[0]
