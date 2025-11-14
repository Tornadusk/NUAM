from django.db import models
from core.models import Moneda, Mercado


class Instrumento(models.Model):
    id_instrumento = models.AutoField(primary_key=True)
    id_mercado = models.ForeignKey(Mercado, on_delete=models.RESTRICT, db_column='id_mercado')
    codigo = models.CharField(max_length=60, unique=True, null=False)
    nombre = models.CharField(max_length=150, null=False)
    tipo = models.CharField(max_length=60, null=True, blank=True)
    emisor = models.CharField(max_length=100, null=True, blank=True)
    id_moneda = models.ForeignKey(Moneda, on_delete=models.RESTRICT, db_column='id_moneda')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'instrumento'
        verbose_name = 'Instrumento'
        verbose_name_plural = 'Instrumentos'
        ordering = ['codigo']
        indexes = [
            # models.Index(fields=['codigo']),  # COMENTADO: Oracle crea automáticamente índice único para campos UNIQUE
            models.Index(fields=['id_mercado']),  # Foreign Key - importante para JOINs
            models.Index(fields=['id_moneda']),  # Foreign Key - importante para JOINs
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class EventoCapital(models.Model):
    id_evento = models.AutoField(primary_key=True)
    id_instrumento = models.ForeignKey(
        Instrumento,
        on_delete=models.CASCADE,
        db_column='id_instrumento'
    )
    secuencia_evento = models.CharField(max_length=40, null=False)
    fecha_pago = models.DateField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    valor_historico = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'evento_capital'
        verbose_name = 'Evento de Capital'
        verbose_name_plural = 'Eventos de Capital'
        unique_together = [['id_instrumento', 'secuencia_evento']]
        indexes = [
            models.Index(fields=['id_instrumento']),  # Foreign Key - importante para JOINs
            # models.Index(fields=['id_instrumento', 'secuencia_evento']),  # COMENTADO: Oracle crea automáticamente índice único para unique_together
        ]

    def __str__(self):
        return f"{self.id_instrumento.codigo} - {self.secuencia_evento}"