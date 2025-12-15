import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from schemas import MarketSummaryResponse, MultiMarketSummaryResponse
from providers import (
    obtener_mercado_chile,
    obtener_mercado_peru,
    obtener_mercado_colombia,
    obtener_mercado_por_pais,
)


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
    )
) -> MultiMarketSummaryResponse:
    """
    Devuelve un resumen de mercados para uno o varios países.

    - Si la API real está disponible, `fuente_real=True`.
    - Si no, se usan datos simulados (`fuente_real=False`) pero con la misma estructura.
    """
    mercados: List[MarketSummaryResponse] = []
    for p in pais:
        resumen = obtener_mercado_por_pais(p)
        mercados.append(resumen)

    success = any(m.success for m in mercados)
    return MultiMarketSummaryResponse(success=success, mercados=mercados)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "5200")), reload=True)


