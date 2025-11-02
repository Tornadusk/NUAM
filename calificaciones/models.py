from django.db import models
from core.models import Moneda


class FactorDef(models.Model):
    id_factor = models.AutoField(primary_key=True)
    codigo_factor = models.CharField(max_length=10, unique=True, null=False)
    nombre_corto = models.CharField(max_length=40, null=False)
    descripcion = models.TextField(null=True, blank=True)
    tipo_valor = models.CharField(
        max_length=20,
        choices=[
            ('factor', 'Factor'),
            ('monto', 'Monto'),
            ('tasa', 'Tasa'),
        ],
        default='factor'
    )
    orden_visual = models.IntegerField(null=True, blank=True)
    aplica_en_suma = models.BooleanField(default=False)
    vigente_desde = models.DateField(null=True, blank=True)
    vigente_hasta = models.DateField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'factor_def'
        verbose_name = 'Factor'
        verbose_name_plural = 'Factores'
        ordering = ['codigo_factor']
        indexes = [
            models.Index(fields=['codigo_factor']),
        ]

    def __str__(self):
        return f"{self.codigo_factor} - {self.nombre_corto}"


class Calificacion(models.Model):
    id_calificacion = models.BigAutoField(primary_key=True)
    id_corredora = models.ForeignKey(
        'corredoras.Corredora',
        on_delete=models.RESTRICT,
        db_column='id_corredora'
    )
    id_instrumento = models.ForeignKey(
        'instrumentos.Instrumento',
        on_delete=models.RESTRICT,
        db_column='id_instrumento'
    )
    id_fuente = models.ForeignKey(
        'core.Fuente',
        on_delete=models.RESTRICT,
        db_column='id_fuente'
    )
    id_evento = models.ForeignKey(
        'instrumentos.EventoCapital',
        on_delete=models.SET_NULL,
        db_column='id_evento',
        null=True,
        blank=True
    )
    ejercicio = models.IntegerField(null=True, blank=True)
    fecha_pago = models.DateField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    secuencia_evento = models.CharField(max_length=40, null=True, blank=True)
    factor_actualizacion = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    valor_historico = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    ingreso_por_montos = models.BooleanField(null=True, blank=True)
    acogido_sfut = models.BooleanField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('borrador', 'Borrador'),
            ('validada', 'Validada'),
            ('publicada', 'Publicada'),
            ('pendiente', 'Pendiente'),
        ],
        default='borrador'
    )
    observaciones = models.TextField(null=True, blank=True)
    id_moneda = models.ForeignKey(Moneda, on_delete=models.RESTRICT, db_column='id_moneda')
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.RESTRICT,
        db_column='creado_por',
        related_name='calificaciones_creadas'
    )
    actualizado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.RESTRICT,
        db_column='actualizado_por',
        related_name='calificaciones_actualizadas'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calificacion'
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        ordering = ['-creado_en', '-id_calificacion']
        unique_together = [['id_corredora', 'id_instrumento', 'ejercicio', 'secuencia_evento']]
        indexes = [
            models.Index(fields=['id_corredora']),
            models.Index(fields=['id_instrumento']),
            models.Index(fields=['id_fuente']),
            models.Index(fields=['id_evento']),
        ]

    def __str__(self):
        return f"Calif #{self.id_calificacion} - {self.id_instrumento.codigo}"


class CalificacionMontoDetalle(models.Model):
    id_calificacion = models.ForeignKey(
        Calificacion,
        on_delete=models.CASCADE,
        db_column='id_calificacion'
    )
    id_factor = models.ForeignKey(
        FactorDef,
        on_delete=models.RESTRICT,
        db_column='id_factor'
    )
    valor_monto = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calificacion_monto_detalle'
        verbose_name = 'Detalle Monto Calificación'
        verbose_name_plural = 'Detalles Montos Calificaciones'
        unique_together = [['id_calificacion', 'id_factor']]
        indexes = [
            models.Index(fields=['id_calificacion']),
            models.Index(fields=['id_factor']),
        ]

    def __str__(self):
        return f"Detalle Monto {self.id_factor.codigo_factor} - {self.id_calificacion.id_calificacion}"


class CalificacionFactorDetalle(models.Model):
    id_calificacion = models.ForeignKey(
        Calificacion,
        on_delete=models.CASCADE,
        db_column='id_calificacion'
    )
    id_factor = models.ForeignKey(
        FactorDef,
        on_delete=models.RESTRICT,
        db_column='id_factor'
    )
    valor_factor = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calificacion_factor_detalle'
        verbose_name = 'Detalle Factor Calificación'
        verbose_name_plural = 'Detalles Factores Calificaciones'
        unique_together = [['id_calificacion', 'id_factor']]
        indexes = [
            models.Index(fields=['id_calificacion']),
            models.Index(fields=['id_factor']),
        ]

    def __str__(self):
        return f"Detalle Factor {self.id_factor.codigo_factor} - {self.id_calificacion.id_calificacion}"