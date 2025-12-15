"""
Vistas para el dashboard de Bolsa de Valores (Chile, Perú, Colombia).
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .helpers import rol_required
from microservicio.services.market_info_client import obtener_resumen_mercados


@login_required
@rol_required('Administrador', 'Analista', 'Operador')
def mercados_dashboard(request):
    """
    Dashboard de información de mercados (Bolsa de Valores).

    URL: /microservicio/mercados/
    """
    return render(request, 'microservicio/mercados/dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@rol_required('Administrador', 'Analista', 'Operador')
def api_mercados_resumen(request):
    """
    API: Proxy hacia el microservicio `market-info-service`.

    Devuelve información resumida de los mercados de Chile, Perú y Colombia.
    """
    pais = request.query_params.get('pais')
    paises = [p.strip().upper() for p in pais.split(',')] if pais else None

    data = obtener_resumen_mercados(paises)
    status_code = 200 if data.get('success') else 502
    return Response(data, status=status_code)


