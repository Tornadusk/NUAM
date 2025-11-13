# Explicación: ¿Se Aplicarán los Índices si los Comentamos en las Migraciones?

## 🔍 Situación Actual

### En los Modelos Django (`models.py`)

Los índices **SÍ están definidos** en los modelos:

**`usuarios/models.py` (línea 111):**
```python
class UsuarioRol(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['id_rol']),  # ✅ ESTÁ DESCOMENTADO
        ]
```

**`auditoria/models.py` (líneas 45-46):**
```python
class Auditoria(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['entidad', 'entidad_id']),  # ✅ ESTÁ DESCOMENTADO
            models.Index(fields=['fecha']),  # ✅ ESTÁ DESCOMENTADO
        ]
```

### En las Migraciones

Los `AddIndex` están **COMENTADOS** en las migraciones:

**`usuarios/migrations/0002_*.py`:**
```python
# migrations.AddIndex(
#     model_name='usuariorol',
#     index=models.Index(fields=['id_rol'], name='usuario_rol_id_rol_52d79a_idx'),
# ),
```

**`auditoria/migrations/0003_*.py`:**
```python
# migrations.AddIndex(
#     model_name='auditoria',
#     index=models.Index(fields=['entidad', 'entidad_id'], name='auditoria_entidad_9c3bf7_idx'),
# ),
# migrations.AddIndex(
#     model_name='auditoria',
#     index=models.Index(fields=['fecha'], name='auditoria_fecha_b71d64_idx'),
# ),
```

## ✅ ¿Qué Significa Esto?

### 1. Django Conoce los Índices

- Los índices están en `models.py`, por lo que Django los conoce
- Django los usará en las queries para optimizar búsquedas
- El ORM sabe que estos índices existen

### 2. Las Migraciones NO Intentarán Crearlos

- Al comentar los `AddIndex`, las migraciones no ejecutarán `CREATE INDEX`
- Esto evita el error `ORA-01408` si Oracle ya tiene los índices

### 3. ¿Los Índices Existen en Oracle?

**Depende del método usado:**

#### Método 1: Solo Migraciones (`python manage.py migrate`)

Oracle crea automáticamente índices para:
- ✅ Campos `UNIQUE` → Oracle crea índice único automáticamente
- ✅ Campos `PRIMARY KEY` → Oracle crea índice automáticamente
- ❌ Foreign Keys → **NO siempre** crea índice automáticamente
- ❌ Campos normales → **NO** crea índice automáticamente

**Para `usuario_rol(id_rol)`:**
- `id_rol` es un Foreign Key
- Oracle **NO siempre** crea índice automáticamente para FKs
- **Necesitamos crearlo manualmente** o descomentar el `AddIndex`

**Para `auditoria(entidad, entidad_id)` y `auditoria(fecha)`:**
- Son campos normales (no UNIQUE, no PK, no FK)
- Oracle **NO** crea índices automáticamente
- **Necesitamos crearlos manualmente** o descomentar los `AddIndex`

#### Método 2: cretable_oracle + Migraciones

- Los índices ya están en `cretetable_oracle` (líneas 132, 410, 411)
- Si ejecutaste `cretetable_oracle`, los índices **YA EXISTEN**
- Por eso comentamos los `AddIndex` para evitar `ORA-01408`

## 🎯 Solución Correcta

### Opción A: Si Usas Método 1 (Solo Migraciones)

**Problema:** Oracle NO crea automáticamente índices para campos normales o FKs.

**Solución:** Descomentar los `AddIndex` en las migraciones, PERO solo si Oracle NO los tiene:

1. **Verifica si los índices existen:**
```sql
-- Conéctate a Oracle
sqlplus nuam/nuam_pwd@127.0.0.1:1521/FREEPDB1

-- Ver índices en usuario_rol
SELECT index_name, column_name 
FROM user_ind_columns 
WHERE table_name = 'USUARIO_ROL' 
AND column_name = 'ID_ROL';

-- Ver índices en auditoria
SELECT index_name, column_name 
FROM user_ind_columns 
WHERE table_name = 'AUDITORIA' 
AND column_name IN ('ENTIDAD', 'ENTIDAD_ID', 'FECHA');
```

2. **Si NO existen, descomenta los `AddIndex` en las migraciones:**
   - `usuarios/migrations/0002_*.py` línea 34-37
   - `auditoria/migrations/0003_*.py` líneas 36-42

3. **Si YA existen, déjalos comentados** (evita `ORA-01408`)

### Opción B: Si Usas Método 2 (cretetable_oracle)

**Los índices YA están creados** por `cretetable_oracle`, así que:
- ✅ Mantén los `AddIndex` comentados en las migraciones
- ✅ Los índices están en la BD
- ✅ Django los conoce (están en `models.py`)

## 📝 Resumen

| Situación | Índices en `models.py` | `AddIndex` en Migraciones | Índices en Oracle | Resultado |
|-----------|------------------------|---------------------------|-------------------|-----------|
| Método 1, índices NO existen | ✅ Descomentados | ❌ Comentados | ❌ No existen | ⚠️ **Problema**: Django los conoce pero no existen en BD |
| Método 1, índices SÍ existen | ✅ Descomentados | ❌ Comentados | ✅ Existen | ✅ **OK**: Todo funciona |
| Método 2 (cretetable_oracle) | ✅ Descomentados | ❌ Comentados | ✅ Existen | ✅ **OK**: Todo funciona |

## 🔧 Recomendación Final

**Para Método 1 (Solo Migraciones):**

1. **Primera vez (esquema limpio):**
   - Descomenta los `AddIndex` en las migraciones
   - Ejecuta `python manage.py migrate`
   - Los índices se crearán correctamente

2. **Si ya ejecutaste migrate y falló:**
   - Verifica qué índices existen en Oracle
   - Si NO existen, descomenta los `AddIndex` y ejecuta `migrate` nuevamente
   - Si YA existen (por UNIQUE constraints), déjalos comentados

**Para Método 2 (cretetable_oracle):**
- ✅ Mantén los `AddIndex` comentados (los índices ya están en `cretetable_oracle`)


Resumen de lo que se hizo:
Se comentaron los índices problemáticos en los modelos (usuarios/models.py, auditoria/models.py, core/models.py, instrumentos/models.py, calificaciones/models.py, cargas/models.py, corredoras/models.py).
Se comentaron los índices en las migraciones recién generadas para evitar ORA-01408.
Se aplicaron todas las migraciones.