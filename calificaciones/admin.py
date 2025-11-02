from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import FactorDef, Calificacion, CalificacionMontoDetalle, CalificacionFactorDetalle


@admin.register(FactorDef)
class FactorDefAdmin(admin.ModelAdmin):
    list_display = ('id_factor', 'codigo_factor', 'nombre_corto', 'tipo_valor', 'orden_visual', 'aplica_en_suma', 'cantidad_calificaciones', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('codigo_factor', 'nombre_corto', 'descripcion')
    list_filter = ('tipo_valor', 'aplica_en_suma', 'creado_en')
    ordering = ('orden_visual', 'codigo_factor')
    list_display_links = ('id_factor', 'codigo_factor')
    date_hierarchy = 'creado_en'
    
    def cantidad_calificaciones(self, obj):
        """Muestra cantidad de calificaciones que usan este factor"""
        return CalificacionFactorDetalle.objects.filter(id_factor=obj).count()
    cantidad_calificaciones.short_description = 'En uso'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/calificaciones/factordef/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


class CalificacionMontoDetalleInline(admin.TabularInline):
    model = CalificacionMontoDetalle
    extra = 1
    fields = ('id_factor', 'valor_monto')


class CalificacionFactorDetalleInline(admin.TabularInline):
    model = CalificacionFactorDetalle
    extra = 1
    fields = ('id_factor', 'valor_factor')


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('id_calificacion', 'id_corredora', 'id_instrumento', 'ejercicio', 'estado', 'fecha_pago', 'creado_por', 'cantidad_factores', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_instrumento__codigo', 'secuencia_evento', 'descripcion', 'id_corredora__nombre')
    list_filter = ('estado', 'ejercicio', 'id_corredora', 'id_fuente', 'creado_en', 'fecha_pago')
    raw_id_fields = ('id_corredora', 'id_instrumento', 'id_fuente', 'id_evento', 'id_moneda', 'creado_por', 'actualizado_por')
    inlines = [CalificacionMontoDetalleInline, CalificacionFactorDetalleInline]
    actions = ['marcar_como_publicada', 'marcar_como_borrador', 'marcar_como_validada']
    ordering = ('-creado_en', 'id_corredora')
    date_hierarchy = 'creado_en'
    list_display_links = ('id_calificacion', 'id_instrumento')
    
    def cantidad_factores(self, obj):
        """Muestra cantidad de factores asociados"""
        return CalificacionFactorDetalle.objects.filter(id_calificacion=obj).count()
    cantidad_factores.short_description = 'Factores'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/calificaciones/calificacion/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''
    
    @admin.action(description='Marcar como publicada')
    def marcar_como_publicada(self, request, queryset):
        """Acción para publicar calificaciones"""
        updated = queryset.update(estado='publicada')
        self.message_user(request, f'{updated} calificacion(es) publicada(s).', messages.SUCCESS)
    
    @admin.action(description='Marcar como borrador')
    def marcar_como_borrador(self, request, queryset):
        """Acción para volver calificaciones a borrador"""
        updated = queryset.update(estado='borrador')
        self.message_user(request, f'{updated} calificacion(es) marcada(s) como borrador.', messages.INFO)
    
    @admin.action(description='Marcar como validada')
    def marcar_como_validada(self, request, queryset):
        """Acción para validar calificaciones"""
        updated = queryset.update(estado='validada')
        self.message_user(request, f'{updated} calificacion(es) validada(s).', messages.SUCCESS)


@admin.register(CalificacionMontoDetalle)
class CalificacionMontoDetalleAdmin(admin.ModelAdmin):
    list_display = ('id_calificacion', 'id_factor', 'valor_monto', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_calificacion__id_calificacion', 'id_factor__codigo_factor')
    list_filter = ('id_factor',)
    raw_id_fields = ('id_calificacion', 'id_factor')
    ordering = ('id_calificacion', 'id_factor')
    list_display_links = ('id_calificacion', 'id_factor')
    date_hierarchy = 'creado_en'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/calificaciones/calificacionmontodetalle/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''


@admin.register(CalificacionFactorDetalle)
class CalificacionFactorDetalleAdmin(admin.ModelAdmin):
    list_display = ('id_calificacion', 'id_factor', 'valor_factor', 'creado_en', 'actualizado_en', 'editar')
    search_fields = ('id_calificacion__id_calificacion', 'id_factor__codigo_factor')
    list_filter = ('id_factor',)
    raw_id_fields = ('id_calificacion', 'id_factor')
    ordering = ('id_calificacion', 'id_factor')
    list_display_links = ('id_calificacion', 'id_factor')
    date_hierarchy = 'creado_en'
    
    def editar(self, obj):
        if obj.pk:
            return format_html('<a href="/admin/calificaciones/calificacionfactordetalle/{}/change/">✏️</a>', obj.pk)
        return '-'
    editar.short_description = ''