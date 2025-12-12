"""
Template tags para verificar roles y permisos de usuarios
"""
from django import template
from microservicio.views.helpers import has_role, es_administrador

register = template.Library()


@register.filter
def tiene_rol(user, rol_name):
    """
    Template filter para verificar si un usuario tiene un rol específico.
    
    Uso:
        {% load user_tags %}
        {% if user|tiene_rol:"Administrador" %}
            ...
        {% endif %}
    """
    return has_role(user, rol_name)


@register.filter
def es_admin(user):
    """
    Template filter para verificar si un usuario es administrador.
    
    Uso:
        {% load user_tags %}
        {% if user|es_admin %}
            ...
        {% endif %}
    """
    return es_administrador(user)


@register.simple_tag
def puede_ver_graficos(user):
    """
    Verifica si el usuario puede ver el dashboard de gráficos.
    Permitido para: Administrador, Operador
    
    Uso:
        {% load user_tags %}
        {% puede_ver_graficos user as puede_ver %}
        {% if puede_ver %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return has_role(user, 'administrador') or has_role(user, 'operador')


@register.simple_tag
def puede_ver_tipos_cambio(user):
    """
    Verifica si el usuario puede ver el dashboard de tipos de cambio.
    Permitido para: Administrador, Analista, Operador
    
    Uso:
        {% load user_tags %}
        {% puede_ver_tipos_cambio user as puede_ver %}
        {% if puede_ver %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return has_role(user, 'administrador') or has_role(user, 'analista') or has_role(user, 'operador')


@register.simple_tag
def puede_ver_pulsar(user):
    """
    Verifica si el usuario puede ver el dashboard de Pulsar.
    Permitido para: Solo Administrador
    
    Uso:
        {% load user_tags %}
        {% puede_ver_pulsar user as puede_ver %}
        {% if puede_ver %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return es_administrador(user)


@register.simple_tag
def puede_ver_tests(user):
    """
    Verifica si el usuario puede ver el dashboard de Tests.
    Permitido para: Solo Administrador
    
    Uso:
        {% load user_tags %}
        {% puede_ver_tests user as puede_ver %}
        {% if puede_ver %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return es_administrador(user)


@register.simple_tag
def puede_ver_swagger(user):
    """
    Verifica si el usuario puede ver Swagger/OpenAPI.
    Permitido para: Solo Administrador
    
    Uso:
        {% load user_tags %}
        {% puede_ver_swagger user as puede_ver %}
        {% if puede_ver %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    return es_administrador(user)


@register.simple_tag
def puede_ver_mantenedor(user):
    """
    Verifica si el usuario puede ver el mantenedor de calificaciones.
    Permitido para: Administrador, Operador, Analista, Consultor, Auditor
    
    Uso:
        {% load user_tags %}
        {% puede_ver_mantenedor user as puede_ver %}
        {% if puede_ver %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    # Todos los roles pueden ver el mantenedor (algunos en solo lectura)
    roles_permitidos = ['administrador', 'operador', 'analista', 'consultor', 'auditor']
    # Verificar si el usuario tiene alguno de los roles permitidos
    for rol in roles_permitidos:
        if has_role(user, rol):
            return True
    # Fallback: si es staff, también puede ver
    return es_administrador(user)

