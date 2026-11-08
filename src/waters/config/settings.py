"""Constantes e caminhos do projeto. Nada de valor magico espalhado no codigo."""

from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"
STATIONS_FILE = CONFIG_DIR / "stations.yaml"
STAGE_AREA_FILE = CONFIG_DIR / "stage_area.yaml"
REACHES_FILE = CONFIG_DIR / "reaches.yaml"
PARAMS_DIR = CONFIG_DIR / "params"
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"

TZ = ZoneInfo("America/Sao_Paulo")

# API ANA (telemetria aberta, XML)
ANA_BASE_URL = "https://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos"
ANA_TIMEOUT_S = 60.0
ANA_MAX_RETRIES = 3
ANA_CHUNK_DAYS = 30          # janela maxima por requisicao no backfill

# Fallback nivelguaiba.com.br (JSON por cidade, so nivel)
NIVELGUAIBA_BASE_URL = "https://nivelguaiba.com.br"
NIVELGUAIBA_TIMEOUT_S = 30.0

# Guaiba / Porto Alegre
GUAIBA_AREA_KM2 = 470.0
COTA_INUNDACAO_POA_M = 3.00
COTA_ALERTA_POA_M = 2.50
NORMAL_GAUGE_M = 0.9        # nivel normal tipico na regua do Gasometro (m)

# Mapa de inundacao (DEM GLO-30)
DEM_DIR = DATA_DIR / "dem"
INUNDATION_DIR = DATA_DIR / "inundation"
INUNDATION_FILE = INUNDATION_DIR / "region.npz"

# Ingestao incremental: re-busca janela de sobreposicao (telemetria chega atrasada)
CACHE_OVERLAP_HOURS = 6
STALE_AFTER_HOURS = 2.0      # dado mais velho que isso vira badge "defasado"

# Modelo
FORECAST_HORIZON_HOURS = 72
FORECAST_DT_MINUTES = 15
BIAS_WINDOW_HOURS = 24
BIAS_RAMP_HOURS = 12      # o vies entra em rampa (0 no inicio) para a curva
                         # conectar no nivel observado; deriva se acumula no tempo
MAX_GAP_INTERP_HOURS = 6     # lacuna maxima interpolavel
SPARSE_MAX_GAP_HOURS = 12    # acima disso, estacao esparsa e considerada muda

# Faixas de plausibilidade dos lags (horas) por grupo de rio
LAG_BOUNDS_HOURS: dict[str, tuple[float, float]] = {
    "jacui": (12.0, 30.0),
    "taquari": (18.0, 36.0),
    "cai": (12.0, 24.0),
    "sinos": (6.0, 18.0),
    "gravatai": (6.0, 18.0),
}
