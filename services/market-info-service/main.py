import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from schemas import MarketSummaryResponse, MultiMarketSummaryResponse, HistoricalResponse, ExportarRequest
from providers import (
    obtener_mercado_chile,
    obtener_mercado_peru,
    obtener_mercado_colombia,
    obtener_mercado_por_pais,
    obtener_historial_simulado,
)
from exportador import generar_pdf, generar_excel, generar_html


load_dotenv()

app = FastAPI(
    title="NUAM Market Info Service",
    version="1.0.0",
    description=(
        "Microservicio independiente para obtener información de las bolsas de "
        "valores de Chile, Perú y Colombia.\n\n"
        "Intenta consultar una API real (por ejemplo Yahoo Finance) y, si no es "
        "posible, devuelve datos simulados pero coherentes para mantener el "
        "sistema operativo."
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
    return {"status": "ok", "service": "market-info-service"}


@app.get(
    "/markets/summary",
    response_model=MultiMarketSummaryResponse,
    tags=["markets"],
)
def markets_summary(
    pais: List[str] = Query(
        default=["CHL", "PER", "COL"],
        description="Lista de países a consultar (CHL, PER, COL).",
    ),
    proveedor: str = Query(
        default="yahoo",
        description="Proveedor de datos: 'yahoo' (Yahoo Finance, sin API key), 'alpha_vantage' (requiere API key), 'simulado' (datos simulados).",
    ),
) -> MultiMarketSummaryResponse:
    """
    Devuelve un resumen de mercados para uno o varios países.

    - Si la API real está disponible, `fuente_real=True` y `proveedor` indica la fuente.
    - Si no, se usan datos simulados (`fuente_real=False`, `proveedor='simulado'`) pero con la misma estructura.
    
    Proveedores disponibles:
    - 'yahoo': Intenta usar Yahoo Finance (gratuito, sin API key), cae a simulado si falla
    - 'alpha_vantage': Alpha Vantage API (gratuito, requiere API key en ALPHA_VANTAGE_API_KEY), cae a simulado si falla
    - 'simulado': Usa directamente datos simulados (siempre disponible)
    """
    mercados: List[MarketSummaryResponse] = []
    for p in pais:
        resumen = obtener_mercado_por_pais(p, proveedor)
        mercados.append(resumen)

    success = any(m.success for m in mercados)
    return MultiMarketSummaryResponse(success=success, mercados=mercados)


@app.get(
    "/markets/history",
    response_model=HistoricalResponse,
    tags=["markets"],
)
def market_history(
    pais: str = Query("CHL", description="País a consultar (CHL, PER, COL).")
) -> HistoricalResponse:
    """
    Devuelve una serie histórica mensual simulada para el índice principal de un país.

    Para este MVP usamos siempre datos simulados; en el futuro se podría
    enriquecer con datos históricos reales si la API lo permite.
    """
    return obtener_historial_simulado(pais)


@app.post("/exportar/pdf", tags=["exportacion"])
def exportar_pdf(payload: ExportarRequest) -> Response:
    """
    Exporta datos de mercados en formato PDF.
    
    Recibe una lista de datos de mercados y devuelve un archivo PDF listo para descargar.
    """
    try:
        pdf_content = generar_pdf(payload.datos_mercado, payload.titulo)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="mercados_{payload.titulo.replace(" ", "_").lower()}.pdf"'
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
    Exporta datos de mercados en formato Excel (.xlsx).
    
    Recibe una lista de datos de mercados y devuelve un archivo Excel listo para descargar.
    """
    try:
        excel_content = generar_excel(payload.datos_mercado, payload.titulo)
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="mercados_{payload.titulo.replace(" ", "_").lower()}.xlsx"'
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
    Exporta datos de mercados en formato HTML.
    
    Recibe una lista de datos de mercados y devuelve un archivo HTML listo para descargar.
    """
    try:
        html_content = generar_html(payload.datos_mercado, payload.titulo)
        return Response(
            content=html_content,
            media_type="text/html; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="mercados_{payload.titulo.replace(" ", "_").lower()}.html"'
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

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "5200")), reload=True)


