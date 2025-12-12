"""
Vistas para Microservicios NUAM
Este módulo importa todas las vistas de los submódulos para mantener compatibilidad hacia atrás
"""
# Importar todas las vistas para compatibilidad
from .graficos import *
from .comprobantes import *
from .tipos_cambio import *
from .pulsar import *
from .testing import *
from .testing import *

__all__ = [
    # Gráficos
    'graficos_dashboard',
    'api_estadisticas_generales',
    'api_calificaciones_por_pais',
    'api_calificaciones_por_moneda',
    'api_actividad_reciente',
    'api_cargas_detalle',
    'api_cargas_por_corredora',
    'api_auditoria_resumen',
    'api_tipos_cambio_resumen',
    'api_kpis_operativos',
    'api_refrescar_grafico',
    'api_exportar_grafico',
    # Comprobantes
    'api_generar_comprobante',
    # Tipos de Cambio
    'tipos_cambio_dashboard',
    'api_tipos_cambio_por_pais',
    'api_tipos_cambio_actuales',
    # Pulsar
    'pulsar_dashboard',
    'api_pulsar_status',
    'api_pulsar_topics',
    'api_pulsar_mensajes_recientes',
    'api_pulsar_publicar_test',
]

