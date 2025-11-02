from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import Corredora, CorredoraIdentificador, UsuarioCorredora


class CorredoraIdentificadorInline(admin.TabularInline):
    model = CorredoraIdentificador
    extra = 1


@admin.register(Corredora)
class CorredoraAdmin(admin.ModelAdmin):
    list_display = ('id_corredora', 'nombre', 'estado', 'id_pais', 'cantidad_identificadores', 'cantidad_usuarios', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('nombre',)
    list_filter = ('estado', 'id_pais', 'creado_en')
    raw_id_fields = ('id_pais',)
    inlines = [CorredoraIdentificadorInline]
    actions = ['activar_corredoras', 'desactivar_corredoras']
    ordering = ('nombre',)
    list_display_links = ('id_corredora', 'nombre')
    date_hierarchy = 'creado_en'
    
    def cantidad_identificadores(self, obj):
        """Muestra cantidad de identificadores fiscales"""
        return obj.corredoraidentificador_set.count()
    cantidad_identificadores.short_description = 'Identificadores'
    
    def cantidad_usuarios(self, obj):
        """Muestra cantidad de usuarios asociados"""
        return obj.usuariocorredora_set.count()
    cantidad_usuarios.short_description = 'Usuarios'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/corredoras/corredora/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''
    
    @admin.action(description='Activar corredoras')
    def activar_corredoras(self, request, queryset):
        """Acción para activar corredoras"""
        updated = queryset.update(estado='activa')
        self.message_user(request, f'{updated} corredora(s) activada(s).', messages.SUCCESS)
    
    @admin.action(description='Desactivar corredoras')
    def desactivar_corredoras(self, request, queryset):
        """Acción para desactivar corredoras"""
        updated = queryset.update(estado='inactiva')
        self.message_user(request, f'{updated} corredora(s) desactivada(s).', messages.WARNING)


@admin.register(CorredoraIdentificador)
class CorredoraIdentificadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_corredora', 'tipo', 'numero', 'id_pais', 'es_principal', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('tipo', 'numero', 'id_corredora__nombre')
    list_filter = ('tipo', 'es_principal', 'id_pais')
    raw_id_fields = ('id_corredora', 'id_pais')
    ordering = ('id_corredora', 'tipo')
    list_display_links = ('id', 'tipo')
    date_hierarchy = 'creado_en'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/corredoras/corredoraidentificador/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(UsuarioCorredora)
class UsuarioCorredoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_usuario', 'id_corredora', 'es_principal', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_usuario__username', 'id_corredora__nombre')
    list_filter = ('es_principal', 'creado_en', 'id_corredora')
    raw_id_fields = ('id_usuario', 'id_corredora')
    ordering = ('id_corredora', 'id_usuario')
    list_display_links = ('id_usuario', 'id_corredora')
    date_hierarchy = 'creado_en'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/corredoras/usuariocorredora/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''