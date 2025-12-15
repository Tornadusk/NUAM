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


def obtener_resumen_mercados(paises: List[str] | None = None) -> Dict[str, Any]:
    """
    Llama a GET /markets/summary del microservicio de Bolsa.

    Devuelve el JSON bruto (o un dict con success=False y mensaje de error).
    """
    base_url = _get_base_url()
    url = f"{base_url}/markets/summary"

    params: Dict[str, Any] = {}
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


