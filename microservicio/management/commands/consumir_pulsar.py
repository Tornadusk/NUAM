"""
Management command para consumir mensajes de Apache Pulsar
Uso: python manage.py consumir_pulsar --topic tipo_cambio
"""
import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from microservicio.pulsar import get_pulsar_client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Consume mensajes de Apache Pulsar para procesar eventos de microservicios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            required=True,
            choices=list(settings.PULSAR_TOPICS.keys()),
            help='Nombre del topic a consumir',
        )
        parser.add_argument(
            '--subscription',
            type=str,
            default='nuam-subscription',
            help='Nombre de la suscripción (default: nuam-subscription)',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=0,
            help='Timeout en milisegundos (0 = sin timeout, consume indefinidamente)',
        )

    def handle(self, *args, **options):
        topic_name = options['topic']
        subscription_name = options['subscription']
        timeout_ms = options['timeout']
        max_redeliver = options['max_redeliver_count']
        
        if not settings.PULSAR_ENABLED:
            self.stdout.write(
                self.style.WARNING('Pulsar está deshabilitado en la configuración')
            )
            return
        
        client = get_pulsar_client()
        if not client:
            self.stdout.write(
                self.style.ERROR('No se pudo conectar con Pulsar')
            )
            return
        
        topic = settings.PULSAR_TOPICS.get(topic_name)
        if not topic:
            self.stdout.write(
                self.style.ERROR(f"Topic '{topic_name}' no está configurado")
            )
            return
        
        try:
            import pulsar
            
            # Configurar Dead Letter Queue
            # Los mensajes que fallan max_redeliver_count veces irán al DLQ
            dead_letter_topic = f"{topic}-dlq"
            dead_letter_policy = pulsar.DeadLetterPolicy(
                max_redeliver_count=max_redeliver,  # Reintentar antes de enviar a DLQ
                dead_letter_topic=dead_letter_topic
            )
            
            # Crear consumidor con balanceo de carga y DLQ
            consumer = client.subscribe(
                topic,
                subscription_name,
                consumer_type=pulsar.ConsumerType.Shared,  # Permite múltiples consumidores (balanceo de carga)
                dead_letter_policy=dead_letter_policy  # Dead Letter Queue para mensajes fallidos
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Consumiendo mensajes del topic: {topic}\n'
                    f'  Suscripción: {subscription_name}\n'
                    f'  Tipo: Shared (balanceo de carga habilitado)\n'
                    f'  Dead Letter Queue: {dead_letter_topic} (max reintentos: 3)\n'
                    f'  Presiona Ctrl+C para detener\n'
                )
            )
            
            # Consumir mensajes
            mensajes_procesados = 0
            try:
                while True:
                    try:
                        # Recibir mensaje con timeout
                        if timeout_ms > 0:
                            msg = consumer.receive(timeout_millis=timeout_ms)
                        else:
                            msg = consumer.receive()
                        
                        if msg:
                            try:
                                # Procesar mensaje
                                self.procesar_mensaje(topic_name, msg)
                                
                                # Confirmar procesamiento exitoso
                                consumer.acknowledge(msg)
                                mensajes_procesados += 1
                            except Exception as e:
                                # Si hay error, el mensaje será reintentado automáticamente
                                # Después de max_redeliver_count reintentos, irá al DLQ
                                logger.error(f'Error al procesar mensaje: {e}')
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'  ⚠ Error al procesar mensaje. '
                                        f'Se reintentará (máx {dead_letter_policy.max_redeliver_count} veces)'
                                    )
                                )
                                # No hacer acknowledge - Pulsar reintentará el mensaje
                                # consumer.negative_acknowledge(msg)  # Opcional: rechazar inmediatamente
                            
                            if mensajes_procesados % 10 == 0:
                                self.stdout.write(
                                    f'  Procesados: {mensajes_procesados} mensajes...'
                                )
                    
                    except pulsar.Timeout:
                        if timeout_ms > 0:
                            self.stdout.write(
                                self.style.WARNING('Timeout alcanzado')
                            )
                            break
                        continue
                    
                    except KeyboardInterrupt:
                        self.stdout.write(
                            self.style.WARNING('\n\nDeteniendo consumidor...')
                        )
                        break
                        
            finally:
                consumer.close()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ Total de mensajes procesados: {mensajes_procesados}'
                    )
                )
                
        except ImportError:
            self.stdout.write(
                self.style.ERROR('pulsar-client no está instalado')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al consumir mensajes: {e}')
            )
            logger.exception("Error en consumidor Pulsar")

    def procesar_mensaje(self, topic_name: str, msg):
        """
        Procesa un mensaje recibido de Pulsar
        """
        try:
            # Decodificar mensaje
            data = msg.data().decode('utf-8')
            mensaje = json.loads(data)
            
            # Obtener propiedades
            propiedades = msg.properties()
            
            self.stdout.write(
                f'\n[{topic_name}] Mensaje recibido:'
            )
            self.stdout.write(f'  Tipo evento: {mensaje.get("tipo_evento", "N/A")}')
            self.stdout.write(f'  Timestamp: {mensaje.get("timestamp", "N/A")}')
            self.stdout.write(f'  Propiedades: {propiedades}')
            
            # Procesar según el tipo de topic
            if topic_name == 'tipo_cambio':
                self.procesar_tipo_cambio(mensaje)
            elif topic_name == 'carga_masiva':
                self.procesar_carga_masiva(mensaje)
            elif topic_name == 'actualizacion_graficos':
                self.procesar_actualizacion_graficos(mensaje)
            else:
                self.stdout.write(
                    self.style.WARNING(f'  No hay procesador específico para {topic_name}')
                )
            
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'  Error al decodificar JSON: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  Error al procesar mensaje: {e}')
            )
            logger.exception("Error al procesar mensaje")

    def procesar_tipo_cambio(self, mensaje: dict):
        """
        Procesa un mensaje de actualización de tipo de cambio
        Aquí se podría actualizar la base de datos o llamar a un servicio externo
        """
        self.stdout.write(
            f'  → Procesando tipo de cambio: '
            f'{mensaje.get("moneda_origen")}/{mensaje.get("moneda_destino")} = {mensaje.get("tasa")}'
        )
        # TODO: Implementar lógica de actualización en BD o llamada a API externa

    def procesar_carga_masiva(self, mensaje: dict):
        """
        Procesa un mensaje de carga masiva para enriquecimiento de datos
        """
        self.stdout.write(
            f'  → Procesando carga masiva: Carga #{mensaje.get("id_carga")}, '
            f'{mensaje.get("filas_total")} filas'
        )
        # TODO: Implementar lógica de enriquecimiento de datos

    def procesar_actualizacion_graficos(self, mensaje: dict):
        """
        Procesa un mensaje de actualización de gráficos
        """
        tipo_grafico = mensaje.get("tipo_grafico", "N/A")
        self.stdout.write(
            f'  → Actualización de gráfico: {tipo_grafico}'
        )
        # TODO: Implementar lógica de actualización de caché o notificación a clientes

