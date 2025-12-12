from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from typing import Optional

app = FastAPI(
    title="Microservicio de Generación de Documentos NUAM",
    description="Servicio para generar comprobantes tributarios en PDF",
    version="1.0.0"
)

# Definimos qué datos esperamos recibir
class DetalleImpuesto(BaseModel):
    monto_base: int
    monto_impuesto: int
    categoria: str
    tasa_impuesto: Optional[float] = None
    moneda: Optional[str] = None
    estado: Optional[str] = None

class DatosComprobante(BaseModel):
    nombre_cliente: str
    rut: str
    fecha: str
    detalle_calculo: DetalleImpuesto
    corredora: Optional[str] = None
    instrumento: Optional[str] = None
    ejercicio: Optional[int] = None
    calificacion_id: Optional[int] = None

# Configuración de templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

@app.get("/")
async def root():
    """Endpoint de salud del microservicio"""
    return {
        "servicio": "Generador de Documentos NUAM",
        "version": "1.0.0",
        "status": "activo",
        "endpoints": {
            "generar_comprobante": "/generar-comprobante (POST)"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/generar-comprobante")
async def generar_pdf(datos: DatosComprobante):
    """
    Genera un comprobante tributario en formato PDF
    
    Recibe los datos de la calificación y genera un PDF profesional
    con el comprobante tributario correspondiente.
    """
    try:
        template = env.get_template("comprobante.html")
        html_content = template.render(
            nombre_cliente=datos.nombre_cliente,
            rut=datos.rut,
            fecha=datos.fecha,
            corredora=datos.corredora,
            instrumento=datos.instrumento,
            ejercicio=datos.ejercicio,
            calificacion_id=datos.calificacion_id,
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