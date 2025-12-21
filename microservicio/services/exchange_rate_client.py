"""
Cliente HTTP para el microservicio independiente de tipos de cambio.

Este módulo permite que Django NUAM llame al servicio `exchange-rate-service`
en lugar de consultar directamente a las APIs externas.
"""

from __future__ import annotations

import os
from typing import Dict, List, Any

import requests
from django.conf import settings


def _get_base_url() -> str:
    """
    Obtiene la URL base del microservicio de tipos de cambio.

    Se puede configurar mediante:
      - Variable de entorno EXCHANGE_RATE_SERVICE_URL
      - O bien en settings.EXCHANGE_RATE_SERVICE_URL
    """
    env_url = os.getenv("EXCHANGE_RATE_SERVICE_URL")
    if env_url:
        return env_url.rstrip("/")

    return getattr(settings, "EXCHANGE_RATE_SERVICE_URL", "http://localhost:5100").rstrip("/")


def llamar_exchange_rate_service_actualizar(
    monedas: List[str],
    moneda_base: str = "USD",
    incluir_proveedores: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Llama al endpoint POST /tipos-cambio/actualizar del microservicio.

    Devuelve el JSON tal cual lo responde el servicio, o un dict con
    'success': False y un mensaje de error si algo falla a nivel HTTP.
    """
    base_url = _get_base_url()
    url = f"{base_url}/tipos-cambio/actualizar"

    payload = {
        "monedas": monedas,
        "moneda_base": moneda_base,
        "incluir_proveedores": incluir_proveedores,
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": f"Error al llamar a exchange-rate-service: {exc}",
            "tipos_cambio": [],
        }


def exportar_tipos_cambio(tipos_cambio: List[Dict], formato: str, titulo: str = "Tipos de Cambio") -> requests.Response:
    """
    Llama al endpoint de exportación del microservicio exchange-rate-service.
    
    Args:
        tipos_cambio: Lista de diccionarios con los datos de tipos de cambio
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
        "tipos_cambio": tipos_cambio,
        "titulo": titulo,
    }
    
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp


