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

## 3. Comunicación Django ↔ Microservicios

### 3.1. Cliente HTTP para exchange-rate-service

- **Archivo**: `microservicio/services/exchange_rate_client.py`.
- **Responsabilidad**:
  - Resolver la URL base del microservicio desde:
    - `EXCHANGE_RATE_SERVICE_URL` (entorno) o
    - `settings.EXCHANGE_RATE_SERVICE_URL`.
  - Enviar peticiones HTTP al endpoint:
    - `POST /tipos-cambio/actualizar`.
- **Función principal**:
  - `llamar_exchange_rate_service_actualizar(monedas, moneda_base, incluir_proveedores)`.

### 3.2. Comando `obtener_tipos_cambio` (Django)

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

## 4. Justificación Arquitectónica (Rúbrica)

- NUAM ahora cuenta con **dos microservicios independientes**:
  1. `docs-generator`: generación de documentos.
  2. `exchange-rate-service`: consulta de tipos de cambio.
- Ambos:
  - Tienen **Dockerfile propio** y servicio en `docker-compose.yml`.
  - Se comunican con el backend Django vía **HTTP interno**.
  - Pueden escalarse / desplegarse de forma independiente si el sistema crece.
- El módulo de **Tipos de Cambio** en Django queda como un **bounded context**
  que:
  - Usa el microservicio de tipos de cambio para obtener datos reales.
  - Almacena y expone esos datos a través de APIs REST y dashboards.


