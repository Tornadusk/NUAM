from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, Field


class IndexItem(BaseModel):
    """Índice o instrumento principal de una bolsa."""

    simbolo: str = Field(..., example="IPSA.SN")
    nombre: str = Field(..., example="IPSA - Índice de Precios Selectivo de Acciones")
    pais: str = Field(..., example="CHL")
    ultimo: float = Field(..., example=5000.12)
    cambio: float = Field(..., example=25.3, description="Cambio absoluto del día")
    cambio_pct: float = Field(..., example=0.54, description="Cambio porcentual del día")
    moneda: str = Field(..., example="CLP")
    volumen: Optional[float] = Field(None, example=12345678)
    hora: Optional[datetime] = None


class MarketSummaryResponse(BaseModel):
    """Respuesta para el resumen de mercado por país."""

    success: bool
    pais: str
    indices: List[IndexItem] = Field(default_factory=list)
    fuente_real: bool = Field(
        False,
        description="True si los datos provienen de una API real, False si son simulados.",
    )
    proveedor: Optional[str] = Field(
        None,
        description="Nombre del proveedor de datos utilizado (ej: 'yahoo', 'alpha_vantage', 'simulado').",
    )
    mensaje: Optional[str] = None


class MultiMarketSummaryResponse(BaseModel):
    """Respuesta para la consulta de múltiples países."""

    success: bool
    mercados: List[MarketSummaryResponse] = Field(default_factory=list)


class HistoricalPoint(BaseModel):
    """Punto de historial mensual para un índice."""

    pais: str = Field(..., example="CHL")
    simbolo: str = Field(..., example="^IPSA")
    año: int = Field(..., example=2025)
    mes: int = Field(..., ge=1, le=12, example=1)
    valor: float = Field(..., example=4800.5)


class HistoricalResponse(BaseModel):
    """Respuesta de historial de mercado por país."""

    success: bool
    pais: str
    puntos: List[HistoricalPoint] = Field(default_factory=list)


