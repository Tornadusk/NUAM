#!/usr/bin/env python
"""Script para eliminar datos simulados de hoy"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_nuam.settings')
django.setup()

from microservicio.models import TipoCambio, TipoCambioFuente
from django.utils import timezone

hoy = timezone.now().date()
fuente_simulado = TipoCambioFuente.objects.filter(codigo='SIMULADO').first()

if fuente_simulado:
    eliminados = TipoCambio.objects.filter(fecha=hoy, id_fuente=fuente_simulado).delete()
    print(f"Eliminados {eliminados[0]} registros simulados de hoy ({hoy})")
    print("\nAhora ejecuta: python manage.py obtener_tipos_cambio --forzar")
    print("Para obtener datos reales actualizados.")
else:
    print("No se encontro fuente SIMULADO")

