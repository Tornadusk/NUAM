# Guía de Inicialización de Base de Datos - NUAM

Este proyecto soporta **DOS métodos** para crear la base de datos Oracle. **Elige UNO** según tu preferencia.

## 🎯 Resumen Rápido

| Método | Cuándo Usar | Ventajas | Desventajas |
|--------|-------------|----------|-------------|
| **Solo Migraciones** | Desarrollo, equipos pequeños | Fácil mantenimiento, automático | Menos control sobre DDL |
| **cretable_oracle** | Producción, control total | Control total, DDL explícito | Requiere sincronización manual |

---

## 📋 Método 1: Solo Migraciones de Django (Recomendado)

### Pasos

1. **Configura la conexión a Oracle** en `proyecto_nuam/settings.py`
2. **Ejecuta migraciones**:
   ```bash
   python manage.py migrate
   ```
3. **Carga datos iniciales**:
   ```bash
   python create_data_initial.py
   ```

### ✅ Ventajas

- Django gestiona el esquema automáticamente
- Los índices se crean mediante migraciones
- Fácil de mantener cuando cambias modelos
- No necesitas modificar scripts SQL manualmente

### ⚠️ Notas

- Los índices están definidos en los modelos Django
- Las migraciones los crean automáticamente
- No necesitas ejecutar `cretable_oracle`

---

## 📋 Método 2: cretable_oracle + Migraciones

### Pasos

1. **Ejecuta `cretable_oracle` en Oracle**:
   ```sql
   -- Conéctate a Oracle como usuario nuam
   sqlplus nuam/nuam_pwd@127.0.0.1:1521/FREEPDB1
   
   -- Ejecuta el script
   @cretetable_oracle
   ```
   Esto crea todas las tablas e **índices** directamente en Oracle.

2. **Comenta los índices en las migraciones** para evitar errores `ORA-01408`:

   **En `usuarios/migrations/0002_usuario_usuario_usernam_284c68_idx_and_more.py`**:
   ```python
   # Comenta esta línea:
   # migrations.AddIndex(
   #     model_name='usuariorol',
   #     index=models.Index(fields=['id_rol'], name='usuario_rol_id_rol_52d79a_idx'),
   # ),
   ```

   **En `auditoria/migrations/0003_alter_auditoria_valores_antes_and_more.py`**:
   ```python
   # Comenta estas líneas:
   # migrations.AddIndex(
   #     model_name='auditoria',
   #     index=models.Index(fields=['entidad', 'entidad_id'], name='auditoria_entidad_9c3bf7_idx'),
   # ),
   # migrations.AddIndex(
   #     model_name='auditoria',
   #     index=models.Index(fields=['fecha'], name='auditoria_fecha_b71d64_idx'),
   # ),
   ```

3. **Ejecuta migraciones con `--fake-initial`**:
   ```bash
   python manage.py migrate --fake-initial
   ```
   Esto registra las migraciones sin intentar crear objetos que ya existen.

4. **Carga datos iniciales**:
   ```bash
   python create_data_initial.py
   ```

### ✅ Ventajas

- Control total sobre el DDL
- Útil para producción donde prefieres scripts SQL explícitos
- Los índices ya están creados en `cretetable_oracle`

### ⚠️ Notas

- **NO mezcles ambos métodos**: Si usas `cretable_oracle`, los índices ya estarán creados
- Si intentas crear los índices mediante migraciones después de usar `cretable_oracle`, obtendrás error `ORA-01408: esta lista de columnas ya está indexada`
- Debes mantener sincronizado `cretatable_oracle` con los modelos Django

---

## 🔍 Índices en el Proyecto

### Índices que Existen en Ambos Lugares

| Índice | Tabla | cretable_oracle | Migraciones |
|--------|-------|-----------------|-------------|
| `ix_usuario_rol_rol` | `usuario_rol(id_rol)` | Línea 132 | `usuarios/0002_*.py` |
| `ix_aud_entidad` | `auditoria(entidad, entidad_id)` | Línea 410 | `auditoria/0003_*.py` |
| `ix_aud_fecha` | `auditoria(fecha)` | Línea 411 | `auditoria/0003_*.py` |

### Índices que Solo Existen en cretable_oracle

| Índice | Tabla | cretable_oracle |
|--------|-------|-----------------|
| `ix_aud_actor` | `auditoria(actor_id)` | Línea 409 |
| `ix_usuario_persona` | `usuario(id_persona)` | Línea 111 |

Estos índices **NO** están en las migraciones porque:
- `ix_aud_actor`: Ya existe como FK index en Oracle
- `ix_usuario_persona`: Ya existe como FK index en Oracle

---

## ⚠️ Errores Comunes

### Error: `ORA-01408: esta lista de columnas ya está indexada`

**Causa**: Intentaste crear un índice que ya existe en Oracle.

**Solución**:
- Si usas **Método 1** (solo migraciones): Asegúrate de no haber ejecutado `cretetable_oracle`
- Si usas **Método 2** (cretable_oracle): Comenta los `AddIndex` en las migraciones

### Error: `ORA-00942: tabla o vista no existe`

**Causa**: Intentaste ejecutar migraciones antes de crear las tablas.

**Solución**:
- Si usas **Método 1**: Ejecuta `python manage.py migrate` primero
- Si usas **Método 2**: Ejecuta `cretetable_oracle` primero, luego `migrate --fake-initial`

---

## 📝 Recomendaciones

### Para Desarrollo
- ✅ Usa **Método 1** (solo migraciones)
- ✅ Más rápido y fácil de mantener
- ✅ Django gestiona todo automáticamente

### Para Producción
- ✅ Usa **Método 2** (cretable_oracle)
- ✅ Control total sobre el DDL
- ✅ Scripts SQL explícitos y versionados
- ⚠️ Asegúrate de comentar los índices en las migraciones

---

## 🔄 Sincronización

Si modificas los modelos Django:

1. **Si usas Método 1**:
   - Ejecuta `python manage.py makemigrations`
   - Ejecuta `python manage.py migrate`

2. **Si usas Método 2**:
   - Actualiza `cretetable_oracle` manualmente
   - Ejecuta el script en Oracle
   - Actualiza las migraciones si es necesario

---

## 📚 Referencias

- `cretetable_oracle`: Script SQL para crear el esquema completo
- `MODELO.DDL`: Diagrama de base de datos (referencia)
- `usuarios/models.py`: Modelos de usuarios (incluye índices)
- `auditoria/models.py`: Modelos de auditoría (incluye índices)
- `readme.md`: Guía de instalación general

