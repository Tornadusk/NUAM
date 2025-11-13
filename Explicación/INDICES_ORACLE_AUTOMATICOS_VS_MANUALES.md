# Índices en Oracle: Automáticos vs Manuales

## ✅ Índices que Oracle crea AUTOMÁTICAMENTE

### 1. PRIMARY KEY
- **Oracle SIEMPRE crea un índice único automáticamente para PRIMARY KEY**
- Ejemplo: `id_calificacion` (PK) → Oracle crea índice automáticamente
- **NO necesitas crear estos índices manualmente** ❌

### 2. UNIQUE constraint
- **Oracle SIEMPRE crea un índice único automáticamente para campos UNIQUE**
- Ejemplos:
  - `usuario.username` (UNIQUE) → Oracle crea índice automáticamente
  - `pais.codigo` (UNIQUE) → Oracle crea índice automáticamente
  - `moneda.codigo` (UNIQUE) → Oracle crea índice automáticamente
  - `instrumento.codigo` (UNIQUE) → Oracle crea índice automáticamente
- **NO necesitas crear estos índices manualmente** ❌

### 3. unique_together
- **Oracle SIEMPRE crea un índice único automáticamente para unique_together**
- Ejemplos:
  - `usuario_rol(id_usuario, id_rol)` (unique_together) → Oracle crea índice automáticamente
  - `calificacion(id_corredora, id_instrumento, ejercicio, secuencia_evento)` (unique_together) → Oracle crea índice automáticamente
  - `calificacion_monto_detalle(id_calificacion, id_factor)` (unique_together) → Oracle crea índice automáticamente
- **NO necesitas crear estos índices manualmente** ❌

## ❌ Índices que Oracle NO crea automáticamente

### 1. Foreign Keys
- **Oracle NO crea índices automáticamente para Foreign Keys**
- **PERO son muy importantes para el rendimiento de JOINs**
- Ejemplos:
  - `calificacion.id_corredora` (FK) → **SÍ necesitas crear este índice manualmente** ✅
  - `calificacion.id_instrumento` (FK) → **SÍ necesitas crear este índice manualmente** ✅
  - `calificacion.id_fuente` (FK) → **SÍ necesitas crear este índice manualmente** ✅
  - `usuario_rol.id_rol` (FK) → **SÍ necesitas crear este índice manualmente** ✅
  - `auditoria.actor_id` (FK) → **SÍ necesitas crear este índice manualmente** ✅

### 2. Campos normales (no UNIQUE, no FK)
- **Oracle NO crea índices automáticamente para campos normales**
- Ejemplos:
  - `auditoria.fecha` (campo normal) → **SÍ necesitas crear este índice manualmente si haces consultas por fecha** ✅
  - `auditoria(entidad, entidad_id)` (campos normales) → **SÍ necesitas crear este índice manualmente si haces consultas por entidad** ✅
  - `carga.estado` (campo normal) → **SÍ necesitas crear este índice manualmente si haces consultas por estado** ✅
  - `corredora.nombre` (campo normal) → **SÍ necesitas crear este índice manualmente si haces búsquedas por nombre** ✅

## 🎯 Resumen: ¿Qué índices comentar?

### ❌ COMENTAR (Oracle los crea automáticamente):
1. Índices en campos con `unique=True`
   - `pais.codigo` → COMENTADO ✅
   - `moneda.codigo` → COMENTADO ✅
   - `instrumento.codigo` → COMENTADO ✅
   - `fuente.codigo` → COMENTADO ✅

2. Índices en `unique_together`
   - `usuario_rol(id_usuario, id_rol)` → COMENTADO ✅
   - `calificacion(id_corredora, id_instrumento, ejercicio, secuencia_evento)` → COMENTADO ✅
   - `calificacion_monto_detalle(id_calificacion, id_factor)` → COMENTADO ✅
   - `calificacion_factor_detalle(id_calificacion, id_factor)` → COMENTADO ✅

### ✅ MANTENER (Oracle NO los crea automáticamente):
1. Índices en Foreign Keys (importantes para JOINs)
   - `calificacion.id_corredora` → **DEBERÍA estar activo** ⚠️
   - `calificacion.id_instrumento` → **DEBERÍA estar activo** ⚠️
   - `calificacion.id_fuente` → **DEBERÍA estar activo** ⚠️
   - `calificacion.id_evento` → **DEBERÍA estar activo** ⚠️
   - `usuario_rol.id_rol` → **DEBERÍA estar activo** ⚠️
   - `calificacion_monto_detalle.id_calificacion` → **DEBERÍA estar activo** ⚠️
   - `calificacion_monto_detalle.id_factor` → **DEBERÍA estar activo** ⚠️
   - `calificacion_factor_detalle.id_calificacion` → **DEBERÍA estar activo** ⚠️
   - `calificacion_factor_detalle.id_factor` → **DEBERÍA estar activo** ⚠️
   - `carga.id_corredora` → **DEBERÍA estar activo** ⚠️
   - `carga.id_fuente` → **DEBERÍA estar activo** ⚠️
   - `carga.creado_por` → **DEBERÍA estar activo** ⚠️
   - `carga_detalle.id_carga` → **DEBERÍA estar activo** ⚠️
   - `corredora.id_pais` → **DEBERÍA estar activo** ⚠️
   - `corredora_identificador.id_corredora` → **DEBERÍA estar activo** ⚠️
   - `usuario_corredora.id_usuario` → **DEBERÍA estar activo** ⚠️
   - `usuario_corredora.id_corredora` → **DEBERÍA estar activo** ⚠️
   - `auditoria.actor_id` → **DEBERÍA estar activo** ⚠️

2. Índices en campos normales (importantes para consultas)
   - `auditoria.fecha` → **DEBERÍA estar activo** ⚠️
   - `auditoria(entidad, entidad_id)` → **DEBERÍA estar activo** ⚠️
   - `carga.estado` → **DEBERÍA estar activo** ⚠️
   - `corredora.nombre` → **DEBERÍA estar activo** ⚠️

## 🔍 ¿Rompe la lógica de las funciones?

### ❌ NO rompe la lógica
- Las funciones seguirán funcionando correctamente
- Las consultas se ejecutarán sin errores
- Los datos se guardarán correctamente

### ⚠️ PERO afecta el rendimiento
- **JOINs en Foreign Keys sin índice**: Pueden ser **muy lentos** con muchas filas
- **Consultas con WHERE en campos sin índice**: Pueden ser **muy lentas** con muchas filas
- **ORDER BY en campos sin índice**: Pueden ser **muy lentas** con muchas filas

### 📊 Ejemplo de impacto:
```sql
-- Sin índice en id_corredora (FK):
SELECT * FROM calificacion WHERE id_corredora = 1;
-- Oracle debe hacer FULL TABLE SCAN → Lento con muchas filas ❌

-- Con índice en id_corredora (FK):
SELECT * FROM calificacion WHERE id_corredora = 1;
-- Oracle usa el índice → Rápido ✅
```

## ✅ Solución Recomendada

### Si usas "Método 1" (solo migraciones de Django):
1. **Descomenta los índices en Foreign Keys** en los modelos y migraciones
2. **Descomenta los índices en campos normales** que uses frecuentemente en consultas
3. **Mantén comentados los índices en campos UNIQUE y unique_together**

### Si usas "Método 2" (cretetable_oracle + migraciones):
1. **Los índices ya están creados en cretable_oracle** ✅
2. **Mantén comentados los AddIndex en las migraciones** para evitar ORA-01408
3. **Mantén comentados los índices en los modelos** (solo para documentación)

## 🎯 Estado Actual

Actualmente, **TODOS los índices están comentados**, incluyendo los que Oracle NO crea automáticamente (Foreign Keys y campos normales).

**Esto NO rompe la lógica, pero puede afectar el rendimiento** si:
- Tienes muchas filas en las tablas
- Haces muchas consultas con JOINs
- Haces consultas con WHERE en campos sin índice

## 📝 Recomendación Final

1. **Si tu base de datos es pequeña (< 10,000 filas)**: Los índices comentados están bien ✅
2. **Si tu base de datos es grande (> 10,000 filas)**: Descomenta los índices en Foreign Keys y campos normales importantes ⚠️
3. **Si usas cretable_oracle**: Los índices ya están creados, así que mantenerlos comentados está bien ✅

