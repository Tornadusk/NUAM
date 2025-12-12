"""
Vistas para Comprobantes
"""
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from calificaciones.models import Calificacion


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def api_generar_comprobante(request, calificacion_id=None):
    """
    API: Genera un comprobante tributario en PDF desde una calificación
    Endpoint: /api/microservicio/generar-comprobante/<calificacion_id>/
    Métodos: POST, GET
    """
    try:
        # Obtener calificacion_id desde URL o body
        if calificacion_id is None:
            if request.method == 'POST':
                calificacion_id = request.data.get('calificacion_id')
            else:
                calificacion_id = request.GET.get('calificacion_id')
        
        if not calificacion_id:
            return Response({'error': 'calificacion_id es requerido'}, status=400)
        
        # Obtener calificación de la BD
        calificacion = Calificacion.objects.select_related(
            'id_corredora', 'id_instrumento', 'id_moneda', 'creado_por', 'creado_por__id_persona'
        ).get(id_calificacion=calificacion_id)
        
        # Obtener datos del usuario/cliente
        usuario = calificacion.creado_por
        persona = getattr(usuario, 'id_persona', None) if hasattr(usuario, 'id_persona') else None
        
        # Obtener datos de la corredora
        corredora = calificacion.id_corredora
        
        # Calcular impuesto (ejemplo: 10% del valor histórico)
        monto_base = float(calificacion.valor_historico or 0)
        tasa_impuesto = 0.10  # 10% - esto debería venir de configuración o cálculo real
        monto_impuesto = monto_base * tasa_impuesto
        
        # Preparar datos para el PDF
        nombre_cliente = persona.nombre_completo if persona else usuario.username
        datos_para_pdf = {
            "nombre_cliente": nombre_cliente,
            "rut": getattr(persona, 'rut', 'N/A') if persona else "N/A",
            "fecha": calificacion.fecha_pago.strftime("%Y-%m-%d") if calificacion.fecha_pago else datetime.now().strftime("%Y-%m-%d"),
            "corredora": corredora.nombre if corredora else "N/A",
            "instrumento": calificacion.id_instrumento.nombre if calificacion.id_instrumento else "N/A",
            "ejercicio": calificacion.ejercicio or datetime.now().year,
            "detalle_calculo": {
                "monto_base": int(monto_base),
                "monto_impuesto": int(monto_impuesto),
                "tasa_impuesto": tasa_impuesto * 100,  # Porcentaje
                "categoria": calificacion.descripcion or "Calificación Tributaria",
                "moneda": calificacion.id_moneda.codigo if calificacion.id_moneda else "CLP",
                "estado": calificacion.get_estado_display(),
            },
            "calificacion_id": calificacion.id_calificacion,
        }
        
        # Llamar al microservicio de documentos
        microservicio_url = getattr(settings, 'MICROSERVICIO_DOCS_URL', 'http://localhost:5001')
        respuesta = requests.post(
            f"{microservicio_url}/generar-comprobante",
            json=datos_para_pdf,
            timeout=30
        )
        
        if respuesta.status_code == 200:
            # Publicar evento en Pulsar
            try:
                from microservicio.pulsar import publicar_comprobante_generado
                publicar_comprobante_generado(
                    calificacion_id=calificacion_id,
                    usuario=request.user.username,
                    monto_impuesto=monto_impuesto,
                    estado='generado'
                )
            except Exception:
                pass  # Continuar si Pulsar no está disponible
            
            # Devolver PDF
            response = HttpResponse(respuesta.content, content_type='application/pdf')
            nombre_archivo = f"comprobante_nuam_{calificacion_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response
        else:
            return Response({
                'error': f'Error del microservicio: {respuesta.status_code}',
                'detalle': respuesta.text
            }, status=respuesta.status_code)
            
    except Calificacion.DoesNotExist:
        return Response({'error': f'Calificación {calificacion_id} no encontrada'}, status=404)
    except requests.exceptions.ConnectionError:
        return Response({
            'error': 'El microservicio de documentos está apagado',
            'mensaje': 'Ejecuta: docker-compose -f services/docker-compose.yml up'
        }, status=503)
    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

