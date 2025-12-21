"""
Cliente HTTP para el microservicio de información de mercados (Bolsa).

Permite que Django NUAM consuma `market-info-service` desde código Python,
en lugar de llamar directamente desde el navegador.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import requests
from django.conf import settings


def _get_base_url() -> str:
    env_url = os.getenv("MARKET_INFO_SERVICE_URL")
    if env_url:
        return env_url.rstrip("/")

    return getattr(settings, "MARKET_INFO_SERVICE_URL", "http://localhost:5200").rstrip("/")


def obtener_resumen_mercados(paises: List[str] | None = None, proveedor: str = "yahoo") -> Dict[str, Any]:
    """
    Llama a GET /markets/summary del microservicio de Bolsa.

    Args:
        paises: Lista de países a consultar (CHL, PER, COL). Si None, usa todos.
        proveedor: Proveedor de datos ('yahoo' o 'simulado'). Por defecto 'yahoo'.

    Devuelve el JSON bruto (o un dict con success=False y mensaje de error).
    """
    base_url = _get_base_url()
    url = f"{base_url}/markets/summary"

    params: Dict[str, Any] = {"proveedor": proveedor}
    if paises:
        params["pais"] = paises

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": f"Error al llamar a market-info-service: {exc}",
            "mercados": [],
        }


def exportar_mercados(datos_mercado: List[Dict], formato: str, titulo: str = "Información de Bolsas") -> requests.Response:
    """
    Llama al endpoint de exportación del microservicio market-info-service.
    
    Args:
        datos_mercado: Lista de diccionarios con los datos de mercados
        formato: Formato de exportación ('pdf', 'excel', 'html')
        titulo: Título del documento
    
    Returns:
        Response object con el archivo generado
    
    Raises:
        requests.exceptions.RequestException: Si hay un error en la petición
    """
    base_url = _get_base_url()
    url = f"{base_url}/exportar/{formato}"
    
    payload = {
        "datos_mercado": datos_mercado,
        "titulo": titulo,
    }
    
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp


def obtener_historial_mercado(pais: str) -> Dict[str, Any]:
    """
    Llama a GET /markets/history del microservicio de Bolsa.
    """
    base_url = _get_base_url()
    url = f"{base_url}/markets/history"

    try:
        resp = requests.get(url, params={"pais": pais}, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": f"Error al llamar a market-info-service (history): {exc}",
            "pais": pais,
            "puntos": [],
        }


