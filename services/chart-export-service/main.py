from datetime import date
import os
import sys
import logging
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv

from schemas import ChartDataRequest, ExportChartRequest
from chart_generator import generar_grafico_imagen, generar_grafico_desde_config


load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NUAM Chart Export Service",
    version="1.0.0",
    description=(
        "Microservicio independiente para exportar gráficos como imágenes.\n\n"
        "Este servicio recibe configuraciones de gráficos (compatible con Chart.js) "
        "y genera imágenes PNG/JPG de alta calidad.\n"
        "Soporta gráficos de tipos de cambio y datos de bolsa."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health() -> dict:
    """Endpoint simple de salud para Docker/monitoring."""
    return {"status": "ok", "service": "chart-export-service", "date": date.today().isoformat()}


@app.post("/exportar/{formato}", tags=["exportacion"])
def exportar_grafico_simple(
    payload: ChartDataRequest,
    formato: str = "png"
) -> Response:
    """
    Exporta un gráfico como imagen (formato simplificado compatible con Chart.js)
    
    Formato: png o jpg
    """
    try:
        # Validar formato
        formato_lower = formato.lower()
        if formato_lower not in ['png', 'jpg', 'jpeg']:
            raise HTTPException(status_code=400, detail=f"Formato no soportado: {formato}. Use 'png' o 'jpg'")
        
        # Generar imagen
        imagen_bytes = generar_grafico_imagen(
            labels=payload.labels,
            datasets=payload.datasets,
            chart_type="line",  # Por defecto línea, se puede extender
            titulo=payload.titulo or f"Gráfico de {payload.tipo_grafico}",
            formato=formato_lower,
            calidad=95
        )
        
        # Determinar content type
        content_type = "image/jpeg" if formato_lower in ['jpg', 'jpeg'] else "image/png"
        extension = "jpg" if formato_lower in ['jpg', 'jpeg'] else "png"
        filename = f"grafico_{payload.tipo_grafico}.{extension}"
        
        return Response(
            content=imagen_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Error al generar gráfico: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR en exportar_grafico_bolsa: {error_detail}")  # Log para debugging
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico: {str(e)}")


@app.post("/exportar/config", tags=["exportacion"])
def exportar_grafico_config(payload: ExportChartRequest) -> Response:
    """
    Exporta un gráfico desde una configuración completa
    
    Permite control total sobre el gráfico (tipo, colores, dimensiones, etc.)
    """
    try:
        config = payload.dict()
        imagen_bytes = generar_grafico_desde_config(config)
        
        # Determinar content type
        formato = payload.format.lower()
        content_type = "image/jpeg" if formato in ['jpg', 'jpeg'] else "image/png"
        extension = "jpg" if formato in ['jpg', 'jpeg'] else "png"
        filename = f"grafico.{extension}"
        
        return Response(
            content=imagen_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Error al generar gráfico: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR en exportar_grafico_bolsa: {error_detail}")  # Log para debugging
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico: {str(e)}")


@app.post("/exportar/tipos-cambio/{formato}", tags=["exportacion"])
def exportar_grafico_tipos_cambio(
    payload: ChartDataRequest,
    formato: str = "png"
) -> Response:
    """
    Endpoint específico para exportar gráficos de tipos de cambio
    """
    try:
        formato_lower = formato.lower()
        if formato_lower not in ['png', 'jpg', 'jpeg']:
            raise HTTPException(status_code=400, detail=f"Formato no soportado: {formato}")
        
        imagen_bytes = generar_grafico_imagen(
            labels=payload.labels,
            datasets=payload.datasets,
            chart_type=payload.chart_type or "line",
            titulo=payload.titulo or "Tipos de Cambio - Evolución Histórica",
            y_label="Tasa de Cambio",
            formato=formato_lower,
            calidad=95
        )
        
        content_type = "image/jpeg" if formato_lower in ['jpg', 'jpeg'] else "image/png"
        extension = "jpg" if formato_lower in ['jpg', 'jpeg'] else "png"
        filename = f"tipos_cambio_grafico.{extension}"
        
        return Response(
            content=imagen_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Error al generar gráfico: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR en exportar_grafico_bolsa: {error_detail}")  # Log para debugging
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico: {str(e)}")


@app.post("/exportar/bolsa/{formato}", tags=["exportacion"])
async def exportar_grafico_bolsa(
    request: Request,
    formato: str = "png"
) -> Response:
    """
    Endpoint específico para exportar gráficos de bolsa
    """
    try:
        formato_lower = formato.lower()
        if formato_lower not in ['png', 'jpg', 'jpeg']:
            raise HTTPException(status_code=400, detail=f"Formato no soportado: {formato}")
        
        # Obtener el JSON crudo para acceder a chart_type antes de la validación de Pydantic
        import json
        body_json = await request.json()
        
        # Extraer chart_type directamente del JSON (debe venir del frontend)
        chart_type_value = body_json.get('chart_type', 'line')
        chart_type_value = str(chart_type_value).strip().lower()
        
        # Validar que sea uno de los tipos soportados
        if chart_type_value not in ['bar', 'radar', 'line']:
            chart_type_value = 'line'
        
        # DEBUG: Ver qué chart_type se está usando
        print(f"MAIN_DEBUG: chart_type extraído del JSON: '{chart_type_value}'", flush=True)
        
        # Crear el payload validado (el chart_type del payload no se usa, usamos chart_type_value)
        payload = ChartDataRequest(**body_json)
        
        imagen_bytes = generar_grafico_imagen(
            labels=payload.labels,
            datasets=payload.datasets,
            chart_type=chart_type_value,
            titulo=payload.titulo or "Bolsa de Valores - Evolución Histórica",
            y_label="Precio",
            formato=formato_lower,
            calidad=95
        )
        
        content_type = "image/jpeg" if formato_lower in ['jpg', 'jpeg'] else "image/png"
        extension = "jpg" if formato_lower in ['jpg', 'jpeg'] else "png"
        filename = f"bolsa_grafico.{extension}"
        
        return Response(
            content=imagen_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Error al generar gráfico: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR en exportar_grafico_bolsa: {error_detail}")  # Log para debugging
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico: {str(e)}")

