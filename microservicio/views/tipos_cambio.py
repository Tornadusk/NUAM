"""
Vistas para Tipos de Cambio
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Max, Min
from django.db.models.functions import Extract
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.management import call_command
from django.core.management.base import CommandError
from core.models import Pais, MonedaPais
from microservicio.models import TipoCambio
from .helpers import rol_required


@login_required
@rol_required('Administrador', 'Analista', 'Operador')
def tipos_cambio_dashboard(request):
    """
    Vista principal para el dashboard de tipos de cambio
    Permitido para: Administrador, Analista, Operador
    """
    return render(request, 'microservicio/tipos_cambio/dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_tipos_cambio_por_pais(request, codigo_pais=None):
    """
    API: Tipos de cambio filtrados por país
    Endpoint: /api/microservicio/tipos-cambio-por-pais/<codigo_pais>/
    Países soportados: CHL (Chile), PER (Perú), COL (Colombia), USA (EE.UU.)
    """
    try:
        # Si no se proporciona código de país, devolver todos
        if codigo_pais:
            codigo_pais = codigo_pais.upper()
            pais = Pais.objects.filter(codigo=codigo_pais).first()
            if not pais:
                return Response({'error': f'País {codigo_pais} no encontrado'}, status=404)
            
            # Obtener monedas del país
            monedas_pais = MonedaPais.objects.filter(id_pais=pais).values_list('id_moneda__codigo', flat=True)
            
            # Filtrar tipos de cambio donde la moneda destino está en las monedas del país
            tipos_cambio = TipoCambio.objects.filter(
                moneda_destino__in=monedas_pais
            ).select_related('id_fuente').order_by('-fecha', '-vigente_desde')
        else:
            # Todos los tipos de cambio
            tipos_cambio = TipoCambio.objects.select_related('id_fuente').order_by('-fecha', '-vigente_desde')
        
        # Últimos 30 días
        treinta_dias_atras = timezone.now() - timedelta(days=30)
        tipos_cambio_recientes = tipos_cambio.filter(fecha__gte=treinta_dias_atras.date())
        
        # Agrupar por par de monedas
        tipos_por_par = tipos_cambio_recientes.values(
            'moneda_origen',
            'moneda_destino'
        ).annotate(
            total=Count('id_tipo_cambio'),
            tasa_promedio=Avg('tasa'),
            tasa_maxima=Max('tasa'),
            tasa_minima=Min('tasa'),
            ultima_fecha=Max('fecha')
        ).order_by('-ultima_fecha')
        
        # Tipos de cambio más recientes por par
        tipos_recientes = []
        for par in tipos_por_par:
            ultimo_tipo = tipos_cambio_recientes.filter(
                moneda_origen=par['moneda_origen'],
                moneda_destino=par['moneda_destino']
            ).order_by('-fecha', '-vigente_desde').first()
            
            tipos_recientes.append({
                'par': f"{par['moneda_origen']}/{par['moneda_destino']}",
                'moneda_origen': par['moneda_origen'],
                'moneda_destino': par['moneda_destino'],
                'tasa_actual': float(ultimo_tipo.tasa) if ultimo_tipo else 0,
                'fecha_actual': ultimo_tipo.fecha.strftime('%Y-%m-%d') if ultimo_tipo else None,
                'fuente': ultimo_tipo.id_fuente.nombre if ultimo_tipo else None,
                'estadisticas': {
                    'total_registros': par['total'],
                    'tasa_promedio': float(par['tasa_promedio'] or 0),
                    'tasa_maxima': float(par['tasa_maxima'] or 0),
                    'tasa_minima': float(par['tasa_minima'] or 0),
                }
            })
        
        # Histórico por mes (últimos 12 meses)
        doce_meses_atras = timezone.now() - timedelta(days=365)
        historico_mensual = tipos_cambio.filter(
            fecha__gte=doce_meses_atras.date()
        ).annotate(
            año=Extract('fecha', 'year'),
            mes=Extract('fecha', 'month')
        ).values(
            'moneda_origen',
            'moneda_destino',
            'año',
            'mes'
        ).annotate(
            tasa_promedio=Avg('tasa'),
            total=Count('id_tipo_cambio')
        ).order_by('moneda_origen', 'moneda_destino', 'año', 'mes')
        
        return Response({
            'pais': codigo_pais if codigo_pais else 'TODOS',
            'tipos_cambio_recientes': tipos_recientes,
            'historico_mensual': list(historico_mensual),
            'periodo_dias': 30,
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_tipos_cambio_actuales(request):
    """
    API: Tipos de cambio actuales (más recientes) por país
    Endpoint: /api/microservicio/tipos-cambio-actuales/
    Devuelve el tipo de cambio más reciente para cada par de monedas por país
    """
    try:
        # Países a consultar
        paises_codigos = ['CHL', 'PER', 'COL', 'USA']
        paises = Pais.objects.filter(codigo__in=paises_codigos)
        
        resultado = {}
        
        for pais in paises:
            # Obtener monedas del país
            monedas_pais = MonedaPais.objects.filter(id_pais=pais).values_list('id_moneda__codigo', flat=True)
            
            # Obtener tipos de cambio más recientes para cada moneda del país
            tipos_actuales = []
            for moneda_destino in monedas_pais:
                # Buscar tipos de cambio donde la moneda destino es la del país
                # y la moneda origen es USD (más común)
                tipo_usd = TipoCambio.objects.filter(
                    moneda_origen='USD',
                    moneda_destino=moneda_destino
                ).order_by('-fecha', '-vigente_desde').first()
                
                if tipo_usd:
                    tipos_actuales.append({
                        'par': f"USD/{moneda_destino}",
                        'moneda_origen': 'USD',
                        'moneda_destino': moneda_destino,
                        'tasa': float(tipo_usd.tasa),
                        'fecha': tipo_usd.fecha.strftime('%Y-%m-%d'),
                        'fuente': tipo_usd.id_fuente.nombre,
                        'vigente_desde': tipo_usd.vigente_desde.isoformat() if tipo_usd.vigente_desde else None,
                    })
            
            resultado[pais.codigo] = {
                'nombre': pais.nombre,
                'tipos_cambio': tipos_actuales
            }
        
        return Response({
            'fecha_consulta': timezone.now().isoformat(),
            'paises': resultado
        })
    except Exception as e:
        import traceback
        return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_obtener_tipos_cambio(request):
    """
    API: Ejecuta el comando obtener_tipos_cambio para actualizar tipos de cambio desde APIs externas
    Endpoint: /api/microservicio/obtener-tipos-cambio/
    Método: POST
    """
    try:
        # Verificar permisos (solo Administrador, Analista, Operador)
        from .helpers import tiene_rol
        if not (tiene_rol(request.user, 'Administrador') or 
                tiene_rol(request.user, 'Analista') or 
                tiene_rol(request.user, 'Operador')):
            return Response({'success': False, 'error': 'No tienes permisos para ejecutar esta acción'}, status=403)
        
        # Obtener parámetros opcionales del request
        fuente = request.data.get('fuente', None)
        monedas = request.data.get('monedas', 'CLP,PEN,COP')
        forzar = request.data.get('forzar', False)
        
        # Preparar argumentos para el comando
        kwargs = {
            'verbosity': 0,  # Silencioso para API
        }
        if fuente:
            kwargs['fuente'] = fuente
        if monedas:
            kwargs['monedas'] = monedas
        if forzar:
            kwargs['forzar'] = True
        
        # Ejecutar el comando
        try:
            call_command('obtener_tipos_cambio', **kwargs)
            
            # Verificar cuántos tipos de cambio se obtuvieron
            tipos_recientes = TipoCambio.objects.filter(
                creado_en__gte=timezone.now() - timedelta(minutes=5)
            ).count()
            
            return Response({
                'success': True,
                'message': 'Tipos de cambio actualizados correctamente',
                'tipos_obtenidos': tipos_recientes,
                'timestamp': timezone.now().isoformat()
            })
        except CommandError as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Error al ejecutar el comando obtener_tipos_cambio'
            }, status=500)
    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

