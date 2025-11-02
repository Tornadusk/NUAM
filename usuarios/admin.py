from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import Persona, Usuario, Rol, UsuarioRol, Colaborador


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id_persona', 'primer_nombre', 'apellido_paterno', 'fecha_nacimiento', 'genero', 'nacionalidad', 'edad', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno')
    list_filter = ('fecha_nacimiento', 'genero', 'nacionalidad', 'creado_en')
    ordering = ('apellido_paterno', 'primer_nombre')
    list_display_links = ('id_persona', 'primer_nombre')
    date_hierarchy = 'creado_en'
    
    def edad(self, obj):
        """Calcula la edad de la persona"""
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - obj.fecha_nacimiento.year - ((today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day))
        return '-'
    edad.short_description = 'Edad'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/usuarios/persona/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre', 'cantidad_usuarios', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    list_display_links = ('id_rol', 'nombre')
    list_filter = ('creado_en',)
    date_hierarchy = 'creado_en'
    
    def cantidad_usuarios(self, obj):
        """Muestra cantidad de usuarios con este rol"""
        return obj.usuariorol_set.count()
    cantidad_usuarios.short_description = 'Usuarios'
    
    def editar(self, obj):
        """Link para editar el registro"""
        if obj.pk:
            return format_html('<a href="/admin/usuarios/rol/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 1


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'username', 'nombre_completo', 'estado', 'tiene_colaborador', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('username', 'id_persona__primer_nombre', 'id_persona__apellido_paterno')
    list_filter = ('estado', 'creado_en')
    raw_id_fields = ('id_persona',)
    inlines = [UsuarioRolInline]
    actions = ['activar_usuarios', 'bloquear_usuarios']
    ordering = ('username',)
    list_display_links = ('id_usuario', 'username')
    date_hierarchy = 'creado_en'
    
    def nombre_completo(self, obj):
        """Muestra el nombre completo de la persona"""
        if obj.id_persona:
            return f"{obj.id_persona.primer_nombre} {obj.id_persona.apellido_paterno}"
        return '-'
    nombre_completo.short_description = 'Nombre'
    
    def tiene_colaborador(self, obj):
        """Indica si el usuario tiene datos de colaborador"""
        return hasattr(obj, 'colaborador')
    tiene_colaborador.short_description = 'Colaborador'
    tiene_colaborador.boolean = True
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/usuarios/usuario/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''
    
    @admin.action(description='Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        """Acción para activar usuarios"""
        updated = queryset.update(estado='activo')
        self.message_user(request, f'{updated} usuario(s) activado(s).', messages.SUCCESS)
    
    @admin.action(description='Bloquear usuarios seleccionados')
    def bloquear_usuarios(self, request, queryset):
        """Acción para bloquear usuarios"""
        updated = queryset.update(estado='bloqueado')
        self.message_user(request, f'{updated} usuario(s) bloqueado(s).', messages.WARNING)


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_usuario', 'id_rol', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_usuario__username', 'id_rol__nombre')
    list_filter = ('id_rol', 'creado_en')
    ordering = ('id_usuario', 'id_rol')
    list_display_links = ('id_usuario', 'id_rol')
    date_hierarchy = 'creado_en'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/usuarios/usuariorol/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('id_colaborador', 'id_usuario', 'gmail', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_usuario__username', 'gmail')
    raw_id_fields = ('id_usuario',)
    ordering = ('id_usuario',)
    list_display_links = ('id_colaborador', 'id_usuario')
    date_hierarchy = 'creado_en'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/usuarios/colaborador/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''