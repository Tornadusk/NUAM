from django.contrib import admin
from django.utils.html import format_html
from .models import TipoCambioFuente, TipoCambio


@admin.register(TipoCambioFuente)
class TipoCambioFuenteAdmin(admin.ModelAdmin):
    list_display = ('id_fuente', 'codigo', 'nombre', 'activa', 'orden_prioridad', 'ultima_consulta_exitosa', 'intentos_fallidos', 'estado_fuente', 'creado_en')
    search_fields = ('codigo', 'nombre', 'url_api')
    list_filter = ('activa', 'creado_en')
    ordering = ('orden_prioridad', 'codigo')
    readonly_fields = ('ultima_consulta_exitosa', 'ultima_consulta_fallida', 'intentos_fallidos', 'creado_en', 'actualizado_en')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'activa', 'orden_prioridad')
        }),
        ('Configuración API', {
            'fields': ('url_api', 'api_key'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('ultima_consulta_exitosa', 'ultima_consulta_fallida', 'intentos_fallidos'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_fuente(self, obj):
        """Muestra el estado visual de la fuente"""
        if obj.activa:
            if obj.intentos_fallidos == 0:
                return format_html('<span style="color: green;">✓ Activa</span>')
            elif obj.intentos_fallidos < 3:
                return format_html('<span style="color: orange;">⚠ Advertencia</span>')
            else:
                return format_html('<span style="color: red;">✗ Fallida</span>')
        return format_html('<span style="color: gray;">○ Inactiva</span>')
    estado_fuente.short_description = 'Estado'


@admin.register(TipoCambio)
class TipoCambioAdmin(admin.ModelAdmin):
    list_display = ('id_tipo_cambio', 'id_fuente', 'moneda_origen', 'moneda_destino', 'tasa', 'fecha', 'vigente_desde', 'creado_en')
    search_fields = ('moneda_origen', 'moneda_destino', 'id_fuente__nombre')
    list_filter = ('id_fuente', 'moneda_origen', 'moneda_destino', 'fecha', 'creado_en')
    raw_id_fields = ('id_fuente',)
    readonly_fields = ('creado_en',)
    date_hierarchy = 'fecha'
    ordering = ('-fecha', 'moneda_origen', 'moneda_destino')




