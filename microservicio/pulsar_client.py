"""
Cliente Apache Pulsar para Microservicios NUAM
Maneja la conexión, publicación y consumo de mensajes desde Django
"""
import json
import logging
from typing import Optional, Dict, Any, Callable
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Inicializar cliente Pulsar solo si está habilitado
_pulsar_client = None
_pulsar_producers = {}
_pulsar_consumers = {}


def get_pulsar_client():
    """
    Obtiene o crea una instancia del cliente Pulsar (singleton)
    """
    global _pulsar_client
    
    if not settings.PULSAR_ENABLED:
        logger.warning("Pulsar está deshabilitado en la configuración")
        return None
    
    if _pulsar_client is None:
        try:
            import pulsar
            _pulsar_client = pulsar.Client(
                settings.PULSAR_SERVICE_URL,
                operation_timeout_seconds=settings.PULSAR_OPERATION_TIMEOUT
            )
            logger.info(f"Cliente Pulsar conectado a {settings.PULSAR_SERVICE_URL}")
        except ImportError:
            logger.error("pulsar-client no está instalado. Ejecuta: pip install pulsar-client")
            return None
        except Exception as e:
            logger.error(f"Error al conectar con Pulsar: {e}")
            return None
    
    return _pulsar_client


def get_producer(topic_name: str):
    """
    Obtiene o crea un productor para un topic específico
    """
    global _pulsar_producers
    
    client = get_pulsar_client()
    if not client:
        return None
    
    if topic_name not in _pulsar_producers:
        try:
            import pulsar
            topic = settings.PULSAR_TOPICS.get(topic_name)
            if not topic:
                logger.error(f"Topic '{topic_name}' no está configurado en PULSAR_TOPICS")
                return None
            
            _pulsar_producers[topic_name] = client.create_producer(topic)
            logger.info(f"Productor creado para topic: {topic}")
        except Exception as e:
            logger.error(f"Error al crear productor para {topic_name}: {e}")
            return None
    
    return _pulsar_producers[topic_name]


def publicar_mensaje(topic_name: str, mensaje: Dict[str, Any], propiedades: Optional[Dict[str, str]] = None) -> bool:
    """
    Publica un mensaje en un topic de Pulsar
    
    Args:
        topic_name: Nombre del topic (clave en PULSAR_TOPICS)
        mensaje: Diccionario con los datos del mensaje (se serializa a JSON)
        propiedades: Diccionario opcional con propiedades/metadatos del mensaje
    
    Returns:
        True si se publicó correctamente, False en caso contrario
    """
    if not settings.PULSAR_ENABLED:
        logger.warning(f"Pulsar deshabilitado. Mensaje no publicado en {topic_name}")
        return False
    
    producer = get_producer(topic_name)
    if not producer:
        logger.error(f"No se pudo obtener productor para {topic_name}")
        return False
    
    try:
        # Serializar mensaje a JSON
        mensaje_json = json.dumps(mensaje, default=str)  # default=str para manejar datetime
        
        # Crear propiedades por defecto
        props = propiedades or {}
        props['timestamp'] = timezone.now().isoformat()
        props['source'] = 'nuam-django'
        
        # Publicar mensaje
        producer.send(
            mensaje_json.encode('utf-8'),
            properties=props
        )
        
        logger.info(f"Mensaje publicado en {topic_name}: {len(mensaje_json)} bytes")
        return True
        
    except Exception as e:
        logger.error(f"Error al publicar mensaje en {topic_name}: {e}")
        return False


def publicar_tipo_cambio(id_fuente: int, moneda_origen: str, moneda_destino: str, 
                         tasa: float, fecha: str) -> bool:
    """
    Publica un evento de actualización de tipo de cambio
    
    Args:
        id_fuente: ID de la fuente de tipo de cambio
        moneda_origen: Código ISO de moneda origen (ej: USD)
        moneda_destino: Código ISO de moneda destino (ej: CLP)
        tasa: Tasa de cambio
        fecha: Fecha del tipo de cambio (formato ISO o YYYY-MM-DD)
    
    Returns:
        True si se publicó correctamente
    """
    mensaje = {
        'tipo_evento': 'actualizacion_tipo_cambio',
        'id_fuente': id_fuente,
        'moneda_origen': moneda_origen,
        'moneda_destino': moneda_destino,
        'tasa': float(tasa),
        'fecha': fecha,
        'timestamp': timezone.now().isoformat(),
    }
    
    propiedades = {
        'evento': 'tipo_cambio',
        'moneda_origen': moneda_origen,
        'moneda_destino': moneda_destino,
    }
    
    return publicar_mensaje('tipo_cambio', mensaje, propiedades)


def publicar_carga_masiva(id_carga: int, tipo: str, nombre_archivo: str, 
                          filas_total: int, usuario_id: Optional[int] = None) -> bool:
    """
    Publica un evento de inicio de carga masiva para enriquecimiento de datos
    
    Args:
        id_carga: ID de la carga
        tipo: Tipo de carga ('manual' o 'masiva')
        nombre_archivo: Nombre del archivo cargado
        filas_total: Número total de filas a procesar
        usuario_id: ID del usuario que realizó la carga (opcional)
    
    Returns:
        True si se publicó correctamente
    """
    mensaje = {
        'tipo_evento': 'inicio_carga_masiva',
        'id_carga': id_carga,
        'tipo': tipo,
        'nombre_archivo': nombre_archivo,
        'filas_total': filas_total,
        'usuario_id': usuario_id,
        'timestamp': timezone.now().isoformat(),
    }
    
    propiedades = {
        'evento': 'carga_masiva',
        'tipo': tipo,
    }
    
    return publicar_mensaje('carga_masiva', mensaje, propiedades)


def publicar_actualizacion_graficos(tipo_grafico: str, datos: Dict[str, Any]) -> bool:
    """
    Publica un evento de actualización de gráficos para refrescar dashboards
    
    Args:
        tipo_grafico: Tipo de gráfico actualizado (ej: 'calificaciones_por_pais', 'estadisticas_generales')
        datos: Datos del gráfico actualizado
    
    Returns:
        True si se publicó correctamente
    """
    mensaje = {
        'tipo_evento': 'actualizacion_grafico',
        'tipo_grafico': tipo_grafico,
        'datos': datos,
        'timestamp': timezone.now().isoformat(),
    }
    
    propiedades = {
        'evento': 'actualizacion_graficos',
        'tipo_grafico': tipo_grafico,
    }
    
    return publicar_mensaje('actualizacion_graficos', mensaje, propiedades)


def publicar_comprobante_generado(calificacion_id: Optional[int], usuario: str, 
                                   monto_impuesto: float, estado: str = 'generado') -> bool:
    """
    Publica un evento cuando se genera un comprobante tributario
    
    Args:
        calificacion_id: ID de la calificación asociada (opcional)
        usuario: Usuario que generó el comprobante
        monto_impuesto: Monto del impuesto calculado
        estado: Estado del comprobante ('generado', 'error', etc.)
    
    Returns:
        True si se publicó correctamente
    """
    mensaje = {
        'tipo_evento': 'comprobante_generado',
        'calificacion_id': calificacion_id,
        'usuario': usuario,
        'monto_impuesto': float(monto_impuesto),
        'estado': estado,
        'timestamp': timezone.now().isoformat(),
    }
    
    propiedades = {
        'evento': 'comprobante_generado',
        'usuario': usuario,
        'estado': estado,
    }
    
    return publicar_mensaje('comprobante_generado', mensaje, propiedades)


def cerrar_cliente():
    """
    Cierra todas las conexiones de Pulsar
    Útil para cleanup al cerrar la aplicación
    """
    global _pulsar_client, _pulsar_producers, _pulsar_consumers
    
    # Cerrar productores
    for topic, producer in _pulsar_producers.items():
        try:
            producer.close()
            logger.info(f"Productor cerrado para {topic}")
        except Exception as e:
            logger.error(f"Error al cerrar productor {topic}: {e}")
    _pulsar_producers.clear()
    
    # Cerrar consumidores
    for topic, consumer in _pulsar_consumers.items():
        try:
            consumer.close()
            logger.info(f"Consumidor cerrado para {topic}")
        except Exception as e:
            logger.error(f"Error al cerrar consumidor {topic}: {e}")
    _pulsar_consumers.clear()
    
    # Cerrar cliente
    if _pulsar_client:
        try:
            _pulsar_client.close()
            logger.info("Cliente Pulsar cerrado")
        except Exception as e:
            logger.error(f"Error al cerrar cliente Pulsar: {e}")
        _pulsar_client = None

