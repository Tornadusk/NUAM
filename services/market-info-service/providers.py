"""
Proveedores de datos de mercado (bolsas de valores) para Chile, Perú y Colombia.

Este módulo intenta primero obtener datos desde una API real (por ejemplo,
Yahoo Finance u otros proveedores públicos). Si la llamada falla por cualquier
motivo (sin internet, cambios en la API, límites, etc.), devuelve datos
simulados pero verosímiles para mantener funcionando el microservicio.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

import requests

from schemas import IndexItem, MarketSummaryResponse


def _llamar_api_yahoo(simbolos: List[str]) -> Dict[str, dict]:
    """
    Intenta obtener cotizaciones desde la API pública de Yahoo Finance.

    Nota: Esta API no es oficial y puede cambiar sin previo aviso. Por eso
    siempre se usa con try/except y se tiene un fallback a datos simulados.
    """
    if not simbolos:
        return {}

    url = "https://query1.finance.yahoo.com/v7/finance/quote"
    params = {"symbols": ",".join(simbolos)}

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("quoteResponse", {}).get("result", [])
        return {item.get("symbol"): item for item in result}
    except Exception:
        # Cualquier error → devolvemos dict vacío para que se use el fallback
        return {}


def _simulados_chile() -> MarketSummaryResponse:
    indices = [
        IndexItem(
            simbolo="IPSA.SN",
            nombre="IPSA - Santiago",
            pais="CHL",
            ultimo=5000.12,
            cambio=25.3,
            cambio_pct=0.51,
            moneda="CLP",
            volumen=12_345_678,
            hora=datetime.now(),
        ),
    ]
    return MarketSummaryResponse(
        success=True,
        pais="CHL",
        indices=indices,
        fuente_real=False,
        mensaje="Datos simulados de la Bolsa de Santiago (sin conexión a API real).",
    )


def _simulados_peru() -> MarketSummaryResponse:
    indices = [
        IndexItem(
            simbolo="SPBLPGPT.INDX",
            nombre="S&P/BVL Peru General",
            pais="PER",
            ultimo=24000.5,
            cambio=-120.3,
            cambio_pct=-0.5,
            moneda="PEN",
            volumen=3_210_000,
            hora=datetime.now(),
        ),
    ]
    return MarketSummaryResponse(
        success=True,
        pais="PER",
        indices=indices,
        fuente_real=False,
        mensaje="Datos simulados de la Bolsa de Valores de Lima (sin conexión a API real).",
    )


def _simulados_colombia() -> MarketSummaryResponse:
    indices = [
        IndexItem(
            simbolo="COLCAP.CO",
            nombre="COLCAP - Colombia",
            pais="COL",
            ultimo=1300.75,
            cambio=5.4,
            cambio_pct=0.42,
            moneda="COP",
            volumen=8_900_000,
            hora=datetime.now(),
        ),
    ]
    return MarketSummaryResponse(
        success=True,
        pais="COL",
        indices=indices,
        fuente_real=False,
        mensaje="Datos simulados de la Bolsa de Colombia (sin conexión a API real).",
    )


def obtener_mercado_chile() -> MarketSummaryResponse:
    """
    Intenta obtener información de mercado para Chile.

    Si la API real falla, retorna datos simulados.
    """
    # Símbolos de ejemplo (pueden ajustarse si Yahoo cambia)
    simbolos = ["^IPSA"]
    quotes = _llamar_api_yahoo(simbolos)

    if not quotes:
        return _simulados_chile()

    indices: List[IndexItem] = []
    for symbol, q in quotes.items():
        try:
            indices.append(
                IndexItem(
                    simbolo=symbol,
                    nombre=q.get("shortName") or "IPSA - Santiago",
                    pais="CHL",
                    ultimo=float(q.get("regularMarketPrice") or 0),
                    cambio=float(q.get("regularMarketChange") or 0),
                    cambio_pct=float(q.get("regularMarketChangePercent") or 0),
                    moneda=q.get("currency") or "CLP",
                    volumen=float(q.get("regularMarketVolume") or 0),
                    hora=datetime.fromtimestamp(q.get("regularMarketTime") or 0),
                )
            )
        except Exception:
            # Si un símbolo falla, lo ignoramos
            continue

    if not indices:
        return _simulados_chile()

    return MarketSummaryResponse(
        success=True,
        pais="CHL",
        indices=indices,
        fuente_real=True,
        mensaje="Datos obtenidos desde Yahoo Finance (IPSA).",
    )


def obtener_mercado_peru() -> MarketSummaryResponse:
    """
    Intenta obtener información de mercado para Perú.

    Yahoo Finance suele exponer el índice S&P/BVL Peru General bajo distintos
    símbolos; aquí usamos uno de ejemplo y si falla, usamos datos simulados.
    """
    simbolos = ["^SPBLPGPT"]
    quotes = _llamar_api_yahoo(simbolos)

    if not quotes:
        return _simulados_peru()

    indices: List[IndexItem] = []
    for symbol, q in quotes.items():
        try:
            indices.append(
                IndexItem(
                    simbolo=symbol,
                    nombre=q.get("shortName") or "S&P/BVL Peru General",
                    pais="PER",
                    ultimo=float(q.get("regularMarketPrice") or 0),
                    cambio=float(q.get("regularMarketChange") or 0),
                    cambio_pct=float(q.get("regularMarketChangePercent") or 0),
                    moneda=q.get("currency") or "PEN",
                    volumen=float(q.get("regularMarketVolume") or 0),
                    hora=datetime.fromtimestamp(q.get("regularMarketTime") or 0),
                )
            )
        except Exception:
            continue

    if not indices:
        return _simulados_peru()

    return MarketSummaryResponse(
        success=True,
        pais="PER",
        indices=indices,
        fuente_real=True,
        mensaje="Datos obtenidos desde Yahoo Finance (S&P/BVL Peru General).",
    )


def obtener_mercado_colombia() -> MarketSummaryResponse:
    """
    Intenta obtener información de mercado para Colombia.
    """
    simbolos = ["^COLCAP"]
    quotes = _llamar_api_yahoo(simbolos)

    if not quotes:
        return _simulados_colombia()

    indices: List[IndexItem] = []
    for symbol, q in quotes.items():
        try:
            indices.append(
                IndexItem(
                    simbolo=symbol,
                    nombre=q.get("shortName") or "COLCAP - Colombia",
                    pais="COL",
                    ultimo=float(q.get("regularMarketPrice") or 0),
                    cambio=float(q.get("regularMarketChange") or 0),
                    cambio_pct=float(q.get("regularMarketChangePercent") or 0),
                    moneda=q.get("currency") or "COP",
                    volumen=float(q.get("regularMarketVolume") or 0),
                    hora=datetime.fromtimestamp(q.get("regularMarketTime") or 0),
                )
            )
        except Exception:
            continue

    if not indices:
        return _simulados_colombia()

    return MarketSummaryResponse(
        success=True,
        pais="COL",
        indices=indices,
        fuente_real=True,
        mensaje="Datos obtenidos desde Yahoo Finance (COLCAP).",
    )


def obtener_mercado_por_pais(pais: str) -> MarketSummaryResponse:
    pais = pais.upper()
    if pais == "CHL":
        return obtener_mercado_chile()
    if pais == "PER":
        return obtener_mercado_peru()
    if pais == "COL":
        return obtener_mercado_colombia()

    # País no soportado → devolver estructura vacía
    return MarketSummaryResponse(success=False, pais=pais, indices=[], fuente_real=False, mensaje="País no soportado")


