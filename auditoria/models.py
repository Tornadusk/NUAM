from django.db import models


class Auditoria(models.Model):
    id_auditoria = models.BigAutoField(primary_key=True)
    actor_id = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        db_column='actor_id',
        null=True,
        blank=True
    )
    entidad = models.CharField(
        max_length=30,
        choices=[
            ('CALIFICACION', 'Calificación'),
            ('CARGA', 'Carga'),
            ('CARGA_DETALLE', 'Carga Detalle'),
            ('INSTRUMENTO', 'Instrumento'),
            ('USUARIO', 'Usuario'),
            ('OTRA', 'Otra'),
        ]
    )
    entidad_id = models.BigIntegerField()
    accion = models.CharField(max_length=20)  # INSERT, UPDATE, DELETE, etc.
    fecha = models.DateTimeField(auto_now_add=True)
    fuente = models.CharField(max_length=50, null=True, blank=True)
    valores_antes = models.JSONField(null=True, blank=True)
    valores_despues = models.JSONField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auditoria'
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-fecha', '-id_auditoria']
        indexes = [
            models.Index(fields=['actor_id']),
            models.Index(fields=['entidad', 'entidad_id']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f"{self.accion} - {self.entidad} #{self.entidad_id}"