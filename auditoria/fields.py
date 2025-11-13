"""
Campo JSONField personalizado para manejar Oracle Database
Oracle devuelve JSONField como dict en lugar de string, lo cual causa errores
en Django's JSONField.from_db_value que intenta hacer json.loads() en un dict
"""
from django.db.models import JSONField
import json


class OracleJSONField(JSONField):
    """
    JSONField personalizado que maneja correctamente Oracle Database
    Oracle devuelve JSON como dict/list de Python, no como string JSON,
    por lo que necesitamos manejar este caso especial en from_db_value
    
    El problema: Django's JSONField.from_db_value intenta hacer
    json.loads(value) pero Oracle ya devuelve el valor como dict,
    causando el error: "the JSON object must be str, bytes or bytearray, not dict"
    """
    
    def from_db_value(self, value, expression, connection):
        """
        Convertir valor de la base de datos a Python
        Oracle devuelve JSON como dict/list, PostgreSQL como string JSON
        
        Sobrescribimos este método para manejar el caso de Oracle donde
        el valor ya viene deserializado como dict/list
        """
        if value is None:
            return value
        
        # Si ya es dict o list, devolverlo directamente (caso Oracle)
        # Oracle ya deserializa el JSON cuando lo lee de la base de datos
        # No necesitamos parsearlo de nuevo
        if isinstance(value, (dict, list)):
            return value
        
        # Si es string o bytes, intentar parsearlo (caso PostgreSQL u otros)
        # Esto es lo que haría el JSONField normal de Django
        if isinstance(value, (str, bytes, bytearray)):
            try:
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                # Usar el decoder del campo si está disponible
                decoder = getattr(self, 'decoder', None)
                if decoder:
                    return json.loads(value, cls=decoder)
                else:
                    return json.loads(value)
            except (json.JSONDecodeError, TypeError, ValueError, UnicodeDecodeError):
                # Si falla, devolver el string original
                return value
        
        # Para cualquier otro tipo (int, float, bool, None), devolverlo tal cual
        # Esto no debería pasar normalmente, pero es seguro manejarlo
        return value

