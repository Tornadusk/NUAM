# Lógica de Almacenamiento de Calificaciones

## 📋 Estructura de Datos

### Tabla Principal: `calificacion`
- **Llave única**: `(id_corredora, id_instrumento, ejercicio, secuencia_evento)`
- **Campo clave**: `ingreso_por_montos` (Boolean)
  - `True`: La calificación se ingresó con montos (Carga x Monto)
  - `False`: La calificación se ingresó con factores (Carga x Factor)

### Tablas de Detalle:
1. **`calificacion_monto_detalle`**: Almacena montos M08-M37
2. **`calificacion_factor_detalle`**: Almacena factores F08-F37

## 🔄 Comportamiento Actual

### Carga x Factor:
1. Busca/crea calificación por llave única
2. Marca `ingreso_por_montos = False`
3. **Elimina** montos antiguos (si existían)
4. **Elimina** factores antiguos
5. **Crea** nuevos factores desde el archivo

### Carga x Monto:
1. Busca/crea calificación por llave única
2. Marca `ingreso_por_montos = True`
3. **Elimina** montos antiguos (si existían)
4. **Elimina** factores antiguos
5. **Crea** nuevos montos desde el archivo
6. **Calcula** factores desde montos
7. **Crea** factores calculados

## ✅ ¿Está bien que ambos se guarden en la misma tabla?

**SÍ, está bien** por las siguientes razones:

### 1. **Modelo de Datos Correcto**
- Una calificación es una entidad única identificada por `(corredora, instrumento, ejercicio, secuencia_evento)`
- No importa cómo se ingresó (factores o montos), es la misma calificación
- El campo `ingreso_por_montos` documenta el origen

### 2. **Consistencia de Datos**
- Ambas cargas actualizan la misma calificación
- Si una calificación ya existe, se actualiza (no se duplica)
- Los detalles (montos/factores) se sobrescriben con los nuevos datos

### 3. **Trazabilidad**
- El campo `ingreso_por_montos` permite saber cómo se ingresó originalmente
- Los registros en `carga` y `carga_detalle` documentan cada carga masiva
- El campo `observaciones` indica el tipo de carga

## ⚠️ Consideraciones Importantes

### 1. **Sobrescritura de Datos**
- Si subes una **Carga x Factor** sobre una calificación que tenía montos:
  - Los montos se eliminan (porque ahora viene de factores)
  - Los factores se actualizan
  
- Si subes una **Carga x Monto** sobre una calificación que tenía factores:
  - Los factores se eliminan (porque ahora se calculan desde montos)
  - Los montos se actualizan
  - Los factores se recalculan

### 2. **Preservación de Información**
- Los montos originales se pierden si cambias a Carga x Factor
- Los factores originales se pierden si cambias a Carga x Monto
- **Recomendación**: Usar el mismo tipo de carga para actualizar una calificación

### 3. **Validación Recomendada**
- Si una calificación ya existe con `ingreso_por_montos = True`:
  - Mostrar advertencia si intentas cargar factores
  - Preguntar si deseas sobrescribir los montos
  
- Si una calificación ya existe con `ingreso_por_montos = False`:
  - Mostrar advertencia si intentas cargar montos
  - Preguntar si deseas sobrescribir los factores

## 🎯 Mejoras Sugeridas

### 1. **Validación de Tipo de Carga**
```python
# Si la calificación ya existe y tiene un tipo diferente de ingreso
if not created:
    if calificacion.ingreso_por_montos and not ingreso_por_montos:
        # Advertencia: calificación tiene montos, pero estás cargando factores
        logger.warning(f"Calificación {calificacion.id_calificacion} tiene montos, sobrescribiendo con factores")
    elif not calificacion.ingreso_por_montos and ingreso_por_montos:
        # Advertencia: calificación tiene factores, pero estás cargando montos
        logger.warning(f"Calificación {calificacion.id_calificacion} tiene factores, sobrescribiendo con montos")
```

### 2. **Historial de Cambios**
- Guardar versión anterior en auditoría antes de sobrescribir
- Permitir revertir cambios si es necesario

### 3. **Modo de Actualización**
- **Modo "Reemplazar"**: Elimina datos antiguos (comportamiento actual)
- **Modo "Merging"**: Combina datos nuevos con existentes (futuro)

## 📊 Ejemplo de Flujo

### Escenario 1: Primera carga
1. Usuario sube **Carga x Monto** para calificación nueva
2. Sistema crea calificación con `ingreso_por_montos = True`
3. Sistema guarda montos en `calificacion_monto_detalle`
4. Sistema calcula y guarda factores en `calificacion_factor_detalle`

### Escenario 2: Actualización con mismo tipo
1. Usuario sube **Carga x Monto** para calificación existente
2. Sistema encuentra calificación existente (`ingreso_por_montos = True`)
3. Sistema elimina montos y factores antiguos
4. Sistema guarda nuevos montos y calcula nuevos factores

### Escenario 3: Cambio de tipo de carga
1. Usuario sube **Carga x Factor** para calificación que tenía montos
2. Sistema encuentra calificación existente (`ingreso_por_montos = True`)
3. Sistema elimina montos antiguos (ya no se necesitan)
4. Sistema elimina factores antiguos (se reemplazan)
5. Sistema guarda nuevos factores
6. Sistema actualiza `ingreso_por_montos = False`

## ✅ Conclusión

**Sí, está bien que ambos tipos de carga se guarden en la misma tabla `calificacion`** porque:

1. ✅ Es la misma entidad de negocio (una calificación)
2. ✅ El modelo de datos lo permite y está diseñado para esto
3. ✅ El campo `ingreso_por_montos` documenta el origen
4. ✅ Los detalles se almacenan en tablas separadas (montos vs factores)
5. ✅ La trazabilidad se mantiene en `carga` y `carga_detalle`

**Mejora implementada**: Ahora Carga x Factor también elimina montos antiguos para mantener consistencia.

