from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MicroservicioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'microservicio'
    verbose_name = 'Microservicios NUAM'

    def ready(self):
        """
        Importa las señales cuando Django carga la app
        Opcionalmente intenta obtener tipos de cambio si no hay datos recientes
        Opcionalmente crea los topics de Pulsar si no existen
        """
        import microservicio.signals  # noqa
        
        # Intentar obtener tipos de cambio automáticamente al iniciar (solo si está habilitado)
        if getattr(settings, 'OBTENER_TIPOS_CAMBIO_AUTOMATICO', False):
            self._intentar_obtener_tipos_cambio()
        
        # Crear topics de Pulsar automáticamente si está habilitado
        if getattr(settings, 'CREAR_TOPICS_PULSAR_AUTOMATICO', False):
            self._crear_topics_pulsar()
    
    def _intentar_obtener_tipos_cambio(self):
        """
        Intenta obtener tipos de cambio automáticamente al iniciar Django
        Solo si no hay tipos de cambio recientes (últimas 24 horas)
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from microservicio.models import TipoCambio
            
            # Verificar si hay tipos de cambio recientes (últimas 24 horas)
            hace_24_horas = timezone.now() - timedelta(hours=24)
            tipos_recientes = TipoCambio.objects.filter(
                creado_en__gte=hace_24_horas
            ).exists()
            
            if not tipos_recientes:
                logger.info("No hay tipos de cambio recientes. Intentando obtener automáticamente...")
                # Ejecutar en un thread separado para no bloquear el inicio
                import threading
                thread = threading.Thread(target=self._ejecutar_obtener_tipos_cambio, daemon=True)
                thread.start()
            else:
                logger.debug("Ya hay tipos de cambio recientes. No se obtendrán automáticamente.")
        except Exception as e:
            logger.warning(f"No se pudo verificar tipos de cambio al iniciar: {e}")
    
    def _ejecutar_obtener_tipos_cambio(self):
        """
        Ejecuta el comando de obtener tipos de cambio en un thread separado
        """
        try:
            from django.core.management import call_command
            call_command('obtener_tipos_cambio', verbosity=0)
            logger.info("Tipos de cambio obtenidos automáticamente al iniciar.")
        except Exception as e:
            logger.error(f"Error al obtener tipos de cambio automáticamente: {e}")
    
    def _crear_topics_pulsar(self):
        """
        Crea los topics de Pulsar automáticamente al iniciar Django
        Solo si no existen ya
        """
        try:
            from django.core.management import call_command
            call_command('crear_topics_pulsar', verbosity=0)
            logger.info("Topics de Pulsar verificados/creados automáticamente al iniciar.")
        except Exception as e:
            logger.warning(f"No se pudieron crear topics de Pulsar automáticamente: {e}")


