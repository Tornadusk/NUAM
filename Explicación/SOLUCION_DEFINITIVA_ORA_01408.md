# Solución Definitiva para ORA-01408

## 🔍 Problema

Tu compañero usó **Método 1** (solo `python manage.py migrate`) y obtuvo el error:

```
ORA-01408: esta lista de columnas ya está indexada
```

Esto significa que **Oracle ya tiene los índices creados**, aunque no hayas ejecutado `cretetable_oracle`.

## 🎯 ¿Por qué pasa esto?

Oracle puede crear índices automáticamente en estos casos:

1. **Foreign Keys**: En algunas versiones/configuraciones de Oracle, se crean índices automáticamente para FKs
2. **UNIQUE constraints**: Oracle siempre crea un índice único automáticamente
3. **PRIMARY KEY**: Oracle siempre crea un índice automáticamente
4. **Si ya ejecutaste `migrate` parcialmente**: Los índices pueden haberse creado antes de que fallara

## ✅ Solución: Verificar y Ajustar

### Paso 1: Verificar qué índices existen en Oracle

Conéctate a Oracle y ejecuta:

```sql
-- Ver índices en usuario_rol
SELECT index_name, column_name, column_position
FROM user_ind_columns 
WHERE table_name = 'USUARIO_ROL' 
ORDER BY index_name, column_position;

-- Ver índices en auditoria
SELECT index_name, column_name, column_position
FROM user_ind_columns 
WHERE table_name = 'AUDITORIA' 
ORDER BY index_name, column_position;
```

### Paso 2: Si los índices YA existen

**Comenta los `AddIndex` en las migraciones:**

**En `usuarios/migrations/0002_usuario_usuario_usernam_284c68_idx_and_more.py` (línea 37-40):**
```python
# migrations.AddIndex(
#     model_name='usuariorol',
#     index=models.Index(fields=['id_rol'], name='usuario_rol_id_rol_52d79a_idx'),
# ),
```

**En `auditoria/migrations/0003_alter_auditoria_valores_antes_and_more.py` (líneas 39-45):**
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

### Paso 3: Ejecutar migrate con --fake para las migraciones problemáticas

Si las migraciones ya están parcialmente aplicadas:

```bash
# Marcar las migraciones como aplicadas (sin ejecutar los AddIndex)
python manage.py migrate usuarios 0002 --fake
python manage.py migrate auditoria 0003 --fake

# Continuar con el resto
python manage.py migrate
```

## 🔄 Alternativa: Empezar desde Cero

Si prefieres un esquema limpio:

```bash
# 1. Borrar todas las tablas en Oracle
sqlplus nuam/nuam_pwd@127.0.0.1:1521/FREEPDB1

-- Ejecutar en SQL*Plus:
DROP TABLE usuario_rol CASCADE CONSTRAINTS;
DROP TABLE auditoria CASCADE CONSTRAINTS;
-- (y otras tablas si es necesario)

-- 2. Asegúrate de tener los últimos cambios
git pull

-- 3. Ejecuta las migraciones (con AddIndex descomentados)
python manage.py migrate
```

## 📝 Recomendación Final

**Para evitar este problema en el futuro:**

1. **Primera vez (esquema limpio):**
   - Deja los `AddIndex` **descomentados** en las migraciones
   - Ejecuta `python manage.py migrate`
   - Los índices se crearán correctamente

2. **Si obtienes ORA-01408:**
   - Verifica qué índices existen en Oracle
   - Comenta los `AddIndex` correspondientes
   - Usa `--fake` para marcar las migraciones como aplicadas

3. **Para nuevos desarrolladores:**
   - Si clonan el proyecto y ejecutan `migrate` por primera vez, los índices se crearán
   - Si el proyecto ya tiene tablas creadas, deben verificar qué índices existen

## 🎯 Estado Actual del Código

Actualmente, los `AddIndex` están **descomentados** en las migraciones. Esto funciona para:
- ✅ Nuevos esquemas (primera vez ejecutando `migrate`)
- ❌ Esquemas existentes donde Oracle ya creó los índices automáticamente

**Solución temporal:** Si tu compañero obtiene `ORA-01408`, debe comentar los `AddIndex` manualmente antes de ejecutar `migrate`.

