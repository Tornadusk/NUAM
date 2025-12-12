"""
Alias de compatibilidad hacia atrás para microservicio.exportador
Este módulo re-exporta ExportadorGraficos desde microservicio.utils
para mantener compatibilidad con código existente.
"""
from microservicio.utils import ExportadorGraficos

__all__ = ['ExportadorGraficos']
