# Arquitectura de Exportación - Calificaciones

## 📋 Resumen de Sistemas de Exportación

El módulo de calificaciones tiene **MÚLTIPLES sistemas de exportación** que coexisten:

---

## 🔵 Sistema 1: Exportación Rápida desde Tabla (JavaScript - Cliente)

**Ubicación**: `templates/static/js/mantenedor/calificaciones.js`

**Función**: `exportarCalificacionesCSV()` (línea 1011)

**Template**: `templates/calificaciones/partials/_tabla.html` (línea 49)

**Uso**: Botón "Descargar CSV" en la tabla de calificaciones

**Características**:
- ✅ Solo CSV
- ✅ Exporta solo datos visibles en la tabla
- ✅ Generado 100% en el navegador
- ✅ Sin dependencias de servidor
- ✅ **EN USO ACTIVO**

---

## 🟡 Sistema 2: Exportación desde Tab Reportes (JavaScript - Cliente/Obsoleto)

**Ubicación**: `templates/static/js/mantenedor/reportes.js`

**Funciones**:
- `exportarCSV()` (línea 27)
- `exportarExcel()` (línea 43) - ⚠️ Llama a `/api/calificaciones/export_excel/` (NO EXISTE)
- `exportarPDF()` (línea 72) - ⚠️ Llama a `/api/calificaciones/export_pdf/` (NO EXISTE)

**Estado**: ⚠️ **CÓDIGO OBSOLETO - NO SE ESTÁ USANDO**

**Razón**: El template `_reportes.html` usa URLs de Django directamente, no estas funciones JavaScript.

**Problema**: Estas funciones llaman a endpoints que no existen:
- `/api/calificaciones/export_excel/` ❌
- `/api/calificaciones/export_pdf/` ❌

---

## 🟢 Sistema 3: Exportación con Microservicio (Django - Servidor)

**Vista Django**: `calificaciones/views.py` → `exportar_datos_view()` (línea 59)

**URL**: `/calificaciones/exportar/<formato>/` (donde formato = csv, excel, pdf)

**Template**: `templates/calificaciones/partials/_reportes.html`

**Características**:
- ✅ Formatos: PDF, CSV, Excel
- ✅ Datos: Hasta 100 registros desde BD
- ✅ Microservicio: `docs-generator` (FastAPI)
- ✅ **Fallback automático**: Si microservicio cae, genera en Django
- ✅ **EN USO ACTIVO**

---

## 📊 Mapa de Uso Actual

### ✅ Sistemas en Uso:

1. **Sistema 1** (`calificaciones.js` → `exportarCalificacionesCSV`)
   - Usado en: Botón "Descargar CSV" en la tabla
   - Estado: ✅ Funcionando

2. **Sistema 3** (`exportar_datos_view` en Django)
   - Usado en: Pestaña "Reportes" (enlaces directos a URLs Django)
   - Estado: ✅ Funcionando con fallback

### ⚠️ Código Obsoleto (No se usa):

1. **Sistema 2** (`reportes.js`)
   - Funciones: `exportarCSV()`, `exportarExcel()`, `exportarPDF()`
   - Estado: ⚠️ Código presente pero NO se invoca
   - Razón: `_reportes.html` no usa estas funciones, usa URLs Django directamente

---

## 🔍 Flujo Actual de Exportación

### Desde la Tabla (Botón "Descargar CSV"):
```
Usuario hace clic en botón
    ↓
JavaScript: exportarCalificacionesCSV()
    ↓
Genera CSV en navegador
    ↓
Descarga archivo
```

### Desde Tab "Reportes":
```
Usuario hace clic en botón (CSV/Excel/PDF)
    ↓
Navegador: GET /calificaciones/exportar/<formato>/
    ↓
Django: exportar_datos_view()
    ↓
¿Microservicio disponible?
    ├── ✅ SÍ → Llama a microservicio
    └── ❌ NO → Fallback en Django (CSV/Excel/PDF)
```

---

## 🧹 Limpieza Recomendada

**Archivo**: `templates/static/js/mantenedor/reportes.js`

**Estado**: Puede eliminarse o actualizarse

**Opciones**:
1. **Eliminar**: Si no se va a usar nunca
2. **Actualizar**: Para usar el nuevo sistema (`/calificaciones/exportar/<formato>/`)
3. **Mantener**: Como referencia histórica (no recomendado)

---

## 📝 Recomendaciones

1. ✅ **Mantener Sistema 1**: Es útil como respaldo rápido
2. ✅ **Mantener Sistema 3**: Es el sistema principal con microservicio
3. ⚠️ **Revisar Sistema 2**: Decidir si eliminar o actualizar `reportes.js`

---

## 🔗 Archivos Relacionados

### Sistema 1 (Activo):
- `templates/static/js/mantenedor/calificaciones.js` (línea 1011)
- `templates/calificaciones/partials/_tabla.html` (línea 49)
- `templates/static/js/mantenedor/core.js` (helpers: `buildCsvContent`, `downloadBlob`)

### Sistema 2 (Obsoleto):
- `templates/static/js/mantenedor/reportes.js` ⚠️
- `templates/static/js/mantenedor/init.js` (líneas 239-241 exportan funciones no usadas)

### Sistema 3 (Activo):
- `calificaciones/views.py` → `exportar_datos_view()` (línea 59)
- `calificaciones/urls.py` → `path('exportar/<str:formato>/', ...)` (línea 9)
- `templates/calificaciones/partials/_reportes.html`
- `services/docs-generator/src/main.py` → `@app.post("/exportar")`

---

## 📅 Historial

- **2025-12-12**: Documentación de arquitectura completa
- **2025-12-12**: Implementación de fallback automático para todos los formatos
- **2025-12-11**: Corrección de campos en sistema nuevo (microservicio)
- **2025-11-XX**: Implementación del sistema nuevo (microservicio)
- **2025-XX-XX**: Sistema antiguo (JavaScript) implementado originalmente

