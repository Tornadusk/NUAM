# Organización de Templates de Microservicios

## Estructura Actual
```
templates/microservicio/
├── graficos_dashboard.html  (915 líneas - TODO mezclado)
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

## Ventajas de Separar

1. **Mantenibilidad**: Cada microservicio en su propio template
2. **Reutilización**: Partials reutilizables entre templates
3. **Escalabilidad**: Fácil agregar nuevos microservicios
4. **Claridad**: Código más organizado y fácil de entender
5. **Testing**: Más fácil probar cada microservicio por separado

## Próximos Pasos

1. Separar `graficos_dashboard.html` en partials
2. Crear template para comprobantes
3. Extraer lógica de exportación a partial
4. Crear base template común para microservicios

