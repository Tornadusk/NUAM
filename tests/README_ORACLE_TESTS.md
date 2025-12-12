# Solución para Error ORA-01031 en Tests

## Problema

Cuando ejecutas tests con `pytest`, puedes encontrar el error:

```
ORA-01031: privilegios insuficientes
Got an error creating the test database: ORA-01031: privilegios insuficientes
```

Este error ocurre porque Django intenta crear una base de datos temporal para los tests, pero el usuario de Oracle no tiene los permisos necesarios.

## Soluciones

### ✅ Opción 1: Usar SQLite para Tests (YA CONFIGURADO - Recomendado para desarrollo)

**El sistema ya está configurado para usar SQLite automáticamente en tests.** 

La configuración usa SQLite solo para los tests, sin afectar la base de datos de producción que usa Oracle.

#### Configuración Actual

El proyecto ya incluye:

1. **`pytest_settings.py`**: Archivo de configuración que sobrescribe la base de datos para usar SQLite en tests
2. **`pytest.ini`**: Configurado para usar `pytest_settings` como módulo de configuración
3. **`.gitignore`**: Incluye `test_db.sqlite3` para no subir la base de datos de tests

#### ¿Cómo funciona?

- Cuando ejecutas `pytest` o usas el dashboard de Testing, automáticamente se usa SQLite
- La base de datos de producción (Oracle) **NO se afecta** - solo se usa para la aplicación normal
- Los tests son más rápidos y no requieren permisos especiales

#### Si ves el error ORA-01031

Si aún ves el error `ORA-01031` en el dashboard de Testing, verifica que:

1. `pytest_settings.py` existe en la raíz del proyecto
2. `pytest.ini` tiene `DJANGO_SETTINGS_MODULE = pytest_settings`
3. Reinicia el servidor Django después de hacer cambios en la configuración

El dashboard mostrará un mensaje claro indicando el problema y la solución cuando detecte este error.

### Opción 2: Otorgar Permisos en Oracle (Solo si tienes acceso DBA)

Si tienes acceso como DBA o puedes solicitar permisos, puedes otorgar los privilegios necesarios al usuario.

#### Conectarse como DBA

```sql
sqlplus sys as sysdba
-- O en Oracle 23c Free:
sqlplus sys/password@localhost:1521/FREEPDB1 as sysdba
```

#### Otorgar permisos

```sql
-- Reemplaza 'nuam' con tu usuario
GRANT CREATE DATABASE LINK TO nuam;
GRANT CREATE MATERIALIZED VIEW TO nuam;
GRANT CREATE TABLE TO nuam;
GRANT CREATE SEQUENCE TO nuam;
GRANT CREATE PROCEDURE TO nuam;
GRANT CREATE TRIGGER TO nuam;
GRANT CREATE TYPE TO nuam;
GRANT CREATE VIEW TO nuam;
GRANT CREATE SYNONYM TO nuam;

-- También otorgar permisos sobre el schema
GRANT UNLIMITED TABLESPACE TO nuam;

COMMIT;
```

**Nota**: En Oracle Database 23c Free, es posible que algunos de estos permisos ya estén otorgados, pero es necesario verificar.

### Opción 3: Desactivar creación de base de datos de prueba

Puedes configurar pytest para reutilizar la base de datos existente (menos recomendado, puede causar conflictos):

En `pytest.ini`:

```ini
[pytest]
addopts = 
    --tb=short
    --strict-markers
    --disable-warnings
    --reuse-db
    --nomigrations  # No ejecutar migraciones en tests
```

Y en tu configuración de Django, puedes desactivar la creación automática de base de datos de prueba:

```python
# En settings.py
TEST = {
    'CREATE_DB': False,  # No crear base de datos para tests
}
```

⚠️ **Advertencia**: Esta opción puede causar que los tests interfieran entre sí o con datos de producción.

## Recomendación

**Para desarrollo local**: Usa la **Opción 1 (SQLite)**. Es la más simple, rápida y segura.

**Para CI/CD o ambientes controlados**: Puedes usar la **Opción 2** si tienes acceso DBA.

**Para producción**: Los tests no deberían ejecutarse contra la base de datos de producción. Siempre usa una base de datos de pruebas separada.

## Verificar la Solución

Después de aplicar cualquiera de las soluciones, ejecuta los tests nuevamente:

```bash
pytest
# O desde el dashboard de Testing en NUAM
```

Si todo funciona correctamente, deberías ver los tests ejecutándose sin el error `ORA-01031`.

## Referencias

- [Django Testing with Oracle](https://docs.djangoproject.com/en/stable/topics/testing/overview/#testing-with-oracle)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)

