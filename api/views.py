from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse, StreamingHttpResponse
import csv
import io
import hashlib
import unicodedata
from datetime import datetime
from decimal import Decimal, InvalidOperation
try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# Renderers personalizados para bypass de content negotiation en DRF
class BinaryFileRenderer(BaseRenderer):
    media_type = 'application/octet-stream'
    format = 'binary'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, HttpResponse):
            # Si data ya es HttpResponse, devolver su contenido
            return data.content
        return data

# Core
from core.models import Pais, Moneda, MonedaPais, Mercado, Fuente
from .serializers import (
    PaisSerializer, MonedaSerializer, MonedaPaisSerializer,
    MercadoSerializer, FuenteSerializer
)

# Usuarios
from usuarios.models import Persona, Usuario, Rol, UsuarioRol, Colaborador
from django.contrib.auth.models import User as DjangoUser
from .serializers import (
    PersonaSerializer, UsuarioSerializer, UsuarioCreateSerializer,
    RolSerializer, UsuarioRolSerializer, ColaboradorSerializer
)

# Corredoras
from corredoras.models import Corredora, CorredoraIdentificador, UsuarioCorredora
from .serializers import (
    CorredoraSerializer, CorredoraIdentificadorSerializer, UsuarioCorredoraSerializer
)

# Instrumentos
from instrumentos.models import Instrumento, EventoCapital
from .serializers import (
    InstrumentoSerializer, EventoCapitalSerializer
)

# Calificaciones
from calificaciones.models import FactorDef, Calificacion, CalificacionMontoDetalle, CalificacionFactorDetalle
from .serializers import (
    FactorDefSerializer, CalificacionSerializer,
    CalificacionMontoDetalleSerializer, CalificacionFactorDetalleSerializer
)

# Cargas
from cargas.models import Carga, CargaDetalle
from .serializers import (
    CargaSerializer, CargaDetalleSerializer
)

# Auditoria
from auditoria.models import Auditoria
from .serializers import AuditoriaSerializer


# ========= VIEWSETS CORE =========

class PaisViewSet(viewsets.ModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """Búsqueda de países por código o nombre"""
        query = request.query_params.get('q', '')
        paises = self.queryset.filter(
            Q(codigo__icontains=query) | Q(nombre__icontains=query)
        )
        serializer = self.get_serializer(paises, many=True)
        return Response(serializer.data)


class MonedaViewSet(viewsets.ModelViewSet):
    queryset = Moneda.objects.all()
    serializer_class = MonedaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        vigente = self.request.query_params.get('vigente')
        if vigente is not None:
            queryset = queryset.filter(vigente=vigente.lower() == 'true')
        return queryset


class MonedaPaisViewSet(viewsets.ModelViewSet):
    queryset = MonedaPais.objects.all()
    serializer_class = MonedaPaisSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MercadoViewSet(viewsets.ModelViewSet):
    queryset = Mercado.objects.all()
    serializer_class = MercadoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        pais_id = self.request.query_params.get('pais')
        if pais_id:
            queryset = queryset.filter(id_pais_id=pais_id)
        return queryset


class FuenteViewSet(viewsets.ModelViewSet):
    queryset = Fuente.objects.all()
    serializer_class = FuenteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ========= VIEWSETS USUARIOS =========

class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    def perform_create(self, serializer):
        password = self.request.data.get('password')
        usuario = serializer.save()
        if password:
            usuario.set_password(password)
            usuario.save()
        # Sincronizar con el sistema de autenticación de Django para permitir login
        django_user, created = DjangoUser.objects.get_or_create(
            username=usuario.username,
            defaults={
                'is_active': usuario.estado == 'activo',
            }
        )
        if password:
            django_user.set_password(password)
        django_user.is_active = usuario.estado == 'activo'
        django_user.save()

    def _refresh_auth_staff(self, usuario: Usuario):
        """Marcar is_staff en auth_user si el usuario tiene rol Administrador."""
        password = None
        if hasattr(self, 'request') and hasattr(self.request, 'data'):
            password = self.request.data.get('password')
        try:
            django_user = DjangoUser.objects.get(username=usuario.username)
        except DjangoUser.DoesNotExist:
            return
        tiene_admin = usuario.usuariorol_set.filter(id_rol__nombre='Administrador').exists()
        if django_user.is_staff != tiene_admin:
            django_user.is_staff = tiene_admin
            django_user.save(update_fields=['is_staff'])
        
        # Sincronizar con Django's User model para autenticación
        from django.contrib.auth.models import User
        from usuarios.models import Rol
        
        # Determinar si es admin basado en roles
        rol_admin = Rol.objects.filter(nombre='Administrador').first()
        es_admin = rol_admin and usuario.usuariorol_set.filter(id_rol=rol_admin).exists()
        
        django_user, created = User.objects.get_or_create(
            username=usuario.username,
            defaults={
                'is_active': usuario.estado == 'activo',
                'is_staff': es_admin,
                'is_superuser': es_admin
            }
        )
        if created and password:
            django_user.set_password(password)
            django_user.save()
        elif not created:
            # Actualizar is_staff si ya existía
            django_user.is_staff = es_admin
            django_user.is_superuser = es_admin
            django_user.is_active = usuario.estado == 'activo'
            django_user.save()
        
        # Registrar en auditoría
        try:
            current_user = Usuario.objects.get(username=self.request.user.username)
            Auditoria.objects.create(
                actor_id=current_user,
                entidad='USUARIO',
                entidad_id=usuario.id_usuario,
                accion='INSERT',
                fuente='API'
            )
        except:
            # Registrar sin actor si no hay usuario actual
            Auditoria.objects.create(
                actor_id=None,
                entidad='USUARIO',
                entidad_id=usuario.id_usuario,
                accion='INSERT',
                fuente='API'
            )
    
    def perform_update(self, serializer):
        usuario = serializer.save()
        
        # Sincronizar con Django's User model para autenticación
        from django.contrib.auth.models import User
        from usuarios.models import Rol
        
        # Determinar si es admin basado en roles
        rol_admin = Rol.objects.filter(nombre='Administrador').first()
        es_admin = rol_admin and usuario.usuariorol_set.filter(id_rol=rol_admin).exists()
        
        try:
            django_user = User.objects.get(username=usuario.username)
            django_user.is_active = usuario.estado == 'activo'
            django_user.is_staff = es_admin
            django_user.is_superuser = es_admin
            django_user.save()
        except User.DoesNotExist:
            pass  # Si no existe, no hacer nada (se creará en el próximo login si es necesario)
        
        # Registrar en auditoría
        try:
            current_user = Usuario.objects.get(username=self.request.user.username)
            Auditoria.objects.create(
                actor_id=current_user,
                entidad='USUARIO',
                entidad_id=usuario.id_usuario,
                accion='UPDATE',
                fuente='API'
            )
        except:
            pass  # Si no hay usuario actual, continuar sin registrar
    
    def perform_destroy(self, instance):
        # Obtener ID antes de eliminar
        id_usuario = instance.id_usuario
        username = instance.username
        
        # Registrar en auditoría antes de eliminar
        try:
            current_user = Usuario.objects.get(username=self.request.user.username)
            Auditoria.objects.create(
                actor_id=current_user,
                entidad='USUARIO',
                entidad_id=id_usuario,
                accion='DELETE',
                fuente='API'
            )
        except:
            # Registrar sin actor si no hay usuario actual
            Auditoria.objects.create(
                actor_id=None,
                entidad='USUARIO',
                entidad_id=id_usuario,
                accion='DELETE',
                fuente='API'
            )
        
        # Sincronizar eliminación con Django's User model
        from django.contrib.auth.models import User
        try:
            User.objects.filter(username=username).delete()
        except:
            pass  # Si no existe, continuar con la eliminación
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Listar solo usuarios activos"""
        usuarios = self.queryset.filter(estado='activo')
        serializer = self.get_serializer(usuarios, many=True)
        return Response(serializer.data)


class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.all()
    serializer_class = UsuarioRolSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        usuario_rol = serializer.save()
        # Actualizar bandera is_staff en auth_user si corresponde
        try:
            from usuarios.models import Usuario
            usuario = Usuario.objects.get(pk=usuario_rol.id_usuario_id)
        except Exception:
            return
        # Reutilizar helper del ViewSet de Usuario
        UsuarioViewSet._refresh_auth_staff(self, usuario)

    def perform_destroy(self, instance):
        from usuarios.models import Usuario
        usuario_id = instance.id_usuario_id
        super().perform_destroy(instance)
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            UsuarioViewSet._refresh_auth_staff(self, usuario)
        except Exception:
            pass


class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.all()
    serializer_class = ColaboradorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        id_usuario = self.request.query_params.get('id_usuario')
        if id_usuario:
            queryset = queryset.filter(id_usuario=id_usuario)
        return queryset


# ========= VIEWSETS CORREDORAS =========

class CorredoraViewSet(viewsets.ModelViewSet):
    queryset = Corredora.objects.all()
    serializer_class = CorredoraSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Listar solo corredoras activas"""
        corredoras = self.queryset.filter(estado='activa')
        serializer = self.get_serializer(corredoras, many=True)
        return Response(serializer.data)


class CorredoraIdentificadorViewSet(viewsets.ModelViewSet):
    queryset = CorredoraIdentificador.objects.all()
    serializer_class = CorredoraIdentificadorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UsuarioCorredoraViewSet(viewsets.ModelViewSet):
    queryset = UsuarioCorredora.objects.all()
    serializer_class = UsuarioCorredoraSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ========= VIEWSETS INSTRUMENTOS =========

class InstrumentoViewSet(viewsets.ModelViewSet):
    queryset = Instrumento.objects.all()
    serializer_class = InstrumentoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        mercado_id = self.request.query_params.get('mercado')
        if mercado_id:
            queryset = queryset.filter(id_mercado_id=mercado_id)
        return queryset


class EventoCapitalViewSet(viewsets.ModelViewSet):
    queryset = EventoCapital.objects.all()
    serializer_class = EventoCapitalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        instrumento_id = self.request.query_params.get('instrumento')
        if instrumento_id:
            queryset = queryset.filter(id_instrumento_id=instrumento_id)
        return queryset


# ========= VIEWSETS CALIFICACIONES =========

class FactorDefViewSet(viewsets.ModelViewSet):
    queryset = FactorDef.objects.all()
    serializer_class = FactorDefSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all().prefetch_related('calificacionfactordetalle_set', 'calificacionmontodetalle_set')
    serializer_class = CalificacionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        corredora_id = self.request.query_params.get('corredora')
        mercado_id = self.request.query_params.get('mercado')
        fuente_id = self.request.query_params.get('origen') or self.request.query_params.get('fuente')
        ejercicio = self.request.query_params.get('ejercicio') or self.request.query_params.get('periodo')
        pendiente = self.request.query_params.get('pendiente')
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if corredora_id:
            queryset = queryset.filter(id_corredora_id=corredora_id)
        if mercado_id:
            # Filtrar por mercado a través del instrumento
            queryset = queryset.filter(id_instrumento__id_mercado_id=mercado_id)
        if fuente_id:
            queryset = queryset.filter(id_fuente_id=fuente_id)
        if ejercicio:
            queryset = queryset.filter(ejercicio=ejercicio)
        if pendiente is not None:
            # Si pendiente=True, filtrar por estado='pendiente'
            if pendiente.lower() == 'true':
                queryset = queryset.filter(estado='pendiente')
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar usuario actual a creado_por y actualizado_por"""
        from usuarios.models import Usuario
        
        try:
            usuario = Usuario.objects.get(username=self.request.user.username)
            calificacion = serializer.save(creado_por=usuario, actualizado_por=usuario)
            
            # Registrar en auditoría
            Auditoria.objects.create(
                actor_id=usuario,
                entidad='CALIFICACION',
                entidad_id=calificacion.id_calificacion,
                accion='INSERT',
                fuente='API'
            )
        except Usuario.DoesNotExist:
            # Si no existe el Usuario, crear la calificación sin usuario
            # Esto no debería pasar en producción, pero lo manejamos por seguridad
            calificacion = serializer.save()
            
            # Registrar en auditoría sin actor
            Auditoria.objects.create(
                actor_id=None,
                entidad='CALIFICACION',
                entidad_id=calificacion.id_calificacion,
                accion='INSERT',
                fuente='API'
            )
    
    def perform_update(self, serializer):
        """Actualizar actualizado_por con el usuario actual"""
        from usuarios.models import Usuario
        
        try:
            usuario = Usuario.objects.get(username=self.request.user.username)
            calificacion = serializer.save(actualizado_por=usuario)
            
            # Registrar en auditoría
            Auditoria.objects.create(
                actor_id=usuario,
                entidad='CALIFICACION',
                entidad_id=calificacion.id_calificacion,
                accion='UPDATE',
                fuente='API'
            )
        except Usuario.DoesNotExist:
            calificacion = serializer.save()
            
            # Registrar en auditoría sin actor
            Auditoria.objects.create(
                actor_id=None,
                entidad='CALIFICACION',
                entidad_id=calificacion.id_calificacion,
                accion='UPDATE',
                fuente='API'
            )
    
    def perform_destroy(self, instance):
        """Registrar eliminación en auditoría antes de borrar"""
        from usuarios.models import Usuario
        
        id_calificacion = instance.id_calificacion
        try:
            usuario = Usuario.objects.get(username=self.request.user.username)
            actor = usuario
        except Usuario.DoesNotExist:
            actor = None
        
        # Registrar en auditoría antes de eliminar
        Auditoria.objects.create(
            actor_id=actor,
            entidad='CALIFICACION',
            entidad_id=id_calificacion,
            accion='DELETE',
            fuente='API'
        )
        
        # Ahora sí eliminar
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """Exportar calificaciones a Excel (.xlsx)"""
        if not OPENPYXL_AVAILABLE:
            return Response(
                {'error': 'openpyxl no está instalado. Ejecuta: pip install openpyxl'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Obtener datos con los filtros aplicados
        queryset = self.get_queryset()
        calificaciones = list(queryset)
        
        if not calificaciones:
            return Response(
                {'error': 'No hay calificaciones para exportar'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Crear workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Calificaciones"
        
        # Headers
        headers = [
            'ID', 'Corredora', 'País', 'Instrumento', 'Moneda', 'Ejercicio',
            'Fecha Pago', 'Descripción', 'Estado', 'Secuencia Evento',
            'Factor Actualización', 'Acogido SFUT', 'Creado En', 'Actualizado En'
        ]
        ws.append(headers)
        
        # Datos
        for cal in calificaciones:
            ws.append([
                cal.id_calificacion,
                cal.id_corredora.nombre if cal.id_corredora else '',
                cal.id_corredora.id_pais.nombre if cal.id_corredora and cal.id_corredora.id_pais else '',
                cal.id_instrumento.nombre if cal.id_instrumento else '',
                cal.id_moneda.codigo if cal.id_moneda else '',
                cal.ejercicio,
                cal.fecha_pago.strftime('%Y-%m-%d') if cal.fecha_pago else '',
                cal.descripcion or '',
                cal.estado,
                cal.secuencia_evento or '',
                float(cal.factor_actualizacion) if cal.factor_actualizacion else '',
                'Sí' if cal.acogido_sfut else 'No',
                cal.creado_en.strftime('%Y-%m-%d %H:%M:%S') if cal.creado_en else '',
                cal.actualizado_en.strftime('%Y-%m-%d %H:%M:%S') if cal.actualizado_en else ''
            ])
        
        # Guardar en buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f'calificaciones_{datetime.now().strftime("%Y%m%d")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Exportar calificaciones a PDF"""
        if not REPORTLAB_AVAILABLE:
            return Response(
                {'error': 'reportlab no está instalado. Ejecuta: pip install reportlab'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Obtener datos con los filtros aplicados
        queryset = self.get_queryset()
        calificaciones = list(queryset)
        
        if not calificaciones:
            return Response(
                {'error': 'No hay calificaciones para exportar'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Crear PDF en buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            textColor=colors.HexColor('#FF3333'),
            spaceAfter=30
        )
        
        # Título
        story.append(Paragraph("Reporte de Calificaciones Tributarias", title_style))
        story.append(Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 20))
        
        # Preparar datos para tabla
        data = [['ID', 'Corredora', 'Instrumento', 'Ejercicio', 'Estado']]
        for cal in calificaciones[:50]:  # Limitar a 50 para no saturar el PDF
            data.append([
                str(cal.id_calificacion),
                cal.id_corredora.nombre if cal.id_corredora else '',
                cal.id_instrumento.nombre if cal.id_instrumento else '',
                str(cal.ejercicio) if cal.ejercicio else '',
                cal.estado
            ])
        
        # Crear tabla
        table = Table(data)
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
        ]))
        story.append(table)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        # Crear respuesta HTTP
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        filename = f'calificaciones_{datetime.now().strftime("%Y%m%d")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class CalificacionMontoDetalleViewSet(viewsets.ModelViewSet):
    queryset = CalificacionMontoDetalle.objects.all()
    serializer_class = CalificacionMontoDetalleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CalificacionFactorDetalleViewSet(viewsets.ModelViewSet):
    queryset = CalificacionFactorDetalle.objects.all()
    serializer_class = CalificacionFactorDetalleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        id_calificacion = self.request.query_params.get('id_calificacion')
        if id_calificacion:
            queryset = queryset.filter(id_calificacion=id_calificacion)
        return queryset


# ========= VIEWSETS CARGAS =========

class CargaViewSet(viewsets.ModelViewSet):
    queryset = Carga.objects.all()
    serializer_class = CargaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload_factores(self, request):
        """Carga masiva de calificaciones con factores ya calculados"""
        
        # Obtener archivo CSV
        if 'file' not in request.FILES:
            return Response({'error': 'No se proporcionó archivo CSV'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response({'error': 'El archivo debe ser CSV'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener usuario actual
        try:
            from usuarios.models import Usuario, Persona, Rol
            usuario = Usuario.objects.get(username=request.user.username)
        except Usuario.DoesNotExist:
            # Si no existe en Usuario, crear automáticamente sincronizado con auth.User
            try:
                # Crear Persona mínima
                persona = Persona.objects.create(
                    primer_nombre=request.user.username,
                    apellido_paterno='Usuario',
                    fecha_nacimiento='1990-01-01'
                )
                # Crear Usuario NUAM
                usuario = Usuario.objects.create(
                    id_persona=persona,
                    username=request.user.username,
                    estado='activo',
                    hash_password=request.user.password  # Ya está hasheado en auth.User
                )
            except Exception as e:
                return Response({'error': f'Error al crear usuario: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Error al obtener usuario: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Leer CSV
        try:
            file_content = file.read().decode('utf-8-sig')
            if file_content.lower().startswith('sep='):
                file_lines = file_content.splitlines()
                file_content = '\n'.join(file_lines[1:]) if len(file_lines) > 1 else ''
            sample = file_content.splitlines()[0] if file_content else ''
            delimiter = ';' if sample.count(';') >= sample.count(',') else ','
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;')
                delimiter = dialect.delimiter
            except Exception:
                pass
            reader = csv.DictReader(io.StringIO(file_content), delimiter=delimiter)
        except Exception as e:
            return Response({'error': f'Error al leer CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        raw_headers = reader.fieldnames or []
        
        def normalize_header(header):
            header = unicodedata.normalize('NFKD', header or '')
            header = ''.join(ch for ch in header if not unicodedata.combining(ch))
            return ''.join(ch for ch in header.lower() if ch.isalnum())
        
        header_map = {normalize_header(h): h for h in raw_headers}
        
        def get_cell(row, *aliases, default=''):
            for alias in aliases:
                normalized = normalize_header(alias)
                original = header_map.get(normalized)
                if original and original in row:
                    value = row[original]
                    if value is None:
                        continue
                    return str(value).strip()
            return default
        
        required_alias_groups = [
            ('corredora',),
            ('instrumento', 'instrumento_codigo'),
            ('fuente', 'fuente_codigo'),
            ('moneda', 'moneda_codigo'),
            ('ejercicio',),
            ('fecha_pago', 'fecha'),
            ('secuencia_evento', 'secuencia')
        ]
        
        missing_headers = []
        for group in required_alias_groups:
            if not any(normalize_header(alias) in header_map for alias in group):
                missing_headers.append(group[0])
        if missing_headers:
            return Response({'error': f'Encabezados faltantes: {", ".join(missing_headers)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener códigos de factores F08-F37
        factor_codigos = [f'F{i:02d}' for i in range(8, 38)]
        factor_map = {}
        for factor in FactorDef.objects.filter(codigo_factor__in=factor_codigos):
            factor_map[factor.codigo_factor] = factor
        
        # Procesar filas
        insertados = 0
        rechazados = 0
        errores = []
        
        with transaction.atomic():
            # Crear registro de Carga
            carga = Carga.objects.create(
                id_corredora_id=1,  # TODO: obtener de request
                creado_por=usuario,
                id_fuente_id=1,  # TODO: obtener de request
                tipo='masiva',
                nombre_archivo=file.name,
                filas_total=0,
                estado='importando'
            )
            
            for linea, row in enumerate(reader, start=2):  # linea 1 = encabezados
                try:
                    linea_referencia = get_cell(row, 'linea', 'fila', default=str(linea))

                    # Resolver corredora
                    corredora = None
                    corredor_raw_id = get_cell(row, 'id_corredora')
                    if corredor_raw_id:
                        try:
                            corredora = Corredora.objects.get(id_corredora=int(corredor_raw_id))
                        except (ValueError, Corredora.DoesNotExist):
                            raise ValueError(f'Corredora con ID {corredor_raw_id} no existe (línea {linea_referencia})')
                    if not corredora:
                        corredora_nombre = get_cell(row, 'corredora')
                        if not corredora_nombre:
                            raise ValueError(f'Corredora es obligatoria (línea {linea_referencia})')
                        try:
                            corredora = Corredora.objects.get(nombre__iexact=corredora_nombre.strip())
                        except Corredora.DoesNotExist:
                            raise ValueError(f'Corredora "{corredora_nombre}" no existe (línea {linea_referencia})')
                        except Corredora.MultipleObjectsReturned:
                            raise ValueError(f'Corredora "{corredora_nombre}" no es única (línea {linea_referencia})')

                    # Resolver instrumento
                    instrumento = None
                    instrumento_id_raw = get_cell(row, 'id_instrumento')
                    if instrumento_id_raw:
                        try:
                            instrumento = Instrumento.objects.get(id_instrumento=int(instrumento_id_raw))
                        except (ValueError, Instrumento.DoesNotExist):
                            raise ValueError(f'Instrumento con ID {instrumento_id_raw} no existe (línea {linea_referencia})')
                    if not instrumento:
                        instrumento_codigo = get_cell(row, 'instrumento_codigo')
                        if instrumento_codigo:
                            instrumento = Instrumento.objects.filter(codigo__iexact=instrumento_codigo).first()
                            if not instrumento:
                                raise ValueError(f'Instrumento con código "{instrumento_codigo}" no existe (línea {linea_referencia})')
                        else:
                            instrumento_nombre = get_cell(row, 'instrumento')
                            if not instrumento_nombre:
                                raise ValueError(f'Instrumento es obligatorio (línea {linea_referencia})')
                            instrumentos_qs = Instrumento.objects.filter(nombre__iexact=instrumento_nombre.strip())
                            if not instrumentos_qs.exists():
                                raise ValueError(f'Instrumento "{instrumento_nombre}" no existe (línea {linea_referencia})')
                            if instrumentos_qs.count() > 1:
                                raise ValueError(f'Instrumento "{instrumento_nombre}" no es único, especifique el código (línea {linea_referencia})')
                            instrumento = instrumentos_qs.first()

                    # Resolver fuente
                    fuente = None
                    fuente_id_raw = get_cell(row, 'id_fuente')
                    if fuente_id_raw:
                        try:
                            fuente = Fuente.objects.get(id_fuente=int(fuente_id_raw))
                        except (ValueError, Fuente.DoesNotExist):
                            raise ValueError(f'Fuente con ID {fuente_id_raw} no existe (línea {linea_referencia})')
                    if not fuente:
                        fuente_codigo = get_cell(row, 'fuente_codigo')
                        if fuente_codigo:
                            fuente = Fuente.objects.filter(codigo__iexact=fuente_codigo).first()
                            if not fuente:
                                raise ValueError(f'Fuente con código "{fuente_codigo}" no existe (línea {linea_referencia})')
                        else:
                            fuente_nombre = get_cell(row, 'fuente')
                            if not fuente_nombre:
                                raise ValueError(f'Fuente es obligatoria (línea {linea_referencia})')
                            fuente = Fuente.objects.filter(nombre__iexact=fuente_nombre.strip()).first()
                            if not fuente:
                                raise ValueError(f'Fuente "{fuente_nombre}" no existe (línea {linea_referencia})')

                    # Resolver moneda
                    moneda = None
                    moneda_id_raw = get_cell(row, 'id_moneda')
                    if moneda_id_raw:
                        try:
                            moneda = Moneda.objects.get(id_moneda=int(moneda_id_raw))
                        except (ValueError, Moneda.DoesNotExist):
                            raise ValueError(f'Moneda con ID {moneda_id_raw} no existe (línea {linea_referencia})')
                    if not moneda:
                        moneda_codigo = get_cell(row, 'moneda_codigo', 'moneda')
                        if not moneda_codigo:
                            raise ValueError(f'Moneda es obligatoria (línea {linea_referencia})')
                        moneda = Moneda.objects.filter(codigo__iexact=moneda_codigo.strip()).first()
                        if not moneda:
                            raise ValueError(f'Moneda "{moneda_codigo}" no existe (línea {linea_referencia})')

                    # Validar ejercicio y fecha
                    ejercicio_raw = get_cell(row, 'ejercicio')
                    try:
                        ejercicio = int(ejercicio_raw)
                    except (TypeError, ValueError):
                        raise ValueError(f'Ejercicio inválido "{ejercicio_raw}" (línea {linea_referencia})')

                    fecha_pago_raw = get_cell(row, 'fecha_pago', 'fecha')
                    fecha_pago = None
                    parsed = False
                    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
                        try:
                            fecha_pago = datetime.strptime(fecha_pago_raw, fmt).date()
                            parsed = True
                            break
                        except ValueError:
                            continue
                    if not parsed:
                        raise ValueError(f'Fecha de pago inválida "{fecha_pago_raw}" (línea {linea_referencia})')

                    def parse_bool(value, default=False):
                        if value is None or value == '':
                            return default
                        value = str(value).strip().lower()
                        if value in ['true', '1', 'si', 'sí', 'yes', 'y']:
                            return True
                        if value in ['false', '0', 'no', 'n']:
                            return False
                        return default

                    ingreso_por_montos = parse_bool(get_cell(row, 'ingreso_por_montos', 'ingreso'), default=False)
                    if ingreso_por_montos:
                        raise ValueError(f'Ingreso por montos debe ser "No" para cargas por factor (línea {linea_referencia})')

                    acogido_sfut = parse_bool(get_cell(row, 'acogido_sfut', 'sfut'))

                    descripcion_val = get_cell(row, 'descripcion')
                    estado_val = get_cell(row, 'estado').lower() or 'borrador'
                    if estado_val not in ['borrador', 'validada', 'publicada', 'pendiente']:
                        raise ValueError(f'Estado "{estado_val}" inválido (línea {linea_referencia})')

                    valor_historico_val = get_cell(row, 'valor_historico')
                    valor_historico = None
                    if valor_historico_val:
                        try:
                            valor_historico = Decimal(valor_historico_val)
                        except InvalidOperation:
                            raise ValueError(f'Valor histórico inválido "{valor_historico_val}" (línea {linea_referencia})')

                    # Calcular suma de factores que aplican en suma
                    suma_factores = Decimal('0')
                    factores_detalle = {}
                    for codigo in factor_codigos:
                        valor_str = get_cell(row, codigo)
                        if valor_str:
                            try:
                                valor = Decimal(valor_str)
                                if valor > 0:
                                    factores_detalle[codigo] = valor
                                    if codigo in factor_map and factor_map[codigo].aplica_en_suma:
                                        suma_factores += valor
                            except InvalidOperation:
                                raise ValueError(f'Factor {codigo} no es un número válido (línea {linea_referencia})')

                    if suma_factores > Decimal('1'):
                        raise ValueError(f'Suma de factores excede 1: {suma_factores} (línea {linea_referencia})')

                    calificacion, created = Calificacion.objects.get_or_create(
                        id_corredora=corredora,
                        id_instrumento=instrumento,
                        ejercicio=ejercicio,
                        secuencia_evento=get_cell(row, 'secuencia_evento', 'secuencia'),
                        defaults={
                            'id_fuente': fuente,
                            'id_moneda': moneda,
                            'fecha_pago': fecha_pago,
                            'descripcion': descripcion_val,
                            'ingreso_por_montos': False,
                            'acogido_sfut': acogido_sfut,
                            'factor_actualizacion': suma_factores,
                            'valor_historico': valor_historico,
                            'estado': estado_val,
                            'observaciones': 'Carga masiva',
                            'creado_por': usuario,
                            'actualizado_por': usuario
                        }
                    )

                    if not created:
                        calificacion.id_fuente = fuente
                        calificacion.id_moneda = moneda
                        calificacion.fecha_pago = fecha_pago
                        calificacion.descripcion = descripcion_val
                        calificacion.acogido_sfut = acogido_sfut
                        calificacion.factor_actualizacion = suma_factores
                        calificacion.valor_historico = valor_historico
                        calificacion.actualizado_por = usuario
                        calificacion.estado = estado_val
                        calificacion.observaciones = 'Carga masiva'
                        calificacion.save()

                    CalificacionFactorDetalle.objects.filter(id_calificacion=calificacion).delete()
                    for codigo, valor in factores_detalle.items():
                        CalificacionFactorDetalle.objects.create(
                            id_calificacion=calificacion,
                            id_factor=factor_map[codigo],
                            valor_factor=valor
                        )

                    hash_value = hashlib.md5(str(row).encode('utf-8')).hexdigest()
                    CargaDetalle.objects.create(
                        id_carga=carga,
                        linea=linea,
                        estado_linea='ok',
                        id_calificacion=calificacion,
                        hash_linea=hash_value
                    )

                    insertados += 1

                except Exception as e:
                    rechazados += 1
                    errores.append({
                        'linea': linea,
                        'error': str(e)
                    })
                    
                    # Calcular hash único de la línea para errores también
                    hash_value = hashlib.md5(str(row).encode('utf-8')).hexdigest()
                    
                    CargaDetalle.objects.create(
                        id_carga=carga,
                        linea=linea,
                        estado_linea='rechazo',
                        mensaje_error=str(e),
                        hash_linea=hash_value
                    )
            
            # Actualizar resumen de Carga
            carga.filas_total = insertados + rechazados
            carga.insertados = insertados
            carga.rechazados = rechazados
            carga.estado = 'done' if rechazados == 0 else 'done'
            carga.save()
        
        return Response({
            'carga_id': carga.id_carga,
            'filas_total': carga.filas_total,
            'insertados': insertados,
            'rechazados': rechazados,
            'errores': errores[:10]  # Limitar a 10 errores para no saturar respuesta
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def upload_montos(self, request):
        """Carga masiva de calificaciones con montos (los factores se calculan automáticamente)"""
        # TODO: Implementar lógica de validación, cálculo y procesamiento CSV
        return Response({'message': 'Funcionalidad en desarrollo'}, status=status.HTTP_501_NOT_IMPLEMENTED)


class CargaDetalleViewSet(viewsets.ModelViewSet):
    queryset = CargaDetalle.objects.all()
    serializer_class = CargaDetalleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ========= VIEWSETS AUDITORIA =========

class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.all()
    serializer_class = AuditoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        entidad = self.request.query_params.get('entidad')
        if entidad:
            queryset = queryset.filter(entidad=entidad)
        return queryset
