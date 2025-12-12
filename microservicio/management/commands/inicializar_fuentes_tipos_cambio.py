"""
Management command para inicializar fuentes de tipos de cambio básicas
Uso: python manage.py inicializar_fuentes_tipos_cambio
"""
from django.core.management.base import BaseCommand
from microservicio.models import TipoCambioFuente


class Command(BaseCommand):
    help = 'Inicializa las fuentes básicas de tipos de cambio en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sobrescribir',
            action='store_true',
            help='Sobrescribir fuentes existentes si ya existen',
        )

    def handle(self, *args, **options):
        sobrescribir = options.get('sobrescribir', False)
        
        fuentes_basicas = [
            {
                'codigo': 'EXCHANGERATE_API',
                'nombre': 'ExchangeRate API',
                'url_api': 'https://v6.exchangerate-api.com/v6',
                'api_key': '',  # Debe configurarse manualmente
                'activa': True,
                'orden_prioridad': 1,
            },
            {
                'codigo': 'FIXER_IO',
                'nombre': 'Fixer.io',
                'url_api': 'http://data.fixer.io/api',
                'api_key': '',  # Debe configurarse manualmente
                'activa': True,
                'orden_prioridad': 2,
            },
            {
                'codigo': 'BANCO_CENTRAL_CHILE',
                'nombre': 'Banco Central de Chile',
                'url_api': 'https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx',
                'api_key': '',  # No requiere API key
                'activa': True,
                'orden_prioridad': 3,
            },
        ]
        
        creadas = 0
        actualizadas = 0
        
        for fuente_data in fuentes_basicas:
            codigo = fuente_data.pop('codigo')
            
            fuente_existente = TipoCambioFuente.objects.filter(codigo=codigo).first()
            
            if fuente_existente:
                if sobrescribir:
                    for key, value in fuente_data.items():
                        setattr(fuente_existente, key, value)
                    fuente_existente.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Actualizada: {codigo}')
                    )
                    actualizadas += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'○ Ya existe: {codigo} (usa --sobrescribir para actualizar)')
                    )
            else:
                TipoCambioFuente.objects.create(codigo=codigo, **fuente_data)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada: {codigo}')
                )
                creadas += 1
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Resumen:'))
        self.stdout.write(f'  Creadas: {creadas}')
        self.stdout.write(f'  Actualizadas: {actualizadas}')
        self.stdout.write(f'  Total fuentes: {TipoCambioFuente.objects.count()}')
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('IMPORTANTE:'))
        self.stdout.write('  - Configura las API keys en el admin: /admin/microservicio/tipocambiofuente/')
        self.stdout.write('  - Para ExchangeRate API: https://www.exchangerate-api.com/')
        self.stdout.write('  - Para Fixer.io: https://fixer.io/')
        self.stdout.write('  - Banco Central de Chile no requiere API key')
        self.stdout.write('\n  Ejecuta: python manage.py obtener_tipos_cambio')

