from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import Pais, Moneda, MonedaPais, Mercado, Fuente


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'creado_en', 'actualizado_en', 'cantidad_mercados', 'editar')
    search_fields = ('codigo', 'nombre')
    list_filter = ('creado_en',)
    ordering = ('codigo',)
    list_display_links = ('codigo', 'nombre')
    date_hierarchy = 'creado_en'
    
    def cantidad_mercados(self, obj):
        """Muestra cantidad de mercados asociados"""
        return obj.mercado_set.count()
    cantidad_mercados.short_description = 'Mercados'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/core/pais/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'decimales', 'vigente', 'cantidad_paises', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('codigo', 'nombre')
    list_filter = ('vigente', 'creado_en')
    ordering = ('codigo',)
    list_display_links = ('codigo', 'nombre')
    actions = ['marcar_como_vigente', 'marcar_como_no_vigente']
    date_hierarchy = 'creado_en'
    
    def cantidad_paises(self, obj):
        """Muestra cantidad de países donde se usa la moneda"""
        return obj.monedapais_set.count()
    cantidad_paises.short_description = 'Paises'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/core/moneda/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''
    
    @admin.action(description='Marcar como vigente')
    def marcar_como_vigente(self, request, queryset):
        """Acción para marcar monedas como vigentes"""
        updated = queryset.update(vigente=True)
        self.message_user(request, f'{updated} moneda(s) marcada(s) como vigente(s).', messages.SUCCESS)
    
    @admin.action(description='Marcar como no vigente')
    def marcar_como_no_vigente(self, request, queryset):
        """Acción para marcar monedas como no vigentes"""
        updated = queryset.update(vigente=False)
        self.message_user(request, f'{updated} moneda(s) marcada(s) como no vigente(s).', messages.WARNING)


@admin.register(MonedaPais)
class MonedaPaisAdmin(admin.ModelAdmin):
    list_display = ('id_moneda', 'id_pais', 'vigente_desde', 'vigente_hasta', 'esta_vigente', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_moneda__codigo', 'id_moneda__nombre', 'id_pais__codigo', 'id_pais__nombre')
    list_filter = ('vigente_desde', 'vigente_hasta', 'id_moneda', 'id_pais')
    raw_id_fields = ('id_moneda', 'id_pais')
    ordering = ('id_pais', 'id_moneda')
    list_display_links = ('id_moneda', 'id_pais')
    date_hierarchy = 'creado_en'
    
    def esta_vigente(self, obj):
        """Indica si la moneda está vigente en el país"""
        if obj.vigente_desde or obj.vigente_hasta:
            return "Sí"
        return "-"
    esta_vigente.short_description = 'Vigente'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/core/monedapais/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'id_pais', 'cantidad_instrumentos', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('codigo', 'nombre', 'id_pais__nombre')
    list_filter = ('id_pais', 'creado_en')
    raw_id_fields = ('id_pais',)
    ordering = ('id_pais', 'codigo')
    list_display_links = ('codigo', 'nombre')
    date_hierarchy = 'creado_en'
    
    def cantidad_instrumentos(self, obj):
        """Muestra cantidad de instrumentos en el mercado"""
        return obj.instrumento_set.count()
    cantidad_instrumentos.short_description = 'Instrumentos'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/core/mercado/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(Fuente)
class FuenteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'cantidad_calificaciones', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('codigo', 'nombre')
    list_filter = ('creado_en',)
    ordering = ('codigo',)
    list_display_links = ('codigo', 'nombre')
    date_hierarchy = 'creado_en'
    
    def cantidad_calificaciones(self, obj):
        """Muestra cantidad de calificaciones de esta fuente"""
        return obj.calificacion_set.count()
    cantidad_calificaciones.short_description = 'Calificaciones'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/core/fuente/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''