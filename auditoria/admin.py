from django.contrib import admin
from .models import Auditoria


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('id_auditoria', 'actor_id', 'entidad', 'entidad_id', 'accion', 'fecha', 'fuente', 'creado_en', 'actualizado_en')
    search_fields = ('entidad', 'accion', 'fuente', 'actor_id__username')
    list_filter = ('entidad', 'accion', 'fecha')
    readonly_fields = ('id_auditoria', 'actor_id', 'entidad', 'entidad_id', 'accion', 'fecha', 'fuente', 'valores_antes', 'valores_despues', 'creado_en', 'actualizado_en')
    raw_id_fields = ('actor_id',)
    ordering = ('-fecha',)
    date_hierarchy = 'fecha'
    
    def has_add_permission(self, request):
        # No permitir crear registros de auditoría manualmente
        return False
    
    def has_change_permission(self, request, obj=None):
        # No permitir modificar registros de auditoría
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Permitir eliminar para limpieza, pero normalmente no recomendado
        return True