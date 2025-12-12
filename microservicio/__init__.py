"""
Microservicios NUAM
Módulo que contiene los microservicios del sistema NUAM
"""

# Alias de compatibilidad hacia atrás
# Permite usar: from microservicio.pulsar_client import ...
# en lugar de: from microservicio.pulsar import ...
from .pulsar import (
    get_pulsar_client,
    get_producer,
    publicar_mensaje,
    publicar_tipo_cambio,
    publicar_carga_masiva,
    publicar_actualizacion_graficos,
    publicar_comprobante_generado,
    cerrar_cliente,
)

# Alias para exportador
from .utils import ExportadorGraficos

# Crear módulo alias para compatibilidad hacia atrás
# Esto permite: from microservicio.pulsar_client import ...
import sys
from types import ModuleType

# Crear módulo pulsar_client como alias
pulsar_client_module = ModuleType('microservicio.pulsar_client')
pulsar_client_module.__dict__.update({
    'get_pulsar_client': get_pulsar_client,
    'get_producer': get_producer,
    'publicar_mensaje': publicar_mensaje,
    'publicar_tipo_cambio': publicar_tipo_cambio,
    'publicar_carga_masiva': publicar_carga_masiva,
    'publicar_actualizacion_graficos': publicar_actualizacion_graficos,
    'publicar_comprobante_generado': publicar_comprobante_generado,
    'cerrar_cliente': cerrar_cliente,
})
sys.modules['microservicio.pulsar_client'] = pulsar_client_module

# Crear módulo exportador como alias
exportador_module = ModuleType('microservicio.exportador')
exportador_module.ExportadorGraficos = ExportadorGraficos
sys.modules['microservicio.exportador'] = exportador_module
