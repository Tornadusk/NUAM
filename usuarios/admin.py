from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django import forms
from core.models import Pais
from .models import Persona, Usuario, Rol, UsuarioRol, Colaborador
from django.contrib.auth.models import User as DjangoUser


class PersonaAdminForm(forms.ModelForm):
    """Formulario de admin para mostrar selects en campos libres."""
    GENERO_CHOICES = (
        ("Masculino", "Masculino"),
        ("Femenino", "Femenino"),
        ("Otro", "Otro"),
    )

    genero = forms.ChoiceField(choices=[("", "Seleccione...")] + list(GENERO_CHOICES), required=False)
    nacionalidad = forms.ChoiceField(choices=[], required=False, help_text="Código ISO‑3166‑1 alpha‑3 (CHL, PER, COL, USA, ...)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar nacionalidades con catálogo de países
        paises = Pais.objects.all().order_by('nombre')
        self.fields['nacionalidad'].choices = [("", "Seleccione...")] + [
            (p.codigo, f"{p.nombre} ({p.codigo})") for p in paises
        ]

    class Meta:
        model = Persona
        fields = '__all__'


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    form = PersonaAdminForm
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


class UsuarioAdminForm(forms.ModelForm):
    """Formulario para enmascarar la contraseña y permitir seteo seguro."""
    password = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text='Dejar vacío para mantener la contraseña actual.'
    )

    class Meta:
        model = Usuario
        exclude = ('hash_password',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm
    list_display = ('id_usuario', 'username', 'nombre_completo', 'estado', 'tiene_colaborador', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('username', 'id_persona__primer_nombre', 'id_persona__apellido_paterno')
    list_filter = ('estado', 'creado_en')
    # Permite buscar personas por nombre/apellido y seleccionar con autocompletado
    autocomplete_fields = ('id_persona',)
    inlines = [UsuarioRolInline]
    actions = ['activar_usuarios', 'bloquear_usuarios']
    ordering = ('username',)
    list_display_links = ('id_usuario', 'username')
    date_hierarchy = 'creado_en'
    fieldsets = (
        ('Datos del Usuario', {
            'fields': ('id_persona', 'username', 'estado', 'password')
        }),
    )

    class Media:
        js = ('js/admin_usuario_password.js',)

    def save_related(self, request, form, formsets, change):
        """Después de guardar inlines (roles), sincronizar is_staff en auth_user."""
        super().save_related(request, form, formsets, change)
        obj = form.instance
        try:
            from django.contrib.auth.models import User as DjangoUser
            django_user = DjangoUser.objects.get(username=obj.username)
            tiene_admin = obj.usuariorol_set.filter(id_rol__nombre='Administrador').exists()
            if django_user.is_staff != tiene_admin:
                django_user.is_staff = tiene_admin
                django_user.save(update_fields=['is_staff'])
        except Exception:
            pass

    def delete_model(self, request, obj):
        """Eliminar también el usuario de auth_user al borrar desde Admin."""
        try:
            from django.contrib.auth.models import User as DjangoUser
            DjangoUser.objects.filter(username=obj.username).delete()
        except Exception:
            pass
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Eliminar en bloque usuarios de auth_user correspondientes."""
        try:
            from django.contrib.auth.models import User as DjangoUser
            usernames = list(queryset.values_list('username', flat=True))
            if usernames:
                DjangoUser.objects.filter(username__in=usernames).delete()
        except Exception:
            pass
        super().delete_queryset(request, queryset)

    def save_model(self, request, obj, form, change):
        # Si se ingresó una contraseña en el admin, setearla con hash seguro
        password = form.cleaned_data.get('password')
        if password:
            obj.set_password(password)
        super().save_model(request, obj, form, change)

        # Sincronizar con django.contrib.auth.User para permitir login
        django_user, created = DjangoUser.objects.get_or_create(
            username=obj.username,
            defaults={
                'is_active': obj.estado == 'activo',
            }
        )
        # Si hay password en el formulario, actualizarlo también en auth
        if password:
            django_user.set_password(password)
        # Mantener estado activo según modelo
        django_user.is_active = obj.estado == 'activo'
        django_user.save()
    
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