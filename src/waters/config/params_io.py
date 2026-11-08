"""Leitura/escrita dos parametros calibrados versionados (config/params/*.json)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from waters.config import settings
from waters.domain.errors import CalibrationError
from waters.domain.models import CalibrationParams

_FILENAME_RE = re.compile(r"^params_v(\d+)_(\d{8})\.json$")


def save_params(params: CalibrationParams, directory: Path | None = None) -> Path:
    target_dir = directory or settings.PARAMS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = params.generated_at.strftime("%Y%m%d")
    path = target_dir / f"params_{params.version}_{stamp}.json"
    path.write_text(params.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_latest_params(directory: Path | None = None) -> CalibrationParams:
    """Carrega o params_vN_YYYYMMDD.json de maior versao (depois data)."""
    target_dir = directory or settings.PARAMS_DIR
    candidates = []
    if target_dir.exists():
        for path in target_dir.glob("params_v*.json"):
            match = _FILENAME_RE.match(path.name)
            if match:
                candidates.append((int(match.group(1)), match.group(2), path))
    if not candidates:
        raise CalibrationError(
            f"Nenhum parametro calibrado em {target_dir}. Rode: python scripts/calibrate.py"
        )
    _, _, newest = max(candidates)
    return load_params_file(newest)


def load_params_file(path: Path) -> CalibrationParams:
    """Carrega um arquivo de parametros especifico."""
    return CalibrationParams.model_validate(
        json.loads(Path(path).read_text(encoding="utf-8"))
    )


def discover_param_files(directory: Path | None = None) -> list[Path]:
    """Lista params disponiveis: operacionais (top-level) + experimentais."""
    base = directory or settings.PARAMS_DIR
    files: list[Path] = []
    if base.exists():
        files += sorted(base.glob("params_v*.json"))
    experimental = base / "experimental"
    if experimental.exists():
        files += sorted(experimental.glob("params_v*.json"))
    return files


def describe_params(params: CalibrationParams, path: Path) -> str:
    """Rotulo curto para o seletor de modelo no dashboard."""
    if params.area_curve is None:
        area = "área constante"
    elif "GLO-30" in params.area_curve.source:
        area = "topografia DEM (GLO-30)"
    else:
        area = "curva aproximada"
    routing = " + roteamento" if params.reaches else ""
    operational = path.parent.name != "experimental"
    label = f"{params.version} — {area}{routing}"
    return label + (" · operacional" if operational else " · experimental")
