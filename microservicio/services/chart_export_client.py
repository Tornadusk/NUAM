"""
Cliente HTTP para el microservicio independiente de exportación de gráficos.

Este módulo permite que Django NUAM llame al servicio `chart-export-service`
para generar imágenes PNG/JPG de los gráficos visuales.
"""

from __future__ import annotations

import os
from typing import Dict, List, Any, Literal

import requests
from django.conf import settings


def _get_base_url() -> str:
    """
    Obtiene la URL base del microservicio de exportación de gráficos.

    Se puede configurar mediante:
      - Variable de entorno CHART_EXPORT_SERVICE_URL
      - O bien en settings.CHART_EXPORT_SERVICE_URL
    """
    env_url = os.getenv("CHART_EXPORT_SERVICE_URL")
    if env_url:
        return env_url.rstrip("/")

    return getattr(settings, "CHART_EXPORT_SERVICE_URL", "http://localhost:5300").rstrip("/")


def exportar_grafico_imagen(
    labels: List[str],
    datasets: List[Dict],
    tipo_grafico: Literal["tipos_cambio", "bolsa"],
    formato: Literal["png", "jpg"] = "png",
    titulo: str = None,
    chart_type: str = "line"
) -> requests.Response:
    """
    Exporta un gráfico como imagen (PNG/JPG).
    
    Args:
        labels: Lista de etiquetas del eje X (fechas, etc.)
        datasets: Lista de datasets compatible con Chart.js (debe tener 'label' y 'data')
        tipo_grafico: Tipo de gráfico ('tipos_cambio' o 'bolsa')
        formato: Formato de imagen ('png' o 'jpg')
        titulo: Título del gráfico (opcional)
    
    Returns:
        Response object con la imagen generada
    
    Raises:
        requests.exceptions.RequestException: Si hay un error en la petición
    """
    base_url = _get_base_url()
    
    # Determinar endpoint según tipo de gráfico
    if tipo_grafico == "tipos_cambio":
        url = f"{base_url}/exportar/tipos-cambio/{formato}"
    elif tipo_grafico == "bolsa":
        url = f"{base_url}/exportar/bolsa/{formato}"
    else:
        url = f"{base_url}/exportar/{formato}"
    
    payload = {
        "tipo_grafico": tipo_grafico,
        "labels": labels,
        "datasets": datasets,
        "formato": formato,
        "titulo": titulo,
        "chart_type": chart_type
    }
    
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp


def exportar_grafico_desde_chartjs_config(
    chart_config: Dict,
    formato: Literal["png", "jpg"] = "png"
) -> requests.Response:
    """
    Exporta un gráfico desde una configuración completa de Chart.js.
    
    Args:
        chart_config: Diccionario con configuración completa del gráfico
            Debe tener: 'labels', 'datasets', y opcionalmente 'type', 'title', etc.
        formato: Formato de imagen ('png' o 'jpg')
    
    Returns:
        Response object con la imagen generada
    
    Raises:
        requests.exceptions.RequestException: Si hay un error en la petición
    """
    base_url = _get_base_url()
    url = f"{base_url}/exportar/config"
    
    payload = {
        "chartConfig": chart_config,
        "format": formato,
        "quality": 95
    }
    
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp

