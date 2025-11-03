================================================================================
ESTRUCTURA MODULAR DEL MANTENEDOR - NUAM
================================================================================

PROPÓSITO:
-----------
Este documento explica la estructura modular del JavaScript del Mantenedor de 
Calificaciones Tributarias, migrado de un archivo monolítico de ~1,370 líneas 
a una arquitectura modular con ES6 Modules.

================================================================================
ARCHIVOS Y RESPONSABILIDADES
================================================================================

1. CORE.JS (utilidades compartidas)
   - getCookie, getCsrfToken, fetchWithCSRF
   - populateSelect, getEstadoBadgeClass
   - formatDate, formatNumber, isValidEmail
   - downloadBlob, showToast
   
2. CALIFICACIONES.JS (CRUD calificaciones)
   - cargarCatalogos, cargarCalificaciones
   - renderCalificaciones, renderPaginacion
   - abrirModalIngresar, abrirModalModificar
   - nextWizardStep, prevWizardStep, resetWizard
   - guardarCalificacion, eliminarCalificacion, copiarCalificacion
   - buscarCalificaciones, limpiarFiltros
   - generarInputsFactores, validarSumaFactores
   - goToPage, selectCalificacion (globales via init.js)
   
3. CARGAS.JS (carga masiva DJ1948)
   - abrirModalCargaFactor, abrirModalCargaMonto
   - cargarFactor, cargarMonto
   - calcularFactores
   - TODO: Implementar con endpoints del backend
   
4. USUARIOS.JS (CRUD usuarios)
   - cargarRoles, cargarUsuarios
   - abrirModalCrearUsuario, guardarUsuario
   - editarUsuario, actualizarUsuario
   - eliminarUsuario
   - setupPasswordToggles, validarPasswordCoincidencia
   
5. AUDITORIA.JS (eventos recientes y logs)
   - cargarAuditoriaReciente (sidebar)
   - cargarAuditoriaCompleta (tab completo)
   - renderAuditoria
   
6. REPORTES.JS (exportación CSV/Excel/PDF)
   - exportarCSV (implementado)
   - exportarExcel (placeholder)
   - exportarPDF (placeholder)
   
7. INIT.JS (punto de entrada)
   - Maneja DOMContentLoaded
   - Orquesta inicialización de módulos
   - Configura listeners de tabs
   - Hace funciones disponibles globalmente
   
8. ORIGINAL_MANTENEDOR_BACKUP.TXT
   - Archivo original monolítico (~1,370 líneas)
   - Mantenido como referencia histórica
   - Útil para debugging si algo se pierde en la migración

================================================================================
DIFERENCIAS CON EL ARCHIVO ORIGINAL
================================================================================

ORIGINAL (mantenedor.js):
  - Todo en un solo archivo de 1,373 líneas
  - Funciones mezcladas con dependencias circulares
  - Difícil de mantener y depurar
  - Conflictos frecuentes en merge de Git

ACTUAL (modular):
  - 7 archivos separados por responsabilidad
  - ~200-400 líneas por módulo (más manejable)
  - Imports explícitos con ES6
  - Más fácil de testear y mantener
  - Menos conflictos en merge

================================================================================
FLUJO DE DATOS
================================================================================

1. Usuario carga /calificaciones/mantenedor/
2. Django renderiza mantenedor.html
3. mantenedor.html carga init.js (type="module")
4. init.js importa todos los módulos
5. init.js configura listeners y arranca
6. Cada módulo maneja su propia funcionalidad

================================================================================
DEPENDENCIAS ENTRE MÓDULOS
================================================================================

core.js
  ↓ (importado por todos)
calificaciones.js
  ↓ (usa setCalificacionesData)
reportes.js

core.js
  ↓ (importado por todos)
usuarios.js
  → depende de core.js para helpers UI

core.js
  ↓ (importado por todos)
auditoria.js
  → independiente

core.js
  ↓ (importado por todos)
cargas.js
  → independiente

init.js
  → importa todos
  → orquesta inicialización
  → expone funciones globales

================================================================================
CÓMO DEBUGEAR SI ALGO FALLA
================================================================================

1. Revisa la consola del navegador para errores de sintaxis
2. Verifica que todos los módulos se carguen correctamente
3. Compara con original_mantenedor_backup.txt
4. Busca la función específica en el módulo correspondiente
5. Verifica imports/exports entre módulos

================================================================================
VENTAJAS DE LA ARQUITECTURA MODULAR
================================================================================

✅ Mantenibilidad: Cada módulo tiene un propósito claro
✅ Testabilidad: Puedes testear cada módulo por separado
✅ Escalabilidad: Agregar funcionalidades es más fácil
✅ Menos conflictos: Cambios en un módulo no afectan otros
✅ Código más limpio: Responsabilidades separadas
✅ Debugging más simple: Sabes dónde buscar cada función

================================================================================
MIGRACIÓN GRADUAL
================================================================================

La migración se hizo en dos fases:

FASE 1 (Completada):
- Estructura de archivos creada
- Módulos funcionales separados
- init.js como punto de entrada
- Archivo original guardado como backup
- mantenedor.js eliminado de ambas ubicaciones
- mantenedor.html actualizado a ES6 modules
- collectstatic regenerado

FASE 2 (Futuro):
- Optimizar imports
- Agregar tests unitarios
- Documentación JSDoc completa

================================================================================
NOTAS IMPORTANTES
================================================================================

✅ La migración modular está COMPLETADA y ACTIVA
✅ mantenedor.html ahora usa `<script type="module" src="mantenedor/init.js">`
✅ El archivo mantenedor.js fue eliminado correctamente
✅ staticfiles/ se regeneró con collectstatic

🔧 Siguientes pasos:
   - Probar todas las funcionalidades del mantenedor
   - Verificar que no se perdieron funciones
   - Compara con original_mantenedor_backup.txt si algo falla

================================================================================
AUTOR Y FECHA
================================================================================
Migración realizada: 02/11/2025
Refactoring: Divide y vencerás - arquitectura modular ES6
Estructura inspirada en: Angular/Frontend modular best practices

================================================================================

