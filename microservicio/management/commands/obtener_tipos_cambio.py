"""
Management command para obtener tipos de cambio desde APIs externas
Uso: python manage.py obtener_tipos_cambio [--fuente CODIGO] [--monedas CLP,PEN,COP]
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from microservicio.models import TipoCambioFuente, TipoCambio
from microservicio.services.exchange_rate_providers import crear_proveedor_desde_fuente

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
        
        # Obtener fuentes activas
        if fuente_codigo:
            fuentes = TipoCambioFuente.objects.filter(
                codigo=fuente_codigo.upper(),
                activa=True
            ).order_by('orden_prioridad')
        else:
            fuentes = TipoCambioFuente.objects.filter(
                activa=True
            ).order_by('orden_prioridad')
        
        if not fuentes.exists():
            self.stdout.write(
                self.style.WARNING('No hay fuentes activas configuradas')
            )
            self.stdout.write(
                self.style.WARNING('Configura fuentes en el admin: /admin/microservicio/tipocambiofuente/')
            )
            return
        
        # Intentar con cada fuente en orden de prioridad
        exito = False
        for fuente in fuentes:
            self.stdout.write(f'\nIntentando con fuente: {fuente.nombre} ({fuente.codigo})...')
            
            proveedor = crear_proveedor_desde_fuente(fuente)
            if not proveedor:
                self.stdout.write(
                    self.style.WARNING(f'  No se pudo crear proveedor para {fuente.codigo}')
                )
                fuente.intentos_fallidos += 1
                fuente.ultima_consulta_fallida = timezone.now()
                fuente.save()
                continue
            
            # Obtener tipos de cambio
            resultado = proveedor.obtener_tipos_cambio(
                moneda_base=moneda_base,
                monedas_destino=monedas_destino
            )
            
            if not resultado.get('exito'):
                error = resultado.get('error', 'Error desconocido')
                self.stdout.write(
                    self.style.ERROR(f'  Error: {error}')
                )
                fuente.intentos_fallidos += 1
                fuente.ultima_consulta_fallida = timezone.now()
                fuente.save()
                continue
            
            # Guardar tipos de cambio
            tipos_guardados = self._guardar_tipos_cambio(
                fuente=fuente,
                tipos_cambio=resultado['tipos_cambio'],
                fecha=resultado['fecha'],
                forzar=forzar
            )
            
            if tipos_guardados > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Guardados {tipos_guardados} tipos de cambio')
                )
                fuente.intentos_fallidos = 0
                fuente.ultima_consulta_exitosa = timezone.now()
                fuente.save()
                exito = True
                break  # Si tuvo éxito, no intentar con otras fuentes
            else:
                self.stdout.write(
                    self.style.WARNING('  No se guardaron nuevos tipos de cambio (ya existen)')
                )
                # Aún así marcamos como exitoso si obtuvo datos
                fuente.intentos_fallidos = 0
                fuente.ultima_consulta_exitosa = timezone.now()
                fuente.save()
                exito = True
                break
        
        if not exito:
            self.stdout.write(
                self.style.ERROR('\n✗ No se pudo obtener tipos de cambio de ninguna fuente')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Proceso completado exitosamente')
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


