from datetime import date
import os
from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv

from schemas import (
    ActualizarRequest,
    ActualizarResponse,
    TipoCambioItem,
    TiposCambioResponse,
    ExportarRequest,
)
from providers import crear_proveedores
from exportador import generar_pdf, generar_excel, generar_html


load_dotenv()

app = FastAPI(
    title="NUAM Exchange Rate Service",
    version="1.0.0",
    description=(
        "Microservicio independiente para consulta de tipos de cambio.\n\n"
        "Este servicio consulta proveedores externos (ExchangeRate API, Fixer.io, "
        "Banco Central de Chile) y devuelve los datos en memoria.\n"
        "El proyecto NUAM es responsable de persistir los resultados en su base de datos."
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
    return {"status": "ok", "service": "exchange-rate-service", "date": date.today().isoformat()}


@app.post("/tipos-cambio/actualizar", response_model=ActualizarResponse, tags=["tipos-cambio"])
def actualizar_tipos_cambio(payload: ActualizarRequest) -> ActualizarResponse:
    """
    Consulta a los proveedores externos de tipos de cambio y devuelve los resultados agregados.

    NUAM llamará a este endpoint en lugar de consultar directamente a las APIs externas.
    """
    monedas_destino: List[str] = payload.monedas or ["CLP", "PEN", "COP"]
    moneda_base = payload.moneda_base or "USD"

    api_key_exchangerate = os.getenv("EXCHANGERATE_API_KEY") or ""
    api_key_fixer = os.getenv("FIXER_API_KEY") or ""

    proveedores = crear_proveedores(
        api_key_exchangerate=api_key_exchangerate or None,
        api_key_fixer=api_key_fixer or None,
        incluir=payload.incluir_proveedores,
    )

    tipos_cambio_items: List[TipoCambioItem] = []
    errores: dict[str, str] = {}

    for proveedor in proveedores:
        resultado = proveedor.obtener_tipos_cambio(moneda_base=moneda_base, monedas_destino=monedas_destino)
        if not resultado.get("exito"):
            errores[proveedor.codigo] = resultado.get("error", "Error desconocido")
            continue

        for tc in resultado.get("tipos_cambio", []):
            tipos_cambio_items.append(
                TipoCambioItem(
                    moneda_origen=tc["moneda_origen"],
                    moneda_destino=tc["moneda_destino"],
                    tasa=tc["tasa"],
                    fecha=tc.get("fecha", date.today()),
                    fuente=proveedor.codigo,
                )
            )

    success = bool(tipos_cambio_items)
    metadata = {
        "moneda_base": moneda_base,
        "monedas_destino": monedas_destino,
        "proveedores_consultados": [p.codigo for p in proveedores],
        "fecha_consulta": date.today().isoformat(),
    }

    return ActualizarResponse(success=success, tipos_cambio=tipos_cambio_items, errores=errores, metadata=metadata)


@app.get("/tipos-cambio/actuales", response_model=TiposCambioResponse, tags=["tipos-cambio"])
def obtener_tipos_cambio_actuales(
    pais: str | None = Query(default=None, description="Código de país ISO3 (ej: CHL, PER, COL)."),
    moneda_base: str = Query(default="USD"),
) -> TiposCambioResponse:
    """
    Endpoint simple de conveniencia que llama internamente a `/tipos-cambio/actualizar`
    y devuelve solo la lista de tipos de cambio, sin guardar nada.

    Para este prototipo, el filtro por país se traduce en distintas combinaciones de monedas.
    """
    if pais == "CHL":
        monedas = ["CLP"]
    elif pais == "PER":
        monedas = ["PEN"]
    elif pais == "COL":
        monedas = ["COP"]
    else:
        monedas = ["CLP", "PEN", "COP"]

    actualizar_request = ActualizarRequest(monedas=monedas, moneda_base=moneda_base)
    actualizar_response = actualizar_tipos_cambio(actualizar_request)

    return TiposCambioResponse(
        success=actualizar_response.success,
        tipos_cambio=actualizar_response.tipos_cambio,
        source="live-providers",
    )


@app.post("/exportar/pdf", tags=["exportacion"])
def exportar_pdf(payload: ExportarRequest) -> Response:
    """
    Exporta tipos de cambio en formato PDF.
    
    Recibe una lista de tipos de cambio y devuelve un archivo PDF listo para descargar.
    """
    try:
        pdf_content = generar_pdf(payload.tipos_cambio, payload.titulo)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="tipos_cambio_{payload.titulo.replace(" ", "_").lower()}.pdf"'
            }
        )
    except Exception as e:
        return Response(
            content=f"Error al generar PDF: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )


@app.post("/exportar/excel", tags=["exportacion"])
def exportar_excel(payload: ExportarRequest) -> Response:
    """
    Exporta tipos de cambio en formato Excel (.xlsx).
    
    Recibe una lista de tipos de cambio y devuelve un archivo Excel listo para descargar.
    """
    try:
        excel_content = generar_excel(payload.tipos_cambio, payload.titulo)
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="tipos_cambio_{payload.titulo.replace(" ", "_").lower()}.xlsx"'
            }
        )
    except Exception as e:
        return Response(
            content=f"Error al generar Excel: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )


@app.post("/exportar/html", tags=["exportacion"])
def exportar_html(payload: ExportarRequest) -> Response:
    """
    Exporta tipos de cambio en formato HTML.
    
    Recibe una lista de tipos de cambio y devuelve un archivo HTML listo para descargar.
    """
    try:
        html_content = generar_html(payload.tipos_cambio, payload.titulo)
        return Response(
            content=html_content,
            media_type="text/html; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="tipos_cambio_{payload.titulo.replace(" ", "_").lower()}.html"'
            }
        )
    except Exception as e:
        return Response(
            content=f"Error al generar HTML: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "5100")), reload=True)


