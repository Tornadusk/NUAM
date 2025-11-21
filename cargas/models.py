from django.db import models


class Carga(models.Model):
    id_carga = models.BigAutoField(primary_key=True)
    id_corredora = models.ForeignKey(
        'corredoras.Corredora',
        on_delete=models.RESTRICT,
        db_column='id_corredora'
    )
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.RESTRICT,
        db_column='creado_por'
    )
    id_fuente = models.ForeignKey(
        'core.Fuente',
        on_delete=models.RESTRICT,
        db_column='id_fuente'
    )
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual'),
            ('masiva', 'Masiva'),
        ]
    )
    nombre_archivo = models.CharField(max_length=255, null=True, blank=True)
    filas_total = models.IntegerField(default=0)
    insertados = models.IntegerField(default=0)
    actualizados = models.IntegerField(default=0)
    rechazados = models.IntegerField(default=0)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('validando', 'Validando'),
            ('importando', 'Importando'),
            ('reconciliando', 'Reconciliando'),
            ('done', 'Completada'),
            ('failed', 'Fallida'),
        ]
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carga'
        verbose_name = 'Carga'
        verbose_name_plural = 'Cargas'
        indexes = [
            # COMENTADO: Oracle crea automáticamente índices para Foreign Keys
            # Los índices en id_corredora, id_fuente, creado_por ya existen automáticamente en Oracle
            models.Index(fields=['estado']),  # Campo normal - importante para consultas por estado
        ]

    def __str__(self):
        return f"Carga #{self.id_carga} - {self.nombre_archivo or 'Sin archivo'}"


class CargaDetalle(models.Model):
    id_detalle = models.BigAutoField(primary_key=True)
    id_carga = models.ForeignKey(Carga, on_delete=models.CASCADE, db_column='id_carga')
    linea = models.IntegerField()
    estado_linea = models.CharField(
        max_length=20,
        choices=[
            ('ok', 'OK'),
            ('rechazo', 'Rechazo'),
        ]
    )
    mensaje_error = models.TextField(null=True, blank=True)
    id_calificacion = models.ForeignKey(
        'calificaciones.Calificacion',
        on_delete=models.SET_NULL,
        db_column='id_calificacion',
        null=True,
        blank=True
    )
    hash_linea = models.CharField(max_length=64, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carga_detalle'
        verbose_name = 'Detalle Carga'
        verbose_name_plural = 'Detalles Cargas'
        unique_together = [
            ['id_carga', 'linea'],
            ['id_carga', 'hash_linea']
        ]
        indexes = [
            # COMENTADO: Oracle crea automáticamente índice para Foreign Key id_carga
            # models.Index(fields=['id_carga', 'linea']),  # COMENTADO: Oracle crea automáticamente índice único para unique_together
        ]

    def __str__(self):
        return f"Línea {self.linea} - {self.estado_linea}"


class HomologacionCampo(models.Model):
    """
    Tabla para homologar/mapear campos de diferentes formatos de archivo CSV/Excel.
    Permite configurar transformaciones de campos entre origen y destino.
    """
    id_homologacion = models.AutoField(primary_key=True)
    origen = models.CharField(max_length=10, null=True, blank=True, help_text="Código del formato origen")
    certificado = models.CharField(max_length=10, null=True, blank=True, help_text="Código del certificado")
    campo_origen = models.CharField(max_length=120, null=True, blank=True, help_text="Nombre del campo en el origen")
    campo_destino = models.CharField(max_length=120, null=True, blank=True, help_text="Nombre del campo destino")
    transform = models.CharField(max_length=200, null=True, blank=True, help_text="Regla de transformación a aplicar")
    obligatorio = models.BooleanField(default=False, help_text="Indica si el campo es obligatorio")
    vigente_desde = models.DateField(null=True, blank=True, help_text="Fecha desde la cual es válida la homologación")
    vigente_hasta = models.DateField(null=True, blank=True, help_text="Fecha hasta la cual es válida la homologación")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'homologacion_campo'
        verbose_name = 'Homologación Campo'
        verbose_name_plural = 'Homologaciones Campos'
        ordering = ['origen', 'certificado', 'campo_origen']
        indexes = [
            # Índice compuesto para búsquedas por origen y certificado
            models.Index(fields=['origen', 'certificado']),
            # Índice compuesto para consultas de vigencia por rango de fechas
            models.Index(fields=['vigente_desde', 'vigente_hasta']),
            # NOTA: Esta tabla no tiene Foreign Keys ni campos UNIQUE,
            # por lo que no hay índices automáticos de Oracle
        ]

    def __str__(self):
        if self.origen and self.campo_origen:
            return f"{self.origen}.{self.certificado or 'N/A'}: {self.campo_origen} → {self.campo_destino or 'N/A'}"
        return f"Homologación #{self.id_homologacion}"

    @property
    def esta_vigente(self):
        """Verifica si la homologación está vigente en la fecha actual"""
        from django.utils import timezone
        hoy = timezone.now().date()
        if self.vigente_desde and self.vigente_desde > hoy:
            return False
        if self.vigente_hasta and self.vigente_hasta < hoy:
            return False
        return True