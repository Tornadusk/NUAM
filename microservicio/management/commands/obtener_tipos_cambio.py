"""
Management command para obtener tipos de cambio desde APIs externas
Uso: python manage.py obtener_tipos_cambio [--fuente CODIGO] [--monedas CLP,PEN,COP]
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from microservicio.models import TipoCambioFuente, TipoCambio
from microservicio.services.exchange_rate_client import (
    llamar_exchange_rate_service_actualizar,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Obtiene tipos de cambio desde APIs externas y los guarda en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fuente',
            type=str,
            help='Código de la fuente a usar (si no se especifica, usa todas las activas en orden de prioridad)',
        )
        parser.add_argument(
            '--monedas',
            type=str,
            default='CLP,PEN,COP',
            help='Monedas destino separadas por comas (default: CLP,PEN,COP)',
        )
        parser.add_argument(
            '--moneda-base',
            type=str,
            default='USD',
            help='Moneda base (default: USD)',
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar actualización incluso si ya existe un tipo de cambio para hoy',
        )

    def handle(self, *args, **options):
        fuente_codigo = options.get('fuente')
        monedas_str = options.get('monedas', 'CLP,PEN,COP')
        moneda_base = options.get('moneda_base', 'USD')
        forzar = options.get('forzar', False)
        
        monedas_destino = [m.strip().upper() for m in monedas_str.split(',')]
        
        self.stdout.write(
            self.style.SUCCESS(f'Obteniendo tipos de cambio: {moneda_base} -> {", ".join(monedas_destino)}')
        )
        
        # Llamar al microservicio de tipos de cambio
        self.stdout.write("\nLlamando a microservicio exchange-rate-service...\n")
        incluir_proveedores = [fuente_codigo.upper()] if fuente_codigo else None
        resultado = llamar_exchange_rate_service_actualizar(
            monedas=monedas_destino,
            moneda_base=moneda_base,
            incluir_proveedores=incluir_proveedores,
        )

        if not resultado.get('success'):
            self.stdout.write(
                self.style.ERROR(f"✗ Error al obtener tipos de cambio desde el microservicio: {resultado.get('error', 'Error desconocido')}")
            )
            return

        tipos_cambio = resultado.get('tipos_cambio', [])
        if not tipos_cambio:
            self.stdout.write(
                self.style.WARNING('No se recibieron tipos de cambio desde el microservicio')
            )
            return

        # Resolver fuentes según código recibido
        fuentes_por_codigo = {
            f.codigo.upper(): f
            for f in TipoCambioFuente.objects.filter(activa=True)
        }

        guardados_total = 0
        for tipo in tipos_cambio:
            codigo_fuente = (tipo.get('fuente') or '').upper()
            fuente = fuentes_por_codigo.get(codigo_fuente)
            if not fuente:
                # Si no encontramos la fuente por código, usar la primera activa como fallback
                fuente = next(iter(fuentes_por_codigo.values()), None)
                if not fuente:
                    continue

            fecha = tipo.get('fecha') or timezone.now().date()
            guardados = self._guardar_tipos_cambio(
                fuente=fuente,
                tipos_cambio=[tipo],
                fecha=fecha,
                forzar=forzar,
            )
            guardados_total += guardados

        if guardados_total > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Guardados {guardados_total} tipos de cambio desde exchange-rate-service')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\nNo se guardaron nuevos tipos de cambio (ya existían o no se recibieron datos válidos)')
            )
    
    def _guardar_tipos_cambio(self, fuente, tipos_cambio, fecha, forzar=False):
        """
        Guarda los tipos de cambio en la base de datos
        """
        guardados = 0
        
        with transaction.atomic():
            for tipo_data in tipos_cambio:
                # Verificar si ya existe
                existe = TipoCambio.objects.filter(
                    id_fuente=fuente,
                    moneda_origen=tipo_data['moneda_origen'],
                    moneda_destino=tipo_data['moneda_destino'],
                    fecha=fecha
                ).exists()
                
                if existe and not forzar:
                    continue
                
                # Crear o actualizar
                tipo_cambio, creado = TipoCambio.objects.update_or_create(
                    id_fuente=fuente,
                    moneda_origen=tipo_data['moneda_origen'],
                    moneda_destino=tipo_data['moneda_destino'],
                    fecha=fecha,
                    defaults={
                        'tasa': tipo_data['tasa'],
                        'vigente_desde': timezone.now()
                    }
                )
                
                if creado:
                    guardados += 1
                    logger.info(
                        f"Tipo de cambio creado: {tipo_data['moneda_origen']}/{tipo_data['moneda_destino']} "
                        f"= {tipo_data['tasa']} desde {fuente.nombre}"
                    )
        
        return guardados


