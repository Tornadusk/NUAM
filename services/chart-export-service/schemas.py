from typing import List, Dict, Optional, Literal
from pydantic import BaseModel


class DatasetItem(BaseModel):
    """Dataset individual para un gráfico"""
    label: str
    data: List[float]
    borderColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    tension: Optional[float] = 0.4


class ChartConfig(BaseModel):
    """Configuración completa del gráfico"""
    type: Literal["line", "bar", "radar"] = "line"
    labels: List[str]
    datasets: List[DatasetItem]
    title: Optional[str] = None
    xLabel: Optional[str] = None
    yLabel: Optional[str] = None
    width: Optional[int] = 1200
    height: Optional[int] = 600
    backgroundColor: Optional[str] = "#ffffff"
    showLegend: Optional[bool] = True


class ExportChartRequest(BaseModel):
    """Request para exportar un gráfico como imagen"""
    chartConfig: ChartConfig
    format: Literal["png", "jpg"] = "png"
    quality: Optional[int] = 95  # Para JPG, 1-100


class ChartDataRequest(BaseModel):
    """Request simplificado con datos directos (para compatibilidad con Chart.js)"""
    tipo_grafico: Literal["tipos_cambio", "bolsa"]
    labels: List[str]
    datasets: List[Dict]  # Compatible con formato Chart.js
    formato: Literal["png", "jpg"] = "png"
    titulo: Optional[str] = None
    chart_type: Optional[Literal["line", "bar", "radar"]] = "line"  # Tipo de gráfico

