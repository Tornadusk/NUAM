from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Core
    PaisViewSet, MonedaViewSet, MonedaPaisViewSet, MercadoViewSet, FuenteViewSet,
    # Usuarios
    PersonaViewSet, UsuarioViewSet, RolViewSet, UsuarioRolViewSet, ColaboradorViewSet,
    # Corredoras
    CorredoraViewSet, CorredoraIdentificadorViewSet, UsuarioCorredoraViewSet,
    # Instrumentos
    InstrumentoViewSet, EventoCapitalViewSet,
    # Calificaciones
    FactorDefViewSet, CalificacionViewSet,
    CalificacionMontoDetalleViewSet, CalificacionFactorDetalleViewSet,
    # Cargas
    CargaViewSet, CargaDetalleViewSet,
    # Auditoria
    AuditoriaViewSet,
    # KPIs
    KPIsViewSet,
)

# Crear router principal
router = DefaultRouter()

# Registrar todos los ViewSets
# Core
router.register(r'paises', PaisViewSet, basename='pais')
router.register(r'monedas', MonedaViewSet, basename='moneda')
router.register(r'moneda-pais', MonedaPaisViewSet, basename='monedapais')
router.register(r'mercados', MercadoViewSet, basename='mercado')
router.register(r'fuentes', FuenteViewSet, basename='fuente')

# Usuarios
router.register(r'personas', PersonaViewSet, basename='persona')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'usuario-rol', UsuarioRolViewSet, basename='usuariorol')
router.register(r'colaboradores', ColaboradorViewSet, basename='colaborador')

# Corredoras
router.register(r'corredoras', CorredoraViewSet, basename='corredora')
router.register(r'corredora-identificador', CorredoraIdentificadorViewSet, basename='corredoraidentificador')
router.register(r'usuario-corredora', UsuarioCorredoraViewSet, basename='usuariocorredora')

# Instrumentos
router.register(r'instrumentos', InstrumentoViewSet, basename='instrumento')
router.register(r'evento-capital', EventoCapitalViewSet, basename='eventocapital')

# Calificaciones
router.register(r'factores', FactorDefViewSet, basename='factor')
router.register(r'calificaciones', CalificacionViewSet, basename='calificacion')
router.register(r'calificacion-monto-detalle', CalificacionMontoDetalleViewSet, basename='calificacionmontodetalle')
router.register(r'calificacion-factor-detalle', CalificacionFactorDetalleViewSet, basename='calificacionfactordetalle')

# Cargas
router.register(r'cargas', CargaViewSet, basename='carga')
router.register(r'carga-detalle', CargaDetalleViewSet, basename='cargadetalle')

# Auditoria
router.register(r'auditoria', AuditoriaViewSet, basename='auditoria')

# KPIs
router.register(r'kpis', KPIsViewSet, basename='kpis')

urlpatterns = [
    path('', include(router.urls)),
]
