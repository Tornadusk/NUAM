"""
Management command para crear los topics de Pulsar configurados
Uso: python manage.py crear_topics_pulsar
"""
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from microservicio.pulsar import get_pulsar_client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Crea los topics de Pulsar configurados en PULSAR_TOPICS si no existen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verificar-solo',
            action='store_true',
            help='Solo verifica si los topics existen, no los crea',
        )

    def handle(self, *args, **options):
        verificar_solo = options.get('verificar_solo', False)
        verbosity = options.get('verbosity', 1)
        
        if not settings.PULSAR_ENABLED:
            if verbosity > 0:
                self.stdout.write(
                    self.style.WARNING('Pulsar está deshabilitado en la configuración')
                )
            return
        
        client = get_pulsar_client()
        if not client:
            if verbosity > 0:
                self.stdout.write(
                    self.style.ERROR('No se pudo conectar con Pulsar. Verifica que esté corriendo.')
                )
            return
        
        # Solo mostrar mensajes si verbosity > 0 (modo silencioso cuando se llama desde apps.py)
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS('Conectado a Pulsar'))
            self.stdout.write('=' * 60)
        
        topics_creados = 0
        topics_existentes = 0
        topics_error = 0
        
        for topic_name, topic_path in settings.PULSAR_TOPICS.items():
            if verbosity > 0:
                self.stdout.write(f'\nTopic: {self.style.SUCCESS(topic_name)}')
                self.stdout.write(f'  Path: {topic_path}')
            
            if verificar_solo:
                # Solo verificar existencia
                existe = self._verificar_topic_existe(topic_path)
                if verbosity > 0:
                    if existe:
                        self.stdout.write(self.style.SUCCESS('  [OK] Topic existe'))
                    else:
                        self.stdout.write(self.style.WARNING('  [X] Topic no existe'))
                if existe:
                    topics_existentes += 1
                else:
                    topics_error += 1
            else:
                # Intentar crear el topic publicando un mensaje de inicialización
                resultado = self._crear_topic(client, topic_name, topic_path)
                if verbosity > 0:
                    if resultado == 'creado':
                        self.stdout.write(self.style.SUCCESS('  [OK] Topic creado'))
                    elif resultado == 'existe':
                        self.stdout.write(self.style.SUCCESS('  [OK] Topic ya existe'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  [ERROR] {resultado}'))
                
                if resultado == 'creado':
                    topics_creados += 1
                elif resultado == 'existe':
                    topics_existentes += 1
                else:
                    topics_error += 1
        
        if verbosity > 0:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('Resumen:'))
            if not verificar_solo:
                self.stdout.write(f'  Creados: {topics_creados}')
            self.stdout.write(f'  Existentes: {topics_existentes}')
            if topics_error > 0:
                self.stdout.write(self.style.WARNING(f'  Con errores: {topics_error}'))
            
            if topics_error == 0:
                self.stdout.write(self.style.SUCCESS('\n[OK] Todos los topics están disponibles'))
            else:
                self.stdout.write(self.style.WARNING('\n[ADVERTENCIA] Algunos topics tienen problemas'))
    
    def _verificar_topic_existe(self, topic_path):
        """Verifica si un topic existe usando la API de administración de Pulsar"""
        try:
            import requests
            pulsar_admin_url = getattr(settings, 'PULSAR_ADMIN_URL', 'http://localhost:8080')
            
            # Convertir topic path a formato de API
            if topic_path.startswith('persistent://'):
                topic_api_path = topic_path.replace('persistent://', '')
            else:
                topic_api_path = topic_path
            
            stats_url = f"{pulsar_admin_url}/admin/v2/persistent/{topic_api_path}/stats"
            response = requests.get(stats_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _crear_topic(self, client, topic_name, topic_path):
        """
        Crea un topic publicando un mensaje de inicialización
        En Pulsar standalone, los topics se crean automáticamente al publicar el primer mensaje
        """
        try:
            import pulsar
            import json
            from django.utils import timezone
            
            # Crear un productor temporal para el topic
            producer = client.create_producer(topic_path)
            
            # Publicar un mensaje de inicialización
            mensaje_inicial = {
                'tipo_evento': 'inicializacion_topic',
                'topic': topic_name,
                'timestamp': timezone.now().isoformat(),
                'mensaje': 'Topic creado automáticamente por NUAM'
            }
            
            producer.send(
                json.dumps(mensaje_inicial).encode('utf-8'),
                properties={
                    'source': 'nuam-init',
                    'tipo': 'inicializacion'
                }
            )
            
            # Cerrar el productor temporal
            producer.close()
            
            # Verificar que el topic existe ahora
            if self._verificar_topic_existe(topic_path):
                return 'creado'
            else:
                return 'creado_verificar'  # Creado pero no se puede verificar aún
                
        except pulsar.AlreadyClosedError:
            return 'existe'
        except pulsar.TopicNotFound:
            # En modo standalone, esto no debería pasar, pero intentamos crear
            return 'error_topic_not_found'
        except Exception as e:
            logger.error(f"Error al crear topic {topic_name}: {e}")
            return f'error: {str(e)[:50]}'

