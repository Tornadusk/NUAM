"""
Vistas para Pulsar - Visualización
"""
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from auditoria.models import Auditoria
from microservicio.pulsar import get_pulsar_client, publicar_mensaje
from .helpers import admin_required

logger = logging.getLogger(__name__)


@login_required
@admin_required
def pulsar_dashboard(request):
    """
    Vista principal para el dashboard de visualización de Pulsar
    Muestra información sobre topics, mensajes y estadísticas en tiempo real
    """
    return render(request, 'microservicio/pulsar/dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_pulsar_status(request):
    """
    API: Obtiene el estado de conexión de Pulsar y Admin API
    """
    try:
        client = get_pulsar_client()
        pulsar_enabled = settings.PULSAR_ENABLED
        pulsar_url = settings.PULSAR_SERVICE_URL if pulsar_enabled else None
        pulsar_admin_url = getattr(settings, 'PULSAR_ADMIN_URL', 'http://localhost:8080')
        
        # Verificar estado de Admin API
        admin_disponible, admin_mensaje, admin_detalles = _verificar_pulsar_admin_api(pulsar_admin_url)
        
        status = {
            'enabled': pulsar_enabled,
            'connected': client is not None,
            'service_url': pulsar_url,
            'admin_api_url': pulsar_admin_url,
            'admin_api_disponible': admin_disponible,
            'admin_api_mensaje': admin_mensaje if not admin_disponible else None,
            'admin_api_detalles': admin_detalles if not admin_disponible else None,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(status)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def _verificar_pulsar_admin_api(pulsar_admin_url):
    """
    Verifica si Pulsar Admin API está disponible
    Retorna: (disponible: bool, mensaje: str, detalles: dict)
    """
    try:
        health_url = f"{pulsar_admin_url}/admin/v2/brokers/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            return True, "Admin API disponible", {'status_code': 200}
        else:
            return False, f"Admin API respondió con código {response.status_code}", {'status_code': response.status_code}
    except requests.exceptions.ConnectionError:
        # Verificar si el contenedor está corriendo
        import subprocess
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'name=nuam-pulsar', '--format', '{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=2
            )
            container_status = result.stdout.strip()
            if container_status:
                if 'Up' in container_status:
                    return False, "Contenedor corriendo pero Admin API no responde (puede estar iniciando)", {'container_status': container_status}
                elif 'Exited' in container_status:
                    return False, "Contenedor detenido. Ejecuta: docker-compose up -d", {'container_status': container_status}
                else:
                    return False, f"Contenedor en estado: {container_status}", {'container_status': container_status}
            else:
                return False, "Pulsar no está corriendo. Ejecuta: docker-compose up -d", {}
        except Exception as e:
            logger.debug(f"No se pudo verificar estado de Docker: {e}")
            return False, f"No se puede conectar a {pulsar_admin_url}. Verifica que Pulsar esté corriendo", {}
    except requests.exceptions.Timeout:
        return False, "Timeout al conectar con Admin API (puede estar iniciando)", {}
    except Exception as e:
        return False, f"Error al verificar Admin API: {str(e)[:100]}", {}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_pulsar_topics(request):
    """
    API: Obtiene información sobre los topics configurados en Pulsar
    """
    try:
        topics_info = []
        pulsar_admin_url = getattr(settings, 'PULSAR_ADMIN_URL', 'http://localhost:8080')
        total_mensajes = 0
        
        # Verificar primero si Admin API está disponible
        admin_disponible, admin_mensaje, admin_detalles = _verificar_pulsar_admin_api(pulsar_admin_url)
        if not admin_disponible:
            # Si Admin API no está disponible, retornar error informativo pero no crítico
            logger.warning(f"Pulsar Admin API no disponible: {admin_mensaje}")
            # Continuar con los topics pero marcando el problema
        
        # Obtener información de cada topic configurado
        for topic_name, topic_path in settings.PULSAR_TOPICS.items():
            topic_info = {
                'nombre': topic_name,
                'path': topic_path,
                'estadisticas': None,
                'mensajes': 0,
                'estado': 'Desconocido',
                'error': None
            }
            
            # Intentar obtener estadísticas del topic desde la API de administración de Pulsar
            try:
                # Convertir topic path a formato de API
                # persistent://public/default/nuam-tipo-cambio -> public/default/nuam-tipo-cambio
                if topic_path.startswith('persistent://'):
                    topic_api_path = topic_path.replace('persistent://', '')
                else:
                    topic_api_path = topic_path
                
                stats_url = f"{pulsar_admin_url}/admin/v2/persistent/{topic_api_path}/stats"
                
                response = requests.get(stats_url, timeout=5)
                if response.status_code == 200:
                    stats = response.json()
                    topic_info['estadisticas'] = stats
                    topic_info['estado'] = 'Activo'
                    
                    # Obtener número de mensajes desde las estadísticas
                    # Las estadísticas pueden tener diferentes estructuras según la versión de Pulsar
                    mensajes_count = 0
                    if 'msgInCounter' in stats:
                        mensajes_count = stats.get('msgInCounter', 0)
                    elif 'count' in stats:
                        mensajes_count = stats.get('count', 0)
                    elif 'storageSize' in stats and 'msgRateIn' in stats:
                        # Si no hay contador directo, usar msgRateIn como aproximación
                        mensajes_count = stats.get('msgRateIn', {}).get('count', 0)
                    # Intentar desde subscriptions si está disponible
                    elif 'subscriptions' in stats and stats['subscriptions']:
                        # Sumar mensajes de todas las suscripciones
                        for sub_name, sub_data in stats['subscriptions'].items():
                            if 'msgOutCounter' in sub_data:
                                mensajes_count += sub_data.get('msgOutCounter', 0)
                    
                    topic_info['mensajes'] = mensajes_count
                    total_mensajes += mensajes_count
                elif response.status_code == 404:
                    # Si el topic no existe en stats, intentar crearlo automáticamente
                    # En Pulsar standalone, los topics se crean al publicar el primer mensaje
                    try:
                        from microservicio.pulsar import get_pulsar_client
                        client = get_pulsar_client()
                        if client:
                            import pulsar
                            try:
                                # Crear un productor temporal - esto creará el topic si no existe
                                temp_producer = client.create_producer(topic_path)
                                # Publicar un mensaje de inicialización para asegurar que el topic se crea
                                mensaje_init = json.dumps({
                                    'tipo': 'inicializacion',
                                    'timestamp': timezone.now().isoformat(),
                                    'mensaje': 'Topic creado automáticamente desde dashboard'
                                })
                                temp_producer.send(mensaje_init.encode('utf-8'), properties={'source': 'nuam-dashboard-init'})
                                temp_producer.close()
                                # El topic ahora debería existir, marcar como activo
                                topic_info['estado'] = 'Activo (creado automáticamente)'
                                topic_info['mensajes'] = 1  # El mensaje de inicialización
                                total_mensajes += 1
                            except Exception as prod_error:
                                # Si falla crear el productor, el topic realmente no existe o hay un problema
                                logger.warning(f"No se pudo crear topic {topic_name}: {prod_error}")
                                topic_info['error'] = 'Topic no existe y no se pudo crear automáticamente'
                                topic_info['estado'] = 'Error al crear'
                        else:
                            topic_info['error'] = 'No se pudo conectar con Pulsar para crear topic'
                            topic_info['estado'] = 'Error conexión'
                    except Exception as e:
                        logger.warning(f"Error al intentar crear topic {topic_name}: {e}")
                        topic_info['error'] = 'Topic no existe aún en Pulsar'
                        topic_info['estado'] = 'No existe'
                else:
                    topic_info['error'] = f"HTTP {response.status_code}: {response.text[:100]}"
                    topic_info['estado'] = 'Error'
            except requests.exceptions.ConnectionError as e:
                # Verificar si el contenedor está corriendo para dar un mensaje más útil
                import subprocess
                error_msg = f'Pulsar Admin API no disponible en {pulsar_admin_url}'
                try:
                    result = subprocess.run(
                        ['docker', 'ps', '-a', '--filter', 'name=nuam-pulsar', '--format', '{{.Status}}'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    container_status = result.stdout.strip()
                    if container_status:
                        if 'Up' in container_status:
                            # Contenedor está corriendo pero Admin API no responde
                            # Puede estar iniciando o tener problemas
                            error_msg = f'Pulsar Admin API no responde (contenedor corriendo). Puede estar iniciando. Espera 30-60 segundos o verifica: docker logs nuam-pulsar'
                        elif 'Exited' in container_status:
                            error_msg = 'Pulsar se detuvo. Ejecuta: docker-compose up -d (o scripts/restart_pulsar.ps1)'
                        else:
                            error_msg = f'Pulsar contenedor en estado: {container_status}. Ejecuta: docker-compose up -d'
                    else:
                        error_msg = 'Pulsar no está corriendo. Ejecuta: docker-compose up -d'
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as check_error:
                    # Si no se puede verificar Docker (no está instalado o no accesible), dar mensaje genérico
                    logger.debug(f"No se pudo verificar estado de Docker: {check_error}")
                    error_msg = f'Pulsar Admin API no disponible. Verifica que Pulsar esté corriendo en {pulsar_admin_url}'
                
                topic_info['error'] = error_msg
                topic_info['estado'] = 'Error conexión'
                logger.warning(f"Error de conexión con Pulsar Admin API para topic {topic_name}: {error_msg}")
            except requests.exceptions.Timeout:
                topic_info['error'] = 'Timeout al conectar con Pulsar Admin API (puede estar iniciando, espera 30-60 segundos)'
                topic_info['estado'] = 'Timeout'
            except Exception as e:
                topic_info['error'] = f"Error: {str(e)[:100]}"
                topic_info['estado'] = 'Error'
            
            topics_info.append(topic_info)
        
        # Verificar estado final de Admin API para incluir en la respuesta
        admin_disponible, admin_mensaje, admin_detalles = _verificar_pulsar_admin_api(pulsar_admin_url)
        
        return Response({
            'topics': topics_info,
            'total_topics': len(topics_info),
            'total_mensajes': total_mensajes,
            'admin_url': pulsar_admin_url,
            'admin_api_disponible': admin_disponible,
            'admin_api_mensaje': admin_mensaje if not admin_disponible else None,
            'admin_api_detalles': admin_detalles if not admin_disponible else None,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_pulsar_mensajes_recientes(request):
    """
    API: Obtiene los últimos mensajes publicados en Pulsar
    Nota: Pulsar no tiene una API directa para leer mensajes históricos sin consumirlos.
    Esta función obtiene mensajes recientes desde:
    1. Eventos de auditoría relacionados con Pulsar
    2. Cargas masivas recientes (directamente de la tabla Carga)
    3. Tipos de cambio recientes (directamente de la tabla TipoCambio)
    """
    try:
        from cargas.models import Carga
        from microservicio.models import TipoCambio
        
        # Obtener eventos recientes de las últimas 24 horas
        ultimas_24h = timezone.now() - timedelta(hours=24)
        
        eventos_pulsar = []
        
        # 1. Buscar eventos relacionados con Pulsar en auditoría
        auditorias = Auditoria.objects.filter(
            creado_en__gte=ultimas_24h
        ).order_by('-creado_en')[:30]
        
        for audit in auditorias:
            # Mapear eventos de auditoría a eventos de Pulsar
            tipo_evento = None
            if audit.entidad == 'CALIFICACION':
                tipo_evento = 'actualizacion_grafico'
            elif audit.entidad == 'CARGA':
                tipo_evento = 'carga_masiva'
            elif audit.entidad == 'TIPOCAMBIO':
                tipo_evento = 'tipo_cambio'
            
            if tipo_evento:
                eventos_pulsar.append({
                    'tipo_evento': tipo_evento,
                    'entidad': audit.entidad,
                    'entidad_id': audit.entidad_id,
                    'accion': audit.accion,
                    'usuario': audit.actor_id.username if audit.actor_id else 'Sistema',
                    'timestamp': audit.creado_en.isoformat(),
                    'fuente': audit.fuente or 'Django'
                })
        
        # 2. Buscar cargas masivas recientes directamente de la tabla Carga
        cargas_recientes = Carga.objects.filter(
            creado_en__gte=ultimas_24h,
            tipo='masiva'
        ).order_by('-creado_en')[:20]
        
        for carga in cargas_recientes:
            # Verificar si ya no está en eventos_pulsar (evitar duplicados)
            ya_existe = any(
                e.get('tipo_evento') == 'carga_masiva' and 
                e.get('entidad_id') == carga.id_carga
                for e in eventos_pulsar
            )
            
            if not ya_existe:
                eventos_pulsar.append({
                    'tipo_evento': 'carga_masiva',
                    'entidad': 'CARGA',
                    'entidad_id': carga.id_carga,
                    'accion': 'CREAR',
                    'usuario': carga.creado_por.username if carga.creado_por else 'Sistema',
                    'timestamp': carga.creado_en.isoformat(),
                    'fuente': 'Pulsar',
                    'detalles': {
                        'nombre_archivo': carga.nombre_archivo,
                        'filas_total': carga.filas_total,
                        'estado': carga.estado
                    }
                })
        
        # 3. Buscar tipos de cambio recientes directamente de la tabla TipoCambio
        tipos_cambio_recientes = TipoCambio.objects.filter(
            creado_en__gte=ultimas_24h
        ).order_by('-creado_en')[:20]
        
        for tipo_cambio in tipos_cambio_recientes:
            # Verificar si ya no está en eventos_pulsar (evitar duplicados)
            ya_existe = any(
                e.get('tipo_evento') == 'tipo_cambio' and 
                e.get('entidad_id') == tipo_cambio.id_tipo_cambio
                for e in eventos_pulsar
            )
            
            if not ya_existe:
                eventos_pulsar.append({
                    'tipo_evento': 'tipo_cambio',
                    'entidad': 'TIPOCAMBIO',
                    'entidad_id': tipo_cambio.id_tipo_cambio,
                    'accion': 'CREAR',
                    'usuario': 'Sistema',
                    'timestamp': tipo_cambio.creado_en.isoformat(),
                    'fuente': tipo_cambio.id_fuente.nombre if tipo_cambio.id_fuente else 'API Externa',
                    'detalles': {
                        'par': f"{tipo_cambio.moneda_origen}/{tipo_cambio.moneda_destino}",
                        'tasa': float(tipo_cambio.tasa),
                        'fecha': tipo_cambio.fecha.strftime('%Y-%m-%d') if tipo_cambio.fecha else None
                    }
                })
        
        # Ordenar todos los eventos por timestamp (más recientes primero)
        eventos_pulsar.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limitar a los 50 más recientes
        eventos_pulsar = eventos_pulsar[:50]
        
        return Response({
            'mensajes': eventos_pulsar,
            'total': len(eventos_pulsar),
            'periodo': '24 horas',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        import traceback
        logger.error(f"Error al obtener mensajes recientes de Pulsar: {e}\n{traceback.format_exc()}")
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_pulsar_publicar_test(request):
    """
    API: Publica un mensaje de prueba en un topic de Pulsar
    """
    try:
        topic_name = request.data.get('topic', 'tipo_cambio')
        mensaje = request.data.get('mensaje', {'test': True, 'timestamp': timezone.now().isoformat()})
        
        resultado = publicar_mensaje(topic_name, mensaje, {'test': 'true', 'usuario': request.user.username})
        
        return Response({
            'exito': resultado,
            'topic': topic_name,
            'mensaje': mensaje,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

