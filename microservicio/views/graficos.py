"""
Vistas para Microservicios NUAM
Microservicio de Gráficos/Métricas: Expone datos agregados de la BD para visualización
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Max, Min, Q, F
from django.db.models.functions import Extract
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests

# Importar modelos
from calificaciones.models import Calificacion, FactorDef
from corredoras.models import Corredora, UsuarioCorredora
from instrumentos.models import Instrumento
from cargas.models import Carga, CargaDetalle
from core.models import Pais, Moneda
from usuarios.models import Usuario
from auditoria.models import Auditoria
from microservicio.models import TipoCambio
from microservicio.pulsar import publicar_actualizacion_graficos
from .helpers import obtener_corredora_usuario


@login_required
def graficos_dashboard(request):
    """
    Vista principal para el dashboard de gráficos
    """
    return render(request, 'microservicio/graficos/dashboard.html')


# Funciones auxiliares para obtener datos (reutilizables por API y exportación)
def _obtener_estadisticas_generales(user, usuario_obj):
    """Función auxiliar para obtener estadísticas generales"""
    calificaciones_qs = Calificacion.objects.all()
    corredora_usuario = obtener_corredora_usuario(usuario_obj)
    # Verificar si el usuario es staff de forma segura
    is_staff = getattr(user, 'is_staff', False)
    if corredora_usuario and not is_staff:
        calificaciones_qs = calificaciones_qs.filter(id_corredora=corredora_usuario)
    
    total_calificaciones = calificaciones_qs.count()
    calificaciones_por_estado = calificaciones_qs.values('estado').annotate(
        total=Count('id_calificacion')
    ).order_by('estado')
    
    total_corredoras = Corredora.objects.filter(estado='activa').count()
    total_instrumentos = Instrumento.objects.count()
    total_cargas = Carga.objects.count()
    cargas_completadas = Carga.objects.filter(estado='done').count()
    cargas_actuales = Carga.objects.filter(
        estado__in=['validando', 'importando', 'reconciliando']
    ).count()
    cargas_fallidas = Carga.objects.filter(estado='failed').count()
    
    calificaciones_por_corredora = calificaciones_qs.values(
        'id_corredora__nombre'
    ).annotate(
        total=Count('id_calificacion')
    ).order_by('-total')[:5]
    
    calificaciones_por_instrumento = calificaciones_qs.values(
        'id_instrumento__codigo', 'id_instrumento__nombre'
    ).annotate(
        total=Count('id_calificacion')
    ).order_by('-total')[:5]
    
    doce_meses_atras = timezone.now() - timedelta(days=365)
    calificaciones_por_mes = calificaciones_qs.filter(
        creado_en__gte=doce_meses_atras
    ).annotate(
        año=Extract('creado_en', 'year'),
        mes=Extract('creado_en', 'month')
    ).values('año', 'mes').annotate(
        total=Count('id_calificacion')
    ).order_by('año', 'mes')
    
    cargas_por_estado = Carga.objects.values('estado').annotate(
        total=Count('id_carga')
    ).order_by('estado')
    
    return {
        'estadisticas_generales': {
            'total_calificaciones': total_calificaciones,
            'total_corredoras': total_corredoras,
            'total_instrumentos': total_instrumentos,
            'total_cargas': total_cargas,
            'cargas_completadas': cargas_completadas,
            'cargas_actuales': cargas_actuales,
            'cargas_fallidas': cargas_fallidas,
        },
        'calificaciones_por_estado': list(calificaciones_por_estado),
        'calificaciones_por_corredora': list(calificaciones_por_corredora),
        'calificaciones_por_instrumento': [
            {
                'codigo': item['id_instrumento__codigo'],
                'nombre': item['id_instrumento__nombre'],
                'total': item['total']
            }
            for item in calificaciones_por_instrumento
        ],
        'calificaciones_por_mes': list(calificaciones_por_mes),
        'cargas_por_estado': list(cargas_por_estado),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_estadisticas_generales(request):
    """
    API: Estadísticas generales del sistema
    Endpoint: /api/microservicio/estadisticas-generales/
    """
    try:
        user = request.user
        usuario_obj = Usuario.objects.filter(username=user.username).first()
        datos = _obtener_estadisticas_generales(user, usuario_obj)
        return Response(datos)
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_calificaciones_por_pais(request):
    """
    API: Calificaciones agrupadas por país
    Endpoint: /api/microservicio/calificaciones-por-pais/
    """
    try:
        user = request.user
        usuario_obj = Usuario.objects.filter(username=user.username).first()
        
        calificaciones_qs = Calificacion.objects.select_related(
            'id_corredora__id_pais'
        )
        
        corredora_usuario = obtener_corredora_usuario(usuario_obj)
        is_staff = getattr(user, 'is_staff', False)
        if corredora_usuario and not is_staff:
            calificaciones_qs = calificaciones_qs.filter(id_corredora=corredora_usuario)
        
        calificaciones_por_pais = calificaciones_qs.values(
            'id_corredora__id_pais__codigo',
            'id_corredora__id_pais__nombre'
        ).annotate(
            total=Count('id_calificacion')
        ).order_by('-total')
        
        return Response({
            'calificaciones_por_pais': [
                {
                    'codigo': item['id_corredora__id_pais__codigo'],
                    'nombre': item['id_corredora__id_pais__nombre'],
                    'total': item['total']
                }
                for item in calificaciones_por_pais
            ]
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_calificaciones_por_moneda(request):
    """
    API: Calificaciones agrupadas por moneda
    Endpoint: /api/microservicio/calificaciones-por-moneda/
    """
    try:
        user = request.user
        usuario_obj = Usuario.objects.filter(username=user.username).first()
        
        calificaciones_qs = Calificacion.objects.select_related('id_moneda')
        
        corredora_usuario = obtener_corredora_usuario(usuario_obj)
        is_staff = getattr(user, 'is_staff', False)
        if corredora_usuario and not is_staff:
            calificaciones_qs = calificaciones_qs.filter(id_corredora=corredora_usuario)
        
        calificaciones_por_moneda = calificaciones_qs.values(
            'id_moneda__codigo',
            'id_moneda__nombre'
        ).annotate(
            total=Count('id_calificacion'),
            monto_total=Sum('valor_historico')
        ).order_by('-total')
        
        return Response({
            'calificaciones_por_moneda': [
                {
                    'codigo': item['id_moneda__codigo'],
                    'nombre': item['id_moneda__nombre'],
                    'total': item['total'],
                    'monto_total': float(item['monto_total'] or 0)
                }
                for item in calificaciones_por_moneda
            ]
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_actividad_reciente(request):
    """
    API: Actividad reciente del sistema (últimas 30 días)
    Endpoint: /api/microservicio/actividad-reciente/
    """
    try:
        treinta_dias_atras = timezone.now() - timedelta(days=30)
        
        # Calificaciones creadas
        calificaciones_recientes = Calificacion.objects.filter(
            creado_en__gte=treinta_dias_atras
        ).count()
        
        # Cargas realizadas
        cargas_recientes = Carga.objects.filter(
            creado_en__gte=treinta_dias_atras
        ).count()
        
        # Cargas exitosas vs fallidas
        cargas_exitosas = Carga.objects.filter(
            creado_en__gte=treinta_dias_atras,
            estado='done'
        ).count()
        
        cargas_fallidas = Carga.objects.filter(
            creado_en__gte=treinta_dias_atras,
            estado='failed'
        ).count()
        
        return Response({
            'periodo_dias': 30,
            'calificaciones_creadas': calificaciones_recientes,
            'cargas_realizadas': cargas_recientes,
            'cargas_exitosas': cargas_exitosas,
            'cargas_fallidas': cargas_fallidas,
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_cargas_detalle(request):
    """
    API: Estadísticas detalladas de cargas
    Endpoint: /api/microservicio/cargas-detalle/
    Incluye: cargas por tipo, progreso (insertados/actualizados/rechazados), cargas actuales
    """
    try:
        user = request.user
        usuario_obj = Usuario.objects.filter(username=user.username).first()
        
        # Filtros según rol
        cargas_qs = Carga.objects.all()
        corredora_usuario = obtener_corredora_usuario(usuario_obj)
        is_staff = getattr(user, 'is_staff', False)
        if corredora_usuario and not is_staff:
            cargas_qs = cargas_qs.filter(id_corredora=corredora_usuario)
        
        # Cargas por tipo (manual vs masiva)
        cargas_por_tipo = cargas_qs.values('tipo').annotate(
            total=Count('id_carga')
        ).order_by('tipo')
        
        # Cargas actuales (en proceso)
        cargas_actuales = cargas_qs.filter(
            estado__in=['validando', 'importando', 'reconciliando']
        ).values('estado').annotate(
            total=Count('id_carga')
        ).order_by('estado')
        
        # Estadísticas agregadas de progreso
        total_insertados = cargas_qs.aggregate(total=Sum('insertados'))['total'] or 0
        total_actualizados = cargas_qs.aggregate(total=Sum('actualizados'))['total'] or 0
        total_rechazados = cargas_qs.aggregate(total=Sum('rechazados'))['total'] or 0
        
        # Cargas por mes (últimos 12 meses)
        doce_meses_atras = timezone.now() - timedelta(days=365)
        cargas_por_mes = cargas_qs.filter(
            creado_en__gte=doce_meses_atras
        ).annotate(
            año=Extract('creado_en', 'year'),
            mes=Extract('creado_en', 'month')
        ).values('año', 'mes').annotate(
            total=Count('id_carga'),
            completadas=Count('id_carga', filter=Q(estado='done')),
            fallidas=Count('id_carga', filter=Q(estado='failed'))
        ).order_by('año', 'mes')
        
        return Response({
            'cargas_por_tipo': list(cargas_por_tipo),
            'cargas_actuales': list(cargas_actuales),
            'progreso_agregado': {
                'total_insertados': total_insertados,
                'total_actualizados': total_actualizados,
                'total_rechazados': total_rechazados,
            },
            'cargas_por_mes': list(cargas_por_mes),
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_cargas_por_corredora(request):
    """
    API: Cargas agrupadas por corredora
    Endpoint: /api/microservicio/cargas-por-corredora/
    """
    try:
        user = request.user
        usuario_obj = Usuario.objects.filter(username=user.username).first()
        
        cargas_qs = Carga.objects.select_related('id_corredora')
        
        corredora_usuario = obtener_corredora_usuario(usuario_obj)
        is_staff = getattr(user, 'is_staff', False)
        if corredora_usuario and not is_staff:
            cargas_qs = cargas_qs.filter(id_corredora=corredora_usuario)
        
        cargas_por_corredora = cargas_qs.filter(
            id_corredora__isnull=False
        ).values(
            'id_corredora__nombre',
            'id_corredora'
        ).annotate(
            total=Count('id_carga'),
            completadas=Count('id_carga', filter=Q(estado='done')),
            fallidas=Count('id_carga', filter=Q(estado='failed')),
            en_proceso=Count('id_carga', filter=Q(estado__in=['validando', 'importando', 'reconciliando']))
        ).order_by('-total')[:10]  # Top 10
        
        return Response({
            'cargas_por_corredora': [
                {
                    'nombre': item['id_corredora__nombre'] or 'Sin corredora',
                    'id': item['id_corredora'],
                    'total': item['total'],
                    'completadas': item['completadas'],
                    'fallidas': item['fallidas'],
                    'en_proceso': item['en_proceso']
                }
                for item in cargas_por_corredora
            ]
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_auditoria_resumen(request):
    """
    API: Resumen de auditoría
    Endpoint: /api/microservicio/auditoria-resumen/
    """
    try:
        treinta_dias_atras = timezone.now() - timedelta(days=30)
        
        # Auditoría por entidad
        auditoria_por_entidad = Auditoria.objects.filter(
            fecha__gte=treinta_dias_atras
        ).values('entidad').annotate(
            total=Count('id_auditoria')
        ).order_by('-total')
        
        # Auditoría por acción
        auditoria_por_accion = Auditoria.objects.filter(
            fecha__gte=treinta_dias_atras
        ).values('accion').annotate(
            total=Count('id_auditoria')
        ).order_by('-total')
        
        # Auditoría por día (últimos 30 días)
        auditoria_por_dia = Auditoria.objects.filter(
            fecha__gte=treinta_dias_atras
        ).annotate(
            dia=Extract('fecha', 'day'),
            mes=Extract('fecha', 'month'),
            año=Extract('fecha', 'year')
        ).values('año', 'mes', 'dia').annotate(
            total=Count('id_auditoria')
        ).order_by('año', 'mes', 'dia')
        
        return Response({
            'periodo_dias': 30,
            'auditoria_por_entidad': list(auditoria_por_entidad),
            'auditoria_por_accion': list(auditoria_por_accion),
            'auditoria_por_dia': list(auditoria_por_dia),
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_tipos_cambio_resumen(request):
    """
    API: Resumen de tipos de cambio
    Endpoint: /api/microservicio/tipos-cambio-resumen/
    """
    try:
        # Tipos de cambio por fuente
        tipos_cambio_por_fuente = TipoCambio.objects.values(
            'id_fuente__codigo',
            'id_fuente__nombre'
        ).annotate(
            total=Count('id_tipo_cambio')
        ).order_by('-total')
        
        # Tipos de cambio por par de monedas (más recientes)
        treinta_dias_atras = timezone.now() - timedelta(days=30)
        tipos_cambio_por_par = TipoCambio.objects.filter(
            fecha__gte=treinta_dias_atras.date()
        ).values(
            'moneda_origen',
            'moneda_destino'
        ).annotate(
            total=Count('id_tipo_cambio'),
            tasa_promedio=Avg('tasa'),
            tasa_maxima=Max('tasa'),
            tasa_minima=Min('tasa')
        ).order_by('-total')[:10]
        
        return Response({
            'tipos_cambio_por_fuente': [
                {
                    'codigo': item['id_fuente__codigo'],
                    'nombre': item['id_fuente__nombre'],
                    'total': item['total']
                }
                for item in tipos_cambio_por_fuente
            ],
            'tipos_cambio_por_par': [
                {
                    'par': f"{item['moneda_origen']}/{item['moneda_destino']}",
                    'total': item['total'],
                    'tasa_promedio': float(item['tasa_promedio'] or 0),
                    'tasa_maxima': float(item['tasa_maxima'] or 0),
                    'tasa_minima': float(item['tasa_minima'] or 0)
                }
                for item in tipos_cambio_por_par
            ]
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_kpis_operativos(request):
    """
    API: KPIs operativos del sistema
    Endpoint: /api/microservicio/kpis-operativos/
    """
    try:
        user = request.user
        usuario_obj = Usuario.objects.filter(username=user.username).first()
        
        # Filtrar según rol
        calificaciones_qs = Calificacion.objects.all()
        cargas_qs = Carga.objects.all()
        
        corredora_usuario = obtener_corredora_usuario(usuario_obj)
        is_staff = getattr(user, 'is_staff', False)
        if corredora_usuario and not is_staff:
            calificaciones_qs = calificaciones_qs.filter(id_corredora=corredora_usuario)
            cargas_qs = cargas_qs.filter(id_corredora=corredora_usuario)
        
        # Últimos 30 días
        treinta_dias_atras = timezone.now() - timedelta(days=30)
        
        # KPIs de Calificaciones
        calificaciones_recientes = calificaciones_qs.filter(creado_en__gte=treinta_dias_atras).count()
        calificaciones_publicadas = calificaciones_qs.filter(estado='publicada').count()
        calificaciones_por_dia = calificaciones_recientes / 30 if calificaciones_recientes > 0 else 0
        
        # KPIs de Cargas
        cargas_recientes = cargas_qs.filter(creado_en__gte=treinta_dias_atras).count()
        cargas_completadas = cargas_qs.filter(estado='done', creado_en__gte=treinta_dias_atras).count()
        cargas_fallidas = cargas_qs.filter(estado='failed', creado_en__gte=treinta_dias_atras).count()
        tasa_exito_cargas = (cargas_completadas / cargas_recientes * 100) if cargas_recientes > 0 else 0
        
        # KPIs de Progreso de Cargas
        detalle_cargas = cargas_qs.filter(creado_en__gte=treinta_dias_atras).aggregate(
            total_insertados=Sum('insertados'),
            total_actualizados=Sum('actualizados'),
            total_rechazados=Sum('rechazados')
        )
        total_procesados = (detalle_cargas['total_insertados'] or 0) + (detalle_cargas['total_actualizados'] or 0)
        tasa_aceptacion = (total_procesados / (total_procesados + (detalle_cargas['total_rechazados'] or 0)) * 100) if total_procesados > 0 else 0
        
        return Response({
            'periodo_dias': 30,
            'calificaciones': {
                'total_recientes': calificaciones_recientes,
                'total_publicadas': calificaciones_publicadas,
                'promedio_por_dia': round(calificaciones_por_dia, 2)
            },
            'cargas': {
                'total_recientes': cargas_recientes,
                'completadas': cargas_completadas,
                'fallidas': cargas_fallidas,
                'tasa_exito': round(tasa_exito_cargas, 2)
            },
            'progreso_cargas': {
                'total_insertados': detalle_cargas['total_insertados'] or 0,
                'total_actualizados': detalle_cargas['total_actualizados'] or 0,
                'total_rechazados': detalle_cargas['total_rechazados'] or 0,
                'tasa_aceptacion': round(tasa_aceptacion, 2)
            }
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_refrescar_grafico(request):
    """
    API: Solicita actualización de un gráfico específico y publica en Pulsar
    Endpoint: /api/microservicio/refrescar-grafico/
    Body: {"tipo_grafico": "estadisticas_generales"}
    """
    try:
        tipo_grafico = request.data.get('tipo_grafico', 'estadisticas_generales')
        
        # Publicar evento en Pulsar para notificar actualización
        publicar_actualizacion_graficos(
            tipo_grafico=tipo_grafico,
            datos={'solicitado_por': request.user.username, 'timestamp': timezone.now().isoformat()}
        )
        
        return Response({
            'mensaje': f'Actualización de gráfico {tipo_grafico} solicitada',
            'tipo_grafico': tipo_grafico
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_exportar_grafico(request, tipo_grafico, formato):
    """
    API: Exporta datos de un gráfico en el formato especificado
    Endpoint: /api/microservicio/exportar/<tipo_grafico>/<formato>/
    Formatos disponibles: csv, excel, pdf, html
    Tipos de gráfico: estadisticas_generales, cargas_detalle, auditoria, kpis, etc.
    """
    from microservicio.utils import ExportadorGraficos
    
    try:
        formato = formato.lower()
        tipo_grafico = tipo_grafico.lower()
        
        # Obtener datos según el tipo de gráfico usando funciones auxiliares
        # Esto evita problemas de tipos entre DRF Request y HttpRequest
        user = request.user
        usuario_obj = Usuario.objects.filter(username=user.username).first()
        
        if tipo_grafico == 'estadisticas_generales':
            datos = _obtener_estadisticas_generales(user, usuario_obj)
        
        elif tipo_grafico == 'cargas_detalle':
            # Extraer lógica directamente
            cargas_qs = Carga.objects.all()
            corredora_usuario = obtener_corredora_usuario(usuario_obj)
            is_staff = getattr(user, 'is_staff', False)
            if corredora_usuario and not is_staff:
                cargas_qs = cargas_qs.filter(id_corredora=corredora_usuario)
            
            cargas_por_tipo = cargas_qs.values('tipo').annotate(
                total=Count('id_carga')
            ).order_by('tipo')
            
            cargas_actuales = cargas_qs.filter(
                estado__in=['validando', 'importando', 'reconciliando']
            ).values('estado').annotate(
                total=Count('id_carga')
            ).order_by('estado')
            
            total_insertados = cargas_qs.aggregate(total=Sum('insertados'))['total'] or 0
            total_actualizados = cargas_qs.aggregate(total=Sum('actualizados'))['total'] or 0
            total_rechazados = cargas_qs.aggregate(total=Sum('rechazados'))['total'] or 0
            
            doce_meses_atras = timezone.now() - timedelta(days=365)
            cargas_por_mes = cargas_qs.filter(
                creado_en__gte=doce_meses_atras
            ).annotate(
                año=Extract('creado_en', 'year'),
                mes=Extract('creado_en', 'month')
            ).values('año', 'mes').annotate(
                total=Count('id_carga'),
                completadas=Count('id_carga', filter=Q(estado='done')),
                fallidas=Count('id_carga', filter=Q(estado='failed'))
            ).order_by('año', 'mes')
            
            datos = {
                'cargas_por_tipo': list(cargas_por_tipo),
                'cargas_actuales': list(cargas_actuales),
                'progreso_agregado': {
                    'total_insertados': total_insertados,
                    'total_actualizados': total_actualizados,
                    'total_rechazados': total_rechazados,
                },
                'cargas_por_mes': list(cargas_por_mes),
            }
        
        elif tipo_grafico == 'cargas_corredora':
            cargas_qs = Carga.objects.select_related('id_corredora')
            corredora_usuario = obtener_corredora_usuario(usuario_obj)
            is_staff = getattr(user, 'is_staff', False)
            if corredora_usuario and not is_staff:
                cargas_qs = cargas_qs.filter(id_corredora=corredora_usuario)
            
            cargas_por_corredora = cargas_qs.values(
                'id_corredora__nombre',
                'id_corredora'
            ).annotate(
                total=Count('id_carga'),
                completadas=Count('id_carga', filter=Q(estado='done')),
                fallidas=Count('id_carga', filter=Q(estado='failed')),
                en_proceso=Count('id_carga', filter=Q(estado__in=['validando', 'importando', 'reconciliando']))
            ).order_by('-total')[:10]
            
            datos = {
                'cargas_por_corredora': [
                    {
                        'nombre': item['id_corredora__nombre'],
                        'id': item['id_corredora'],
                        'total': item['total'],
                        'completadas': item['completadas'],
                        'fallidas': item['fallidas'],
                        'en_proceso': item['en_proceso']
                    }
                    for item in cargas_por_corredora
                ]
            }
        
        elif tipo_grafico == 'auditoria':
            treinta_dias_atras = timezone.now() - timedelta(days=30)
            auditoria_por_entidad = Auditoria.objects.filter(
                fecha__gte=treinta_dias_atras
            ).values('entidad').annotate(
                total=Count('id_auditoria')
            ).order_by('-total')
            
            auditoria_por_accion = Auditoria.objects.filter(
                fecha__gte=treinta_dias_atras
            ).values('accion').annotate(
                total=Count('id_auditoria')
            ).order_by('-total')
            
            auditoria_por_dia = Auditoria.objects.filter(
                fecha__gte=treinta_dias_atras
            ).annotate(
                dia=Extract('fecha', 'day'),
                mes=Extract('fecha', 'month'),
                año=Extract('fecha', 'year')
            ).values('año', 'mes', 'dia').annotate(
                total=Count('id_auditoria')
            ).order_by('año', 'mes', 'dia')
            
            datos = {
                'periodo_dias': 30,
                'auditoria_por_entidad': list(auditoria_por_entidad),
                'auditoria_por_accion': list(auditoria_por_accion),
                'auditoria_por_dia': list(auditoria_por_dia),
            }
        
        elif tipo_grafico == 'tipos_cambio':
            tipos_cambio_por_fuente = TipoCambio.objects.values(
                'id_fuente__codigo',
                'id_fuente__nombre'
            ).annotate(
                total=Count('id_tipo_cambio')
            ).order_by('-total')
            
            treinta_dias_atras = timezone.now() - timedelta(days=30)
            tipos_cambio_por_par = TipoCambio.objects.filter(
                fecha__gte=treinta_dias_atras.date()
            ).values(
                'moneda_origen',
                'moneda_destino'
            ).annotate(
                total=Count('id_tipo_cambio'),
                tasa_promedio=Avg('tasa'),
                tasa_maxima=Max('tasa'),
                tasa_minima=Min('tasa')
            ).order_by('-total')[:10]
            
            datos = {
                'tipos_cambio_por_fuente': [
                    {
                        'codigo': item['id_fuente__codigo'],
                        'nombre': item['id_fuente__nombre'],
                        'total': item['total']
                    }
                    for item in tipos_cambio_por_fuente
                ],
                'tipos_cambio_por_par': [
                    {
                        'par': f"{item['moneda_origen']}/{item['moneda_destino']}",
                        'total': item['total'],
                        'tasa_promedio': float(item['tasa_promedio'] or 0),
                        'tasa_maxima': float(item['tasa_maxima'] or 0),
                        'tasa_minima': float(item['tasa_minima'] or 0)
                    }
                    for item in tipos_cambio_por_par
                ]
            }
        
        elif tipo_grafico == 'kpis':
            calificaciones_qs = Calificacion.objects.all()
            cargas_qs = Carga.objects.all()
            
            corredora_usuario = obtener_corredora_usuario(usuario_obj)
            is_staff = getattr(user, 'is_staff', False)
            if corredora_usuario and not is_staff:
                calificaciones_qs = calificaciones_qs.filter(id_corredora=corredora_usuario)
                cargas_qs = cargas_qs.filter(id_corredora=corredora_usuario)
            
            treinta_dias_atras = timezone.now() - timedelta(days=30)
            
            calificaciones_recientes = calificaciones_qs.filter(creado_en__gte=treinta_dias_atras).count()
            calificaciones_publicadas = calificaciones_qs.filter(estado='publicada').count()
            calificaciones_por_dia = (calificaciones_recientes / 30) if calificaciones_recientes > 0 else 0
            
            cargas_recientes = cargas_qs.filter(creado_en__gte=treinta_dias_atras).count()
            cargas_completadas = cargas_qs.filter(estado='done', creado_en__gte=treinta_dias_atras).count()
            cargas_fallidas = cargas_qs.filter(estado='failed', creado_en__gte=treinta_dias_atras).count()
            tasa_exito_cargas = (cargas_completadas / cargas_recientes * 100) if cargas_recientes > 0 else 0
            
            detalle_cargas = cargas_qs.filter(creado_en__gte=treinta_dias_atras).aggregate(
                total_insertados=Sum('insertados'),
                total_actualizados=Sum('actualizados'),
                total_rechazados=Sum('rechazados')
            )
            total_procesados = (detalle_cargas['total_insertados'] or 0) + (detalle_cargas['total_actualizados'] or 0)
            tasa_aceptacion = (total_procesados / (total_procesados + (detalle_cargas['total_rechazados'] or 0)) * 100) if total_procesados > 0 else 0
            
            datos = {
                'periodo_dias': 30,
                'calificaciones': {
                    'total_recientes': calificaciones_recientes,
                    'total_publicadas': calificaciones_publicadas,
                    'promedio_por_dia': round(calificaciones_por_dia, 2)
                },
                'cargas': {
                    'total_recientes': cargas_recientes,
                    'completadas': cargas_completadas,
                    'fallidas': cargas_fallidas,
                    'tasa_exito': round(tasa_exito_cargas, 2)
                },
                'progreso_cargas': {
                    'total_insertados': detalle_cargas['total_insertados'] or 0,
                    'total_actualizados': detalle_cargas['total_actualizados'] or 0,
                    'total_rechazados': detalle_cargas['total_rechazados'] or 0,
                    'tasa_aceptacion': round(tasa_aceptacion, 2)
                }
            }
        
        elif tipo_grafico == 'actividad_reciente':
            treinta_dias_atras = timezone.now() - timedelta(days=30)
            
            calificaciones_recientes = Calificacion.objects.filter(
                creado_en__gte=treinta_dias_atras
            ).count()
            
            cargas_recientes = Carga.objects.filter(
                creado_en__gte=treinta_dias_atras
            ).count()
            
            cargas_exitosas = Carga.objects.filter(
                creado_en__gte=treinta_dias_atras,
                estado='done'
            ).count()
            
            cargas_fallidas = Carga.objects.filter(
                creado_en__gte=treinta_dias_atras,
                estado='failed'
            ).count()
            
            datos = {
                'periodo_dias': 30,
                'calificaciones_creadas': calificaciones_recientes,
                'cargas_realizadas': cargas_recientes,
                'cargas_exitosas': cargas_exitosas,
                'cargas_fallidas': cargas_fallidas,
            }
        
        else:
            return Response({'error': f'Tipo de gráfico no válido: {tipo_grafico}'}, status=400)
        
        if datos is None:
            return Response({'error': 'No se pudieron obtener los datos'}, status=500)
        
        # Preparar datos para exportación
        datos_export = datos
        if isinstance(datos, dict) and 'estadisticas_generales' in datos:
            # Convertir dict anidado a lista plana
            datos_export = []
            for key, value in datos.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        datos_export.append({'campo': f"{key}.{sub_key}", 'valor': sub_value})
                else:
                    datos_export.append({'campo': key, 'valor': value})
        
        # Crear exportador
        exportador = ExportadorGraficos(datos_export, titulo=f"Reporte: {tipo_grafico.replace('_', ' ').title()}")
        
        # Exportar según formato
        # Asegurar que el formato Excel use la extensión .xlsx
        if formato in ['excel', 'xlsx']:
            extension = 'xlsx'
            nombre_archivo = f"{tipo_grafico}_{exportador.timestamp}.{extension}"
            return exportador.exportar_excel(nombre_archivo, tipo_grafico.replace('_', ' ').title())
        else:
            nombre_archivo = f"{tipo_grafico}_{exportador.timestamp}.{formato}"
        
        if formato == 'csv':
            return exportador.exportar_csv(nombre_archivo)
        elif formato == 'pdf':
            return exportador.exportar_pdf(nombre_archivo)
        elif formato == 'html':
            return exportador.exportar_html(nombre_archivo)
        else:
            return Response({'error': f'Formato no válido: {formato}. Formatos disponibles: csv, xlsx, pdf, html'}, status=400)
    
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

