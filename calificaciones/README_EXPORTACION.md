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

## 🟢 Sistema 2: Reportes Completos (Microservicio - Servidor)

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
- ⚠️ **PDF**: Muestra mensaje amigable sugiriendo usar CSV/Excel o el sistema antiguo

**Ventaja**: El sistema es resiliente y sigue funcionando aunque el microservicio falle.

### Cuándo usar

- Para reportes formales y completos
- Cuando necesitas PDF o Excel
- Para análisis con todos los datos de la BD
- Para presentaciones profesionales

---

## 🔄 Comparación Rápida

| Característica | Sistema Antiguo (JS) | Sistema Nuevo (Microservicio) |
|----------------|---------------------|------------------------------|
| **Formatos** | Solo CSV | PDF, CSV, Excel |
| **Datos** | Solo visibles en tabla | Hasta 100 desde BD |
| **Velocidad** | ⚡ Muy rápido | 🐢 Más lento |
| **Dependencias** | Ninguna | Requiere microservicio |
| **Formateo** | Básico | Profesional |
| **Respaldo** | ✅ Funciona siempre | ❌ Requiere microservicio |

---

## 🛡️ Respaldo y Resiliencia

**¿Por qué mantener ambos sistemas?**

1. **Respaldo**: Si el microservicio se cae, el sistema antiguo sigue funcionando
2. **Flexibilidad**: Los usuarios pueden elegir según su necesidad
3. **Rendimiento**: Para exportaciones rápidas, el sistema antiguo es más eficiente
4. **Compatibilidad**: No rompe funcionalidad existente

**Escenario de falla del microservicio:**

```
Microservicio docs-generator caído
    ↓
Sistema Nuevo:
    - CSV: ✅ Fallback automático (generado en Django)
    - Excel: ✅ Fallback automático (generado en Django)
    - PDF: ⚠️ Mensaje amigable con opciones alternativas
Sistema Antiguo: ✅ Sigue funcionando (exportación CSV rápida)
```

**Resultado**: El sistema es resiliente y mantiene funcionalidad incluso con el microservicio caído.

---

## 📝 Archivos Relacionados

### Sistema Antiguo
- `templates/static/js/mantenedor/calificaciones.js` (línea 1011)
- `templates/calificaciones/partials/_tabla.html` (línea 49)

### Sistema Nuevo
- `calificaciones/views.py` → `exportar_datos_view()` (línea 42)
- `calificaciones/urls.py` → `path('exportar/<str:formato>/', ...)` (línea 9)
- `templates/calificaciones/partials/_reportes.html`
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

