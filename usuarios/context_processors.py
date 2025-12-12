"""
Context processors para usuarios
Proporciona información del usuario autenticado a todos los templates
"""
from usuarios.models import Usuario, UsuarioRol, Colaborador


def user_info(request):
    """
    Context processor que agrega información del usuario a todos los templates:
    - Roles del usuario
    - Nombre completo (desde Persona)
    - Email de colaborador (si existe)
    - Badge del rol principal
    - is_admin: si el usuario es administrador
    - rol_actual: rol principal actual del usuario
    """
    context = {
        'user_roles': [],
        'user_rol_display': None,
        'user_nombre_completo': None,
        'user_email': None,
        'user_usuario_obj': None,
        'is_admin': False,
        'rol_actual': None,
    }
    
    if request.user and request.user.is_authenticated:
        try:
            # Obtener el objeto Usuario desde la BD
            usuario_obj = Usuario.objects.select_related('id_persona', 'colaborador').get(username=request.user.username)
            context['user_usuario_obj'] = usuario_obj
            
            # Obtener nombre completo desde Persona
            if usuario_obj.id_persona:
                persona = usuario_obj.id_persona
                context['user_nombre_completo'] = persona.nombre_completo
            
            # Obtener email de colaborador si existe
            try:
                if hasattr(usuario_obj, 'colaborador'):
                    context['user_email'] = usuario_obj.colaborador.gmail
            except Colaborador.DoesNotExist:
                pass
            
            # Obtener roles del usuario
            roles = UsuarioRol.objects.filter(id_usuario=usuario_obj).select_related('id_rol')
            role_names = [ur.id_rol.nombre for ur in roles]
            role_names_lower = [rol.lower() for rol in role_names if rol]
            context['user_roles'] = role_names_lower
            
            # Determinar si es administrador
            is_admin = 'administrador' in role_names_lower or request.user.is_staff
            context['is_admin'] = is_admin
            
            # Determinar rol principal para display (prioridad: Administrador > otros)
            if 'Administrador' in role_names or is_admin:
                context['user_rol_display'] = 'Administrador'
                context['rol_actual'] = 'administrador'
            elif 'Operador' in role_names:
                context['user_rol_display'] = 'Operador'
                context['rol_actual'] = 'operador'
            elif 'Analista' in role_names:
                context['user_rol_display'] = 'Analista'
                context['rol_actual'] = 'analista'
            elif 'Consultor' in role_names:
                context['user_rol_display'] = 'Consultor'
                context['rol_actual'] = 'consultor'
            elif 'Auditor' in role_names:
                context['user_rol_display'] = 'Auditor'
                context['rol_actual'] = 'auditor'
            elif role_names:
                context['user_rol_display'] = role_names[0]
                context['rol_actual'] = role_names_lower[0]
            elif request.user.is_staff:
                context['user_rol_display'] = 'Administrador'
                context['rol_actual'] = 'administrador'
                context['is_admin'] = True
                
        except Usuario.DoesNotExist:
            # Usuario de Django pero no existe en nuestro modelo Usuario
            # Fallback: usar is_staff para determinar si es admin
            if request.user.is_staff:
                context['is_admin'] = True
                context['user_rol_display'] = 'Administrador'
                context['rol_actual'] = 'administrador'
    
    return context

