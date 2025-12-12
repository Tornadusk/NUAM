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
    try:
        formato = datos.formato.lower()
        
        if formato == 'pdf':
            return await _generar_pdf(datos)
        elif formato == 'csv':
            return await _generar_csv(datos)
        elif formato == 'excel':
            return await _generar_excel(datos)
        else:
            raise HTTPException(status_code=400, detail=f"Formato no soportado: {formato}")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
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
    try:
        output = io.StringIO()
        
        # Escribir encabezados (usar las claves del primer item)
        if datos.items:
            fieldnames = list(datos.items[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(datos.items)
        
        csv_content = output.getvalue()
        output.close()
        
        return Response(
            content=csv_content.encode('utf-8-sig'),  # BOM para Excel
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="reporte.csv"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando CSV: {str(e)}")

async def _generar_excel(datos: DatosReporte):
    """Genera un archivo Excel (.xlsx)"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        
        # Escribir encabezados
        if datos.items:
            fieldnames = list(datos.items[0].keys())
            ws.append(fieldnames)
            
            # Escribir datos
            for item in datos.items:
                row = [item.get(field, '') for field in fieldnames]
                ws.append(row)
        
        # Guardar en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="reporte.xlsx"'}
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