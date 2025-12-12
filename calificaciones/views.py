from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from usuarios.models import Usuario, UsuarioRol
import requests
from django.http import HttpResponse
from .models import Calificacion
from datetime import datetime


def check_staff_required(user):
    """Verifica si el usuario tiene permisos de staff (Administrador)"""
    return user.is_authenticated and user.is_staff


def get_user_roles(user):
    """
    Obtener los nombres de los roles del usuario desde la BD
    Retorna lista de nombres de roles (lowercase)
    """
    if not user or not user.is_authenticated:
        return []
    
    try:
        usuario_obj = Usuario.objects.get(username=user.username)
        roles = UsuarioRol.objects.filter(id_usuario=usuario_obj).values_list('id_rol__nombre', flat=True)
        return [rol.lower() for rol in roles if rol]
    except Usuario.DoesNotExist:
        return []


def has_role(user, role_name):
    """
    Verificar si el usuario tiene un rol específico
    role_name puede ser: 'administrador', 'operador', 'analista', 'consultor', 'auditor'
    """
    roles = get_user_roles(user)
    return role_name.lower() in roles

@login_required
def exportar_datos_view(request, formato):
    """
    Vista para exportar calificaciones en diferentes formatos (PDF, CSV, Excel)
    Utiliza el microservicio de documentos para generar los archivos
    """
    # 1. Validar formato
    if formato not in ['pdf', 'csv', 'excel']:
        return HttpResponse("Formato no válido", status=400)

    # 2. Obtener datos de Oracle (usando campos reales del modelo Calificacion)
    calificaciones = Calificacion.objects.select_related(
        'id_corredora', 'id_instrumento', 'id_moneda', 'id_fuente'
    ).all()[:100]

    # 3. Preparar JSON para el microservicio con campos reales
    lista_items = []
    for c in calificaciones:
        # Usar campos reales del modelo Calificacion
        descripcion_corta = (c.descripcion[:50] + '...') if c.descripcion and len(c.descripcion) > 50 else (c.descripcion or 'Sin descripción')
        
        lista_items.append({
            "columna1": str(c.id_calificacion),  # ID de la calificación
            "columna2": c.id_corredora.nombre if c.id_corredora else 'N/A',  # Nombre de la corredora
            "columna3": c.id_instrumento.codigo if c.id_instrumento else 'N/A',  # Código del instrumento
            "columna4": c.estado or 'N/A',  # Estado (borrador, validada, publicada, pendiente)
            "columna5": str(c.ejercicio) if c.ejercicio else 'N/A',  # Ejercicio
            "columna6": c.fecha_pago.strftime("%d/%m/%Y") if c.fecha_pago else 'N/A',  # Fecha de pago
            "columna7": descripcion_corta,  # Descripción (truncada)
        })

    payload = {
        "titulo": "Reporte Maestro de Calificaciones",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "generado_por": request.user.username or "Anonimo",
        "formato": formato,  # Le decimos al microservicio qué formato generar
        "items": lista_items
    }

    try:
        # 4. Llamar al Microservicio de Documentos
        resp = requests.post("http://localhost:5001/exportar", json=payload, timeout=30)
        
        if resp.status_code == 200:
            # Definir extensión y tipo de archivo según formato
            if formato == 'pdf':
                ext, mime = 'pdf', 'application/pdf'
            elif formato == 'csv':
                ext, mime = 'csv', 'text/csv'
            elif formato == 'excel':
                ext, mime = 'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            response = HttpResponse(resp.content, content_type=mime)
            response['Content-Disposition'] = f'attachment; filename="Reporte_Calificaciones_NUAM_{datetime.now().strftime("%Y%m%d")}.{ext}"'
            return response
        else:
            return HttpResponse(f"Error del microservicio: {resp.status_code} - {resp.text}", status=500)
            
    except requests.exceptions.ConnectionError:
        return HttpResponse(
            "Error: No se pudo conectar al microservicio de documentos. "
            "Asegúrate de que el servicio esté corriendo en http://localhost:5001",
            status=503
        )
    except requests.exceptions.Timeout:
        return HttpResponse("Error: El microservicio tardó demasiado en responder", status=504)
    except Exception as e:
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)


@login_required
def mantenedor_calificaciones(request):
    """Vista principal del Mantenedor de Calificaciones Tributarias"""
    import json
    
    # Obtener roles del usuario desde BD
    user_roles = get_user_roles(request.user) if request.user.is_authenticated else []
    
    # Determinar permisos según roles
    # Asegurar que todas las variables booleanas tengan un valor por defecto (False)
    # Esto es crítico para evitar errores en los templates
    is_admin = bool(request.user.is_staff) if request.user.is_authenticated else False
    is_administrador = bool('administrador' in user_roles or is_admin)
    is_operador = bool('operador' in user_roles)
    is_analista = bool('analista' in user_roles)
    is_consultor = bool('consultor' in user_roles)
    is_auditor = bool('auditor' in user_roles)
    
    # Variables combinadas para simplificar las condiciones en los templates
    # Esto evita problemas con múltiples 'or' en las expresiones {% if %}
    # IMPORTANTE: Estas variables deben estar siempre definidas (nunca None)
    # Auditor puede ver Mantenedor (solo lectura) y Auditoría (completa)
    can_view_mantenedor = bool(is_administrador or is_operador or is_analista or is_consultor or is_auditor)
    can_view_cargas = bool(is_administrador or is_operador or is_analista)
    can_view_auditoria = bool(is_administrador or is_auditor)
    can_edit_calificaciones = bool(is_administrador or is_operador or is_analista)
    is_read_only = bool(is_consultor or is_auditor)
    
    # Convertir user_roles a JSON para pasarlo al JavaScript
    # Asegurar que siempre sea una cadena JSON válida (nunca None o vacío)
    user_roles_json = json.dumps(user_roles) if user_roles else "[]"
    
    # Determinar qué pestaña debe estar activa por defecto
    # Para Auditor, la pestaña de Auditoría debe ser la activa por defecto
    # Para otros roles, Mantenedor es la activa por defecto
    default_active_tab = 'auditoria' if (is_auditor and not is_administrador) else 'mantenedor'
    
    # Agregar información de usuario al contexto para usar en template
    # IMPORTANTE: Todas estas variables deben estar siempre definidas para evitar errores en los templates
    context = {
        'user': request.user,
        'is_admin': is_admin,
        'is_administrador': is_administrador,
        'is_operador': is_operador,
        'is_analista': is_analista,
        'is_consultor': is_consultor,
        'is_auditor': is_auditor,
        'can_view_mantenedor': can_view_mantenedor,
        'can_view_cargas': can_view_cargas,
        'can_view_auditoria': can_view_auditoria,
        'can_edit_calificaciones': can_edit_calificaciones,
        'is_read_only': is_read_only,
        'default_active_tab': default_active_tab,  # Pestaña activa por defecto
        'user_roles': user_roles,  # Lista de roles del usuario
        'user_roles_json': user_roles_json,  # JSON para JavaScript
    }
    return render(request, 'calificaciones/mantenedor.html', context)
