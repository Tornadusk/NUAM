from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
import csv
import io
import hashlib
from datetime import datetime
from decimal import Decimal, InvalidOperation

# Core
from core.models import Pais, Moneda, MonedaPais, Mercado, Fuente
from .serializers import (
    PaisSerializer, MonedaSerializer, MonedaPaisSerializer,
    MercadoSerializer, FuenteSerializer
)

# Usuarios
from usuarios.models import Persona, Usuario, Rol, UsuarioRol, Colaborador
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
    
    def perform_destroy(self, instance):
        # Sincronizar eliminación con Django's User model
        from django.contrib.auth.models import User
        try:
            User.objects.filter(username=instance.username).delete()
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
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if corredora_id:
            queryset = queryset.filter(id_corredora_id=corredora_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar usuario actual a creado_por y actualizado_por"""
        from usuarios.models import Usuario
        
        try:
            usuario = Usuario.objects.get(username=self.request.user.username)
            serializer.save(creado_por=usuario, actualizado_por=usuario)
        except Usuario.DoesNotExist:
            # Si no existe el Usuario, crear la calificación sin usuario
            # Esto no debería pasar en producción, pero lo manejamos por seguridad
            serializer.save()
    
    def perform_update(self, serializer):
        """Actualizar actualizado_por con el usuario actual"""
        from usuarios.models import Usuario
        
        try:
            usuario = Usuario.objects.get(username=self.request.user.username)
            serializer.save(actualizado_por=usuario)
        except Usuario.DoesNotExist:
            serializer.save()


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
            file_content = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(file_content))
        except Exception as e:
            return Response({'error': f'Error al leer CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar encabezados requeridos
        required_headers = [
            'id_corredora', 'id_instrumento', 'id_fuente', 'id_moneda',
            'ejercicio', 'fecha_pago', 'descripcion', 'ingreso_por_montos',
            'acogido_sfut', 'secuencia_evento'
        ]
        if not all(header in reader.fieldnames for header in required_headers):
            missing = [h for h in required_headers if h not in reader.fieldnames]
            return Response({'error': f'Encabezados faltantes: {", ".join(missing)}'}, status=status.HTTP_400_BAD_REQUEST)
        
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
                    # Validar FK existentes
                    id_corredora = int(row['id_corredora'])
                    id_instrumento = int(row['id_instrumento'])
                    id_fuente = int(row['id_fuente'])
                    id_moneda = int(row['id_moneda'])
                    
                    if not Corredora.objects.filter(id_corredora=id_corredora).exists():
                        raise ValueError(f'Corredora {id_corredora} no existe')
                    if not Instrumento.objects.filter(id_instrumento=id_instrumento).exists():
                        raise ValueError(f'Instrumento {id_instrumento} no existe')
                    if not Fuente.objects.filter(id_fuente=id_fuente).exists():
                        raise ValueError(f'Fuente {id_fuente} no existe')
                    if not Moneda.objects.filter(id_moneda=id_moneda).exists():
                        raise ValueError(f'Moneda {id_moneda} no existe')
                    
                    # Validar ejercicio y fecha
                    ejercicio = int(row['ejercicio'])
                    fecha_pago = datetime.strptime(row['fecha_pago'], '%Y-%m-%d').date()
                    
                    # Validar ingreso_por_montos (debe ser false para carga por factores)
                    ingreso_por_montos = (row.get('ingreso_por_montos') or '').lower() in ['true', '1', 'yes']
                    if ingreso_por_montos:
                        raise ValueError('ingreso_por_montos debe ser false para carga por factores')
                    
                    # Validar acogido_sfut
                    acogido_sfut = (row.get('acogido_sfut') or '').lower() in ['true', '1', 'yes']
                    
                    # Calcular suma de factores que aplican en suma
                    suma_factores = Decimal('0')
                    factores_detalle = {}
                    
                    for codigo in factor_codigos:
                        if codigo in row and row[codigo] and row[codigo].strip():
                            try:
                                valor = Decimal(row[codigo])
                                if valor > 0:
                                    factores_detalle[codigo] = valor
                                    # Solo sumar si aplica_en_suma
                                    if codigo in factor_map and factor_map[codigo].aplica_en_suma:
                                        suma_factores += valor
                            except InvalidOperation:
                                raise ValueError(f'Factor {codigo} no es un número válido')
                    
                    # Validar suma de factores ≤ 1
                    if suma_factores > Decimal('1'):
                        raise ValueError(f'Suma de factores excede 1: {suma_factores}')
                    
                    # Obtener o crear Calificacion
                    calificacion, created = Calificacion.objects.get_or_create(
                        id_corredora_id=id_corredora,
                        id_instrumento_id=id_instrumento,
                        ejercicio=ejercicio,
                        secuencia_evento=row['secuencia_evento'],
                        defaults={
                            'id_fuente_id': id_fuente,
                            'id_moneda_id': id_moneda,
                            'fecha_pago': fecha_pago,
                            'descripcion': row.get('descripcion', ''),
                            'ingreso_por_montos': False,
                            'acogido_sfut': acogido_sfut,
                            'factor_actualizacion': suma_factores,
                            'valor_historico': None,
                            'estado': 'borrador',
                            'observaciones': 'Carga masiva',
                            'creado_por': usuario,
                            'actualizado_por': usuario
                        }
                    )
                    
                    # Si ya existe, actualizar (no rechazar)
                    if not created:
                        calificacion.id_fuente_id = id_fuente
                        calificacion.id_moneda_id = id_moneda
                        calificacion.fecha_pago = fecha_pago
                        calificacion.descripcion = row.get('descripcion', '')
                        calificacion.acogido_sfut = acogido_sfut
                        calificacion.factor_actualizacion = suma_factores
                        calificacion.actualizado_por = usuario
                        calificacion.estado = 'borrador'
                        calificacion.observaciones = 'Carga masiva'
                        calificacion.save()
                    
                    # Eliminar factores antiguos
                    CalificacionFactorDetalle.objects.filter(id_calificacion=calificacion).delete()
                    
                    # Crear nuevos factores
                    for codigo, valor in factores_detalle.items():
                        CalificacionFactorDetalle.objects.create(
                            id_calificacion=calificacion,
                            id_factor=factor_map[codigo],
                            valor_factor=valor
                        )
                    
                    # Calcular hash único de la línea para detección de duplicados
                    hash_value = hashlib.md5(str(row).encode('utf-8')).hexdigest()
                    
                    # Registrar en CargaDetalle
                    CargaDetalle.objects.create(
                        id_carga=carga,
                        linea=linea,
                        estado_linea='ok',
                        id_calificacion=calificacion,
                        hash_linea=hash_value
                    )
                    
                    insertados += 1
                    
                except Exception as e:
                    # Registrar error
                    rechazados += 1
                    errores.append({
                        'linea': linea,
                        'error': str(e),
                        'datos': dict(row)
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
