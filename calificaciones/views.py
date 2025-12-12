from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from usuarios.models import Usuario, UsuarioRol
import requests
from django.http import HttpResponse
from .models import Calificacion
from datetime import datetime
import csv
import io
try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


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
        # 4. Intentar llamar al Microservicio de Documentos
        resp = requests.post("http://localhost:5001/exportar", json=payload, timeout=10)
        
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
            # Si el microservicio responde con error, usar fallback
            raise requests.exceptions.ConnectionError("Microservicio respondió con error")
            
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # FALLBACK: Si el microservicio está caído, generar el archivo directamente en Django
        # Solo para CSV y Excel (PDF requiere librerías más complejas)
        
        if formato == 'pdf':
            # Para PDF, no podemos generar sin el microservicio, mostrar mensaje amigable
            error_html = f"""
            <html>
            <head><title>Microservicio no disponible</title></head>
            <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                <h2 style="color: #d32f2f;">⚠️ Microservicio de documentos no disponible</h2>
                <p>El microservicio de generación de PDFs no está disponible en este momento.</p>
                <p><strong>Opciones disponibles:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Usar el botón "Descargar CSV" en la tabla para exportación rápida</li>
                    <li>Exportar en formato CSV o Excel (disponibles sin microservicio)</li>
                    <li>Intentar nuevamente más tarde</li>
                </ul>
                <p style="margin-top: 30px;">
                    <a href="/calificaciones/mantenedor/" style="background: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Volver al Mantenedor
                    </a>
                </p>
            </body>
            </html>
            """
            return HttpResponse(error_html, status=503)
        
        elif formato == 'csv':
            # Generar CSV directamente en Django
            response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = f'attachment; filename="Reporte_Calificaciones_NUAM_{datetime.now().strftime("%Y%m%d")}.csv"'
            
            writer = csv.writer(response)
            # Encabezados
            writer.writerow(['ID', 'Corredora', 'Instrumento', 'Estado', 'Ejercicio', 'Fecha Pago', 'Descripción'])
            # Datos
            for item in lista_items:
                writer.writerow([
                    item['columna1'],
                    item['columna2'],
                    item['columna3'],
                    item['columna4'],
                    item['columna5'],
                    item['columna6'],
                    item['columna7']
                ])
            
            return response
        
        elif formato == 'excel':
            # Generar Excel directamente en Django (si openpyxl está disponible)
            if not OPENPYXL_AVAILABLE:
                return HttpResponse(
                    "Error: openpyxl no está instalado. No se puede generar Excel sin el microservicio.",
                    status=503
                )
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Calificaciones"
            
            # Encabezados
            ws.append(['ID', 'Corredora', 'Instrumento', 'Estado', 'Ejercicio', 'Fecha Pago', 'Descripción'])
            
            # Datos
            for item in lista_items:
                ws.append([
                    item['columna1'],
                    item['columna2'],
                    item['columna3'],
                    item['columna4'],
                    item['columna5'],
                    item['columna6'],
                    item['columna7']
                ])
            
            # Guardar en memoria
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="Reporte_Calificaciones_NUAM_{datetime.now().strftime("%Y%m%d")}.xlsx"'
            return response
    
    except Exception as e:
        # Error inesperado
        return HttpResponse(
            f"Error inesperado: {str(e)}<br><br>"
            f"<a href='/calificaciones/mantenedor/'>Volver al Mantenedor</a>",
            status=500
        )


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
