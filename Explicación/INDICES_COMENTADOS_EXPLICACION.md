# Explicación: ¿Qué Índices Comentamos y Por Qué?

## ✅ Índices que SÍ son para UNIQUE/PRIMARY KEY (Oracle los crea automáticamente)

Estos índices **SÍ deben comentarse** porque Oracle los crea automáticamente:

### 1. `usuario.username` (línea 18-21)
```python
# migrations.AddIndex(
#     model_name='usuario',
#     index=models.Index(fields=['username'], name='usuario_usernam_284c68_idx'),
# ),
```
**Razón:** `username` tiene `unique=True` → Oracle crea índice único automáticamente ✅

### 2. `usuario_rol(id_usuario, id_rol)` (línea 26-29)
```python
# migrations.AddIndex(
#     model_name='usuariorol',
#     index=models.Index(fields=['id_usuario', 'id_rol'], name='usuario_rol_id_usua_517075_idx'),
# ),
```
**Razón:** `unique_together = [['id_usuario', 'id_rol']]` → Oracle crea índice único automáticamente ✅

### 3. PRIMARY KEY (todos los modelos)
- `id_persona` (PK de `Persona`)
- `id_usuario` (PK de `Usuario`)
- `id_rol` (PK de `Rol`)
- `id_auditoria` (PK de `Auditoria`)

**Razón:** Oracle crea índice automáticamente para PRIMARY KEY ✅

## ⚠️ Índices que NO son para UNIQUE/PRIMARY KEY (pero también los comentamos)

Estos índices **NO son** para UNIQUE/PRIMARY KEY, pero los comentamos porque Oracle ya los creó por otra razón:

### 1. `usuario_rol(id_rol)` (línea 36-39)
```python
# migrations.AddIndex(
#     model_name='usuariorol',
#     index=models.Index(fields=['id_rol'], name='usuario_rol_id_rol_52d79a_idx'),
# ),
```
**Razón para comentar:**
- `id_rol` es un **Foreign Key** (NO es UNIQUE ni PRIMARY KEY)
- Oracle **NO siempre** crea índices automáticamente para FKs
- Pero si ya existe (por ejecución previa de `migrate` o por `cretetable_oracle`), debemos comentarlo para evitar `ORA-01408`

### 2. `auditoria(entidad, entidad_id)` (línea 38-41)
```python
# migrations.AddIndex(
#     model_name='auditoria',
#     index=models.Index(fields=['entidad', 'entidad_id'], name='auditoria_entidad_9c3bf7_idx'),
# ),
```
**Razón para comentar:**
- Son **campos normales** (NO son UNIQUE ni PRIMARY KEY)
- Oracle **NO** crea índices automáticamente para campos normales
- Pero si ya existe (por ejecución previa de `migrate` o por `cretetable_oracle`), debemos comentarlo para evitar `ORA-01408`

### 3. `auditoria(fecha)` (línea 42-45)
```python
# migrations.AddIndex(
#     model_name='auditoria',
#     index=models.Index(fields=['fecha'], name='auditoria_fecha_b71d64_idx'),
# ),
```
**Razón para comentar:**
- Es un **campo normal** (NO es UNIQUE ni PRIMARY KEY)
- Oracle **NO** crea índices automáticamente para campos normales
- Pero si ya existe (por ejecución previa de `migrate` o por `cretetable_oracle`), debemos comentarlo para evitar `ORA-01408`

## 📊 Resumen

| Índice | Tipo | Oracle lo crea automáticamente? | ¿Por qué comentarlo? |
|--------|------|--------------------------------|----------------------|
| `usuario.username` | UNIQUE | ✅ Sí | Oracle lo crea automáticamente |
| `usuario_rol(id_usuario, id_rol)` | UNIQUE (unique_together) | ✅ Sí | Oracle lo crea automáticamente |
| Todos los PRIMARY KEY | PRIMARY KEY | ✅ Sí | Oracle lo crea automáticamente |
| `usuario_rol(id_rol)` | Foreign Key | ❌ No (depende) | Ya existe por otra razón |
| `auditoria(entidad, entidad_id)` | Campos normales | ❌ No | Ya existe por otra razón |
| `auditoria(fecha)` | Campo normal | ❌ No | Ya existe por otra razón |

## 🎯 Conclusión

**Sí, los índices de UNIQUE y PRIMARY KEY son los que Oracle crea automáticamente y deben comentarse.**

**PERO** también comentamos otros índices que:
- NO son para UNIQUE/PRIMARY KEY
- Oracle NO los crea automáticamente
- Pero **YA EXISTEN** en Oracle por alguna razón (ejecución previa de `migrate`, `cretetable_oracle`, etc.)

**Regla general:** Si obtienes `ORA-01408`, significa que el índice **YA EXISTE** en Oracle, independientemente de si es UNIQUE/PRIMARY KEY o no. Por lo tanto, debes comentarlo en las migraciones.

