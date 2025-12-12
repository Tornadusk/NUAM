"""
Vistas para Pulsar - Visualización
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from auditoria.models import Auditoria
from microservicio.pulsar import get_pulsar_client, publicar_mensaje


@login_required
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
    API: Obtiene el estado de conexión de Pulsar
    """
    try:
        client = get_pulsar_client()
        pulsar_enabled = settings.PULSAR_ENABLED
        pulsar_url = settings.PULSAR_SERVICE_URL if pulsar_enabled else None
        
        status = {
            'enabled': pulsar_enabled,
            'connected': client is not None,
            'service_url': pulsar_url,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(status)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


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
                    
                    topic_info['mensajes'] = mensajes_count
                    total_mensajes += mensajes_count
                elif response.status_code == 404:
                    topic_info['error'] = 'Topic no existe aún en Pulsar'
                    topic_info['estado'] = 'No existe'
                else:
                    topic_info['error'] = f"HTTP {response.status_code}: {response.text[:100]}"
                    topic_info['estado'] = 'Error'
            except requests.exceptions.ConnectionError:
                topic_info['error'] = 'Pulsar Admin API no disponible (¿está corriendo Pulsar?)'
                topic_info['estado'] = 'Error conexión'
            except requests.exceptions.Timeout:
                topic_info['error'] = 'Timeout al conectar con Pulsar Admin API'
                topic_info['estado'] = 'Timeout'
            except Exception as e:
                topic_info['error'] = f"Error: {str(e)[:100]}"
                topic_info['estado'] = 'Error'
            
            topics_info.append(topic_info)
        
        return Response({
            'topics': topics_info,
            'total_topics': len(topics_info),
            'total_mensajes': total_mensajes,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_pulsar_mensajes_recientes(request):
    """
    API: Obtiene los últimos mensajes publicados en Pulsar (simulado desde auditoría)
    Nota: Pulsar no tiene una API directa para leer mensajes históricos sin consumirlos.
    Esta función simula mensajes recientes basándose en eventos del sistema.
    """
    try:
        # Obtener eventos recientes de auditoría que corresponden a eventos de Pulsar
        ultimas_24h = timezone.now() - timedelta(hours=24)
        
        eventos_pulsar = []
        
        # Buscar eventos relacionados con Pulsar en auditoría
        auditorias = Auditoria.objects.filter(
            creado_en__gte=ultimas_24h
        ).order_by('-creado_en')[:50]
        
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
        
        return Response({
            'mensajes': eventos_pulsar,
            'total': len(eventos_pulsar),
            'periodo': '24 horas',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        import traceback
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

