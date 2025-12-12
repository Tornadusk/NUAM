from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import csv
import io
from openpyxl import Workbook  # Para Excel
from typing import List, Optional, Dict, Any
import os

app = FastAPI()

# Definimos qué datos esperamos recibir
class DetalleImpuesto(BaseModel):
    monto_base: int
    monto_impuesto: int
    categoria: str

class DatosComprobante(BaseModel):
    nombre_cliente: str
    rut: str
    fecha: str
    detalle_calculo: DetalleImpuesto

class DatosReporte(BaseModel):
    titulo: str
    fecha: str
    generado_por: str
    formato: str  # 'pdf', 'csv', 'excel'
    items: List[Dict[str, Any]]  # Lista de diccionarios con los datos

# Configuración Jinja2 (Solo para PDF)
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

@app.get("/health")
async def health():
    """Endpoint de salud para verificar que el microservicio está funcionando"""
    return {"status": "ok", "service": "docs-generator"}

@app.post("/exportar")
async def exportar(datos: DatosReporte):
    """
    Endpoint principal para exportar datos en diferentes formatos (PDF, CSV, Excel)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[MICROSERVICIO] Recibida petición de exportación: formato={datos.formato}, título={datos.titulo}, items={len(datos.items)}")
        print(f"[MICROSERVICIO] Recibida petición: formato={datos.formato}, título={datos.titulo}, {len(datos.items)} items", flush=True)
        
        formato = datos.formato.lower()
        
        if formato == 'pdf':
            logger.info("[MICROSERVICIO] Generando PDF...")
            result = await _generar_pdf(datos)
            logger.info("[MICROSERVICIO] PDF generado exitosamente")
            return result
        elif formato == 'csv':
            logger.info("[MICROSERVICIO] Generando CSV...")
            result = await _generar_csv(datos)
            logger.info("[MICROSERVICIO] CSV generado exitosamente")
            return result
        elif formato == 'excel':
            logger.info("[MICROSERVICIO] Generando Excel...")
            result = await _generar_excel(datos)
            logger.info("[MICROSERVICIO] Excel generado exitosamente")
            return result
        else:
            logger.error(f"[MICROSERVICIO] Formato no soportado: {formato}")
            raise HTTPException(status_code=400, detail=f"Formato no soportado: {formato}")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"[MICROSERVICIO] Error al generar archivo: {str(e)}")
        print(f"[MICROSERVICIO] ERROR: {str(e)}", flush=True)
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)

async def _generar_pdf(datos: DatosReporte):
    """Genera un PDF usando el template reporte_tabla.html"""
    try:
        template = env.get_template("reporte_tabla.html")
        html_content = template.render(
            titulo=datos.titulo,
            fecha=datos.fecha,
            generado_por=datos.generado_por,
            items=datos.items
        )
        # Crear PDF en memoria
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        # Devolver el PDF
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")

async def _generar_csv(datos: DatosReporte):
    """Genera un archivo CSV"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[MICROSERVICIO CSV] Generando CSV con {len(datos.items)} items")
        print(f"[MICROSERVICIO CSV] Generando CSV con {len(datos.items)} items", flush=True)
        
        output = io.StringIO()
        
        # Escribir encabezados (usar las claves del primer item o usar encabezados fijos)
        if datos.items:
            # Usar encabezados fijos para mantener consistencia
            fieldnames = ['columna1', 'columna2', 'columna3', 'columna4', 'columna5', 'columna6', 'columna7']
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(datos.items)
        
        csv_content = output.getvalue()
        output.close()
        
        # Usar el título del payload para el nombre del archivo
        filename = f"{datos.titulo.replace(' ', '_')}_{datos.fecha.replace('/', '-')}.csv"
        
        return Response(
            content=csv_content.encode('utf-8-sig'),  # BOM para Excel
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando CSV: {str(e)}")

async def _generar_excel(datos: DatosReporte):
    """Genera un archivo Excel (.xlsx)"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[MICROSERVICIO Excel] Generando Excel con {len(datos.items)} items")
        print(f"[MICROSERVICIO Excel] Generando Excel con {len(datos.items)} items", flush=True)
        
        wb = Workbook()
        ws = wb.active
        # Usar el título del payload para el nombre de la hoja (máximo 31 caracteres)
        ws.title = datos.titulo[:31] if len(datos.titulo) <= 31 else datos.titulo[:28] + "..."
        
        # Escribir encabezados (usar encabezados fijos para mantener consistencia)
        if datos.items:
            fieldnames = ['columna1', 'columna2', 'columna3', 'columna4', 'columna5', 'columna6', 'columna7']
            ws.append(['ID', 'Corredora', 'Instrumento', 'Estado', 'Ejercicio', 'Fecha Pago', 'Descripción'])
            
            # Escribir datos
            for item in datos.items:
                row = [item.get(field, '') for field in fieldnames]
                ws.append(row)
        
        # Guardar en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Usar el título del payload para el nombre del archivo
        filename = f"{datos.titulo.replace(' ', '_')}_{datos.fecha.replace('/', '-')}.xlsx"
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando Excel: {str(e)}")

@app.post("/generar-comprobante")
async def generar_comprobante(datos: DatosComprobante):
    """Endpoint para generar comprobantes PDF (legacy - mantener compatibilidad)"""
    try:
        template = env.get_template("comprobante.html")
        html_content = template.render(
            nombre_cliente=datos.nombre_cliente,
            rut=datos.rut,
            fecha=datos.fecha,
            detalle_calculo=datos.detalle_calculo.dict()
        )
        # Crear PDF en memoria
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        # Devolver el PDF
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)