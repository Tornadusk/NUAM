"""
Serializers para Microservicios NUAM
"""
from rest_framework import serializers
from .models import TipoCambioFuente, TipoCambio


class TipoCambioFuenteSerializer(serializers.ModelSerializer):
    """Serializer para TipoCambioFuente"""
    
    class Meta:
        model = TipoCambioFuente
        fields = '__all__'
        read_only_fields = ('id_fuente', 'creado_en', 'actualizado_en')


class TipoCambioSerializer(serializers.ModelSerializer):
    """Serializer para TipoCambio"""
    id_fuente_nombre = serializers.CharField(source='id_fuente.nombre', read_only=True)
    id_fuente_codigo = serializers.CharField(source='id_fuente.codigo', read_only=True)
    
    class Meta:
        model = TipoCambio
        fields = '__all__'
        read_only_fields = ('id_tipo_cambio', 'creado_en')


