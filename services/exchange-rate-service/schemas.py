from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class TipoCambioItem(BaseModel):
    """Representa un tipo de cambio individual devuelto por el microservicio."""

    moneda_origen: str = Field(..., example="USD")
    moneda_destino: str = Field(..., example="CLP")
    tasa: Decimal = Field(..., example="950.50")
    fecha: date = Field(..., example="2025-12-15")
    fuente: Optional[str] = Field(None, description="Código de la fuente de tipos de cambio")


class ActualizarRequest(BaseModel):
    """
    Petición para actualizar tipos de cambio desde las APIs externas.

    Por simplicidad, este microservicio solo consulta las APIs externas y devuelve
    los datos en memoria. NUAM es responsable de persistirlos en su propia base de datos.
    """

    monedas: Optional[List[str]] = Field(
        default=None,
        description="Lista de monedas destino (ej: ['CLP', 'PEN', 'COP']). Si es None, se usa el set por defecto.",
    )
    moneda_base: str = Field(default="USD", description="Moneda base para las consultas.")
    incluir_proveedores: Optional[List[str]] = Field(
        default=None,
        description="Lista opcional de códigos de proveedores a consultar (EXCHANGERATE_API, FIXER_IO, BANCO_CENTRAL_CHILE).",
    )


class ActualizarResponse(BaseModel):
    """Respuesta estándar del endpoint de actualización."""

    success: bool
    tipos_cambio: List[TipoCambioItem] = Field(default_factory=list)
    errores: Dict[str, str] = Field(
        default_factory=dict,
        description="Errores por proveedor, con el código del proveedor como clave.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Información adicional (fechas consultadas, número de proveedores, etc.).",
    )


class TiposCambioResponse(BaseModel):
    """Respuesta para consultas de tipos de cambio 'actuales'."""

    success: bool
    tipos_cambio: List[TipoCambioItem] = Field(default_factory=list)
    source: str = Field(..., description="Descripción del origen de los datos (cache, última actualización, etc.).")


