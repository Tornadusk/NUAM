import requests
from django.http import HttpResponse
from django.shortcuts import render

def generar_comprobante_view(request):
    # Datos de prueba para enviar al microservicio
    datos_para_pdf = {
        "nombre_cliente": "Usuario NUAM",
        "rut": "12.345.678-9",
        "fecha": "2025-12-11",
        "detalle_calculo": {
            "monto_base": 500000,
            "monto_impuesto": 50000,
            "categoria": "Prueba Integracion"
        }
    }

    try:
        # Petición al microservicio (localhost:5001 porque Django corre en tu PC)
        respuesta = requests.post(
            "http://localhost:5001/generar-comprobante", 
            json=datos_para_pdf
        )

        if respuesta.status_code == 200:
            response = HttpResponse(respuesta.content, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="comprobante_nuam.pdf"'
            return response
        else:
            return HttpResponse(f"Error del microservicio: {respuesta.status_code}", status=500)

    except requests.exceptions.ConnectionError:
        return HttpResponse("Error: El microservicio está apagado. Ejecuta 'docker-compose up'", status=503)