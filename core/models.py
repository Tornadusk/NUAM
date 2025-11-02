from django.db import models


# ========= ENUMS =========
class TipoDocumento(models.TextChoices):
    RUT = 'RUT', 'RUT'  # Chile
    DNI = 'DNI', 'DNI'  # Perú
    CC = 'CC', 'CC'  # Colombia (Cédula de Ciudadanía)
    CE = 'CE', 'CE'  # Cédula/Carné de Extranjería
    PASAPORTE = 'PASAPORTE', 'Pasaporte'


class EstadoCorredora(models.TextChoices):
    ACTIVA = 'activa', 'Activa'
    INACTIVA = 'inactiva', 'Inactiva'


class EstadoUsuario(models.TextChoices):
    ACTIVO = 'activo', 'Activo'
    BLOQUEADO = 'bloqueado', 'Bloqueado'


class EstadoCalificacion(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'
    VALIDADA = 'validada', 'Validada'
    PUBLICADA = 'publicada', 'Publicada'
    PENDIENTE = 'pendiente', 'Pendiente'


class TipoCarga(models.TextChoices):
    MANUAL = 'manual', 'Manual'
    MASIVA = 'masiva', 'Masiva'


class EstadoCarga(models.TextChoices):
    VALIDANDO = 'validando', 'Validando'
    IMPORTANDO = 'importando', 'Importando'
    RECONCILIANDO = 'reconciliando', 'Reconciliando'
    DONE = 'done', 'Completada'
    FAILED = 'failed', 'Fallida'


class EstadoLinea(models.TextChoices):
    OK = 'ok', 'OK'
    RECHAZO = 'rechazo', 'Rechazo'


class TipoValorFactor(models.TextChoices):
    FACTOR = 'factor', 'Factor'
    MONTO = 'monto', 'Monto'
    TASA = 'tasa', 'Tasa'


class EntidadAuditoria(models.TextChoices):
    CALIFICACION = 'CALIFICACION', 'Calificación'
    CARGA = 'CARGA', 'Carga'
    CARGA_DETALLE = 'CARGA_DETALLE', 'Carga Detalle'
    INSTRUMENTO = 'INSTRUMENTO', 'Instrumento'
    USUARIO = 'USUARIO', 'Usuario'
    OTRA = 'OTRA', 'Otra'


# ========= CORE MODELS =========
class Pais(models.Model):
    id_pais = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=3, unique=True, null=False)  # ISO-3166-1 alpha-3
    nombre = models.CharField(max_length=100, null=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pais'
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Moneda(models.Model):
    id_moneda = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=3, unique=True, null=False)  # ISO-4217
    nombre = models.CharField(max_length=60, null=False)
    decimales = models.SmallIntegerField(default=2, null=False)
    vigente = models.BooleanField(default=True, null=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'moneda'
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MonedaPais(models.Model):
    id_moneda_pais = models.AutoField(primary_key=True)
    id_moneda = models.ForeignKey(Moneda, on_delete=models.CASCADE, db_column='id_moneda')
    id_pais = models.ForeignKey(Pais, on_delete=models.CASCADE, db_column='id_pais')
    vigente_desde = models.DateField(null=True, blank=True)
    vigente_hasta = models.DateField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'moneda_pais'
        verbose_name = 'Moneda por País'
        verbose_name_plural = 'Monedas por País'
        unique_together = [['id_moneda', 'id_pais']]
        indexes = [
            models.Index(fields=['id_moneda', 'id_pais']),
            models.Index(fields=['id_pais']),
        ]

    def __str__(self):
        return f"{self.id_moneda.codigo} en {self.id_pais.codigo}"


class Mercado(models.Model):
    id_mercado = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=30, unique=True, null=False)
    nombre = models.CharField(max_length=120, null=False)
    id_pais = models.ForeignKey(Pais, on_delete=models.RESTRICT, db_column='id_pais')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mercado'
        verbose_name = 'Mercado'
        verbose_name_plural = 'Mercados'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['id_pais']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Fuente(models.Model):
    id_fuente = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=30, unique=True, null=False)
    nombre = models.CharField(max_length=80, null=False)
    descripcion = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fuente'
        verbose_name = 'Fuente'
        verbose_name_plural = 'Fuentes'
        indexes = [
            models.Index(fields=['codigo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"