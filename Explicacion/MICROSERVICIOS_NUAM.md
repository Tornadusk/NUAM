# Microservicios en NUAM

Este documento resume los microservicios implementados en el proyecto NUAM y
cómo se comunican con el backend principal (Django).

## 1. docs-generator (Microservicio de Reportes)

- **Tecnología**: FastAPI + Uvicorn.
- **Ubicación**: `services/docs-generator/`.
- **Propósito**: Generar reportes en formato **CSV, Excel y PDF** a partir de
  datos que le envía NUAM.
- **Despliegue**:
  - Contenedor Docker propio (`nuam-docs-generator`).
  - Puerto interno `5000`, expuesto como `5001` en el host.
  - Definido en `docker-compose.yml`.
- **Comunicación con NUAM**:
  - Django llama al endpoint `POST /exportar` desde vistas como
    el mantenedor de calificaciones.
  - Protocolo: HTTP interno (`http://localhost:5001/exportar`).

## 2. exchange-rate-service (Microservicio de Tipos de Cambio)

- **Tecnología**: FastAPI + Uvicorn.
- **Ubicación**: `services/exchange-rate-service/`.
- **Propósito**:
  - Consultar proveedores externos de tipos de cambio
    (ExchangeRate API, Fixer.io, Banco Central de Chile).
  - Devolver los tipos de cambio **en memoria** a NUAM, sin persistencia propia.
- **Endpoints principales**:
  - `GET /health`  
    Verificación de salud del servicio.
  - `POST /tipos-cambio/actualizar`  
    Consulta a las APIs externas y devuelve una lista de tipos de cambio con
    metadatos y errores por proveedor.
  - `GET /tipos-cambio/actuales`  
    Endpoint de conveniencia que llama internamente a `actualizar` y devuelve
    los tipos de cambio actuales según país/moneda base.
- **Schemas (Pydantic)**:
  - `TipoCambioItem`: moneda_origen, moneda_destino, tasa, fecha, fuente.
  - `ActualizarRequest`: monedas, moneda_base, incluir_proveedores.
  - `ActualizarResponse`: success, tipos_cambio, errores, metadata.
- **Despliegue**:
  - Contenedor Docker propio (`nuam-exchange-rate-service`).
  - Puerto `5100`.
  - Definido en el `docker-compose.yml` raíz:
    - Build desde `./services/exchange-rate-service`.
    - Variables de entorno opcionales:
      - `EXCHANGERATE_API_KEY`
      - `FIXER_API_KEY`

## 3. market-info-service (Microservicio de Información de Mercados)

- **Tecnología**: FastAPI + Uvicorn.
- **Ubicación**: `services/market-info-service/`.
- **Propósito**:
  - Consultar información de los mercados de Chile, Perú y Colombia
    (índices principales como IPSA, S&P/BVL Peru General, COLCAP).
- **Comportamiento**:
  - Primero intenta obtener datos desde una **API real** (por ejemplo Yahoo Finance).
  - Si la llamada falla (sin internet, cambios en la API, límites, etc.),
    devuelve **datos simulados** pero coherentes, con la misma estructura.
- **Endpoints principales**:
  - `GET /health`  
    Verificación de salud del servicio.
  - `GET /markets/summary`  
    Devuelve, para uno o varios países, un resumen de índices:
    símbolo, nombre, último valor, variación diaria, % variación, volumen,
    moneda y hora de cotización.
- **Schemas (Pydantic)**:
  - `IndexItem`: información de un índice/instrumento principal.
  - `MarketSummaryResponse`: respuesta por país (incluye flag `fuente_real`
    que indica si los datos vienen de API real o son simulados).
  - `MultiMarketSummaryResponse`: respuesta agregada para varios países.
- **Despliegue**:
  - Contenedor Docker propio (`nuam-market-info-service`).
  - Puerto `5200`.
  - Definido en el `docker-compose.yml` raíz.

## 4. Comunicación Django ↔ Microservicios

### 4.1. Cliente HTTP para exchange-rate-service

- **Archivo**: `microservicio/services/exchange_rate_client.py`.
- **Responsabilidad**:
  - Resolver la URL base del microservicio desde:
    - `EXCHANGE_RATE_SERVICE_URL` (entorno) o
    - `settings.EXCHANGE_RATE_SERVICE_URL`.
  - Enviar peticiones HTTP al endpoint:
    - `POST /tipos-cambio/actualizar`.
- **Función principal**:
  - `llamar_exchange_rate_service_actualizar(monedas, moneda_base, incluir_proveedores)`.

### 4.2. Comando `obtener_tipos_cambio` (Django)

- **Archivo**: `microservicio/management/commands/obtener_tipos_cambio.py`.
- **Cambio clave**:
  - Antes: llamaba directamente a las APIs externas mediante
    `exchange_rate_providers` dentro de Django.
  - Ahora: llama al microservicio `exchange-rate-service` usando el cliente
    HTTP y luego **guarda** los resultados en las tablas:
    - `tipo_cambio_fuente`
    - `tipo_cambio`.
- **Ventajas**:
  - Separamos la **lógica de integración con proveedores externos** en un
    microservicio reutilizable.
  - Django se centra en la **persistencia y presentación** de los datos.

### 4.3. Cliente HTTP para market-info-service

- **Archivo**: `microservicio/services/market_info_client.py`.
- **Función principal**:
  - `obtener_resumen_mercados(paises)` llama a `GET /markets/summary` y
    devuelve el JSON con la lista de mercados e índices.
- **Vista y API Django**:
  - `microservicio/views/mercados.py` define:
    - `mercados_dashboard` → `/microservicio/mercados/` (pestaña “Bolsa”).
    - `api_mercados_resumen` → `/microservicio/api/mercados/resumen/`  
      (proxy autenticado que llama al microservicio y reenvía la respuesta).
  - El dashboard se renderiza en
    `templates/microservicio/mercados/dashboard.html` y se muestra junto a:
    - Gráficos
    - Tipos de Cambio
    - Pulsar
    - Tests
    - Swagger API

## 5. Justificación Arquitectónica (Rúbrica)

- NUAM ahora cuenta con **tres microservicios independientes en producción**:
  1. `docs-generator`: generación de documentos.
  2. `exchange-rate-service`: consulta de tipos de cambio.
  3. `market-info-service`: información de bolsas de valores (Chile, Perú, Colombia).
- Ambos:
  - Tienen **Dockerfile propio** y servicio en `docker-compose.yml`.
  - Se comunican con el backend Django vía **HTTP interno**.
  - Pueden escalarse / desplegarse de forma independiente si el sistema crece.
- El módulo de **Tipos de Cambio** en Django queda como un **bounded context**
  que:
  - Usa el microservicio de tipos de cambio para obtener datos reales.
  - Almacena y expone esos datos a través de APIs REST y dashboards.

- El nuevo módulo de **Mercados/Bolsa** funciona como un dashboard ligero que
  consume `market-info-service` para mostrar al usuario información de contexto
  (índices de referencia por país) sin mezclar esta lógica con las
  calificaciones tributarias ni con el microservicio de tipos de cambio.



