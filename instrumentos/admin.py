from django.contrib import admin
from django.utils.html import format_html
from .models import Instrumento, EventoCapital


class EventoCapitalInline(admin.TabularInline):
    model = EventoCapital
    extra = 1


@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ('id_instrumento', 'codigo', 'nombre', 'tipo', 'id_mercado', 'id_moneda', 'cantidad_eventos', 'cantidad_calificaciones', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('codigo', 'nombre', 'emisor', 'isin')
    list_filter = ('tipo', 'id_mercado', 'id_moneda')
    raw_id_fields = ('id_mercado', 'id_moneda')
    inlines = [EventoCapitalInline]
    ordering = ('codigo',)
    list_display_links = ('id_instrumento', 'codigo')
    date_hierarchy = 'creado_en'
    
    def cantidad_eventos(self, obj):
        """Muestra cantidad de eventos de capital"""
        return obj.eventocapital_set.count()
    cantidad_eventos.short_description = 'Eventos'
    
    def cantidad_calificaciones(self, obj):
        """Muestra cantidad de calificaciones asociadas"""
        return obj.calificacion_set.count()
    cantidad_calificaciones.short_description = 'Calificaciones'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/instrumentos/instrumento/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(EventoCapital)
class EventoCapitalAdmin(admin.ModelAdmin):
    list_display = ('id_evento', 'id_instrumento', 'secuencia_evento', 'fecha_pago', 'valor_historico', 'descripcion_corta', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_instrumento__codigo', 'secuencia_evento', 'descripcion')
    list_filter = ('fecha_pago',)
    raw_id_fields = ('id_instrumento',)
    ordering = ('-fecha_pago', 'id_instrumento')
    date_hierarchy = 'fecha_pago'
    list_display_links = ('id_evento', 'secuencia_evento')
    
    def descripcion_corta(self, obj):
        """Muestra descripción truncada"""
        if obj.descripcion:
            return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
        return '-'
    descripcion_corta.short_description = 'Descripción'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/instrumentos/eventocapital/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''