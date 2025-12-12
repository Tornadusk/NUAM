from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
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

# Configuración de templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

@app.post("/generar-comprobante")
async def generar_pdf(datos: DatosComprobante):
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
        raise HTTPException(status_code=500, detail=str(e))