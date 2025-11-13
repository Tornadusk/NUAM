# Solución para ORA-01408 en Método 1 (Solo Migraciones)

## 🔍 Problema

Cuando usas **Método 1** (solo `python manage.py migrate`), Oracle crea automáticamente índices para campos `UNIQUE`. Luego, cuando Django intenta crear índices adicionales en las mismas columnas, Oracle lanza el error:

```
ORA-01408: esta lista de columnas ya está indexada
```

## ✅ Solución Rápida

### Paso 1: Verificar qué índices ya existen

Conéctate a Oracle y ejecuta:

```sql
-- Ver índices en usuario_rol
SELECT index_name, column_name 
FROM user_ind_columns 
WHERE table_name = 'USUARIO_ROL' 
ORDER BY index_name, column_position;

-- Ver índices en auditoria
SELECT index_name, column_name 
FROM user_ind_columns 
WHERE table_name = 'AUDITORIA' 
ORDER BY index_name, column_position;
```

### Paso 2: Comentar los AddIndex problemáticos

**En `usuarios/migrations/0002_usuario_usuario_usernam_284c68_idx_and_more.py`:**

Comenta la línea 34-37 (el índice `id_rol` en `usuario_rol`):

```python
# migrations.AddIndex(
#     model_name='usuariorol',
#     index=models.Index(fields=['id_rol'], name='usuario_rol_id_rol_52d79a_idx'),
# ),
```

**En `auditoria/migrations/0003_alter_auditoria_valores_antes_and_more.py`:**

Comenta las líneas 36-42 (los índices `entidad, entidad_id` y `fecha`):

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

### Paso 3: Ejecutar migraciones nuevamente

```bash
python manage.py migrate
```

## 🔄 Alternativa: Usar --fake para índices específicos

Si prefieres no modificar las migraciones, puedes marcar solo las operaciones problemáticas como "fake":

```bash
# Marcar la migración de usuarios como aplicada (sin ejecutar)
python manage.py migrate usuarios 0002 --fake

# Marcar la migración de auditoria como aplicada (sin ejecutar)
python manage.py migrate auditoria 0003 --fake

# Continuar con el resto
python manage.py migrate
```

## 📝 Nota Importante

- **Método 1 (Solo Migraciones)**: Los índices se crean mediante migraciones. Si Oracle ya los creó automáticamente, comenta los `AddIndex` en las migraciones.
- **Método 2 (cretetable_oracle)**: Los índices ya están en `cretetable_oracle`, así que siempre debes comentar los `AddIndex` en las migraciones.

## 🎯 ¿Por qué pasa esto?

Oracle crea automáticamente índices para:
- Campos con constraint `UNIQUE`
- Campos con constraint `PRIMARY KEY`
- Foreign keys (en algunas versiones)

Cuando Django intenta crear un índice adicional en la misma columna (aunque no sea único), Oracle detecta que ya existe un índice y lanza `ORA-01408`.

## ✅ Verificación

Después de aplicar la solución, verifica que las migraciones se aplicaron correctamente:

```bash
python manage.py showmigrations
```

Todas las migraciones de `usuarios` y `auditoria` deben mostrar `[X]` (aplicadas).

