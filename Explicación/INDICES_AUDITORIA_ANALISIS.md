# Análisis de Índices para Auditoría

## Índices Actuales en `cretetable_oracle`

En `cretetable_oracle` (línea 408) solo existe:
- `ix_aud_actor` en `auditoria(actor_id)`

## Índices que NO Existen en `cretetable_oracle`

1. **`(entidad, entidad_id)`** - Índice compuesto
2. **`fecha`** - Índice simple

## ¿Son Importantes para Evitar Errores?

**NO**, estos índices **NO son necesarios para evitar errores**. El error que solucionamos era del **JSONField** (Oracle devuelve dict en lugar de string), no de índices.

## ¿Son Importantes para el Rendimiento?

**SÍ**, estos índices **SÍ son importantes para el rendimiento** porque:

### 1. Índice en `fecha` - **MUY IMPORTANTE**

**Uso en la aplicación:**
- `Auditoria.Meta.ordering = ['-fecha', '-id_auditoria']` (línea 38 de `auditoria/models.py`)
- `AuditoriaAdmin.ordering = ('-fecha',)` (línea 12 de `auditoria/admin.py`)
- `AuditoriaAdmin.date_hierarchy = 'fecha'` (línea 13 de `auditoria/admin.py`)
- Consultas frecuentes ordenadas por fecha descendente

**Sin índice:**
- Oracle debe hacer un **FULL TABLE SCAN** y ordenar todos los registros cada vez
- Con muchos registros de auditoría, esto será **MUY LENTO**

**Con índice:**
- Oracle puede usar el índice para ordenar directamente
- Consultas mucho más rápidas

### 2. Índice en `(entidad, entidad_id)` - **IMPORTANTE**

**Uso en la aplicación:**
- `AuditoriaViewSet.get_queryset()` filtra por `entidad` (línea 2065-2067 de `api/views.py`)
- `AuditoriaAdmin.list_filter = ('entidad', 'accion', 'fecha')` (línea 9 de `auditoria/admin.py`)
- Consultas como: "Buscar todos los eventos de auditoría para una calificación específica"

**Sin índice:**
- Oracle debe hacer un **FULL TABLE SCAN** y filtrar por `entidad`
- Con muchos registros, puede ser lento

**Con índice:**
- Oracle puede usar el índice para filtrar rápidamente
- Especialmente útil para buscar eventos de una entidad específica

## Recomendación

**SÍ, deberías agregar estos índices a `cretetable_oracle`** para mejorar el rendimiento:

```sql
-- Agregar al final de cretable_oracle (después de línea 408)
CREATE INDEX ix_aud_entidad ON auditoria(entidad, entidad_id);
CREATE INDEX ix_aud_fecha ON auditoria(fecha);
```

## Impacto

- **Sin índices**: Consultas lentas cuando hay muchos registros de auditoría (miles o millones)
- **Con índices**: Consultas rápidas incluso con millones de registros

## ¿Cuándo se Nota la Diferencia?

- **Pocos registros (< 1000)**: Diferencia mínima, pero buena práctica
- **Muchos registros (> 10,000)**: Diferencia significativa
- **Millones de registros**: Diferencia crítica, sin índices puede ser inutilizable

## Conclusión

Los índices **NO son necesarios para evitar errores**, pero **SÍ son importantes para el rendimiento**, especialmente:
1. **`fecha`**: Crítico porque se usa en `ordering` y `date_hierarchy`
2. **`(entidad, entidad_id)`**: Importante para filtros por entidad

**Recomendación**: Agregar estos índices a `cretetable_oracle` y ejecutarlos manualmente en Oracle.

