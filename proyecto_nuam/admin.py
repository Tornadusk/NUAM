"""
Personalización del Admin Site de Django para NUAM
Organiza las apps en categorías lógicas y mejora la experiencia de uso
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group


class NuamAdminSite(AdminSite):
    """Admin site personalizado para NUAM con mejor organización"""
    site_header = _('NUAM - Administración')
    site_title = _('NUAM Admin')
    index_title = _('Panel de Administración')


# Crear instancia personalizada del admin (opcional)
# admin_site = NuamAdminSite(name='nuam_admin')


# Personalizar el admin estándar
admin.site.site_header = 'NUAM - Sistema de Calificaciones Tributarias'
admin.site.site_title = 'NUAM Admin'
admin.site.index_title = 'Panel de Administración'


# OCULTAR Usuarios y Grupos nativos de Django
# Los usuarios NUAM se gestionan en la app "usuarios"

def ocultar_modelos_nativos():
    """Desregistra User y Group de Django para evitar duplicación"""
    try:
        admin.site.unregister(User)
    except admin.sites.NotRegistered:
        pass
    
    try:
        admin.site.unregister(Group)
    except admin.sites.NotRegistered:
        pass

# Intentar ocultar (puede fallar si se ejecuta antes de que Django esté listo)
try:
    ocultar_modelos_nativos()
except Exception:
    pass

# Organización automática de apps en el admin
# Django ya ordena automáticamente por orden de INSTALLED_APPS