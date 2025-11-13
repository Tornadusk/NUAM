from rest_framework import serializers
import json
from core.models import Pais, Moneda, MonedaPais, Mercado, Fuente
from usuarios.models import Persona, Usuario, Rol, UsuarioRol, Colaborador
from corredoras.models import Corredora, CorredoraIdentificador, UsuarioCorredora
from instrumentos.models import Instrumento, EventoCapital
from calificaciones.models import FactorDef, Calificacion, CalificacionMontoDetalle, CalificacionFactorDetalle
from cargas.models import Carga, CargaDetalle
from auditoria.models import Auditoria


# ========= SERIALIZERS CORE =========

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = '__all__'


class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = '__all__'


class MonedaPaisSerializer(serializers.ModelSerializer):
    id_moneda_nombre = serializers.CharField(source='id_moneda.nombre', read_only=True)
    id_pais_nombre = serializers.CharField(source='id_pais.nombre', read_only=True)
    
    class Meta:
        model = MonedaPais
        fields = '__all__'


class MercadoSerializer(serializers.ModelSerializer):
    id_pais_nombre = serializers.CharField(source='id_pais.nombre', read_only=True)
    
    class Meta:
        model = Mercado
        fields = '__all__'


class FuenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuente
        fields = '__all__'


# ========= SERIALIZERS USUARIOS =========

class PersonaSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Persona
        fields = '__all__'


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioRolSerializer(serializers.ModelSerializer):
    id_usuario_username = serializers.CharField(source='id_usuario.username', read_only=True)
    id_rol_nombre = serializers.CharField(source='id_rol.nombre', read_only=True)
    
    class Meta:
        model = UsuarioRol
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    id_persona_detalle = PersonaSerializer(source='id_persona', read_only=True)
    roles = serializers.SerializerMethodField()
    roles_ids = serializers.SerializerMethodField()
    colaborador = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = '__all__'
        extra_kwargs = {
            'hash_password': {'write_only': True}
        }
    
    def get_roles(self, obj):
        roles = obj.usuariorol_set.all()
        return [ur.id_rol.nombre for ur in roles]
    
    def get_roles_ids(self, obj):
        """Retorna los IDs de los UsuarioRol para poder eliminarlos"""
        roles = obj.usuariorol_set.all()
        return [{'id': ur.id, 'id_rol': ur.id_rol.id_rol} for ur in roles]
    
    def get_colaborador(self, obj):
        """Retorna el email del colaborador si existe"""
        try:
            return obj.colaborador.gmail
        except:
            return None


class UsuarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'id_persona', 'username', 'estado']
        read_only_fields = ['id_usuario']  # Automático, pero devolverlo
    
    def create(self, validated_data):
        # El password se maneja en perform_create del ViewSet
        usuario = Usuario(**validated_data)
        usuario.save()
        return usuario


class ColaboradorSerializer(serializers.ModelSerializer):
    id_usuario_username = serializers.CharField(source='id_usuario.username', read_only=True)
    
    class Meta:
        model = Colaborador
        fields = '__all__'


# ========= SERIALIZERS CORREDORAS =========

class CorredoraIdentificadorSerializer(serializers.ModelSerializer):
    id_pais_nombre = serializers.CharField(source='id_pais.nombre', read_only=True)
    
    class Meta:
        model = CorredoraIdentificador
        fields = '__all__'


class CorredoraSerializer(serializers.ModelSerializer):
    id_pais_nombre = serializers.CharField(source='id_pais.nombre', read_only=True)
    identificadores = CorredoraIdentificadorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Corredora
        fields = '__all__'


class UsuarioCorredoraSerializer(serializers.ModelSerializer):
    id_usuario_username = serializers.CharField(source='id_usuario.username', read_only=True)
    id_corredora_nombre = serializers.CharField(source='id_corredora.nombre', read_only=True)
    
    class Meta:
        model = UsuarioCorredora
        fields = '__all__'


# ========= SERIALIZERS INSTRUMENTOS =========

class EventoCapitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoCapital
        fields = '__all__'


class InstrumentoSerializer(serializers.ModelSerializer):
    id_mercado_nombre = serializers.CharField(source='id_mercado.nombre', read_only=True)
    id_moneda_codigo = serializers.CharField(source='id_moneda.codigo', read_only=True)
    eventos = EventoCapitalSerializer(many=True, read_only=True)
    
    class Meta:
        model = Instrumento
        fields = '__all__'


# ========= SERIALIZERS CALIFICACIONES =========

class FactorDefSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactorDef
        fields = '__all__'


class CalificacionMontoDetalleSerializer(serializers.ModelSerializer):
    id_factor_codigo = serializers.CharField(source='id_factor.codigo_factor', read_only=True)
    
    class Meta:
        model = CalificacionMontoDetalle
        fields = '__all__'


class CalificacionFactorDetalleSerializer(serializers.ModelSerializer):
    id_factor_codigo = serializers.CharField(source='id_factor.codigo_factor', read_only=True)
    
    class Meta:
        model = CalificacionFactorDetalle
        fields = '__all__'


class CalificacionSerializer(serializers.ModelSerializer):
    id_corredora_nombre = serializers.CharField(source='id_corredora.nombre', read_only=True)
    id_corredora_pais_codigo = serializers.CharField(source='id_corredora.id_pais.codigo', read_only=True)
    id_corredora_pais_nombre = serializers.CharField(source='id_corredora.id_pais.nombre', read_only=True)
    id_instrumento_codigo = serializers.CharField(source='id_instrumento.codigo', read_only=True)
    id_instrumento_nombre = serializers.CharField(source='id_instrumento.nombre', read_only=True)
    id_fuente_nombre = serializers.CharField(source='id_fuente.nombre', read_only=True)
    id_moneda_codigo = serializers.CharField(source='id_moneda.codigo', read_only=True)
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    detalles_montos = CalificacionMontoDetalleSerializer(many=True, read_only=True, source='calificacionmontodetalle_set')
    detalles_factores = CalificacionFactorDetalleSerializer(many=True, read_only=True, source='calificacionfactordetalle_set')
    
    class Meta:
        model = Calificacion
        fields = '__all__'
        read_only_fields = ['creado_por', 'actualizado_por', 'creado_en', 'actualizado_en']


# ========= SERIALIZERS CARGAS =========

class CargaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargaDetalle
        fields = '__all__'


class CargaSerializer(serializers.ModelSerializer):
    id_corredora_nombre = serializers.CharField(source='id_corredora.nombre', read_only=True)
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    id_fuente_nombre = serializers.CharField(source='id_fuente.nombre', read_only=True)
    detalles = CargaDetalleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Carga
        fields = '__all__'
        read_only_fields = ['filas_total', 'insertados', 'actualizados', 'rechazados']


# ========= SERIALIZERS AUDITORIA =========

class AuditoriaSerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Auditoria
        fields = [
            'id_auditoria', 'actor_id', 'actor_username', 'entidad', 'entidad_id',
            'accion', 'fecha', 'fuente', 'valores_antes', 'valores_despues',
            'creado_en', 'actualizado_en'
        ]
        read_only_fields = ['id_auditoria', 'actor_id', 'fecha', 'creado_en', 'actualizado_en']
    
    def get_actor_username(self, obj):
        """Obtener username del actor de forma segura"""
        if obj.actor_id:
            return obj.actor_id.username
        return None
    
    # Los campos valores_antes y valores_despues se manejan automáticamente
    # por el OracleJSONField personalizado, que ya devuelve dict/list directamente
    # DRF puede serializar estos tipos sin problemas

