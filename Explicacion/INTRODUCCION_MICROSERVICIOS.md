# Introducción a los Microservicios y Dashboards de NUAM

## Barra de Navegación Secundaria

Debajo del menú principal de NUAM (Inicio, Catálogos, Corredoras, Instrumentos, Calificaciones, Administración, API), se encuentra una **segunda barra de navegación horizontal** que proporciona acceso a funcionalidades adicionales del sistema. Esta barra contiene tanto **dashboards web integrados** (módulos monolíticos dentro de Django) como enlaces a **microservicios independientes** (servicios FastAPI ejecutándose en contenedores Docker).

### Visibilidad según Rol

La visibilidad de los elementos en esta barra depende del rol del usuario:

- **Administrador** (`admin` / `admin123`): Acceso completo a todos los dashboards y microservicios (Gráficos, Tipos de Cambio, Bolsa, Pulsar, Tests, Swagger API).
- **Operador** (`operador` / `op123456`): Acceso a Gráficos y Tipos de Cambio.
- **Analista** (`analista` / `analista123`): Acceso a Gráficos y Tipos de Cambio.
- **Consultor** (`consultor` / `consultor123`): Sin acceso a microservicios (solo lectura en el Mantenedor).
- **Auditor** (`auditor` / `auditor123`): Sin acceso a microservicios (solo lectura en el Mantenedor y Auditoría).

---

## Dashboards Web Integrados (Módulos Monolíticos)

Estos son **dashboards web** implementados como vistas Django dentro del sistema principal. No son microservicios independientes, sino módulos integrados que se ejecutan en el mismo servidor Django:

### 📊 Gráficos (`/microservicio/graficos/`)

**Tipo:** Dashboard Web (vista Django integrada)

**Descripción:** Dashboard de visualización de métricas y estadísticas operativas del sistema NUAM.

**Funcionalidades:**
- Estadísticas generales (calificaciones, corredoras, instrumentos)
- Gráficos por país, moneda, corredora
- KPIs operativos (tiempo de carga, errores)
- Análisis de cargas por corredora
- Exportación de gráficos a CSV, Excel, PDF, HTML
- Filtrado automático por corredora (Operador ve solo su corredora asignada)

**Acceso:** Administrador, Operador, Analista

---

### 💱 Tipos de Cambio (`/microservicio/tipos-cambio/`)

**Tipo:** Dashboard Web (vista Django integrada) que consume el microservicio `exchange-rate-service`

**Descripción:** Dashboard de monitoreo de tipos de cambio de monedas en tiempo real para Chile, Perú, Colombia y Estados Unidos.

**Funcionalidades:**
- Visualización de tipos de cambio actuales por país (CHL, PER, COL, USA)
- Histórico de tasas de cambio con gráficos de tendencias
- Estadísticas y análisis de variaciones
- Integración con APIs externas (ExchangeRate API, Fixer.io, Banco Central de Chile)
- Actualización automática de tasas desde fuentes externas
- Generación de datos simulados para pruebas

**Microservicio Backend:** Consume `nuam-exchange-rate-service` (puerto 5100) para obtener datos de tipos de cambio desde proveedores externos.

**Acceso:** Administrador, Analista, Operador

---

### 📈 Bolsa (`/microservicio/mercados/`)

**Tipo:** Dashboard Web (vista Django integrada) que consume el microservicio `market-info-service`

**Descripción:** Dashboard de información de mercados y bolsa de valores para Chile, Perú y Colombia.

**Funcionalidades:**
- Consulta de información de mercado (acciones, índices)
- Visualización de datos de bolsa por país
- Gráficos de evolución histórica
- Exportación de datos a PDF, Excel, HTML

**Microservicio Backend:** Consume `nuam-market-info-service` (puerto 5200) que utiliza Alpha Vantage API para obtener información de mercados.

**Acceso:** Administrador, Analista, Operador

---

### 📡 Pulsar (`/microservicio/pulsar/`)

**Tipo:** Dashboard Web (vista Django integrada) para monitoreo de infraestructura

**Descripción:** Dashboard de visualización y monitoreo de Apache Pulsar, el sistema de mensajería asíncrona utilizado por NUAM.

**Funcionalidades:**
- Estado de conexión con Pulsar (online/offline)
- Lista de topics y estadísticas de mensajes
- Visualización de mensajes recientes del sistema
- Contador de mensajes en las últimas 24 horas
- Publicación de mensajes de prueba
- Interfaz visual estilo "holográfico/hacker"

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

**Responsabilidad:** Obtener y entregar tipos de cambio (por ejemplo, CLP↔USD, PEN↔USD, COP↔USD) desde proveedores externos (ExchangeRate API, Fixer.io, Banco Central de Chile).

**Uso típico:** Cuando NUAM necesita convertir montos o calcular valores en distintas monedas, el sistema Django consume este microservicio para obtener las tasas de cambio actuales.

**Endpoints:** Documentación disponible en `http://localhost:5100/docs`

**Consumido por:** Dashboard de Tipos de Cambio (`/microservicio/tipos-cambio/`)

---

### 2. nuam-market-info-service (Puerto 5200)

**Tipo:** Microservicio FastAPI independiente

**Responsabilidad:** Consultar información de mercado (acciones, índices, datos de bolsa) usando APIs externas (Alpha Vantage como proveedor por defecto).

**Uso típico:** Alimentar reportes, dashboards o análisis de mercado para Chile, Perú y Colombia. El sistema Django consume este microservicio para obtener información actualizada de los mercados financieros.

**Endpoints:** Documentación disponible en `http://localhost:5200/docs`

**Consumido por:** Dashboard de Bolsa (`/microservicio/mercados/`)

---

### 3. nuam-chart-export-service (Puerto 5300)

**Tipo:** Microservicio FastAPI independiente

**Responsabilidad:** Generar imágenes de gráficos (PNG/JPG) a partir de datos proporcionados.

**Uso típico:** Exportar gráficos para reportes, PDFs o vistas que necesiten un "snapshot" del gráfico en formato de imagen.

**Endpoints:** Documentación disponible en `http://localhost:5300/docs`

**Consumido por:** Sistema de exportación de reportes

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

**Endpoints:** Documentación disponible en `http://localhost:5001/docs`

**Consumido por:** 
- Pestaña **Mantenedor** → Botones de descarga (CSV, Excel, PDF)
- Pestaña **Reportes** → Botones "Descargar CSV", "Descargar Excel", "Descargar PDF"

**Nota importante:** Este microservicio funciona de forma transparente para el usuario. Si el servicio está disponible, se usa para generar documentos de forma más eficiente. Si está offline, el sistema automáticamente usa métodos locales de Django sin interrumpir la funcionalidad.

---

## Infraestructura de Mensajería

### Apache Pulsar (Puertos 6650 y 8080)

**Tipo:** Infraestructura (broker de mensajería pub/sub), no es un microservicio de negocio

**Qué es:** Sistema de mensajería asíncrona (similar a Kafka) que permite comunicación entre diferentes partes del sistema mediante eventos.

**Para qué sirve:** 
- Comunicación asíncrona entre componentes del sistema
- Publicación de eventos del sistema (por ejemplo: "tipo de cambio actualizado", "carga masiva creada", "calificación validada")
- Desacoplamiento de servicios mediante mensajería

**Puertos:**
- **6650:** Puerto para conexión de productores y consumidores de mensajes
- **8080:** Admin API para gestión y healthcheck del broker

**Monitoreo:** Disponible a través del dashboard Pulsar (`/microservicio/pulsar/`) para usuarios Administrador

---

## Resumen de Arquitectura

### Dashboards Web (Monolíticos - Django)
- Gráficos
- Tipos de Cambio (consume microservicio)
- Bolsa (consume microservicio)
- Pulsar (monitoreo de infraestructura)
- Tests
- Swagger API

### Microservicios Backend (FastAPI Independientes)
- `exchange-rate-service` (5100) → Tipos de cambio
- `market-info-service` (5200) → Información de bolsa
- `chart-export-service` (5300) → Exportación de gráficos
- `docs-generator` (5001) → Generación de documentos (PDF, CSV, Excel)

### Infraestructura
- Apache Pulsar (6650, 8080) → Mensajería asíncrona

---

## Nota para el Usuario

Los microservicios y dashboards descritos en esta sección son **funcionalidades adicionales** que complementan el sistema principal de NUAM. El funcionamiento básico del sistema (gestión de usuarios, corredoras, instrumentos, calificaciones, cargas masivas y auditoría) **no depende de estos microservicios** y funciona de forma independiente.

Los microservicios proporcionan:
- **Visualización avanzada:** Dashboards con gráficos y métricas
- **Integración con APIs externas:** Tipos de cambio y datos de bolsa en tiempo real
- **Exportación mejorada:** Generación eficiente de documentos en múltiples formatos
- **Monitoreo:** Herramientas para supervisar el estado del sistema y la infraestructura

Si algún microservicio no está disponible, el sistema principal continúa funcionando normalmente, y en el caso del generador de documentos, el sistema automáticamente usa métodos alternativos integrados.

