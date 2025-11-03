================================================================================
MANTENEDOR DE CALIFICACIONES - ESTRUCTURA DE PARTIALS
================================================================================

Resumen visual de la estructura modular del Mantenedor.

================================================================================
ESTRUCTURA DE ARCHIVOS
================================================================================

templates/calificaciones/
├── mantenedor.html (58 líneas - archivo principal)
└── partials/
    ├── _header.html (13 líneas)
    ├── _tabs_nav.html (30 líneas)
    ├── _filtros.html (40 líneas)
    ├── _tabla.html (80 líneas)
    ├── _kpis_auditoria.html (50 líneas)
    ├── _cargas_masivas.html (60 líneas) ⚠️ Requiere {% load static %}
    ├── _usuarios.html (40 líneas)
    ├── _auditoria.html (35 líneas)
    ├── _reportes.html (45 líneas)
    ├── _modals_calificaciones.html (250 líneas)
    ├── _modals_usuarios.html (270 líneas)
    ├── TREE.txt (documentación completa)
    └── README.txt (este archivo)

Total: 11 partials + 1 archivo principal = 58 líneas (vs 937 originales)

================================================================================
JERARQUÍA DE INCLUSIÓN
================================================================================

mantenedor.html
│
├── _header.html (título y badge)
│
├── _tabs_nav.html (navegación de tabs)
│
├── Tab Content (mainTabsContent)
│   │
│   ├── Mantenedor Tab (show active)
│   │   ├── _filtros.html
│   │   ├── _tabla.html
│   │   └── _kpis_auditoria.html
│   │
│   ├── Cargas Masivas Tab
│   │   └── _cargas_masivas.html ⚠️ {% load static %}
│   │
│   ├── Usuarios Tab (solo admin)
│   │   └── _usuarios.html
│   │
│   ├── Auditoría Tab (solo admin)
│   │   └── _auditoria.html
│   │
│   └── Reportes Tab
│       └── _reportes.html
│
├── _modals_calificaciones.html (modales de CRUD calificaciones)
│
└── _modals_usuarios.html (modales de CRUD usuarios, solo admin)

================================================================================
ETIQUETAS DJANGO Y {% load %}
================================================================================

✅ CORRECTO - Ya tiene {% load static %}:
   - _cargas_masivas.html (usa {% static %} en línea 18)
   - mantenedor.html (usa {% static %} en línea 56)

✅ NO REQUIERE {% load %}:
   - _tabs_nav.html (usa {% if is_admin %})
   - _usuarios.html (usa {% if is_admin %})
   - _auditoria.html (usa {% if is_admin %})
   - _modals_usuarios.html (usa {% if is_admin %})

   Razón: {% if %} es parte del lenguaje básico de Django y no requiere {% load %}

================================================================================
DEPENDENCIAS JAVASCRIPT
================================================================================

Partial                  → Módulo JavaScript
─────────────────────────────────────────────────────────────────
_filtros.html            → calificaciones.js
_tabla.html              → calificaciones.js
_kpis_auditoria.html     → auditoria.js
_cargas_masivas.html     → cargas.js
_usuarios.html           → usuarios.js
_auditoria.html          → auditoria.js
_reportes.html           → reportes.js
_modals_calificaciones.html → calificaciones.js
_modals_usuarios.html    → usuarios.js

Todos los módulos se cargan mediante:
  templates/static/js/mantenedor/init.js

================================================================================
VARIABLES DE CONTEXTO
================================================================================

Desde calificaciones/views.py:
  - is_admin: Boolean (controla visibilidad de tabs y modales de admin)
  - user: Usuario autenticado (Django User object)

Todos los partials comparten el mismo contexto del template padre.

================================================================================
REGLAS IMPORTANTES
================================================================================

1. Si un partial usa {% static %}:
   → DEBE tener {% load static %} al inicio del archivo

2. Si un partial usa {% url %}:
   → DEBE tener {% load url %} o similar según el caso

3. {% if %}, {% for %}, {% include %} NO requieren {% load %}

4. Rutas de partials:
   → Siempre usar: 'calificaciones/partials/_nombre.html'
   → El prefijo 'calificaciones/partials/' es obligatorio

================================================================================
VERIFICACIÓN COMPLETA
================================================================================

✅ Todos los partials revisados
✅ Solo _cargas_masivas.html usa {% static %} y ya tiene {% load static %}
✅ El archivo principal mantenedor.html tiene {% load static %}
✅ No hay otros usos de etiquetas que requieran {% load %}
✅ Estructura documentada en TREE.txt

================================================================================

