# Microservicios NUAM

Este módulo contiene los microservicios del sistema NUAM.

## Estructura del Código

El código está organizado en módulos separados por funcionalidad:

```
microservicio/
├── views/              # Vistas organizadas por funcionalidad
│   ├── graficos.py     # Gráficos y métricas
│   ├── tipos_cambio.py # Tipos de cambio
│   ├── comprobantes.py # Generación de comprobantes
│   ├── pulsar.py       # Visualización de Pulsar
│   └── helpers.py      # Funciones auxiliares
├── pulsar/             # Cliente y funciones de Pulsar
│   └── client.py
├── utils/              # Utilidades
│   └── exportador.py
└── docs/               # Documentación
```

Ver `ESTRUCTURA_IMPLEMENTADA.md` para más detalles.

## Microservicios Implementados

### 1. Microservicio de Gráficos/Métricas ✅
**Ubicación:** `microservicio/views/graficos.py`

Este microservicio expone datos agregados de la base de datos para visualización mediante gráficos.

#### Endpoints disponibles:
- `GET /microservicio/api/estadisticas-generales/` - Estadísticas generales del sistema
- `GET /microservicio/api/calificaciones-por-pais/` - Calificaciones agrupadas por país
- `GET /microservicio/api/calificaciones-por-moneda/` - Calificaciones agrupadas por moneda
- `GET /microservicio/api/actividad-reciente/` - Actividad de los últimos 30 días
- `GET /microservicio/api/cargas-detalle/` - Estadísticas detalladas de cargas
- `GET /microservicio/api/cargas-por-corredora/` - Cargas agrupadas por corredora
- `GET /microservicio/api/auditoria-resumen/` - Resumen de auditoría
- `GET /microservicio/api/kpis-operativos/` - KPIs operativos del sistema
- `GET /microservicio/api/exportar/<tipo>/<formato>/` - Exportar datos (CSV, Excel, PDF, HTML)

#### Vista de gráficos:
- `GET /microservicio/graficos/` - Dashboard de gráficos interactivos

#### Características:
- ✅ Respeta Row-Level Security (RLS) según el rol del usuario
- ✅ Operadores solo ven datos de su corredora asignada
- ✅ Administradores ven todos los datos
- ✅ Usa Chart.js para visualización interactiva
- ✅ Exportación en múltiples formatos (CSV, Excel, PDF, HTML)

### 2. Microservicio de Tipos de Cambio (Monedas) ✅
**Ubicación:** `microservicio/views/tipos_cambio.py` y `microservicio/models.py`

Este microservicio gestiona múltiples fuentes de tipos de cambio con sistema de respaldo automático. Permite consultar y visualizar tipos de cambio para diferentes países y pares de monedas.

#### Modelos:
- **TipoCambioFuente**: Tabla para gestionar múltiples fuentes de tipos de cambio
  - Soporta múltiples APIs (ExchangeRate API, Banco Central, Fixer.io, etc.)
  - Sistema de prioridades y fallback automático (`orden_prioridad`)
  - Tracking de éxito/fallo de consultas (`ultima_consulta_exitosa`, `ultima_consulta_fallida`, `intentos_fallidos`)
  - Campos: `nombre`, `codigo`, `url_api`, `api_key`, `activa`, `orden_prioridad`
  
- **TipoCambio**: Almacena los tipos de cambio obtenidos
  - Relación con fuente (`id_fuente`)
  - Soporte para múltiples pares de monedas (`moneda_origen`, `moneda_destino`)
  - Historial temporal (`fecha`, `vigente_desde`, `vigente_hasta`)
  - Tasa de cambio con precisión decimal (`tasa`)

#### Países y Monedas Soportados:
- **CHL (Chile)**: CLP (Peso Chileno)
- **PER (Perú)**: PEN (Sol Peruano)
- **COL (Colombia)**: COP (Peso Colombiano)
- **USA (Estados Unidos)**: USD (Dólar Estadounidense)

#### Endpoints disponibles:
- `GET /microservicio/tipos-cambio/` - Dashboard interactivo de tipos de cambio
- `GET /microservicio/api/tipos-cambio-por-pais/` - Todos los tipos de cambio (últimos 30 días)
- `GET /microservicio/api/tipos-cambio-por-pais/<codigo>/` - Tipos de cambio filtrados por país (CHL, PER, COL, USA)
  - Devuelve: tipos recientes, estadísticas (promedio, máximo, mínimo), histórico mensual (12 meses)
- `GET /microservicio/api/tipos-cambio-actuales/` - Tipos de cambio más recientes por país
  - Devuelve el tipo de cambio más actual para cada par USD/moneda_local por país
- `GET /microservicio/api/tipos-cambio-resumen/` - Resumen estadístico de tipos de cambio
  - Agrupa por fuente y por par de monedas
  - Incluye estadísticas (total, promedio, máximo, mínimo)

#### Características implementadas:
- ✅ Dashboard interactivo para visualización (`/microservicio/tipos-cambio/`)
- ✅ Endpoints API REST para consulta por país y resumen estadístico
- ✅ Histórico de tipos de cambio (últimos 30 días y 12 meses)
- ✅ Estadísticas por par de monedas (promedio, máximo, mínimo)
- ✅ Integración automática con Pulsar: cada nuevo `TipoCambio` se publica en el topic `nuam-tipo-cambio` ✅
- ✅ Filtrado por país usando códigos ISO (CHL, PER, COL, USA)
- ✅ Soporte para múltiples fuentes con sistema de prioridades
- ✅ Tracking de vigencia de tipos de cambio (`vigente_desde`, `vigente_hasta`)
- ✅ **Consumidor automático de APIs externas** ✅
  - Soporte para ExchangeRate API, Fixer.io, Banco Central de Chile
  - Sistema de fallback automático entre fuentes
  - Comando: `python manage.py obtener_tipos_cambio`
  - Ver `CONFIGURACION_TIPOS_CAMBIO.md` para configuración completa

#### Integración con Pulsar:
Cuando se crea un nuevo registro en `TipoCambio`, automáticamente se publica un evento en Pulsar:
- **Topic**: `persistent://public/default/nuam-tipo-cambio`
- **Datos publicados**: `id_fuente`, `moneda_origen`, `moneda_destino`, `tasa`, `fecha`
- **Señal Django**: `post_save` en `microservicio/signals.py`

### 3. Microservicio de Comprobantes ✅
**Ubicación:** `microservicio/views/comprobantes.py`

Genera comprobantes tributarios en PDF desde calificaciones.

#### Endpoints disponibles:
- `GET/POST /microservicio/api/generar-comprobante/<calificacion_id>/` - Genera PDF de comprobante

#### Características:
- ✅ Integración con microservicio FastAPI de documentos
- ✅ Publicación de eventos en Pulsar al generar comprobantes ✅
- ✅ Fallback automático si el microservicio está inactivo

### 4. Microservicio de Pulsar - Visualización ✅
**Ubicación:** `microservicio/views/pulsar.py` y `microservicio/pulsar/`

Visualización en tiempo real de eventos de Apache Pulsar con diseño holográfico/hacker.

#### Vista principal:
- `GET /microservicio/pulsar/` - Dashboard holográfico de visualización de Pulsar

#### Endpoints disponibles:
- `GET /microservicio/api/pulsar/status/` - Estado de conexión de Pulsar
- `GET /microservicio/api/pulsar/topics/` - Información de topics configurados
- `GET /microservicio/api/pulsar/mensajes-recientes/` - Mensajes recientes (24h)
- `POST /microservicio/api/pulsar/publicar-test/` - Publicar mensaje de prueba

#### Características:
- ✅ Dashboard con diseño holográfico/hacker respetando colores NUAM
- ✅ Visualización en tiempo real de topics y mensajes
- ✅ Estadísticas de conexión y actividad
- ✅ Actualización automática cada 10 segundos

### 5. Integración con Apache Pulsar ✅
**Ubicación:** `microservicio/pulsar/client.py` y `microservicio/signals.py`

Apache Pulsar está completamente integrado para eventos asíncronos.

#### Funciones disponibles:
- `publicar_tipo_cambio()` - Publica eventos cuando se actualizan tipos de cambio
- `publicar_carga_masiva()` - Notifica inicio de cargas masivas
- `publicar_actualizacion_graficos()` - Notifica cambios que requieren actualizar dashboards
- `publicar_comprobante_generado()` - Notifica cuando se genera un comprobante

#### Señales automáticas:
- ✅ TipoCambio creado → Publica en topic `tipo_cambio`
- ✅ Carga creada → Publica en topic `carga_masiva`
- ✅ Calificacion creada/actualizada → Publica en topic `actualizacion_graficos`
- ✅ Carga actualizada → Publica evento de actualización de gráficos

#### Topics configurados:
- `persistent://public/default/nuam-tipo-cambio`
- `persistent://public/default/nuam-carga-masiva`
- `persistent://public/default/nuam-enriquecimiento`
- `persistent://public/default/nuam-actualizacion-graficos`
- `persistent://public/default/nuam-comprobante-generado`

#### Consumo de mensajes:
- `python manage.py consumir_pulsar --topic <nombre_topic>` - Consumir mensajes desde terminal

Ver `PULSAR_USO.md` para más detalles sobre el uso de Pulsar.

## Instalación

1. Asegúrate de que el microservicio está registrado en `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'microservicio',
]
```

2. Ejecuta las migraciones:
```bash
python manage.py makemigrations microservicio
python manage.py migrate
```

3. Accede a los gráficos desde el menú principal o directamente en `/microservicio/graficos/`

## Estado de Implementación

### ✅ Completado:
- [x] **Integrar Apache Pulsar para eventos asíncronos** - Completamente integrado con señales automáticas
- [x] **Agregar más gráficos y métricas personalizadas** - Dashboard completo con múltiples gráficos y KPIs
- [x] **Microservicio de Tipos de Cambio** - Dashboard y APIs implementados
- [x] **Microservicio de Comprobantes** - Generación de PDFs con integración Pulsar
- [x] **Visualización de Pulsar** - Dashboard holográfico/hacker para monitoreo
- [x] **Estructura organizada** - Código separado en módulos por funcionalidad

### 🔄 Pendiente:
- [ ] Implementar microservicio de enriquecimiento de cargas (consumidor de Pulsar)
- [ ] Implementar caché para mejorar rendimiento
- [ ] Agregar más tipos de gráficos y visualizaciones personalizadas

### ✅ Recientemente Completado:
- [x] **Consumidor de tipos de cambio desde APIs externas** - Sistema completo con fallback automático
  - Soporte para ExchangeRate API, Fixer.io, Banco Central de Chile
  - Comando de management: `python manage.py obtener_tipos_cambio`
  - Sistema de fallback automático entre fuentes
  - Ver `CONFIGURACION_TIPOS_CAMBIO.md` para más detalles



