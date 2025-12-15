from datetime import datetime
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
    mensaje: Optional[str] = None


class MultiMarketSummaryResponse(BaseModel):
    """Respuesta para la consulta de múltiples países."""

    success: bool
    mercados: List[MarketSummaryResponse] = Field(default_factory=list)


