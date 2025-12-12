# Sistemas de Exportación de Calificaciones

Este documento describe los dos sistemas de exportación que coexisten en el módulo de Calificaciones.

## 📋 Resumen

El mantenedor de calificaciones tiene **DOS sistemas de exportación** que funcionan de forma complementaria:

1. **Sistema Antiguo (JavaScript)**: Exportación rápida desde la tabla
2. **Sistema Nuevo (Microservicio)**: Reportes completos y profesionales

---

## 🔵 Sistema 1: Exportación Rápida (JavaScript - Cliente)

### Características

- **Ubicación**: Botón "Descargar CSV" en la tabla de calificaciones
- **Archivo**: `templates/static/js/mantenedor/calificaciones.js`
- **Función**: `exportarCalificacionesCSV()`
- **Template**: `templates/calificaciones/partials/_tabla.html` (línea 49)

### Funcionalidad

- ✅ **Formato**: Solo CSV
- ✅ **Datos**: Solo las calificaciones visibles en la tabla actual
- ✅ **Procesamiento**: 100% en el navegador (JavaScript)
- ✅ **Sin dependencias externas**: No requiere microservicio ni servidor adicional

### Ventajas

- ⚡ **Rápido**: No requiere comunicación con servidor
- 🛡️ **Respaldo**: Funciona aunque el microservicio esté caído
- 📊 **Filtrado**: Respeta los filtros aplicados en la tabla
- 🔒 **Privado**: Los datos no salen del navegador del usuario

### Limitaciones

- ❌ Solo formato CSV
- ❌ Solo exporta lo visible en la tabla (no todos los datos de BD)
- ❌ No incluye formateo profesional

### Cuándo usar

- Cuando necesitas exportar rápidamente lo que estás viendo
- Cuando el microservicio está caído
- Para exportaciones pequeñas y rápidas

---

## 🟡 Sistema 2: Endpoints Antiguos (API REST - Redirige al Nuevo)

### Características

- **Ubicación**: Endpoints antiguos de la API REST
- **Vista Django**: `api/views.py` → `CalificacionViewSet.export_pdf()` y `export_excel()`
- **URLs**: `/api/calificaciones/export_pdf/` y `/api/calificaciones/export_excel/`
- **Comportamiento**: Redirigen automáticamente al método nuevo

### Funcionalidad

- ✅ **Formatos**: PDF, CSV, Excel (a través del método nuevo)
- ✅ **Datos**: Hasta 100 registros desde la base de datos
- ✅ **Procesamiento**: Usa el método nuevo (microservicio + fallback)
- ✅ **Información**: **Más completa** que la versión original (7 columnas: ID, Corredora, Instrumento, Estado, Ejercicio, Fecha Pago, Descripción)

### Ventajas

- 🔄 **Compatibilidad**: Mantiene compatibilidad con código que llama a endpoints antiguos
- 📊 **Mejora**: Ahora muestra más información que la versión original
- 🛡️ **Respaldo**: Tiene fallback automático si el microservicio está caído
- 🎯 **Unificación**: Usa el mismo sistema que el método nuevo

### Cuándo usar

- Cuando código existente llama a estos endpoints (mantiene compatibilidad)
- Para obtener la misma funcionalidad del método nuevo desde endpoints antiguos

---

## 🟢 Sistema 3: Reportes Completos (Microservicio - Servidor)

### Características

- **Ubicación**: Pestaña "Reportes" del mantenedor
- **Vista Django**: `calificaciones/views.py` → `exportar_datos_view()`
- **Microservicio**: `services/docs-generator` (FastAPI)
- **Template**: `templates/calificaciones/partials/_reportes.html`
- **URL**: `/calificaciones/exportar/<formato>/`

### Funcionalidad

- ✅ **Formatos**: PDF, CSV, Excel (.xlsx)
- ✅ **Datos**: Hasta 100 registros desde la base de datos
- ✅ **Procesamiento**: En el servidor (microservicio FastAPI)
- ✅ **Formateo**: Reportes profesionales con encabezados, estilos y metadatos

### Ventajas

- 📄 **Múltiples formatos**: PDF, CSV, Excel
- 📊 **Datos completos**: Desde la base de datos, no solo lo visible
- 🎨 **Formateo profesional**: Encabezados, estilos, metadatos
- 📈 **Reportes formales**: Ideales para presentaciones y análisis

### Limitaciones

- ❌ PDF requiere microservicio corriendo (`docs-generator`)
- ❌ Más lento (comunicación con servidor)
- ❌ Límite de 100 registros por exportación

### 🛡️ Fallback Automático

**¡NUEVO!** Si el microservicio está caído:
- ✅ **CSV**: Se genera automáticamente en Django (sin microservicio)
- ✅ **Excel**: Se genera automáticamente en Django (si `openpyxl` está instalado)
- ✅ **PDF**: Se genera automáticamente en Django (si `reportlab` está instalado)

**Ventaja**: El sistema es completamente resiliente y mantiene TODOS los formatos funcionando aunque el microservicio falle.

### Cuándo usar

- Para reportes formales y completos
- Cuando necesitas PDF o Excel
- Para análisis con todos los datos de la BD
- Para presentaciones profesionales

---

## 🔄 Comparación Rápida

| Característica | Sistema Antiguo (JS) | Sistema Antiguo (API) | Sistema Nuevo (Microservicio) |
|----------------|---------------------|----------------------|------------------------------|
| **Formatos** | Solo CSV | PDF, CSV, Excel (redirige al nuevo) | PDF, CSV, Excel |
| **Datos** | Solo visibles en tabla | Hasta 100 desde BD (igual que nuevo) | Hasta 100 desde BD |
| **Velocidad** | ⚡ Muy rápido | 🐢 Más lento (usa método nuevo) | 🐢 Más lento |
| **Dependencias** | Ninguna | Microservicio + fallback Django | Microservicio + fallback Django |
| **Formateo** | Básico | Profesional (igual que nuevo) | Profesional |
| **Respaldo** | ✅ Funciona siempre | ✅ Fallback automático | ✅ Fallback automático |
| **Información** | Básica (tabla) | Completa (7 columnas) | Completa (7 columnas) |

**Nota**: El sistema antiguo de API (`/api/calificaciones/export_pdf/`) ahora redirige al método nuevo, por lo que ofrece la misma funcionalidad y **más información** que la versión original.

---

## 🛡️ Respaldo y Resiliencia

**¿Por qué mantener ambos sistemas?**

1. **Respaldo**: Si el microservicio se cae, el sistema nuevo tiene fallback automático en Django
2. **Flexibilidad**: Los usuarios pueden elegir según su necesidad
3. **Rendimiento**: Para exportaciones rápidas, el sistema antiguo (JavaScript) es más eficiente
4. **Compatibilidad**: Los endpoints antiguos (`/api/calificaciones/export_pdf/`) redirigen al nuevo, manteniendo compatibilidad
5. **Mejora**: Al usar el método antiguo, ahora obtienes más información que antes (mismo resultado que el método nuevo)

**Escenario de falla del microservicio:**

```
Microservicio docs-generator caído
    ↓
Sistema Nuevo (/calificaciones/exportar/<formato>/):
    - CSV: ✅ Fallback automático (generado en Django con openpyxl)
    - Excel: ✅ Fallback automático (generado en Django con openpyxl)
    - PDF: ✅ Fallback automático (generado en Django con reportlab)
Sistema Antiguo (/api/calificaciones/export_pdf/):
    - Redirige automáticamente al método nuevo
    - Obtiene el mismo resultado (microservicio + fallback)
    - Muestra MÁS información que la versión original del método antiguo
Sistema Antiguo (JavaScript - CSV rápido):
    - ✅ Sigue funcionando (exportación CSV rápida desde tabla)
```

**Resultado**: El sistema es completamente resiliente y mantiene funcionalidad incluso con el microservicio caído. Además, los endpoints antiguos ahora ofrecen mejor funcionalidad al redirigir al método nuevo.

---

## 📝 Archivos Relacionados

### Sistema Antiguo (JavaScript - Activo)
- `templates/static/js/mantenedor/calificaciones.js` (línea 1011) → `exportarCalificacionesCSV()`
- `templates/calificaciones/partials/_tabla.html` (línea 49) → Botón "Descargar CSV"
- `templates/static/js/mantenedor/core.js` → Helpers: `buildCsvContent()`, `downloadBlob()`

### Sistema Antiguo (API REST - Redirige al Nuevo)
- `api/views.py` → `CalificacionViewSet.export_pdf()` y `export_excel()` (líneas 911-920)
- **Endpoints**: `/api/calificaciones/export_pdf/` y `/api/calificaciones/export_excel/`
- **Comportamiento**: Estos métodos ahora **redirigen automáticamente** al método nuevo (`/calificaciones/exportar/<formato>/`)
- **Ventaja**: Mantiene compatibilidad con código antiguo que pueda llamar a estos endpoints
- **Resultado**: Al usar el método antiguo, obtienes el mismo resultado que el método nuevo (microservicio + fallback), con **más información** que la versión original del método antiguo

### Sistema Antiguo (JavaScript - ⚠️ Obsoleto/No usado)
- `templates/static/js/mantenedor/reportes.js` → Funciones que NO se usan:
  - `exportarCSV()` - No se llama desde templates
  - `exportarExcel()` - Llama a endpoint inexistente (`/api/calificaciones/export_excel/`)
  - `exportarPDF()` - Llama a endpoint inexistente (`/api/calificaciones/export_pdf/`)
- **Nota**: El template `_reportes.html` usa URLs Django directamente, no estas funciones

### Sistema Antiguo (API REST - Redirige al Nuevo)
- `api/views.py` → `CalificacionViewSet.export_pdf()` y `export_excel()` (líneas 911-920)
- **Endpoints**: `/api/calificaciones/export_pdf/` y `/api/calificaciones/export_excel/`
- **Comportamiento**: Redirigen automáticamente a `calificaciones.views.exportar_datos_view()`
- **Resultado**: Mismo comportamiento que el método nuevo, con más información que la versión original

### Sistema Nuevo (Microservicio - Activo)
- `calificaciones/views.py` → `exportar_datos_view()` (línea 59)
- `calificaciones/urls.py` → `path('exportar/<str:formato>/', ...)` (línea 9)
- `templates/calificaciones/partials/_reportes.html` → Enlaces a URLs Django
- `services/docs-generator/src/main.py` → `@app.post("/exportar")`
- `services/docs-generator/src/templates/reporte_tabla.html`

---

## 🚀 Uso Recomendado

### Para usuarios finales:

- **Exportación rápida**: Usar botón "Descargar CSV" en la tabla
- **Reportes formales**: Usar pestaña "Reportes" → Elegir formato (PDF/CSV/Excel)

### Para desarrolladores:

- **Mantener ambos sistemas**: No eliminar el sistema antiguo
- **Mejoras futuras**: Agregar más formatos al microservicio
- **Monitoreo**: Verificar que el microservicio esté disponible

---

## 📅 Historial

- **2025-12-12**: 
  - Métodos antiguos (`/api/calificaciones/export_pdf/`, `/export_excel/`) ahora redirigen al método nuevo
  - Los endpoints antiguos ahora muestran más información al usar el sistema nuevo con microservicio + fallback
  - Documentación actualizada sobre el comportamiento de redirección
- **2025-12-12**: Documentación de coexistencia de sistemas
- **2025-12-11**: Corrección de campos en sistema nuevo (microservicio)
- **2025-11-XX**: Implementación del sistema nuevo (microservicio)
- **2025-XX-XX**: Sistema antiguo (JavaScript) implementado originalmente

---

## ⚠️ Notas Importantes

1. **No eliminar el sistema antiguo**: Funciona como respaldo crítico
2. **Monitorear microservicio**: Verificar que `docs-generator` esté corriendo
3. **Documentar cambios**: Actualizar este README si se hacen modificaciones
4. **Testing**: Probar ambos sistemas después de cambios importantes

---

## 🔗 Referencias

- [TREE.txt](./templates/calificaciones/partials/TREE.txt) - Estructura de templates
- [views.py](./views.py) - Vista de exportación con microservicio
- [docs-generator README](../../services/docs-generator/README.md) - Documentación del microservicio

