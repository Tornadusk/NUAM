from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import Carga, CargaDetalle


class CargaDetalleInline(admin.TabularInline):
    model = CargaDetalle
    extra = 0
    readonly_fields = ('linea', 'estado_linea', 'mensaje_error')
    can_delete = False
    can_add = False
    max_num = 100  # Limitamos a 100 para rendimiento


@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
    list_display = ('id_carga', 'tipo', 'nombre_archivo', 'id_corredora', 'estado', 'resumen_carga', 'porcentaje_exito', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('nombre_archivo',)
    list_filter = ('tipo', 'estado', 'id_corredora', 'id_fuente', 'creado_en')
    raw_id_fields = ('id_corredora', 'creado_por', 'id_fuente')
    readonly_fields = ('filas_total', 'insertados', 'actualizados', 'rechazados', 'porcentaje_exito')
    inlines = [CargaDetalleInline]
    ordering = ('-creado_en',)
    date_hierarchy = 'creado_en'
    list_display_links = ('id_carga', 'nombre_archivo')
    
    def resumen_carga(self, obj):
        """Muestra resumen de la carga"""
        if obj.filas_total:
            return f"{obj.insertados or 0}/{obj.filas_total}"
        return '-'
    resumen_carga.short_description = 'Exitosas'
    
    def porcentaje_exito(self, obj):
        """Calcula porcentaje de éxito de la carga"""
        if obj.filas_total and obj.filas_total > 0:
            exitosos = obj.insertados or 0
            porcentaje = (exitosos / obj.filas_total) * 100
            return f"{porcentaje:.1f}%"
        return '-'
    porcentaje_exito.short_description = '% Éxito'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/cargas/carga/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(CargaDetalle)
class CargaDetalleAdmin(admin.ModelAdmin):
    list_display = ('id_detalle', 'id_carga', 'linea', 'estado_linea', 'mensaje_error_corto', 'id_calificacion', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_carga__nombre_archivo', 'mensaje_error')
    list_filter = ('estado_linea', 'id_carga')
    raw_id_fields = ('id_carga', 'id_calificacion')
    readonly_fields = ('id_carga', 'linea', 'estado_linea', 'mensaje_error')
    ordering = ('id_carga', 'linea')
    list_display_links = ('id_detalle', 'id_carga')
    date_hierarchy = 'creado_en'
    
    def mensaje_error_corto(self, obj):
        """Muestra mensaje de error truncado"""
        if obj.mensaje_error:
            return obj.mensaje_error[:60] + '...' if len(obj.mensaje_error) > 60 else obj.mensaje_error
        return '-'
    mensaje_error_corto.short_description = 'Error'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/cargas/cargadetalle/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''