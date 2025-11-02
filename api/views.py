from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

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
    queryset = Calificacion.objects.all()
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


class CalificacionMontoDetalleViewSet(viewsets.ModelViewSet):
    queryset = CalificacionMontoDetalle.objects.all()
    serializer_class = CalificacionMontoDetalleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CalificacionFactorDetalleViewSet(viewsets.ModelViewSet):
    queryset = CalificacionFactorDetalle.objects.all()
    serializer_class = CalificacionFactorDetalleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


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
