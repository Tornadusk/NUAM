"""
Helpers compartidos para vistas de microservicios

NOTA: Este módulo reutiliza y extiende las funciones de roles ya existentes
en calificaciones/views.py (get_user_roles, has_role) para mantener consistencia.
"""
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.http import HttpResponseForbidden


def obtener_corredora_usuario(usuario_obj):
    """
    Obtiene la corredora asociada a un usuario.
    Si el usuario tiene múltiples corredoras, devuelve la principal.
    Si no tiene corredoras, devuelve None.
    """
    try:
        from corredoras.models import UsuarioCorredora
        # Buscar la corredora principal del usuario
        usuario_corredora = UsuarioCorredora.objects.filter(
            id_usuario=usuario_obj
        ).filter(es_principal=True).first()
        
        # Si no tiene principal, obtener la primera
        if not usuario_corredora:
            usuario_corredora = UsuarioCorredora.objects.filter(
                id_usuario=usuario_obj
            ).first()
        
        return usuario_corredora.id_corredora if usuario_corredora else None
    except Exception:
        return None


def obtener_usuario_nuam(user):
    """
    Obtiene el objeto Usuario de NUAM a partir del Django User.
    Relaciona por username.
    
    Reutiliza la misma lógica que calificaciones/views.py
    """
    if not user or not user.is_authenticated:
        return None
    try:
        from usuarios.models import Usuario
        return Usuario.objects.get(username=user.username)
    except Usuario.DoesNotExist:
        return None
    except Exception:
        return None


def get_user_roles(user):
    """
    Obtiene los nombres de los roles del usuario desde la BD.
    Retorna lista de nombres de roles (lowercase).
    
    Esta función es compatible con calificaciones/views.py
    para mantener consistencia en todo el sistema.
    """
    if not user or not user.is_authenticated:
        return []
    
    try:
        from usuarios.models import Usuario, UsuarioRol
        usuario_obj = Usuario.objects.get(username=user.username)
        roles = UsuarioRol.objects.filter(id_usuario=usuario_obj).values_list('id_rol__nombre', flat=True)
        return [rol.lower() for rol in roles if rol]
    except Usuario.DoesNotExist:
        return []
    except Exception:
        return []


def has_role(user, role_name):
    """
    Verificar si el usuario tiene un rol específico.
    role_name puede ser: 'administrador', 'operador', 'analista', 'consultor', 'auditor'
    
    Esta función es compatible con calificaciones/views.py
    para mantener consistencia en todo el sistema.
    """
    roles = get_user_roles(user)
    return role_name.lower() in roles


def es_administrador(user):
    """
    Verifica si el usuario es administrador usando el sistema de roles de NUAM.
    Usa las funciones compatibles con calificaciones/views.py (has_role).
    Fallback a is_staff si no se puede verificar por roles de NUAM.
    """
    if not user or not user.is_authenticated:
        return False
    
    # Usar has_role que es compatible con el sistema existente del mantenedor
    if has_role(user, 'administrador'):
        return True
    
    # Fallback a is_staff si no se puede verificar por roles
    return user.is_staff


def obtener_roles_usuario(user):
    """
    Obtiene todos los roles del usuario en el sistema de roles de NUAM.
    Retorna una lista con los nombres de los roles (lowercase para compatibilidad).
    
    Reutiliza get_user_roles() para mantener consistencia con calificaciones/views.py
    """
    return get_user_roles(user)


def es_operador(user):
    """
    Verifica si el usuario es operador (no es administrador)
    """
    if not user or not user.is_authenticated:
        return False
    return not es_administrador(user)


def admin_required(view_func):
    """
    Decorador para requerir que el usuario sea administrador.
    Usa el sistema de roles de NUAM (rol "Administrador") o is_staff como fallback.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.conf import settings
            login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
            return redirect(login_url)
        if not es_administrador(request.user):
            roles_usuario = obtener_roles_usuario(request.user)
            roles_str = ', '.join(roles_usuario) if roles_usuario else 'ninguno'
            return HttpResponseForbidden(
                f"Acceso denegado. Se requieren permisos de administrador. "
                f"Tu rol actual: {roles_str}"
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def rol_required(*roles_permitidos):
    """
    Decorador para requerir que el usuario tenga uno de los roles especificados.
    
    Uso:
        @rol_required('Administrador', 'Analista')
        def mi_vista(request):
            ...
    
    Nota: Los nombres de roles se comparan en lowercase, así que 'Administrador' 
    coincide con 'administrador', 'ADMINISTRADOR', etc.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                from django.conf import settings
                login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
                return redirect(login_url)
            
            # Verificar si el usuario tiene alguno de los roles permitidos
            roles_usuario = obtener_roles_usuario(request.user)
            # Convertir roles_permitidos a lowercase para comparación
            roles_permitidos_lower = [r.lower() for r in roles_permitidos]
            tiene_acceso = any(rol.lower() in roles_permitidos_lower for rol in roles_usuario)
            
            # Si no tiene rol en NUAM, usar is_staff como fallback solo para Administrador
            if not tiene_acceso and 'Administrador' in roles_permitidos:
                tiene_acceso = request.user.is_staff
            
            if not tiene_acceso:
                roles_str = ', '.join(roles_usuario) if roles_usuario else 'ninguno'
                roles_requeridos_str = ' o '.join(roles_permitidos)
                return HttpResponseForbidden(
                    f"Acceso denegado. Se requiere uno de los siguientes roles: {roles_requeridos_str}. "
                    f"Tu rol actual: {roles_str}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def tiene_rol(user, nombre_rol):
    """
    Verifica si el usuario tiene un rol específico en el sistema de roles de NUAM.
    Wrapper para has_role() para mantener compatibilidad con código existente.
    
    nombre_rol puede ser en cualquier caso: 'Administrador', 'administrador', etc.
    """
    return has_role(user, nombre_rol)
