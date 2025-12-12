"""
Modelos para Microservicios NUAM
"""
from django.db import models
from django.utils import timezone


class TipoCambioFuente(models.Model):
    """
    Tabla para gestionar múltiples fuentes de tipos de cambio.
    Permite tener varias fuentes activas y si una falla, usar otra como respaldo.
    """
    id_fuente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre descriptivo de la fuente (ej: ExchangeRate API, Banco Central Chile)")
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único de la fuente")
    url_api = models.URLField(null=True, blank=True, help_text="URL base de la API")
    api_key = models.CharField(max_length=255, null=True, blank=True, help_text="API Key si es necesario")
    activa = models.BooleanField(default=True, help_text="Indica si la fuente está activa")
    orden_prioridad = models.IntegerField(default=0, help_text="Orden de prioridad (menor número = mayor prioridad)")
    ultima_consulta_exitosa = models.DateTimeField(null=True, blank=True)
    ultima_consulta_fallida = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.IntegerField(default=0, help_text="Contador de intentos fallidos consecutivos")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tipo_cambio_fuente'
        verbose_name = 'Fuente de Tipo de Cambio'
        verbose_name_plural = 'Fuentes de Tipo de Cambio'
        ordering = ['orden_prioridad', 'codigo']
        indexes = [
            models.Index(fields=['activa', 'orden_prioridad'], name='tipo_cambio_fuente_activa_idx'),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TipoCambio(models.Model):
    """
    Tabla para almacenar tipos de cambio obtenidos de diferentes fuentes.
    """
    id_tipo_cambio = models.AutoField(primary_key=True)
    id_fuente = models.ForeignKey(
        TipoCambioFuente,
        on_delete=models.RESTRICT,
        db_column='id_fuente',
        related_name='tipos_cambio'
    )
    moneda_origen = models.CharField(max_length=3, help_text="Código ISO de moneda origen (ej: USD)")
    moneda_destino = models.CharField(max_length=3, help_text="Código ISO de moneda destino (ej: CLP)")
    tasa = models.DecimalField(max_digits=20, decimal_places=8, help_text="Tasa de cambio")
    fecha = models.DateField(help_text="Fecha del tipo de cambio")
    vigente_desde = models.DateTimeField(default=timezone.now)
    vigente_hasta = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tipo_cambio'
        verbose_name = 'Tipo de Cambio'
        verbose_name_plural = 'Tipos de Cambio'
        unique_together = [['id_fuente', 'moneda_origen', 'moneda_destino', 'fecha']]
        indexes = [
            models.Index(fields=['moneda_origen', 'moneda_destino', 'fecha'], name='tipo_cambio_monedas_fecha_idx'),
            models.Index(fields=['vigente_desde', 'vigente_hasta'], name='tipo_cambio_vigencia_idx'),
        ]

    def __str__(self):
        return f"{self.moneda_origen}/{self.moneda_destino}: {self.tasa} ({self.fecha})"


