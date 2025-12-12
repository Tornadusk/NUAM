# Organización de Templates de Microservicios

## Estructura Actual
```
templates/microservicio/
├── graficos/                 (✅ Directorio creado)
│   └── dashboard.html        (✅ Movido desde raíz)
├── comprobantes/             (✅ Directorio creado)
├── exportacion/              (✅ Directorio creado)
├── pulsar/                   (✅ Directorio creado con dashboard.html)
└── tipos_cambio/             (Existente)
```

## Estructura Recomendada

```
templates/microservicio/
├── graficos/
│   ├── dashboard.html              # Dashboard principal de gráficos
│   ├── _estadisticas_generales.html  # Partial: Estadísticas generales
│   ├── _calificaciones.html        # Partial: Gráficos de calificaciones
│   ├── _cargas.html                # Partial: Gráficos de cargas
│   └── _auditoria.html             # Partial: Gráficos de auditoría
│
├── comprobantes/
│   └── generar.html                # Vista para generar comprobantes
│
├── exportacion/
│   └── _exportar_modal.html        # Modal para exportar datos
│
├── pulsar/
│   └── dashboard.html              # Dashboard holográfico/hacker para visualización de Pulsar
│
└── base_microservicio.html         # Base template para microservicios
```

## Microservicios Identificados

### 1. Microservicio de Gráficos/Métricas
- **Ubicación actual**: `graficos_dashboard.html`
- **Funcionalidad**: Visualización de datos y estadísticas
- **Endpoints**: `/microservicio/graficos/`
- **APIs**: 
  - `/api/estadisticas-generales/`
  - `/api/calificaciones-por-pais/`
  - `/api/cargas-detalle/`
  - etc.

### 2. Microservicio de Comprobantes
- **Ubicación actual**: Solo API (sin template)
- **Funcionalidad**: Generación de PDFs de comprobantes
- **Endpoints**: 
  - `/probar-pdf/` (vista tradicional)
  - `/microservicio/api/generar-comprobante/` (API REST)
- **Servicio externo**: FastAPI en `services/docs-generator/`

### 3. Microservicio de Exportación
- **Ubicación actual**: Integrado en `graficos_dashboard.html`
- **Funcionalidad**: Exportar datos en CSV, Excel, PDF, HTML
- **Clase**: `microservicio/exportador.py`

### 4. Microservicio de Pulsar (Visualización)
- **Ubicación actual**: `templates/microservicio/pulsar/dashboard.html`
- **Funcionalidad**: Visualización en tiempo real de eventos de Apache Pulsar
- **Endpoints**: 
  - `/microservicio/pulsar/` (vista principal)
  - `/microservicio/api/pulsar/status/` (estado de conexión)
  - `/microservicio/api/pulsar/topics/` (información de topics)
  - `/microservicio/api/pulsar/mensajes-recientes/` (mensajes recientes)
  - `/microservicio/api/pulsar/publicar-test/` (publicar mensaje de prueba)
- **Características**:
  - Diseño holográfico/hacker con colores NUAM
  - Visualización en tiempo real de topics y mensajes
  - Estadísticas de conexión y actividad
  - Actualización automática cada 10 segundos

## Ventajas de Separar

1. **Mantenibilidad**: Cada microservicio en su propio template
2. **Reutilización**: Partials reutilizables entre templates
3. **Escalabilidad**: Fácil agregar nuevos microservicios
4. **Claridad**: Código más organizado y fácil de entender
5. **Testing**: Más fácil probar cada microservicio por separado

## Estado Actual

✅ **Completado:**
- Microservicio de Pulsar (visualización) - Implementado con diseño holográfico/hacker
- Estructura de directorios organizada por microservicio
- Integración en menú de navegación

✅ **Completado:**
- `graficos_dashboard.html` movido a `graficos/dashboard.html` ✅
- Referencia actualizada en `views.py` ✅

🔄 **Pendiente:**
1. Separar `graficos/dashboard.html` en partials (graficos/_estadisticas_generales.html, etc.)
2. Crear template para comprobantes (comprobantes/generar.html)
3. Extraer lógica de exportación a partial (exportacion/_exportar_modal.html)
4. Crear base template común para microservicios (base_microservicio.html)
5. ✅ **Mejorar estructura de código Python** - COMPLETADO (ver `microservicio/ESTRUCTURA_IMPLEMENTADA.md`)

## Nota sobre Errores en Pulsar

Si ves "Error" en todos los topics del dashboard de Pulsar, puede ser porque:
- **Pulsar no está corriendo**: Verifica con `docker-compose ps` o `docker ps | grep pulsar`
- **Los topics no existen aún**: Los topics se crean automáticamente cuando se publica el primer mensaje
- **Pulsar Admin API no accesible**: Verifica que `PULSAR_ADMIN_URL` en `settings.py` sea correcto (por defecto: `http://localhost:8080`)

**Solución**: Los topics mostrarán "Error" hasta que:
1. Pulsar esté corriendo
2. Se publique al menos un mensaje en cada topic (esto crea el topic automáticamente)

## Notas de Diseño

### Microservicio de Pulsar
- **Estilo**: Holográfico/hacker con toques futuristas
- **Colores**: 
  - Rojo NUAM (#FF3333) como color principal
  - Verde hacker (#00FF41) para estados activos
  - Cyan (#00FFFF) para información secundaria
  - Fondo oscuro (#0a0a0a) para contraste
- **Efectos**: 
  - Grid overlay holográfico
  - Animaciones de escaneo
  - Efectos de brillo y sombras
  - Tipografía monospace (Courier New)

