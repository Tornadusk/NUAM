# pytest_settings.py
# Configuración específica para tests usando SQLite
# Esto permite ejecutar tests sin necesidad de permisos especiales en Oracle

from proyecto_nuam.settings import *
from pathlib import Path

# Sobrescribir DATABASES solo para tests - usar SQLite en lugar de Oracle
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Desactivar migraciones en tests para hacerlos más rápidos (opcional)
# Si tienes problemas con migraciones, puedes descomentar esto:
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# 
# MIGRATION_MODULES = DisableMigrations()

# Mantener otras configuraciones de settings.py
# (PULSAR, SECRET_KEY, etc. se heredan automáticamente)

