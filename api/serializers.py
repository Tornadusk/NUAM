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
    
    def validate_fecha_nacimiento(self, value):
        """Validar que la fecha de nacimiento no sea futura y sea razonable"""
        from django.utils import timezone
        from datetime import date, timedelta
        
        hoy = date.today()
        
        # No puede ser una fecha futura
        if value > hoy:
            raise serializers.ValidationError(
                "La fecha de nacimiento no puede ser superior a la fecha actual."
            )
        
        # Edad mínima: 18 años (opcional, puedes ajustar)
        edad_minima = hoy - timedelta(days=18*365 + 4)  # Aproximadamente 18 años (considerando años bisiestos)
        if value > edad_minima:
            raise serializers.ValidationError(
                "La fecha de nacimiento debe ser de al menos 18 años atrás."
            )
        
        # Edad máxima: 120 años (evitar fechas muy antiguas o erróneas)
        edad_maxima = hoy - timedelta(days=120*365 + 30)  # Aproximadamente 120 años
        if value < edad_maxima:
            raise serializers.ValidationError(
                "La fecha de nacimiento no puede ser anterior a 120 años."
            )
        
        return value
    
    def validate_primer_nombre(self, value):
        """Validar que el primer nombre tenga contenido válido"""
        if not value or not value.strip():
            raise serializers.ValidationError("El primer nombre no puede estar vacío.")
        
        value = value.strip()
        
        # No puede ser solo números
        if value.isdigit():
            raise serializers.ValidationError("El primer nombre no puede ser solo números.")
        
        # Validar longitud mínima
        if len(value) < 2:
            raise serializers.ValidationError("El primer nombre debe tener al menos 2 caracteres.")
        
        # Validar longitud máxima (80 caracteres según el modelo)
        if len(value) > 80:
            raise serializers.ValidationError("El primer nombre no puede tener más de 80 caracteres.")
        
        return value
    
    def validate_apellido_paterno(self, value):
        """Validar que el apellido paterno tenga contenido válido"""
        if not value or not value.strip():
            raise serializers.ValidationError("El apellido paterno no puede estar vacío.")
        
        value = value.strip()
        
        # No puede ser solo números
        if value.isdigit():
            raise serializers.ValidationError("El apellido paterno no puede ser solo números.")
        
        # Validar longitud mínima
        if len(value) < 2:
            raise serializers.ValidationError("El apellido paterno debe tener al menos 2 caracteres.")
        
        # Validar longitud máxima (80 caracteres según el modelo)
        if len(value) > 80:
            raise serializers.ValidationError("El apellido paterno no puede tener más de 80 caracteres.")
        
        return value
    
    def validate_segundo_nombre(self, value):
        """Validar segundo nombre si se proporciona"""
        if value:
            value = value.strip()
            # No puede ser solo números
            if value.isdigit():
                raise serializers.ValidationError("El segundo nombre no puede ser solo números.")
            # Validar longitud mínima si se proporciona
            if len(value) < 2:
                raise serializers.ValidationError("El segundo nombre debe tener al menos 2 caracteres.")
            # Validar longitud máxima (80 caracteres según el modelo)
            if len(value) > 80:
                raise serializers.ValidationError("El segundo nombre no puede tener más de 80 caracteres.")
        return value
    
    def validate_apellido_materno(self, value):
        """Validar apellido materno si se proporciona"""
        if value:
            value = value.strip()
            # No puede ser solo números
            if value.isdigit():
                raise serializers.ValidationError("El apellido materno no puede ser solo números.")
            # Validar longitud mínima si se proporciona
            if len(value) < 2:
                raise serializers.ValidationError("El apellido materno debe tener al menos 2 caracteres.")
            # Validar longitud máxima (80 caracteres según el modelo)
            if len(value) > 80:
                raise serializers.ValidationError("El apellido materno no puede tener más de 80 caracteres.")
        return value
    
    def validate_nacionalidad(self, value):
        """Validar formato de nacionalidad ISO-3"""
        if value:
            value = value.strip().upper()
            # Debe ser exactamente 3 caracteres
            if len(value) != 3:
                raise serializers.ValidationError(
                    "La nacionalidad debe ser un código ISO-3 de 3 caracteres (ej: CHL, PER, COL)."
                )
            # Debe contener solo letras
            if not value.isalpha():
                raise serializers.ValidationError(
                    "La nacionalidad solo puede contener letras (código ISO-3)."
                )
        return value


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
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'id_persona', 'username', 'estado', 'password']
        read_only_fields = ['id_usuario']  # Automático, pero devolverlo
    
    def validate_username(self, value):
        """Validar que el username tenga contenido válido"""
        if not value or not value.strip():
            raise serializers.ValidationError("El username no puede estar vacío.")
        
        # Longitud mínima: 3 caracteres
        if len(value.strip()) < 3:
            raise serializers.ValidationError("El username debe tener al menos 3 caracteres.")
        
        # Longitud máxima: 60 caracteres (definido en el modelo)
        if len(value.strip()) > 60:
            raise serializers.ValidationError("El username no puede tener más de 60 caracteres.")
        
        # Solo puede contener letras, números, guiones y guiones bajos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value.strip()):
            raise serializers.ValidationError(
                "El username solo puede contener letras, números, guiones (-) y guiones bajos (_)."
            )
        
        return value.strip()
    
    def validate_password(self, value):
        """Validar que la contraseña cumpla con los requisitos mínimos"""
        if not value:
            raise serializers.ValidationError("La contraseña es obligatoria.")
        
        # Longitud mínima: 6 caracteres
        if len(value) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        
        # Longitud máxima: 128 caracteres (límite razonable para contraseñas)
        if len(value) > 128:
            raise serializers.ValidationError("La contraseña no puede tener más de 128 caracteres.")
        
        return value
    
    def create(self, validated_data):
        # El password se extrae y se maneja en perform_create del ViewSet
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)
        usuario.save()
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario


class ColaboradorSerializer(serializers.ModelSerializer):
    id_usuario_username = serializers.CharField(source='id_usuario.username', read_only=True)
    
    class Meta:
        model = Colaborador
        fields = '__all__'
    
    def validate_gmail(self, value):
        """Validar que el email Gmail tenga formato válido y longitud adecuada"""
        if not value:
            raise serializers.ValidationError("El email es obligatorio.")
        
        value = value.strip().lower()
        
        # Debe ser Gmail
        if not value.endswith('@gmail.com'):
            raise serializers.ValidationError(
                "El email debe ser una cuenta de Gmail válida (ej: usuario@gmail.com)."
            )
        
        # Extraer la parte local (antes de @gmail.com)
        parte_local = value.replace('@gmail.com', '')
        
        # Longitud mínima de la parte local: 1 carácter
        if len(parte_local) < 1:
            raise serializers.ValidationError(
                "El email debe tener al menos 1 carácter antes de @gmail.com."
            )
        
        # Longitud máxima de la parte local: 64 caracteres (RFC 5322)
        if len(parte_local) > 64:
            raise serializers.ValidationError(
                "La parte del email antes de @gmail.com no puede tener más de 64 caracteres."
            )
        
        # Longitud máxima total: 254 caracteres (RFC 5322, aunque Gmail es más restrictivo)
        if len(value) > 254:
            raise serializers.ValidationError(
                "El email no puede tener más de 254 caracteres en total."
            )
        
        # Validar caracteres permitidos en la parte local (según RFC 5322)
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+$', parte_local):
            raise serializers.ValidationError(
                "El email contiene caracteres no permitidos. Solo se permiten letras, números, puntos (.), guiones bajos (_), porcentajes (%), signos más (+) y guiones (-)."
            )
        
        # No puede empezar o terminar con punto
        if parte_local.startswith('.') or parte_local.endswith('.'):
            raise serializers.ValidationError(
                "La parte del email antes de @gmail.com no puede empezar o terminar con punto."
            )
        
        # No puede tener dos puntos consecutivos
        if '..' in parte_local:
            raise serializers.ValidationError(
                "La parte del email antes de @gmail.com no puede tener dos puntos consecutivos."
            )
        
        return value


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

