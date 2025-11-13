# Solución para Índices Duplicados en Oracle

## Problema

Oracle Database lanza el error `ORA-01408: esta lista de columnas ya está indexada` cuando Django intenta crear índices que ya existen en la base de datos.

## Causa

1. **Índices creados por `cretetable_oracle`**:
   - `ix_usuario_persona` en `usuario(id_persona)` (línea 111)
   - `ix_aud_actor` en `auditoria(actor_id)` (línea 408)

2. **Índices automáticos de Oracle**:
   - Oracle crea automáticamente índices para columnas `UNIQUE`
   - Oracle crea automáticamente índices para constraints `UNIQUE`

3. **Django intenta crear índices duplicados**:
   - En `usuarios/models.py`: `username` (ya tiene índice por UNIQUE), `id_persona` (ya existe `ix_usuario_persona`)
   - En `usuario_rol`: `(id_usuario, id_rol)` (ya tiene índice por UNIQUE constraint)
   - En `auditoria/models.py`: `actor_id` (ya existe `ix_aud_actor`)

## Solución Implementada

### 1. Comentar índices en los modelos

**`usuarios/models.py`**:
- Comentados `indexes` para `Usuario` y `UsuarioRol` porque:
  - `username` tiene índice automático por `UNIQUE`
  - `id_persona` ya tiene `ix_usuario_persona` en Oracle
  - `(id_usuario, id_rol)` tiene índice automático por `UNIQUE` constraint

**`auditoria/models.py`**:
- Comentados `indexes` porque:
  - `actor_id` ya tiene `ix_aud_actor` en Oracle
  - Los otros índices (`entidad, entidad_id` y `fecha`) no existen en `cretetable_oracle`

### 2. Comentar operaciones en migraciones

**`usuarios/migrations/0002_*.py`**:
- Todas las operaciones `AddIndex` están comentadas

**`auditoria/migrations/0003_*.py`**:
- Todas las operaciones `AddIndex` están comentadas

## Archivo `db.sqlite3`

El archivo `db.sqlite3` existe porque:
1. Django crea automáticamente este archivo cuando se usa SQLite (base de datos por defecto)
2. El proyecto ahora usa Oracle, pero el archivo SQLite puede quedar de pruebas anteriores
3. Está en `.gitignore` (línea 59), por lo que no se sube al repositorio
4. **No afecta el funcionamiento** porque `settings.py` está configurado para usar Oracle

### ¿Eliminarlo?

Puedes eliminarlo de forma segura si:
- Estás 100% seguro de que no lo necesitas
- No tienes datos importantes en SQLite
- Solo usas Oracle en producción

**Comando para eliminar**:
```bash
rm db.sqlite3
# o en Windows:
del db.sqlite3
```

## ¿Modificó la BD?

**NO**, las migraciones **NO modifican** los archivos `cretetable_oracle` ni `MODELO.DDL` porque:
1. Esos archivos son **documentación/referencia** del esquema de la BD
2. Las migraciones de Django solo afectan la **BD Oracle** cuando ejecutas `python manage.py migrate`
3. `cretetable_oracle` es un script SQL que debes ejecutar manualmente en Oracle
4. `MODELO.DDL` es un archivo de diseño/documentación (formato dbdiagram.io)

## Flujo Correcto

1. **Primera vez (setup inicial)**:
   ```bash
   # 1. Ejecutar cretable_oracle en Oracle (crea tablas e índices)
   # 2. Ejecutar migrations de Django (sin crear índices duplicados)
   python manage.py migrate --fake
   ```

2. **Desarrollo continuo**:
   ```bash
   # Si necesitas nuevos índices:
   # 1. Agregarlos a cretable_oracle
   # 2. Ejecutarlos manualmente en Oracle
   # 3. Comentar los índices en los modelos de Django
   # 4. Crear migraciones sin índices
   python manage.py makemigrations
   python manage.py migrate
   ```

## Índices que Faltan en `cretetable_oracle`

Si necesitas estos índices, agrégalos a `cretetable_oracle`:

```sql
-- Para auditoria (no existen actualmente)
CREATE INDEX ix_aud_entidad ON auditoria(entidad, entidad_id);
CREATE INDEX ix_aud_fecha ON auditoria(fecha);

-- Para usuario_rol (no existe actualmente)
CREATE INDEX ix_usuario_rol_rol ON usuario_rol(id_rol);
```

Luego, en los modelos de Django, **NO** agregues estos índices en `Meta.indexes`, porque ya existirán en Oracle.

## Conclusión

- Los índices están **comentados en los modelos** para evitar que Django intente crearlos
- Los índices están **comentados en las migraciones** para evitar errores al aplicar migraciones
- Los índices **ya existen en Oracle** (creados por `cretetable_oracle` o automáticamente por Oracle)
- El archivo `db.sqlite3` **no afecta** el funcionamiento (proyecto usa Oracle)
- Las migraciones **NO modifican** `cretetable_oracle` ni `MODELO.DDL` (son archivos de referencia)

