from django.db import models
from core.models import Pais


class Corredora(models.Model):
    id_corredora = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, null=False)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activa', 'Activa'),
            ('inactiva', 'Inactiva'),
        ],
        default='activa'
    )
    id_pais = models.ForeignKey(Pais, on_delete=models.RESTRICT, db_column='id_pais')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'corredora'
        verbose_name = 'Corredora'
        verbose_name_plural = 'Corredoras'
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['id_pais']),
        ]

    def __str__(self):
        return self.nombre


class CorredoraIdentificador(models.Model):
    id = models.AutoField(primary_key=True)
    id_corredora = models.ForeignKey(Corredora, on_delete=models.CASCADE, db_column='id_corredora')
    tipo = models.CharField(max_length=10, null=False)  # RUT, RUC, NIT
    numero = models.CharField(max_length=30, null=False)
    id_pais = models.ForeignKey(Pais, on_delete=models.RESTRICT, db_column='id_pais', null=False)
    es_principal = models.BooleanField(default=True, null=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'corredora_identificador'
        verbose_name = 'Identificador Corredora'
        verbose_name_plural = 'Identificadores Corredoras'
        unique_together = [['tipo', 'numero', 'id_pais']]
        indexes = [
            models.Index(fields=['tipo', 'numero', 'id_pais']),
            models.Index(fields=['id_corredora']),
        ]

    def __str__(self):
        return f"{self.tipo} {self.numero}"


class UsuarioCorredora(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        db_column='id_usuario'
    )
    id_corredora = models.ForeignKey(
        Corredora,
        on_delete=models.RESTRICT,
        db_column='id_corredora'
    )
    es_principal = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuario_corredora'
        verbose_name = 'Usuario Corredora'
        verbose_name_plural = 'Usuario Corredoras'
        unique_together = [['id_usuario', 'id_corredora']]
        indexes = [
            models.Index(fields=['id_usuario', 'id_corredora']),
            models.Index(fields=['id_usuario']),
            models.Index(fields=['id_corredora']),
        ]

    def __str__(self):
        return f"{self.id_usuario.username} - {self.id_corredora.nombre}"