from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from core.models import Pais


class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)
    primer_nombre = models.CharField(max_length=80, null=False)
    segundo_nombre = models.CharField(max_length=80, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=80, null=False)
    apellido_materno = models.CharField(max_length=80, null=True, blank=True)
    genero = models.CharField(max_length=30, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=False)
    nacionalidad = models.CharField(max_length=3, null=True, blank=True)  # ISO-3166-1 alpha-3
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'persona'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        indexes = [
            models.Index(fields=['apellido_paterno', 'apellido_materno']),
        ]

    def __str__(self):
        return f"{self.primer_nombre} {self.apellido_paterno}"

    @property
    def nombre_completo(self):
        nombres = f"{self.primer_nombre} {self.segundo_nombre or ''}".strip()
        apellidos = f"{self.apellido_paterno} {self.apellido_materno or ''}".strip()
        return f"{nombres} {apellidos}"


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(Persona, on_delete=models.RESTRICT, db_column='id_persona')
    username = models.CharField(max_length=60, unique=True, null=False)
    hash_password = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('bloqueado', 'Bloqueado'),
        ],
        default='activo'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        # Índices comentados porque:
        # - username es UNIQUE, Oracle crea automáticamente un índice único
        # - id_persona ya tiene índice ix_usuario_persona en Oracle (creado por cretable_oracle, línea 111)
        # Crear estos índices manualmente causa error ORA-01408: "esta lista de columnas ya está indexada"
        # indexes = [
        #     models.Index(fields=['username']),  # Índice automático por UNIQUE constraint
        #     models.Index(fields=['id_persona']),  # Ya existe: ix_usuario_persona
        # ]

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        """Hash y guarda la contraseña"""
        self.hash_password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Verifica si la contraseña es correcta"""
        if self.hash_password:
            return check_password(raw_password, self.hash_password)
        return False


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True, null=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class UsuarioRol(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, db_column='id_rol')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuario_rol'
        verbose_name = 'Usuario Rol'
        verbose_name_plural = 'Usuario Roles'
        unique_together = [['id_usuario', 'id_rol']]
        # Índices:
        # - (id_usuario, id_rol) tiene UNIQUE constraint, Oracle crea automáticamente un índice único
        # - id_rol ya tiene índice ix_usuario_rol_rol en cretable_oracle (línea 132)
        indexes = [
            # models.Index(fields=['id_usuario', 'id_rol']),  # COMENTADO: Oracle crea automáticamente índice único para unique_together
            # COMENTADO: Oracle crea automáticamente índice para Foreign Key id_rol
        ]

    def __str__(self):
        return f"{self.id_usuario.username} - {self.id_rol.nombre}"


class Colaborador(models.Model):
    id_colaborador = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        null=False,
        unique=True
    )
    gmail = models.EmailField(max_length=254, unique=True, null=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'colaborador'
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'

    def __str__(self):
        return f"{self.id_usuario.username} - {self.gmail}"