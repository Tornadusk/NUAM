import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from calificaciones.models import Calificacion
from usuarios.models import Usuario, Persona
from corredoras.models import Corredora
from datetime import datetime
import json

# URL del microservicio de generación de documentos
MICROSERVICIO_DOCS_URL = getattr(settings, 'MICROSERVICIO_DOCS_URL', 'http://localhost:5001')


@login_required
def generar_comprobante_view(request, calificacion_id=None):
    """
    Vista para generar comprobante tributario desde una calificación.
    Si no se proporciona calificacion_id, usa datos de prueba.
    """
    if calificacion_id:
        # Obtener calificación real de la BD
        calificacion = get_object_or_404(Calificacion, id_calificacion=calificacion_id)
        
        # Obtener datos del usuario/cliente
        usuario = calificacion.creado_por
        persona = None
        if hasattr(usuario, 'persona'):
            persona = usuario.persona
        
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
    else:
        # Datos de prueba (comportamiento anterior)
        datos_para_pdf = {
            "nombre_cliente": request.user.get_full_name() or request.user.username,
            "rut": "12.345.678-9",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "corredora": "Corredora de Prueba",
            "instrumento": "Instrumento de Prueba",
            "ejercicio": datetime.now().year,
            "detalle_calculo": {
                "monto_base": 500000,
                "monto_impuesto": 50000,
                "tasa_impuesto": 10.0,
                "categoria": "Prueba Integración",
                "moneda": "CLP",
                "estado": "Publicada",
            },
        }

    try:
        # Petición al microservicio
        respuesta = requests.post(
            f"{MICROSERVICIO_DOCS_URL}/generar-comprobante",
            json=datos_para_pdf,
            timeout=30
        )

        if respuesta.status_code == 200:
            response = HttpResponse(respuesta.content, content_type='application/pdf')
            nombre_archivo = f"comprobante_nuam_{calificacion_id or 'prueba'}_{datetime.now().strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            # Publicar evento en Pulsar (si está configurado)
            try:
                from microservicio.pulsar import publicar_comprobante_generado
                monto_impuesto = datos_para_pdf['detalle_calculo']['monto_impuesto']
                publicar_comprobante_generado(
                    calificacion_id=calificacion_id,
                    usuario=request.user.username,
                    monto_impuesto=monto_impuesto,
                    estado='generado'
                )
            except Exception as e:
                # Si Pulsar no está disponible, continuar sin error
                pass
            
            return response
        else:
            return HttpResponse(
                f"Error del microservicio: {respuesta.status_code} - {respuesta.text}",
                status=500
            )

    except requests.exceptions.ConnectionError:
        return HttpResponse(
            "Error: El microservicio de documentos está apagado. "
            "Ejecuta 'docker-compose -f services/docker-compose.yml up' para iniciarlo.",
            status=503
        )
    except Exception as e:
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)