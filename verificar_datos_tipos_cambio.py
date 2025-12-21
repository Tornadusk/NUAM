#!/usr/bin/env python
"""Script para verificar datos de tipos de cambio"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_nuam.settings')
django.setup()

from microservicio.models import TipoCambio, TipoCambioFuente
from django.utils import timezone
from datetime import date, timedelta

print("=" * 70)
print("VERIFICACION DE DATOS DE TIPOS DE CAMBIO")
print("=" * 70)

hoy = timezone.now().date()

print(f"\nFecha de hoy: {hoy}")
print(f"Total registros para hoy: {TipoCambio.objects.filter(fecha=hoy).count()}")

print("\nPor fuente (hoy):")
for fuente in TipoCambioFuente.objects.all().order_by('orden_prioridad'):
    count = TipoCambio.objects.filter(fecha=hoy, id_fuente=fuente).count()
    activa = "[ACTIVA]" if fuente.activa else "[INACTIVA]"
    print(f"  {activa} {fuente.nombre} ({fuente.codigo}): {count} registros")

print("\nUltimos registros de hoy (ultimos 10):")
registros_hoy = TipoCambio.objects.filter(fecha=hoy).select_related('id_fuente').order_by('-vigente_desde')[:10]
if registros_hoy:
    for tc in registros_hoy:
        es_simulado = "[SIMULADO]" if tc.id_fuente.codigo == 'SIMULADO' else "[REAL]"
        print(f"  {es_simulado} {tc.moneda_origen}/{tc.moneda_destino}: {tc.tasa} - {tc.id_fuente.nombre} - {tc.fecha}")
else:
    print("  No hay registros para hoy")

# Buscar datos de ExchangeRate API en los últimos 7 días
print("\nDatos de ExchangeRate API (ultimos 7 dias):")
hace_7_dias = hoy - timedelta(days=7)
try:
    fuente_exchangerate = TipoCambioFuente.objects.filter(codigo__icontains='EXCHANGERATE').first()
    if fuente_exchangerate:
        datos_reales = TipoCambio.objects.filter(
            fecha__gte=hace_7_dias,
            id_fuente=fuente_exchangerate
        ).order_by('-fecha', '-vigente_desde')[:10]
        if datos_reales:
            for tc in datos_reales:
                print(f"  [REAL] {tc.moneda_origen}/{tc.moneda_destino}: {tc.tasa} - Fecha: {tc.fecha}")
        else:
            print("  [AVISO] No hay datos de ExchangeRate API en los ultimos 7 dias")
    else:
        print("  [AVISO] No se encontro fuente ExchangeRate API")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 70)

