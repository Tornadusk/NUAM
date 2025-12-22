# Introducción a los Microservicios y Dashboards de NUAM

## Barra de Navegación Secundaria

Debajo del menú principal de NUAM (Inicio, Catálogos, Corredoras, Instrumentos, Calificaciones, Administración, API), se encuentra una **segunda barra de navegación horizontal** que proporciona acceso a funcionalidades adicionales del sistema. Esta barra contiene tanto **dashboards web integrados** (módulos monolíticos dentro de Django) como enlaces a **microservicios independientes** (servicios FastAPI ejecutándose en contenedores Docker).

### Visibilidad según Rol

La visibilidad de los elementos en esta barra depende del rol del usuario:

- **Administrador** (`admin` / `admin123`): Acceso completo a todos los dashboards y microservicios (Gráficos, Tipos de Cambio, Bolsa, Pulsar, Tests, Swagger API).
- **Operador** (`operador` / `op123456`): Acceso a Gráficos, Tipos de Cambio y Bolsa.
- **Analista** (`analista` / `analista123`): Acceso a Tipos de Cambio y Bolsa.
- **Consultor** (`consultor` / `consultor123`): Sin acceso a microservicios (solo lectura en el Mantenedor).
- **Auditor** (`auditor` / `auditor123`): Sin acceso a microservicios (solo lectura en el Mantenedor y Auditoría).

---

## Dashboards Web Integrados (Módulos Monolíticos)

Estos son **dashboards web** implementados como vistas Django dentro del sistema principal. No son microservicios independientes, sino módulos integrados que se ejecutan en el mismo servidor Django:

### 📊 Gráficos (`/microservicio/graficos/`)

**Tipo:** Dashboard Web (vista Django integrada - monolítico puro)

**Descripción:** Dashboard de visualización de métricas y estadísticas operativas del sistema NUAM. Este dashboard es completamente monolítico y no consume microservicios externos; obtiene todos los datos directamente de la base de datos de Django.

**Funcionalidades:**
- Estadísticas generales (calificaciones, corredoras, instrumentos)
- Gráficos por país, moneda, corredora
- KPIs operativos (tiempo de carga, errores)
- Análisis de cargas por corredora
- Exportación de datos a CSV, Excel, PDF, HTML (generación local en Django)
- Filtrado automático por corredora (Operador ve solo su corredora asignada)
- Publicación de eventos a Pulsar cuando se actualizan gráficos

**Microservicios Backend:** Ninguno (dashboard completamente monolítico)

**Acceso:** Administrador, Operador

---

### 💱 Tipos de Cambio (`/microservicio/tipos-cambio/`)

**Tipo:** Dashboard Web (vista Django integrada) que consume el microservicio `exchange-rate-service`

**Descripción:** Dashboard de monitoreo de tipos de cambio de monedas en tiempo real para Chile, Perú, Colombia y Estados Unidos.

**Funcionalidades:**
- Visualización de tipos de cambio actuales por país (CHL, PER, COL, USA)
- Histórico de tasas de cambio con gráficos de tendencias (Chart.js)
- Estadísticas y análisis de variaciones
- Actualización de tasas desde APIs externas (ExchangeRate API, Fixer.io, Banco Central de Chile)
- Generación de datos simulados para pruebas
- Exportación de gráficos a PNG/JPG (botones en el dashboard)
- Exportación de datos a CSV, Excel, PDF, HTML (botones en el dashboard que usan el microservicio exchange-rate-service)

**Microservicios Backend:** 
- Consume `nuam-exchange-rate-service` (puerto 5100) para:
  - Obtener tipos de cambio desde proveedores externos (endpoint `/tipos-cambio/actualizar`)
  - Exportar datos a PDF, Excel, HTML (endpoints `/exportar/pdf`, `/exportar/excel`, `/exportar/html`) cuando el usuario hace clic en los botones de exportación
- Consume `nuam-chart-export-service` (puerto 5300) para exportar gráficos visuales en formato PNG/JPG cuando el usuario hace clic en los botones "PNG" o "JPG"

**Acceso:** Administrador, Operador, Analista

---

### 📈 Bolsa (`/microservicio/mercados/`)

**Tipo:** Dashboard Web (vista Django integrada) que consume el microservicio `market-info-service`

**Descripción:** Dashboard de información de mercados y bolsa de valores para Chile, Perú y Colombia.

**Funcionalidades:**
- Consulta de información de mercado (acciones, índices) para Chile, Perú y Colombia
- Visualización de datos de bolsa por país con gráficos de evolución histórica (Chart.js)
- Soporte para múltiples proveedores: Yahoo Finance (gratuito), Alpha Vantage (requiere API key), o datos simulados
- Exportación de datos a PDF, Excel, HTML (botones en el dashboard que usan el microservicio market-info-service)
- Exportación de gráficos a PNG/JPG (botones en el dashboard)

**Microservicios Backend:** 
- Consume `nuam-market-info-service` (puerto 5200) para:
  - Obtener información de mercados desde APIs externas (endpoint `/markets/summary`)
  - Obtener historial de mercados (endpoint `/markets/history`)
  - Exportar datos a PDF, Excel, HTML (endpoints `/exportar/pdf`, `/exportar/excel`, `/exportar/html`) cuando el usuario hace clic en los botones de exportación
- Consume `nuam-chart-export-service` (puerto 5300) para exportar gráficos visuales en formato PNG/JPG cuando el usuario hace clic en los botones "PNG" o "JPG"

**Acceso:** Administrador, Operador, Analista

---

### 📡 Pulsar (`/microservicio/pulsar/`)

**Tipo:** Dashboard Web (vista Django integrada) para monitoreo de infraestructura

**Descripción:** Dashboard de visualización y monitoreo de Apache Pulsar, el sistema de mensajería asíncrona utilizado por NUAM.

**Funcionalidades:**
- Estado de conexión con Pulsar (online/offline) y Admin API
- Lista de topics configurados (`nuam-tipo-cambio`, `nuam-carga-masiva`, `nuam-actualizacion-graficos`, etc.)
- Estadísticas de mensajes por topic
- Visualización de mensajes recientes del sistema (últimos mensajes publicados)
- Contador de mensajes en las últimas 24 horas
- Publicación de mensajes de prueba directamente desde el dashboard
- Interfaz visual estilo "holográfico/hacker" con efectos visuales

**Integración con el sistema:**
- El sistema Django publica eventos automáticamente en Pulsar cuando ocurren cambios importantes (creación de tipos de cambio, cargas masivas, actualizaciones de calificaciones)
- Los eventos se publican mediante señales Django (`signals.py`) que se ejecutan cuando se guardan modelos específicos

**Nota:** Pulsar es una **infraestructura de mensajería** (broker pub/sub), no un microservicio de negocio. Se ejecuta en los puertos 6650 (productores/consumidores) y 8080 (Admin API).

**Acceso:** Solo Administrador

---

### 🧪 Tests (`/microservicio/testing/`)

**Tipo:** Dashboard Web (vista Django integrada)

**Descripción:** Dashboard para ejecutar y visualizar tests del sistema desde la interfaz web.

**Funcionalidades:**
- Ejecución de tests con pytest desde el navegador
- Visualización de resultados en tiempo real
- Cálculo de cobertura de código
- Lista de tests disponibles en el proyecto
- Modo verbose para debugging
- Manejo especial de errores (especialmente relacionados con Oracle)

**Acceso:** Solo Administrador

---

### 📚 Swagger API (`/api/docs/`)

**Tipo:** Dashboard Web (documentación interactiva integrada)

**Descripción:** Documentación interactiva y autogenerada de la API REST de NUAM usando Swagger/OpenAPI.

**Funcionalidades:**
- Documentación automática de todos los endpoints de la API
- Pruebas interactivas directamente desde el navegador
- Ejemplos de requests y responses
- Autenticación integrada (Session, Basic Auth)
- Esquemas de validación para cada endpoint
- Descarga de schema OpenAPI en formato JSON/YAML

**Acceso:** Solo Administrador

---

## Microservicios Backend (FastAPI Independientes)

Estos son **microservicios reales** implementados como servicios FastAPI independientes que se ejecutan en contenedores Docker separados. Proporcionan funcionalidades específicas que son consumidas por el sistema principal Django:

### 1. nuam-exchange-rate-service (Puerto 5100)

**Tipo:** Microservicio FastAPI independiente

**Responsabilidad:** 
- Obtener y entregar tipos de cambio (por ejemplo, CLP↔USD, PEN↔USD, COP↔USD) desde proveedores externos (ExchangeRate API, Fixer.io, Banco Central de Chile)
- Exportar datos de tipos de cambio a PDF, Excel y HTML

**Endpoints principales:**
- `POST /tipos-cambio/actualizar` - Consulta proveedores externos y devuelve tipos de cambio actualizados
- `POST /exportar/pdf` - Genera archivo PDF con tipos de cambio
- `POST /exportar/excel` - Genera archivo Excel (.xlsx) con tipos de cambio
- `POST /exportar/html` - Genera archivo HTML con tipos de cambio
- `GET /health` - Health check del servicio

**Uso típico:** 
- El dashboard de Tipos de Cambio llama a `/tipos-cambio/actualizar` para obtener tasas actualizadas desde APIs externas cuando el usuario hace clic en "Actualizar desde APIs"
- Los botones de exportación (CSV, Excel, PDF, HTML) en el dashboard llaman a los endpoints `/exportar/*` para generar documentos con los datos de tipos de cambio almacenados en la base de datos

**Endpoints:** Documentación completa disponible en `http://localhost:5100/docs`

**Consumido por:** Dashboard de Tipos de Cambio (`/microservicio/tipos-cambio/`) mediante los clientes HTTP en `microservicio/services/exchange_rate_client.py`

---

### 2. nuam-market-info-service (Puerto 5200)

**Tipo:** Microservicio FastAPI independiente

**Responsabilidad:** 
- Consultar información de mercado (acciones, índices, datos de bolsa) usando APIs externas (Yahoo Finance, Alpha Vantage, o datos simulados)
- Exportar datos de mercados a PDF, Excel y HTML

**Endpoints principales:**
- `GET /markets/summary` - Obtiene resumen de mercados por país (CHL, PER, COL)
- `GET /markets/history` - Obtiene historial mensual de un mercado específico
- `POST /exportar/pdf` - Genera archivo PDF con datos de mercados
- `POST /exportar/excel` - Genera archivo Excel (.xlsx) con datos de mercados
- `POST /exportar/html` - Genera archivo HTML con datos de mercados
- `GET /health` - Health check del servicio

**Proveedores soportados:**
- `yahoo`: Yahoo Finance (gratuito, sin API key requerida)
- `alpha_vantage`: Alpha Vantage API (requiere API key en variable de entorno)
- `simulado`: Datos simulados (siempre disponible como fallback)

**Uso típico:** 
- El dashboard de Bolsa llama a `/markets/summary` para obtener información actualizada de los mercados al cargar la página
- El dashboard llama a `/markets/history` para obtener historial cuando el usuario selecciona un país
- Los botones de exportación (PDF, Excel, HTML) en el dashboard llaman a los endpoints `/exportar/*` para generar documentos con los datos de mercados obtenidos del microservicio

**Endpoints:** Documentación completa disponible en `http://localhost:5200/docs`

**Consumido por:** Dashboard de Bolsa (`/microservicio/mercados/`) mediante los clientes HTTP en `microservicio/services/market_info_client.py`

---

### 3. nuam-chart-export-service (Puerto 5300)

**Tipo:** Microservicio FastAPI independiente

**Responsabilidad:** Generar imágenes de gráficos (PNG/JPG) a partir de configuraciones de Chart.js proporcionadas.

**Endpoints principales:**
- `POST /exportar/{formato}` - Exporta gráfico simple (formato: `png` o `jpg`)
- `POST /exportar/tipos-cambio/{formato}` - Exporta gráfico específico de tipos de cambio
- `POST /exportar/bolsa/{formato}` - Exporta gráfico específico de bolsa
- `POST /exportar/config` - Exporta gráfico desde configuración completa de Chart.js
- `GET /health` - Health check del servicio

**Uso típico:** 
- Los dashboards de Tipos de Cambio y Bolsa tienen botones "PNG" y "JPG" que llaman a este servicio cuando el usuario hace clic
- El servicio recibe la configuración del gráfico Chart.js (labels, datasets, tipo de gráfico, título) y devuelve una imagen renderizada en el formato solicitado
- El dashboard envía la configuración actual del gráfico visible al usuario y recibe la imagen generada

**Endpoints:** Documentación completa disponible en `http://localhost:5300/docs`

**Consumido por:** 
- Dashboard de **Tipos de Cambio** (`/microservicio/tipos-cambio/`) → Botones de descarga PNG/JPG de gráficos (mediante `microservicio/services/chart_export_client.py`)
- Dashboard de **Bolsa** (`/microservicio/mercados/`) → Botones de descarga PNG/JPG de gráficos (mediante `microservicio/services/chart_export_client.py`)

---

### 4. nuam-docs-generator (Puerto 5001 → interno 5000)

**Tipo:** Microservicio FastAPI independiente

**Responsabilidad:** Generar documentos en múltiples formatos (PDFs, reportes, comprobantes tributarios, archivos CSV y Excel).

**Uso típico:** Cuando NUAM necesita emitir documentos descargables o adjuntos. Este microservicio es consumido automáticamente por las pestañas **Mantenedor** y **Reportes** cuando el usuario descarga archivos en formato PDF, CSV o Excel.

**Funcionalidades:**
- Generación de PDFs con templates HTML usando Jinja2
- Exportación a CSV con encoding UTF-8-BOM (compatible con Excel)
- Exportación a Excel (.xlsx) con formato estructurado
- Endpoint `/health` para monitoreo del servicio
- **Fallback automático:** Si el microservicio está offline, Django genera los documentos localmente usando métodos integrados

**Endpoints principales:**
- `POST /exportar` - Genera documentos en formato PDF, CSV o Excel según el parámetro `formato` en el payload
- `GET /health` - Health check del servicio

**Uso típico:** 
- Las pestañas **Mantenedor** y **Reportes** intentan usar este microservicio automáticamente cuando el usuario hace clic en los botones de descarga
- Si el microservicio está disponible, se usa para generar documentos de forma más eficiente
- Si está offline, Django automáticamente usa métodos locales integrados (fallback) sin interrumpir la funcionalidad

**Endpoints:** Documentación disponible en `http://localhost:5001/docs`

**Consumido por:** 
- Pestaña **Mantenedor** (`/calificaciones/mantenedor/`) → Botones de descarga CSV, Excel, PDF de calificaciones
- Pestaña **Reportes** (`/calificaciones/mantenedor/` → pestaña Reportes) → Botones "Descargar CSV", "Descargar Excel", "Descargar PDF"

**Nota importante:** Este microservicio funciona de forma transparente para el usuario. El código en `calificaciones/views.py` (función `exportar_datos_view`) intenta primero usar el microservicio, y si falla, automáticamente genera los documentos localmente usando métodos integrados de Django (reportlab para PDF, openpyxl para Excel, csv para CSV).

---

## Infraestructura de Mensajería

### Apache Pulsar (Puertos 6650 y 8080)

**Tipo:** Infraestructura (broker de mensajería pub/sub), no es un microservicio de negocio

**Qué es:** Sistema de mensajería asíncrona (similar a Kafka) que permite comunicación entre diferentes partes del sistema mediante eventos.

**Para qué sirve:** 
- Comunicación asíncrona entre componentes del sistema
- Publicación de eventos del sistema cuando ocurren cambios importantes
- Desacoplamiento de servicios mediante mensajería
- Permite que otros sistemas o servicios consuman eventos sin estar acoplados directamente

**Topics configurados en NUAM:**
- `nuam-tipo-cambio` → Eventos cuando se crea un nuevo tipo de cambio
- `nuam-carga-masiva` → Eventos cuando se inicia una carga masiva
- `nuam-actualizacion-graficos` → Eventos cuando se actualizan gráficos o estadísticas
- `nuam-comprobante-generado` → Eventos cuando se genera un comprobante
- `nuam-enriquecimiento` → Eventos para procesos de enriquecimiento de datos

**Eventos publicados automáticamente:**
- Cuando se crea un `TipoCambio` → Se publica en `nuam-tipo-cambio`
- Cuando se crea una `Carga` masiva → Se publica en `nuam-carga-masiva`
- Cuando se crea/actualiza una `Calificacion` → Se publica en `nuam-actualizacion-graficos`
- Cuando se actualiza el estado de una `Carga` → Se publica en `nuam-actualizacion-graficos`
- Cuando se refrescan gráficos manualmente → Se publica en `nuam-actualizacion-graficos`

**Puertos:**
- **6650:** Puerto para conexión de productores y consumidores de mensajes
- **8080:** Admin API para gestión y healthcheck del broker

**Monitoreo:** Disponible a través del dashboard Pulsar (`/microservicio/pulsar/`) para usuarios Administrador, donde se pueden ver topics, mensajes recientes y estadísticas

---

## Resumen de Arquitectura

### Dashboards Web (Monolíticos - Django)
- **Gráficos** → Completamente monolítico (solo BD Django, sin microservicios)
- **Tipos de Cambio** → Consume `exchange-rate-service` (datos) + `chart-export-service` (imágenes)
- **Bolsa** → Consume `market-info-service` (datos) + `chart-export-service` (imágenes)
- **Pulsar** → Monitoreo de infraestructura (no consume microservicios de negocio)
- **Tests** → Completamente monolítico (ejecuta pytest localmente)
- **Swagger API** → Documentación integrada (no consume microservicios)

### Microservicios Backend (FastAPI Independientes)
- **`exchange-rate-service` (5100)** → Consulta APIs externas + Exportación PDF/Excel/HTML
- **`market-info-service` (5200)** → Consulta APIs externas + Exportación PDF/Excel/HTML
- **`chart-export-service` (5300)** → Generación de imágenes PNG/JPG desde Chart.js
- **`docs-generator` (5001)** → Generación de documentos PDF/CSV/Excel para Mantenedor y Reportes

### Infraestructura
- **Apache Pulsar (6650, 8080)** → Mensajería asíncrona (pub/sub) para eventos del sistema

---

## Nota para el Usuario

Los microservicios y dashboards descritos en esta sección son **funcionalidades adicionales** que complementan el sistema principal de NUAM. El funcionamiento básico del sistema (gestión de usuarios, corredoras, instrumentos, calificaciones, cargas masivas y auditoría) **no depende de estos microservicios** y funciona de forma independiente.

Los microservicios proporcionan:
- **Visualización avanzada:** Dashboards con gráficos y métricas
- **Integración con APIs externas:** Tipos de cambio y datos de bolsa en tiempo real
- **Exportación mejorada:** Generación eficiente de documentos en múltiples formatos
- **Monitoreo:** Herramientas para supervisar el estado del sistema y la infraestructura

Si algún microservicio no está disponible, el sistema principal continúa funcionando normalmente, y en el caso del generador de documentos, el sistema automáticamente usa métodos alternativos integrados.

