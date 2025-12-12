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

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


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

    # 4. Intentar llamar al Microservicio de Documentos
    # IMPORTANTE: Siempre intenta el microservicio primero en cada exportación.
    # Si el microservicio vuelve a estar disponible, se usará automáticamente.
    import logging
    import sys
    logger = logging.getLogger(__name__)
    
    # Forzar salida a consola también
    print(f"[EXPORT] [INFO] Intentando conectar con microservicio en http://localhost:5001/exportar para formato {formato}", file=sys.stderr)
    print(f"[EXPORT] [INFO] Payload: {len(lista_items)} items, titulo: {payload['titulo']}", file=sys.stderr)
    logger.info(f"Intentando conectar con microservicio en http://localhost:5001/exportar para formato {formato}")
    logger.info(f"Payload enviado: {len(lista_items)} items, titulo: {payload['titulo']}")
    
    # Intentar conectar con el microservicio (SIEMPRE se intenta primero)
    microservicio_disponible = False
    try:
        print(f"[EXPORT] [DEBUG] Llamando a microservicio: http://localhost:5001/exportar", file=sys.stderr)
        print(f"[EXPORT] [DEBUG] Payload tiene {len(payload['items'])} items", file=sys.stderr)
        resp = requests.post("http://localhost:5001/exportar", json=payload, timeout=10)
        print(f"[EXPORT] [DEBUG] Microservicio respondio con status {resp.status_code}", file=sys.stderr)
        print(f"[EXPORT] [DEBUG] Content-Type: {resp.headers.get('content-type', 'N/A')}", file=sys.stderr)
        print(f"[EXPORT] [DEBUG] Tamaño contenido: {len(resp.content)} bytes", file=sys.stderr)
        logger.info(f"Microservicio respondio con status {resp.status_code}, content-type: {resp.headers.get('content-type', 'N/A')}, tamaño: {len(resp.content)} bytes")
        
        if resp.status_code == 200:
            # Verificar que el contenido no esté vacío
            if len(resp.content) == 0:
                print(f"[EXPORT] [ERROR] Microservicio respondio con 200 pero contenido vacio, usando fallback", file=sys.stderr)
                logger.error("[ERROR] Microservicio respondio con 200 pero contenido vacio, usando fallback")
            else:
                # Microservicio funcionó correctamente - ¡Se detectó que está disponible!
                microservicio_disponible = True
                print(f"[EXPORT] [DEBUG] microservicio_disponible = True", file=sys.stderr)
                
                # Definir extensión y tipo de archivo según formato
                if formato == 'pdf':
                    ext, mime = 'pdf', 'application/pdf'
                elif formato == 'csv':
                    ext, mime = 'csv', 'text/csv'
                elif formato == 'excel':
                    ext, mime = 'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                print(f"[EXPORT] [OK] Microservicio ACTIVO - Devolviendo archivo {formato} generado por microservicio (tamano: {len(resp.content)} bytes)", file=sys.stderr)
                print(f"[EXPORT] [DEBUG] Creando HttpResponse con content_type={mime}, ext={ext}", file=sys.stderr)
                logger.info(f"[OK] Microservicio ACTIVO - Devolviendo archivo {formato} generado por microservicio (tamano: {len(resp.content)} bytes)")
                response = HttpResponse(resp.content, content_type=mime)
                response['Content-Disposition'] = f'attachment; filename="Reporte_Calificaciones_NUAM_{datetime.now().strftime("%Y%m%d")}.{ext}"'
                print(f"[EXPORT] [DEBUG] Retornando respuesta del microservicio (NO debe llegar al fallback)", file=sys.stderr)
                return response
        else:
            # Si el microservicio responde con error HTTP (4xx, 5xx), usar fallback
            error_detail = ""
            try:
                error_detail = resp.text[:200]  # Primeros 200 caracteres del error
            except:
                pass
            print(f"[EXPORT] [WARNING] Microservicio respondio con error HTTP {resp.status_code}: {error_detail}", file=sys.stderr)
            logger.warning(f"[WARNING] Microservicio respondio con error HTTP {resp.status_code}: {error_detail}, usando fallback Django")
            
    except requests.exceptions.ConnectionError as e:
        # Error de conexión (microservicio caído o no responde)
        print(f"[EXPORT] [WARNING] Microservicio NO DISPONIBLE (conexion fallida): {str(e)}", file=sys.stderr)
        print(f"[EXPORT] [WARNING] Usando fallback Django. Si el microservicio vuelve, se usara automaticamente en la proxima exportacion.", file=sys.stderr)
        logger.warning(f"[WARNING] Error de conexion con microservicio: {str(e)}, usando fallback Django")
    except requests.exceptions.Timeout as e:
        # Timeout
        print(f"[EXPORT] [WARNING] Microservicio NO DISPONIBLE (timeout): {str(e)}", file=sys.stderr)
        print(f"[EXPORT] [WARNING] Usando fallback Django. Si el microservicio vuelve, se usara automaticamente en la proxima exportacion.", file=sys.stderr)
        logger.warning(f"[WARNING] Timeout al conectar con microservicio: {str(e)}, usando fallback Django")
    except Exception as e:
        # Cualquier otro error
        print(f"[EXPORT] [WARNING] Microservicio NO DISPONIBLE (error inesperado): {type(e).__name__} - {str(e)}", file=sys.stderr)
        print(f"[EXPORT] [WARNING] Usando fallback Django. Si el microservicio vuelve, se usara automaticamente en la proxima exportacion.", file=sys.stderr)
        logger.warning(f"[WARNING] Error inesperado: {type(e).__name__} - {str(e)}, usando fallback Django")
    
    # Si llegamos aquí, el microservicio no está disponible o falló
    # Usar fallback de Django
    # NOTA: En la próxima exportación, se intentará el microservicio nuevamente automáticamente
    print(f"[EXPORT] [DEBUG] Llegamos al bloque de fallback. microservicio_disponible = {microservicio_disponible}", file=sys.stderr)
    if not microservicio_disponible:
        # FALLBACK: Si el microservicio está caído, intentar generar el archivo directamente en Django
        # Si no se puede generar en Django, devolver error para que JavaScript use sistema antiguo
        import logging
        import sys
        logger = logging.getLogger(__name__)
        print(f"[EXPORT] ⚠️ FALLBACK Django activado - Microservicio no disponible, generando {formato} directamente en Django", file=sys.stderr)
        print(f"[EXPORT] ℹ️ NOTA: En la próxima exportación se intentará el microservicio nuevamente automáticamente", file=sys.stderr)
        logger.warning(f"[WARNING] Fallback Django activado - Microservicio no disponible, generando {formato} directamente en Django")
        
        if formato == 'pdf':
            # Generar PDF directamente en Django (si reportlab está disponible)
            try:
                if not REPORTLAB_AVAILABLE:
                    error_html = f"""
                    <html>
                    <head><title>Error - PDF no disponible</title></head>
                    <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                        <h2 style="color: #d32f2f;">⚠️ Error al generar PDF</h2>
                        <p>La librería <code>reportlab</code> no está instalada.</p>
                        <p><strong>Soluciones:</strong></p>
                        <ul style="text-align: left; display: inline-block;">
                            <li>Instalar reportlab: <code>pip install reportlab</code></li>
                            <li>Usar el formato CSV o Excel que están disponibles</li>
                            <li>Usar el botón "Descargar CSV" en la tabla</li>
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
                
                # Generar PDF con reportlab
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                elements = []
                
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#FF3333'),
                    alignment=1,  # Center
                    spaceAfter=30
                )
                
                # Título
                elements.append(Paragraph(payload['titulo'], title_style))
                elements.append(Spacer(1, 0.2*inch))
                
                # Metadatos
                meta_text = f"Fecha: {payload['fecha']} | Generado por: {payload['generado_por']}"
                elements.append(Paragraph(meta_text, styles['Normal']))
                elements.append(Spacer(1, 0.3*inch))
                
                # Preparar datos para tabla
                headers = ['ID', 'Corredora', 'Instrumento', 'Estado', 'Ejercicio', 'Fecha Pago', 'Descripción']
                data = [headers]
                
                for item in lista_items[:100]:  # Limitar a 100 filas
                    row = [
                        item['columna1'],
                        item['columna2'],
                        item['columna3'],
                        item['columna4'],
                        item['columna5'],
                        item['columna6'],
                        item['columna7'][:50] if len(item['columna7']) > 50 else item['columna7']  # Truncar descripción
                    ]
                    data.append(row)
                
                # Crear tabla
                table = Table(data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 0.8*inch, 0.6*inch, 0.8*inch, 1.8*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF3333')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(table)
                
                # Construir PDF
                doc.build(elements)
                buffer.seek(0)
                
                response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="Reporte_Calificaciones_NUAM_{datetime.now().strftime("%Y%m%d")}.pdf"'
                return response
            
            except Exception as e:
                # Error al generar PDF
                error_html = f"""
                <html>
                <head><title>Error - PDF</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h2 style="color: #d32f2f;">⚠️ Error al generar archivo PDF</h2>
                    <p>Ocurrió un error inesperado: <code>{str(e)}</code></p>
                    <p><strong>Opciones disponibles:</strong></p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>Usar el formato CSV o Excel que están disponibles</li>
                        <li>Usar el botón "Descargar CSV" en la tabla</li>
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
                return HttpResponse(error_html, status=500)
        
        elif formato == 'csv':
            # Generar CSV directamente en Django
            try:
                logger.info(f"Generando CSV con fallback Django ({len(lista_items)} items)")
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
                
                logger.info("CSV generado exitosamente con fallback Django")
                return response
            except Exception as e:
                logger.error(f"Error al generar CSV con fallback Django: {str(e)}")
                error_html = f"""
                <html>
                <head><title>Error - CSV</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h2 style="color: #d32f2f;">⚠️ Error al generar archivo CSV</h2>
                    <p>Ocurrió un error inesperado: <code>{str(e)}</code></p>
                    <p><strong>El sistema usará el exportador JavaScript como alternativa.</strong></p>
                    <p style="margin-top: 30px;">
                        <a href="/calificaciones/mantenedor/" style="background: #d32f2f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Volver al Mantenedor
                        </a>
                    </p>
                </body>
                </html>
                """
                return HttpResponse(error_html, status=500)
        
        elif formato == 'excel':
            # Generar Excel directamente en Django (si openpyxl está disponible)
            try:
                if not OPENPYXL_AVAILABLE:
                    error_html = f"""
                    <html>
                    <head><title>Error - Excel no disponible</title></head>
                    <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                        <h2 style="color: #d32f2f;">⚠️ Error al generar Excel</h2>
                        <p>La librería <code>openpyxl</code> no está instalada.</p>
                        <p><strong>Soluciones:</strong></p>
                        <ul style="text-align: left; display: inline-block;">
                            <li>Instalar openpyxl: <code>pip install openpyxl</code></li>
                            <li>Usar el formato CSV que está disponible</li>
                            <li>Usar el botón "Descargar CSV" en la tabla</li>
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
                # Error al generar Excel
                error_html = f"""
                <html>
                <head><title>Error - Excel</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h2 style="color: #d32f2f;">⚠️ Error al generar archivo Excel</h2>
                    <p>Ocurrió un error inesperado: <code>{str(e)}</code></p>
                    <p><strong>Opciones disponibles:</strong></p>
                    <ul style="text-align: left; display: inline-block;">
                        <li>Usar el formato CSV que está disponible</li>
                        <li>Usar el botón "Descargar CSV" en la tabla</li>
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
                return HttpResponse(error_html, status=500)


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
