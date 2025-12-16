"""
Proveedores de datos de mercado (bolsas de valores) para Chile, Perú y Colombia.

Este módulo intenta primero obtener datos desde una API real (por ejemplo,
Yahoo Finance u otros proveedores públicos). Si la llamada falla por cualquier
motivo (sin internet, cambios en la API, límites, etc.), devuelve datos
simulados pero verosímiles para mantener funcionando el microservicio.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import os

import requests

from schemas import IndexItem, MarketSummaryResponse, HistoricalPoint, HistoricalResponse


def _llamar_api_yahoo(simbolos: List[str]) -> tuple[Dict[str, dict], Optional[str]]:
    """
    Intenta obtener cotizaciones desde la API pública de Yahoo Finance.

    Returns:
        Tuple[Dict, Optional[str]]: (datos, mensaje_error)
    
    Nota: Esta API no es oficial y puede cambiar sin previo aviso. Por eso
    siempre se usa con try/except y se tiene un fallback a datos simulados.
    """
    if not simbolos:
        return {}, None

    url = "https://query1.finance.yahoo.com/v7/finance/quote"
    params = {"symbols": ",".join(simbolos)}

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("quoteResponse", {}).get("result", [])
        if not result:
            return {}, "Yahoo Finance no devolvió datos válidos"
        return {item.get("symbol"): item for item in result}, None
    except requests.exceptions.Timeout:
        return {}, "Yahoo Finance no respondió a tiempo (timeout)"
    except requests.exceptions.ConnectionError:
        return {}, "No se pudo conectar a Yahoo Finance (error de conexión)"
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 0
        if status_code == 429:
            return {}, "Yahoo Finance está limitando las solicitudes (error 429: Too Many Requests). Espera unos minutos o usa 'Datos Simulados'."
        elif status_code == 503:
            return {}, "Yahoo Finance está temporalmente no disponible (error 503: Service Unavailable)"
        elif status_code == 0:
            return {}, "Yahoo Finance no respondió (error HTTP 0: posible timeout o servidor inaccesible)"
        else:
            return {}, f"Yahoo Finance devolvió error HTTP {status_code}"
    except Exception as e:
        error_str = str(e)
        if "0" in error_str or "timeout" in error_str.lower() or "connection" in error_str.lower():
            return {}, f"Yahoo Finance no respondió (error: {error_str})"
        return {}, f"Error al llamar a Yahoo Finance: {error_str}"


def _llamar_api_alpha_vantage(simbolo: str) -> tuple[Dict[str, dict], Optional[str]]:
    """
    Intenta obtener cotizaciones desde Alpha Vantage API.
    
    Requiere API key en variable de entorno ALPHA_VANTAGE_API_KEY.
    Plan gratuito: 5 requests/minuto, 500 requests/día.
    
    Returns:
        Tuple[Dict, Optional[str]]: (datos, mensaje_error)
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return {}, "Alpha Vantage requiere API key (configurar ALPHA_VANTAGE_API_KEY en .env)"
    
    # Mapeo de símbolos latinoamericanos para Alpha Vantage
    simbolos_map = {
        "^IPSA": "IPSA",  # Alpha Vantage puede no tener este, usar genérico
        "^SPBLPGPT": "SPBLPGPT",
        "^COLCAP": "COLCAP"
    }
    
    simbolo_av = simbolos_map.get(simbolo, simbolo.replace("^", ""))
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": simbolo_av,
        "apikey": api_key
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Alpha Vantage puede devolver error en el JSON
        if "Error Message" in data:
            return {}, f"Alpha Vantage: {data['Error Message']}"
        if "Note" in data:
            return {}, f"Alpha Vantage: {data['Note']} (límite de requests alcanzado)"
        
        quote = data.get("Global Quote", {})
        if not quote or not quote.get("05. price"):
            # Alpha Vantage no tiene índices latinoamericanos en su base de datos gratuita
            return {}, "Alpha Vantage no tiene datos para este índice latinoamericano. Usa Yahoo Finance o Datos Simulados."
        
        # Formatear datos en estructura similar a Yahoo
        return {
            simbolo: {
                "symbol": simbolo,
                "regularMarketPrice": float(quote.get("05. price", 0)),
                "regularMarketChange": float(quote.get("09. change", 0)),
                "regularMarketChangePercent": float(quote.get("10. change percent", "0%").replace("%", "")),
                "regularMarketVolume": float(quote.get("06. volume", 0)),
                "regularMarketTime": datetime.now().timestamp(),
                "currency": quote.get("08. currency", "USD"),
                "shortName": quote.get("01. symbol", simbolo)
            }
        }, None
        
    except requests.exceptions.Timeout:
        return {}, "Alpha Vantage no respondió a tiempo (timeout)"
    except requests.exceptions.ConnectionError:
        return {}, "No se pudo conectar a Alpha Vantage (error de conexión)"
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 0
        return {}, f"Alpha Vantage devolvió error HTTP {status_code}"
    except Exception as e:
        return {}, f"Error al llamar a Alpha Vantage: {str(e)}"


def obtener_mercado_chile() -> MarketSummaryResponse:
    """Versión legacy - usar obtener_mercado_chile_con_proveedor() en su lugar."""
    return obtener_mercado_chile_con_proveedor("yahoo")


def obtener_mercado_peru() -> MarketSummaryResponse:
    """Versión legacy - usar obtener_mercado_peru_con_proveedor() en su lugar."""
    return obtener_mercado_peru_con_proveedor("yahoo")


def obtener_mercado_colombia() -> MarketSummaryResponse:
    """Versión legacy - usar obtener_mercado_colombia_con_proveedor() en su lugar."""
    return obtener_mercado_colombia_con_proveedor("yahoo")


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
        proveedor="simulado",
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
        proveedor="simulado",
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
        proveedor="simulado",
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


def obtener_mercado_chile_con_proveedor(proveedor: str = "yahoo") -> MarketSummaryResponse:
    """Obtiene datos de mercado para Chile usando el proveedor especificado."""
    proveedor = proveedor.lower()
    
    if proveedor == "simulado":
        resultado = _simulados_chile()
        resultado.proveedor = "simulado"
        return resultado
    elif proveedor == "yahoo":
        simbolos = ["^IPSA"]
        quotes, error_msg = _llamar_api_yahoo(simbolos)
        
        if not quotes:
            resultado = _simulados_chile()
            resultado.proveedor = "simulado"
            if error_msg:
                resultado.mensaje = f"Yahoo Finance falló: {error_msg}. Usando datos simulados."
            return resultado
        
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
                continue
        
        if not indices:
            resultado = _simulados_chile()
            resultado.proveedor = "simulado"
            return resultado
        
        return MarketSummaryResponse(
            success=True,
            pais="CHL",
            indices=indices,
            fuente_real=True,
            proveedor="yahoo",
            mensaje="Datos obtenidos desde Yahoo Finance (IPSA).",
        )
    elif proveedor == "alpha_vantage":
        simbolo = "^IPSA"
        quote_data, error_msg = _llamar_api_alpha_vantage(simbolo)
        
        if not quote_data:
            resultado = _simulados_chile()
            resultado.proveedor = "simulado"
            if error_msg:
                resultado.mensaje = f"⚠️ Alpha Vantage falló: {error_msg}. Usando datos simulados."
            return resultado
        
        # Procesar datos de Alpha Vantage
        q = list(quote_data.values())[0] if quote_data else {}
        try:
            indices = [
                IndexItem(
                    simbolo=q.get("symbol", "^IPSA"),
                    nombre=q.get("shortName", "IPSA - Santiago"),
                    pais="CHL",
                    ultimo=float(q.get("regularMarketPrice", 0)),
                    cambio=float(q.get("regularMarketChange", 0)),
                    cambio_pct=float(q.get("regularMarketChangePercent", 0)),
                    moneda=q.get("currency", "CLP"),
                    volumen=float(q.get("regularMarketVolume", 0)),
                    hora=datetime.fromtimestamp(q.get("regularMarketTime", datetime.now().timestamp())),
                )
            ]
            
            return MarketSummaryResponse(
                success=True,
                pais="CHL",
                indices=indices,
                fuente_real=True,
                proveedor="alpha_vantage",
                mensaje="Datos obtenidos desde Alpha Vantage (IPSA).",
            )
        except Exception:
            resultado = _simulados_chile()
            resultado.proveedor = "simulado"
            resultado.mensaje = "Error al procesar datos de Alpha Vantage. Usando datos simulados."
            return resultado
    else:
        # Proveedor desconocido, usar simulado
        resultado = _simulados_chile()
        resultado.proveedor = "simulado"
        resultado.mensaje = f"Proveedor '{proveedor}' no disponible, usando datos simulados."
        return resultado


def obtener_mercado_peru_con_proveedor(proveedor: str = "yahoo") -> MarketSummaryResponse:
    """Obtiene datos de mercado para Perú usando el proveedor especificado."""
    proveedor = proveedor.lower()
    
    if proveedor == "simulado":
        resultado = _simulados_peru()
        resultado.proveedor = "simulado"
        return resultado
    elif proveedor == "yahoo":
        simbolos = ["^SPBLPGPT"]
        quotes, error_msg = _llamar_api_yahoo(simbolos)
        
        if not quotes:
            resultado = _simulados_peru()
            resultado.proveedor = "simulado"
            if error_msg:
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    resultado.mensaje = f"⚠️ Yahoo Finance está limitando solicitudes (demasiadas peticiones). {error_msg}. Usando datos simulados."
                else:
                    resultado.mensaje = f"⚠️ Yahoo Finance falló: {error_msg}. Usando datos simulados."
            return resultado
        
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
            resultado = _simulados_peru()
            resultado.proveedor = "simulado"
            return resultado
        
        return MarketSummaryResponse(
            success=True,
            pais="PER",
            indices=indices,
            fuente_real=True,
            proveedor="yahoo",
            mensaje="Datos obtenidos desde Yahoo Finance (S&P/BVL Peru General).",
        )
    elif proveedor == "alpha_vantage":
        simbolo = "^SPBLPGPT"
        quote_data, error_msg = _llamar_api_alpha_vantage(simbolo)
        
        if not quote_data:
            resultado = _simulados_peru()
            resultado.proveedor = "simulado"
            if error_msg:
                resultado.mensaje = f"⚠️ Alpha Vantage falló: {error_msg}. Usando datos simulados."
            return resultado
        
        # Procesar datos de Alpha Vantage
        q = list(quote_data.values())[0] if quote_data else {}
        try:
            indices = [
                IndexItem(
                    simbolo=q.get("symbol", "^SPBLPGPT"),
                    nombre=q.get("shortName", "S&P/BVL Peru General"),
                    pais="PER",
                    ultimo=float(q.get("regularMarketPrice", 0)),
                    cambio=float(q.get("regularMarketChange", 0)),
                    cambio_pct=float(q.get("regularMarketChangePercent", 0)),
                    moneda=q.get("currency", "PEN"),
                    volumen=float(q.get("regularMarketVolume", 0)),
                    hora=datetime.fromtimestamp(q.get("regularMarketTime", datetime.now().timestamp())),
                )
            ]
            
            return MarketSummaryResponse(
                success=True,
                pais="PER",
                indices=indices,
                fuente_real=True,
                proveedor="alpha_vantage",
                mensaje="Datos obtenidos desde Alpha Vantage (S&P/BVL Peru General).",
            )
        except Exception:
            resultado = _simulados_peru()
            resultado.proveedor = "simulado"
            resultado.mensaje = "Error al procesar datos de Alpha Vantage. Usando datos simulados."
            return resultado
    else:
        resultado = _simulados_peru()
        resultado.proveedor = "simulado"
        resultado.mensaje = f"Proveedor '{proveedor}' no disponible, usando datos simulados."
        return resultado


def obtener_mercado_colombia_con_proveedor(proveedor: str = "yahoo") -> MarketSummaryResponse:
    """Obtiene datos de mercado para Colombia usando el proveedor especificado."""
    proveedor = proveedor.lower()
    
    if proveedor == "simulado":
        resultado = _simulados_colombia()
        resultado.proveedor = "simulado"
        return resultado
    elif proveedor == "yahoo":
        simbolos = ["^COLCAP"]
        quotes, error_msg = _llamar_api_yahoo(simbolos)
        
        if not quotes:
            resultado = _simulados_colombia()
            resultado.proveedor = "simulado"
            if error_msg:
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    resultado.mensaje = f"⚠️ Yahoo Finance está limitando solicitudes (demasiadas peticiones). {error_msg}. Usando datos simulados."
                else:
                    resultado.mensaje = f"⚠️ Yahoo Finance falló: {error_msg}. Usando datos simulados."
            return resultado
        
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
            resultado = _simulados_colombia()
            resultado.proveedor = "simulado"
            return resultado
        
        return MarketSummaryResponse(
            success=True,
            pais="COL",
            indices=indices,
            fuente_real=True,
            proveedor="yahoo",
            mensaje="Datos obtenidos desde Yahoo Finance (COLCAP).",
        )
    elif proveedor == "alpha_vantage":
        simbolo = "^COLCAP"
        quote_data, error_msg = _llamar_api_alpha_vantage(simbolo)
        
        if not quote_data:
            resultado = _simulados_colombia()
            resultado.proveedor = "simulado"
            if error_msg:
                resultado.mensaje = f"⚠️ Alpha Vantage falló: {error_msg}. Usando datos simulados."
            return resultado
        
        # Procesar datos de Alpha Vantage
        q = list(quote_data.values())[0] if quote_data else {}
        try:
            indices = [
                IndexItem(
                    simbolo=q.get("symbol", "^COLCAP"),
                    nombre=q.get("shortName", "COLCAP - Colombia"),
                    pais="COL",
                    ultimo=float(q.get("regularMarketPrice", 0)),
                    cambio=float(q.get("regularMarketChange", 0)),
                    cambio_pct=float(q.get("regularMarketChangePercent", 0)),
                    moneda=q.get("currency", "COP"),
                    volumen=float(q.get("regularMarketVolume", 0)),
                    hora=datetime.fromtimestamp(q.get("regularMarketTime", datetime.now().timestamp())),
                )
            ]
            
            return MarketSummaryResponse(
                success=True,
                pais="COL",
                indices=indices,
                fuente_real=True,
                proveedor="alpha_vantage",
                mensaje="Datos obtenidos desde Alpha Vantage (COLCAP).",
            )
        except Exception:
            resultado = _simulados_colombia()
            resultado.proveedor = "simulado"
            resultado.mensaje = "Error al procesar datos de Alpha Vantage. Usando datos simulados."
            return resultado
    else:
        resultado = _simulados_colombia()
        resultado.proveedor = "simulado"
        resultado.mensaje = f"Proveedor '{proveedor}' no disponible, usando datos simulados."
        return resultado


def obtener_mercado_por_pais(pais: str, proveedor: str = "yahoo") -> MarketSummaryResponse:
    """Obtiene datos de mercado para un país usando el proveedor especificado."""
    pais = pais.upper()
    if pais == "CHL":
        return obtener_mercado_chile_con_proveedor(proveedor)
    if pais == "PER":
        return obtener_mercado_peru_con_proveedor(proveedor)
    if pais == "COL":
        return obtener_mercado_colombia_con_proveedor(proveedor)

    # País no soportado → devolver estructura vacía
    return MarketSummaryResponse(
        success=False, 
        pais=pais, 
        indices=[], 
        fuente_real=False, 
        proveedor=None,
        mensaje="País no soportado"
    )


def obtener_historial_simulado(pais: str) -> HistoricalResponse:
    """
    Genera una serie simulada de valores mensuales para el último año.

    Se usa tanto como fallback cuando la API real falla como para simplificar
    el cálculo de histogramas en este MVP.
    """
    pais = pais.upper()
    hoy = date.today()
    año_actual = hoy.year

    # Valores base por país (aprox)
    base_por_pais = {
        "CHL": 5000.0,
        "PER": 24000.0,
        "COL": 1300.0,
    }
    simbolo_por_pais = {
        "CHL": "^IPSA",
        "PER": "^SPBLPGPT",
        "COL": "^COLCAP",
    }

    base = base_por_pais.get(pais, 1000.0)
    simbolo = simbolo_por_pais.get(pais, "DESCONOCIDO")

    puntos: List[HistoricalPoint] = []

    # Últimos 12 meses
    for i in range(11, -1, -1):
        mes = ((hoy.month - i - 1) % 12) + 1
        año = año_actual if hoy.month - i > 0 else año_actual - 1
        # Pequeña variación senoidal + ruido
        factor_mes = 1 + (0.03 * ((i - 6) / 6))  # tendencia suave
        valor = base * factor_mes
        puntos.append(
            HistoricalPoint(
                pais=pais,
                simbolo=simbolo,
                año=año,
                mes=mes,
                valor=round(valor, 2),
            )
        )

    return HistoricalResponse(success=True, pais=pais, puntos=puntos)


