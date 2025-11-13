from django.db import models
from .fields import OracleJSONField


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
    valores_antes = OracleJSONField(null=True, blank=True)
    valores_despues = OracleJSONField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auditoria'
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-fecha', '-id_auditoria']
        # Índices:
        # - actor_id ya tiene índice ix_aud_actor en Oracle (creado por cretable_oracle, línea 408)
        # - (entidad, entidad_id) ya tiene índice ix_aud_entidad en Oracle (creado por cretable_oracle, línea 409)
        # - fecha ya tiene índice ix_aud_fecha en Oracle (creado por cretable_oracle, línea 410)
        indexes = [
            # models.Index(fields=['actor_id']),  # Ya existe: ix_aud_actor (en cretable_oracle)
            # models.Index(fields=['entidad', 'entidad_id']),  # Ya existe: ix_aud_entidad (en cretable_oracle)
            # models.Index(fields=['fecha']),  # Ya existe: ix_aud_fecha (en cretable_oracle)
            # COMENTADOS: Si obtienes ORA-01408, significa que los índices ya existen en Oracle.
            # Si necesitas crearlos, descomenta estas líneas y genera las migraciones.
        ]

    def __str__(self):
        return f"{self.accion} - {self.entidad} #{self.entidad_id}"