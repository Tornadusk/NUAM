from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import csv
import io
from openpyxl import Workbook # Para Excel
from typing import List, Optional
import os

app = FastAPI(title="Docs Generator Universal")

# --- MODELOS DE DATOS ---
class ItemReporte(BaseModel):
    columna1: str
    columna2: str
    columna3: str
    columna4: str

class DatosReporte(BaseModel):
    titulo: str
    fecha: str
    generado_por: str
    formato: str  # <--- NUEVO: "pdf", "csv", or "excel"
    items: List[ItemReporte]

# Configuración Jinja2 (Solo para PDF)
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

# --- LÓGICA DE GENERACIÓN ---

def generar_pdf(datos: DatosReporte):
    template = env.get_template("reporte_tabla.html")
    html_content = template.render(
        titulo=datos.titulo,
        fecha=datos.fecha,
        generado_por=datos.generado_por,
        items=datos.items
    )
    return HTML(string=html_content).write_pdf(), "application/pdf"

def generar_csv(datos: DatosReporte):
    # Usamos StringIO para escribir texto en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezados
    writer.writerow(["Código", "Nombre", "Descripción", "Estado"])
    
    # Datos
    for item in datos.items:
        writer.writerow([item.columna1, item.columna2, item.columna3, item.columna4])
    
    # Convertimos a bytes para enviarlo
    return output.getvalue().encode('utf-8'), "text/csv"

def generar_excel(datos: DatosReporte):
    # Usamos openpyxl para crear un Excel real
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte NUAM"
    
    # Título y Fecha en las primeras filas
    ws.append([datos.titulo])
    ws.append(["Fecha:", datos.fecha])
    ws.append([]) # Fila vacía
    
    # Encabezados de tabla
    headers = ["Código", "Nombre", "Descripción", "Estado"]
    ws.append(headers)
    
    # Datos
    for item in datos.items:
        ws.append([item.columna1, item.columna2, item.columna3, item.columna4])
    
    # Guardar en memoria (BytesIO)
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# --- ENDPOINT PRINCIPAL ---

@app.post("/exportar")
async def exportar_documento(datos: DatosReporte):
    try:
        if datos.formato == "pdf":
            content, media_type = generar_pdf(datos)
        elif datos.formato == "csv":
            content, media_type = generar_csv(datos)
        elif datos.formato == "excel":
            content, media_type = generar_excel(datos)
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use pdf, csv o excel.")

        return Response(content=content, media_type=media_type)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))