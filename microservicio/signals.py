"""
Señales Django para publicar eventos en Apache Pulsar
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from microservicio.models import TipoCambio
from cargas.models import Carga
from calificaciones.models import Calificacion
from microservicio.pulsar import (
    publicar_tipo_cambio,
    publicar_carga_masiva,
    publicar_actualizacion_graficos
)


@receiver(post_save, sender=TipoCambio)
def publicar_tipo_cambio_en_pulsar(sender, instance, created, **kwargs):
    """
    Publica un mensaje en Pulsar cuando se guarda un TipoCambio
    """
    if created:  # Solo publicar cuando se crea, no cuando se actualiza
        try:
            fecha_str = instance.fecha.strftime('%Y-%m-%d') if instance.fecha else None
            publicar_tipo_cambio(
                id_fuente=instance.id_fuente.id_fuente,
                moneda_origen=instance.moneda_origen,
                moneda_destino=instance.moneda_destino,
                tasa=float(instance.tasa),
                fecha=fecha_str
            )
        except Exception as e:
            # No interrumpir el guardado si falla Pulsar
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al publicar tipo de cambio en Pulsar: {e}")


@receiver(post_save, sender=Carga)
def publicar_carga_masiva_en_pulsar(sender, instance, created, **kwargs):
    """
    Publica un mensaje en Pulsar cuando se crea una carga masiva
    """
    if created and instance.tipo == 'masiva':
        try:
            usuario_id = instance.creado_por.id_usuario if instance.creado_por else None
            publicar_carga_masiva(
                id_carga=instance.id_carga,
                tipo=instance.tipo,
                nombre_archivo=instance.nombre_archivo or 'Sin archivo',
                filas_total=instance.filas_total,
                usuario_id=usuario_id
            )
        except Exception as e:
            # No interrumpir el guardado si falla Pulsar
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al publicar carga masiva en Pulsar: {e}")


@receiver(post_save, sender=Calificacion)
def publicar_actualizacion_calificacion_en_pulsar(sender, instance, created, **kwargs):
    """
    Publica un mensaje en Pulsar cuando se crea o actualiza una Calificacion
    Esto permite actualizar gráficos en tiempo real
    """
    try:
        from microservicio.pulsar import publicar_actualizacion_graficos
        
        tipo_evento = 'nueva_calificacion' if created else 'calificacion_actualizada'
        datos = {
            'id_calificacion': instance.id_calificacion,
            'estado': instance.estado,
            'id_corredora': instance.id_corredora.id_corredora if instance.id_corredora else None,
        }
        
        # Publicar evento para actualizar gráficos relacionados
        publicar_actualizacion_graficos(
            tipo_grafico='calificaciones',
            datos=datos
        )
    except Exception as e:
        # No interrumpir el guardado si falla Pulsar
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al publicar actualización de calificación en Pulsar: {e}")


@receiver(post_save, sender=Carga)
def publicar_actualizacion_carga_en_pulsar(sender, instance, created, **kwargs):
    """
    Publica un mensaje en Pulsar cuando se actualiza el estado de una Carga
    Permite actualizar gráficos de cargas en tiempo real
    """
    if not created:  # Solo publicar actualizaciones de estado, no creación (ya se maneja arriba)
        try:
            from microservicio.pulsar import publicar_actualizacion_graficos
            
            datos = {
                'id_carga': instance.id_carga,
                'estado': instance.estado,
                'insertados': instance.insertados,
                'actualizados': instance.actualizados,
                'rechazados': instance.rechazados,
                'filas_total': instance.filas_total,
            }
            
            # Publicar evento para actualizar gráficos de cargas
            publicar_actualizacion_graficos(
                tipo_grafico='cargas',
                datos=datos
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al publicar actualización de carga en Pulsar: {e}")


# Nota: Para actualizaciones de gráficos, se puede llamar manualmente desde las vistas
# cuando se actualizan estadísticas o calificaciones, o usar señales adicionales si es necesario

