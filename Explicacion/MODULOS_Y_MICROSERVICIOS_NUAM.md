# Explicación de Módulos y Microservicios en NUAM

Este documento explica cada sección del proyecto NUAM y cuáles son microservicios reales vs módulos del monolito (Django).

---

## 📊 1. Gráficos

**¿Qué es?**
- **Módulo del monolito Django** (NO es microservicio)
- Dashboard de visualización de estadísticas y métricas del sistema

**¿Qué hace?**
- Muestra gráficos de:
  - Calificaciones por país y moneda
  - Actividad reciente del sistema
  - Cargas por corredora
  - Resumen de auditoría
  - KPIs operativos
- Permite exportar gráficos en formatos: CSV, Excel, PDF, HTML

**¿Dónde está?**
- Vista Django: `microservicio/views/graficos.py`
- Template: `templates/microservicio/graficos/dashboard.html`
- URL: `/microservicio/graficos/`
- Exportación: `microservicio/utils/exportador.py` (directo desde Django, NO usa microservicio)

**Tecnología:**
- Django + Chart.js (frontend)
- Exportación directa con ReportLab (PDF), openpyxl (Excel), CSV nativo

---

## 💱 2. Tipos de Cambio

**¿Qué es?**
- **Módulo del monolito Django** que **consume** un microservicio
- Dashboard para visualizar y gestionar tipos de cambio de monedas

**¿Qué hace?**
- Muestra tipos de cambio actuales por país
- Permite actualizar tipos de cambio manualmente (botón "Actualizar")
- Visualiza histórico de tipos de cambio
- Almacena datos en base de datos Oracle (tablas `tipo_cambio_fuente` y `tipo_cambio`)

**¿Cómo funciona?**
1. El dashboard Django muestra datos desde la BD
2. Al presionar "Actualizar", Django llama al **microservicio** `exchange-rate-service`
3. El microservicio consulta APIs externas (ExchangeRate API, Fixer.io, Banco Central de Chile)
4. Django recibe los datos y los guarda en Oracle
5. El dashboard se actualiza con los nuevos datos

**¿Dónde está?**
- Vista Django: `microservicio/views/tipos_cambio.py`
- Template: `templates/microservicio/tipos_cambio/dashboard.html`
- URL: `/microservicio/tipos-cambio/`
- Cliente microservicio: `microservicio/services/exchange_rate_client.py`
- **Microservicio usado**: `services/exchange-rate-service/` (FastAPI, puerto 5100)

**Arquitectura:**
```
Dashboard Django → Cliente HTTP → exchange-rate-service (FastAPI) → APIs externas
                  ↓
            Guarda en Oracle
```

---

## 📈 3. Bolsa (Mercados)

**¿Qué es?**
- **Módulo del monolito Django** que **consume** un microservicio
- Dashboard para visualizar información de bolsas de valores (Chile, Perú, Colombia)

**¿Qué hace?**
- Muestra índices principales: IPSA (Chile), S&P/BVL (Perú), COLCAP (Colombia)
- Permite seleccionar proveedor de datos: Yahoo Finance, Alpha Vantage, Datos Simulados
- Muestra gráficos históricos (línea, barra, radar)
- Permite actualizar datos manualmente
- Indicador de peticiones diarias restantes (Alpha Vantage)

**¿Cómo funciona?**
1. El dashboard Django solicita datos al **microservicio** `market-info-service`
2. El microservicio intenta obtener datos reales (Yahoo Finance o Alpha Vantage)
3. Si falla, devuelve datos simulados coherentes
4. Django muestra los datos en el dashboard con gráficos interactivos

**¿Dónde está?**
- Vista Django: `microservicio/views/mercados.py`
- Template: `templates/microservicio/mercados/dashboard.html`
- URL: `/microservicio/mercados/`
- Cliente microservicio: `microservicio/services/market_info_client.py`
- **Microservicio usado**: `services/market-info-service/` (FastAPI, puerto 5200)

**Arquitectura:**
```
Dashboard Django → Cliente HTTP → market-info-service (FastAPI) → APIs externas (Yahoo/Alpha Vantage)
                                                                    ↓ (si falla)
                                                                 Datos simulados
```

---

## 🔔 4. Pulsar

**¿Qué es?**
- **Sistema de mensajería** (Apache Pulsar) - NO es microservicio NUAM, es **infraestructura**
- Dashboard Django para visualizar el estado de Pulsar

**¿Qué hace?**
- Muestra el estado de Pulsar (conectado/desconectado)
- Lista los topics disponibles (ej: `tipo_cambio`)
- Muestra mensajes recientes de los topics
- Permite publicar mensajes de prueba
- Indica qué servicios publican/consumen de cada topic

**¿Cómo se usa?**
- El microservicio `exchange-rate-service` publica tipos de cambio al topic `tipo_cambio`
- Otros servicios pueden consumir estos mensajes
- El dashboard Django solo **visualiza** el estado, no es un consumidor activo

**¿Dónde está?**
- Vista Django: `microservicio/views/pulsar.py`
- Template: `templates/microservicio/pulsar/dashboard.html`
- URL: `/microservicio/pulsar/`
- Infraestructura: Contenedor Docker `nuam-pulsar` (puerto 6650, 8080)

**Importante:**
- Pulsar es una herramienta externa (Apache Pulsar), no un microservicio desarrollado por NUAM
- El dashboard Django solo muestra su estado y contenido

---

## 🧪 5. Tests

**¿Qué es?**
- **Dashboard Django** para ejecutar y visualizar tests - NO es microservicio
- Interfaz web para pytest

**¿Qué hace?**
- Muestra el estado de los tests (pasando/fallando)
- Permite ejecutar tests desde la interfaz web
- Muestra lista de tests disponibles
- Muestra resultados detallados de cada ejecución

**¿Dónde está?**
- Vista Django: `microservicio/views/testing.py`
- Template: `templates/microservicio/testing/dashboard.html`
- URL: `/microservicio/testing/`
- Tests reales: `tests/` (pytest)

**Tecnología:**
- Pytest (framework de testing)
- Dashboard Django solo ejecuta `pytest` y muestra resultados

---

## 📚 6. Swagger API

**¿Qué es?**
- **Documentación interactiva de la API REST** - NO es microservicio, es **parte del monolito**
- Interfaz generada automáticamente por Django REST Framework

**¿Qué hace?**
- Documenta todos los endpoints REST de NUAM
- Permite probar endpoints directamente desde el navegador
- Muestra esquemas de datos (request/response)
- Incluye autenticación integrada

**¿Dónde está?**
- URL: `/api/docs/` (Swagger UI) o `/api/redoc/` (ReDoc)
- Generado por: `drf-spectacular` (Django REST Framework)
- Endpoints documentados: `api/urls.py`

**Tecnología:**
- OpenAPI 3.0 (Swagger)
- Django REST Framework + drf-spectacular
- Todo dentro del monolito Django

---

## 📄 7. Reportes (Mantenedor)

**¿Qué es?**
- **Microservicio real** - `docs-generator` (FastAPI)

**¿Qué hace?**
- Genera reportes profesionales en formato PDF, Excel y CSV
- Se usa desde la pestaña "Reportes" del mantenedor de calificaciones
- Formatea reportes con encabezados, estilos y metadatos
- Exporta datos filtrados de calificaciones tributarias

**¿Cómo funciona?**
1. Usuario selecciona formato (PDF/Excel/CSV) en el mantenedor
2. Django envía datos filtrados al microservicio `docs-generator`
3. El microservicio genera el archivo formateado
4. Django devuelve el archivo al usuario para descarga

**¿Dónde está?**
- Vista Django: `calificaciones/views.py` → `exportar_datos_view()`
- URL Django: `/calificaciones/exportar/<formato>/`
- **Microservicio**: `services/docs-generator/` (FastAPI, puerto 5001)

**Arquitectura:**
```
Mantenedor Django → Vista exportar_datos_view() → HTTP POST → docs-generator (FastAPI)
                                                                    ↓
                                                            Genera PDF/Excel/CSV
                                                                    ↓
                                                            Django devuelve archivo
```

**Nota importante:**
- La exportación de **gráficos** (desde el dashboard de Gráficos) NO usa este microservicio
- La exportación de gráficos es directa desde Django (`exportador.py`)
- Solo los **reportes del mantenedor** usan `docs-generator`

---

## 📊 Resumen: Microservicios vs Módulos

### ✅ Microservicios Reales (3)

1. **`docs-generator`** (puerto 5001)
   - Genera reportes PDF/Excel/CSV desde el mantenedor
   - FastAPI + Docker
   - Comunicación: HTTP

2. **`exchange-rate-service`** (puerto 5100)
   - Consulta tipos de cambio de APIs externas
   - FastAPI + Docker
   - Comunicación: HTTP

3. **`market-info-service`** (puerto 5200)
   - Consulta información de bolsas de valores
   - FastAPI + Docker
   - Comunicación: HTTP

### ❌ NO son Microservicios

| Módulo | Tipo | Descripción |
|--------|------|-------------|
| **Gráficos** | Módulo Django | Dashboard con visualizaciones, exporta directamente |
| **Tipos de Cambio** | Módulo Django | Dashboard que consume `exchange-rate-service` |
| **Bolsa** | Módulo Django | Dashboard que consume `market-info-service` |
| **Pulsar** | Infraestructura | Sistema de mensajería (Apache Pulsar), dashboard solo visualiza |
| **Tests** | Herramienta | Dashboard para ejecutar pytest |
| **Swagger API** | Documentación | Interfaz de documentación de la API REST |

---

## 🔄 Flujo de Comunicación

```
┌─────────────────────────────────────────────────────────┐
│              Django (Monolito Principal)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Gráficos │  │ Tipos    │  │  Bolsa   │  │ Tests   │ │
│  │ (Directo)│  │ Cambio   │  │ (Cliente)│  │(Ejecuta)│ │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └─────────┘ │
│                     │              │                     │
│                     ▼              ▼                     │
│            ┌─────────────────────────────┐              │
│            │   Cliente HTTP (Django)      │              │
│            └───────────┬─────────────────┘              │
└────────────────────────┼────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ exchange-rate│ │ market-info  │ │ docs-generator│
│ -service     │ │ -service     │ │               │
│ (5100)       │ │ (5200)       │ │ (5001)        │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🎯 Para el Video

**Estructura sugerida:**

1. **Introducción**: Explicar que NUAM tiene 3 microservicios reales + módulos Django
2. **Microservicios** (3):
   - docs-generator (Reportes)
   - exchange-rate-service (Tipos de Cambio)
   - market-info-service (Bolsa)
3. **Módulos Django** (4):
   - Gráficos (standalone)
   - Tipos de Cambio (consume microservicio)
   - Bolsa (consume microservicio)
   - Tests (ejecuta pytest)
4. **Herramientas/Infraestructura** (2):
   - Pulsar (mensajería)
   - Swagger API (documentación)
5. **Conclusión**: Resumir arquitectura híbrida (monolito + microservicios)

