"""
Funciones auxiliares compartidas para las vistas de microservicios
"""
from corredoras.models import UsuarioCorredora


def obtener_corredora_usuario(usuario_obj):
    """
    Función auxiliar para obtener la corredora principal de un usuario
    
    Args:
        usuario_obj: Instancia del modelo Usuario
        
    Returns:
        Corredora o None
    """
    if not usuario_obj:
        return None
    usuario_corredora = UsuarioCorredora.objects.filter(
        id_usuario=usuario_obj,
        es_principal=True
    ).first()
    return usuario_corredora.id_corredora if usuario_corredora else None

