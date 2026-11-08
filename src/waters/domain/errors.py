"""Excecoes de dominio do modelo hidrologico."""


class WatersError(Exception):
    """Base para erros do projeto."""


class IngestError(WatersError):
    """Falha ao buscar ou interpretar dados de uma fonte externa."""


class StationOfflineError(IngestError):
    """Estacao sem dados recentes em nenhuma fonte."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(f"Estacao {code} sem dados disponiveis. {detail}".strip())


class InsufficientDataError(WatersError):
    """Serie curta ou com lacunas demais para o calculo pedido."""


class CalibrationError(WatersError):
    """Falha no ajuste de parametros (lags, rating, crista)."""
