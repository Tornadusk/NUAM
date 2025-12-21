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

**⚠️ Importante - Exportación de Gráficos:**
- **NO usa** el microservicio `docs-generator`
- Exporta **directamente** desde Django usando `microservicio/utils/exportador.py`
- Solo los **reportes del mantenedor** usan `docs-generator`

---

## 💱 2. Tipos de Cambio

**¿Qué es?**
- **Módulo del monolito Django** (vista + template) que **consume** un microservicio
- **NO es un microservicio** - es solo la interfaz/cliente que usa el microservicio

**⚠️ Importante:** "Módulo que consume un microservicio" significa:
- Es código Django (vistas, templates, URLs) dentro del monolito
- Llama por HTTP a un microservicio externo (`exchange-rate-service`)
- El microservicio es el servicio independiente (FastAPI en Docker, puerto 5100)
- El módulo Django es solo el cliente/frontend que consume ese servicio

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
- Vista Django: `microservicio/views/tipos_cambio.py` ← **Módulo Django (cliente)**
- Template: `templates/microservicio/tipos_cambio/dashboard.html`
- URL: `/microservicio/tipos-cambio/`
- Cliente microservicio: `microservicio/services/exchange_rate_client.py` ← **Cliente HTTP**
- **Microservicio usado**: `services/exchange-rate-service/` (FastAPI, puerto 5100) ← **Este SÍ es microservicio**

**Arquitectura:**
```
┌─────────────────────────────────┐
│  Módulo Django (Cliente)        │
│  - Vista tipos_cambio.py        │  ← NO es microservicio
│  - Template dashboard.html      │     (es parte del monolito)
│  - Cliente HTTP                 │
└──────────────┬──────────────────┘
               │ HTTP POST
               ▼
┌─────────────────────────────────┐
│  exchange-rate-service          │  ← SÍ es microservicio
│  (FastAPI, Docker, puerto 5100) │     (servicio independiente)
│  - Consulta APIs externas       │
│  - Si APIs fallan: devuelve     │     (servicio sigue funcionando,
│    error en respuesta           │      pero sin datos nuevos)
└─────────────────────────────────┘
               │
               ▼
     ┌─────────────────┐
     │ APIs Externas   │  ← Pueden fallar (sin internet, límites, etc.)
     │ - ExchangeRate  │     Pero el microservicio SÍ funciona
     │ - Fixer.io      │
     │ - Banco Central │
     └─────────────────┘
```

**⚠️ Importante - ¿Si las APIs externas fallan, el microservicio no funciona?**
- ✅ **SÍ, el microservicio sigue funcionando** (está corriendo, responde a requests HTTP)
- ❌ **Las APIs externas pueden fallar** (sin internet, límites de rate, servidor caído)
- 📊 **Resultado**: El microservicio devuelve una respuesta con errores, pero **sigue operativo**
- 🔄 Django puede manejar estos errores y mostrar mensajes al usuario

**¿Cumple como microservicio?**
- ❌ **NO**, el módulo Django NO es microservicio
- ✅ El **microservicio** es `exchange-rate-service` (servicio independiente en Docker)

---

## 📈 3. Bolsa (Mercados)

**¿Qué es?**
- **Módulo del monolito Django** (vista + template) que **consume** un microservicio
- **NO es un microservicio** - es solo la interfaz/cliente que usa el microservicio

**⚠️ Importante:** "Módulo que consume un microservicio" significa:
- Es código Django (vistas, templates, URLs) dentro del monolito
- Llama por HTTP a un microservicio externo (`market-info-service`)
- El microservicio es el servicio independiente (FastAPI en Docker, puerto 5200)
- El módulo Django es solo el cliente/frontend que consume ese servicio

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
- Vista Django: `microservicio/views/mercados.py` ← **Módulo Django (cliente)**
- Template: `templates/microservicio/mercados/dashboard.html`
- URL: `/microservicio/mercados/`
- Cliente microservicio: `microservicio/services/market_info_client.py` ← **Cliente HTTP**
- **Microservicio usado**: `services/market-info-service/` (FastAPI, puerto 5200) ← **Este SÍ es microservicio**

**Arquitectura:**
```
┌─────────────────────────────────┐
│  Módulo Django (Cliente)        │
│  - Vista mercados.py            │  ← NO es microservicio
│  - Template dashboard.html      │     (es parte del monolito)
│  - Cliente HTTP                 │
└──────────────┬──────────────────┘
               │ HTTP GET
               ▼
┌─────────────────────────────────┐
│  market-info-service            │  ← SÍ es microservicio
│  (FastAPI, Docker, puerto 5200) │     (servicio independiente)
│  - Consulta APIs externas       │
│  - Si APIs fallan: devuelve     │     (servicio sigue funcionando,
│    datos simulados (fallback)   │      pero con datos simulados)
└─────────────────────────────────┘
               │
               ▼
     ┌─────────────────┐
     │ APIs Externas   │  ← Pueden fallar (sin internet, límites, etc.)
     │ - Yahoo Finance │     Pero el microservicio SÍ funciona
     │ - Alpha Vantage │     y devuelve datos simulados
     └─────────────────┘
```

**⚠️ Importante - ¿Si las APIs externas fallan, el microservicio no funciona?**
- ✅ **SÍ, el microservicio sigue funcionando** (está corriendo, responde a requests HTTP)
- ❌ **Las APIs externas pueden fallar** (sin internet, límites de rate, servidor caído)
- 📊 **Resultado**: El microservicio devuelve **datos simulados** (fallback inteligente)
- 🎯 **Ventaja**: El servicio nunca "cae", siempre devuelve algo útil aunque sean datos simulados

**¿Cumple como microservicio?**
- ❌ **NO**, el módulo Django NO es microservicio
- ✅ El **microservicio** es `market-info-service` (servicio independiente en Docker)

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

**⚠️ IMPORTANTE - Diferencia entre exportaciones:**

1. **Exportación de Gráficos** (desde dashboard "Gráficos"):
   - ❌ **NO usa** el microservicio `docs-generator`
   - ✅ Exporta directamente desde Django usando `microservicio/utils/exportador.py`
   - Formato: CSV, Excel, PDF, HTML
   - Vista: `microservicio/views/graficos.py` → `api_exportar_grafico()`

2. **Exportación de Reportes** (desde pestaña "Reportes" del mantenedor):
   - ✅ **SÍ usa** el microservicio `docs-generator`
   - Formato: PDF, Excel, CSV (con formato profesional)
   - Vista: `calificaciones/views.py` → `exportar_datos_view()`

**Resumen:**
- Gráficos → Exportación directa Django (NO microservicio)
- Reportes del mantenedor → Microservicio `docs-generator` (SÍ microservicio)

---

## 📊 Resumen: Microservicios vs Módulos

### ✅ Microservicios Reales (3)

**¿Qué hace que algo sea un microservicio?**
- Servicio independiente (corre en su propio proceso/contenedor)
- Tiene su propio puerto
- Tiene Dockerfile propio
- Se comunica por HTTP/red con otros servicios
- Puede escalarse/desplegarse independientemente

1. **`docs-generator`** (puerto 5001)
   - Genera reportes PDF/Excel/CSV desde el mantenedor
   - FastAPI + Docker
   - Comunicación: HTTP
   - **Ubicación**: `services/docs-generator/`

2. **`exchange-rate-service`** (puerto 5100)
   - Consulta tipos de cambio de APIs externas
   - FastAPI + Docker
   - Comunicación: HTTP
   - **Ubicación**: `services/exchange-rate-service/`

3. **`market-info-service`** (puerto 5200)
   - Consulta información de bolsas de valores
   - FastAPI + Docker
   - Comunicación: HTTP
   - **Ubicación**: `services/market-info-service/`

### ❌ NO son Microservicios

**¿Por qué NO son microservicios?**
- Son código Django (vistas, templates) dentro del monolito
- No tienen Dockerfile propio
- No tienen puerto independiente
- Corren dentro del proceso de Django

| Módulo | Tipo | Descripción | ¿Consume microservicio? |
|--------|------|-------------|------------------------|
| **Gráficos** | Módulo Django | Dashboard con visualizaciones, exporta directamente (usa `exportador.py`, NO `docs-generator`) | ❌ NO |
| **Tipos de Cambio** | Módulo Django | Dashboard que **consume** `exchange-rate-service` | ✅ SÍ (consume `exchange-rate-service`) |
| **Bolsa** | Módulo Django | Dashboard que **consume** `market-info-service` | ✅ SÍ (consume `market-info-service`) |
| **Pulsar** | Infraestructura | Sistema de mensajería (Apache Pulsar), dashboard solo visualiza | ❌ NO (solo visualiza) |
| **Tests** | Herramienta | Dashboard para ejecutar pytest | ❌ NO |
| **Swagger API** | Documentación | Interfaz de documentación de la API REST | ❌ NO |

### 🔑 Aclaración Importante

**"Módulo que consume un microservicio" NO significa que sea microservicio:**

- ❌ **NO es microservicio**: El módulo Django (vista/template) que llama al microservicio
- ✅ **SÍ es microservicio**: El servicio independiente (FastAPI en Docker) que es llamado

**Ejemplo con Tipos de Cambio:**
- ❌ `microservicio/views/tipos_cambio.py` → **NO es microservicio** (es módulo Django)
- ✅ `services/exchange-rate-service/` → **SÍ es microservicio** (servicio independiente)

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

---

## ❓ FAQ: Preguntas Frecuentes

### ¿Los datos simulados son APIs también?

**Respuesta corta:** NO, los datos simulados **NO son APIs externas**. Son **funciones dentro del código** que generan datos de prueba.

**Explicación:**

Los datos simulados son **código hardcodeado** dentro del microservicio. Por ejemplo, en `market-info-service/providers.py`:

```python
def _simulados_chile() -> MarketSummaryResponse:
    indices = [
        IndexItem(
            simbolo="IPSA.SN",
            nombre="IPSA - Santiago",
            pais="CHL",
            ultimo=5000.12,  # ← Valor hardcodeado en el código
            cambio=25.3,
            cambio_pct=0.51,
            moneda="CLP",
            volumen=12_345_678,
            hora=datetime.now(),
        ),
    ]
    return MarketSummaryResponse(
        success=True,
        pais="CHL",
        indices=indices,
        fuente_real=False,  # ← Marca que NO es de API real
        proveedor="simulado",  # ← Indica que es simulado
        mensaje="Datos simulados de la Bolsa de Santiago (sin conexión a API real).",
    )
```

**Flujo:**
1. El microservicio intenta llamar a una API externa (Yahoo Finance, Alpha Vantage)
2. Si la API falla → llama a la función `_simulados_chile()` (código interno)
3. Devuelve datos hardcodeados con `fuente_real=False` y `proveedor="simulado"`

**Resumen:**
- ❌ Datos simulados **NO son APIs externas**
- ✅ Son **funciones dentro del código** del microservicio
- ✅ Se usan como **fallback** cuando las APIs reales fallan
- ✅ Permiten que el servicio siempre devuelva algo útil

---

### ¿Si las APIs externas fallan, el microservicio no está funcionando?

**Respuesta corta:** NO, el microservicio **SÍ está funcionando**, solo que las APIs externas fallaron.

**Explicación:**

Hay que diferenciar dos cosas:

1. **Estado del microservicio** (¿está corriendo y respondiendo?)
   - ✅ El microservicio está funcionando si:
     - El contenedor Docker está corriendo
     - Responde a requests HTTP (puerto 5100 o 5200)
     - Devuelve respuestas (aunque sean errores o datos simulados)

2. **Estado de las APIs externas** (¿pudieron obtener datos reales?)
   - ❌ Las APIs externas pueden fallar por:
     - Sin internet
     - Límites de rate (demasiadas peticiones)
     - Servidor de la API caído
     - API keys inválidas o expiradas
     - Timeouts

**Comportamiento de cada microservicio:**

#### `exchange-rate-service` (Tipos de Cambio):
- ✅ **SÍ funciona** aunque las APIs externas fallen
- 📊 Devuelve una respuesta con `success=false` y lista de errores por proveedor
- 🔄 Django puede manejar estos errores y mostrar mensajes al usuario
- 💾 No se guardan datos nuevos en la BD si todas las APIs fallan

#### `market-info-service` (Bolsa):
- ✅ **SÍ funciona** aunque las APIs externas fallen
- 📊 Devuelve **datos simulados** (fallback inteligente)
- 🎯 El servicio **nunca "cae"**, siempre devuelve algo útil
- 🏷️ Marca `fuente_real=False` y `proveedor='simulado'` cuando usa datos simulados
- ✅ Django puede mostrar al usuario que son datos simulados

**Cómo verificar si un microservicio está funcionando:**

```bash
# Verificar que el contenedor está corriendo
docker ps | grep exchange-rate-service
docker ps | grep market-info-service

# Probar el endpoint de salud
curl http://localhost:5100/health  # exchange-rate-service
curl http://localhost:5200/health  # market-info-service

# Debería responder: {"status": "ok", ...}
```

**Resumen:**
- El microservicio funciona si está corriendo y respondiendo a requests
- Las APIs externas pueden fallar independientemente
- El microservicio maneja estos errores elegantemente (errores o datos simulados)

---

### ¿Los datos simulados solo se muestran si el microservicio está activo?

**Respuesta corta:** SÍ, los datos simulados **solo se pueden mostrar si el microservicio está activo y corriendo**.

**Explicación:**

Los datos simulados están dentro del código del microservicio (`services/market-info-service/providers.py`). Por lo tanto:

#### ✅ Si el microservicio ESTÁ activo:
```
Django → microservicio (corriendo) → API externa falla → Función _simulados_chile()
                                                          ↓
                                                    Devuelve datos simulados ✅
```

#### ❌ Si el microservicio NO está activo:
```
Django → microservicio (NO corriendo) → Error de conexión (ConnectionError)
                                         ↓
                                    Django devuelve error 502 Bad Gateway ❌
                                    No se pueden obtener datos (ni reales ni simulados)
```

**Código que maneja esto:**

En `microservicio/services/market_info_client.py`:
```python
try:
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()  # ← Aquí obtendríamos datos reales o simulados
except requests.exceptions.RequestException as exc:
    return {
        "success": False,
        "error": f"Error al llamar a market-info-service: {exc}",  # ← Error si microservicio no está activo
        "mercados": [],
    }
```

**Diferencia clave:**

| Situación | Microservicio | API Externa | Resultado |
|-----------|---------------|-------------|-----------|
| Todo funciona | ✅ Activo | ✅ Funciona | Datos reales |
| API externa falla | ✅ Activo | ❌ Falla | **Datos simulados** (fallback) |
| Microservicio caído | ❌ Inactivo | - | Error 502 (no hay datos simulados disponibles) |

**Resumen:**
- ✅ Los datos simulados están dentro del código del microservicio
- ✅ Solo están disponibles si el microservicio está corriendo
- ❌ Si el microservicio no está activo, Django obtiene un error de conexión, no datos simulados
- 🔄 Los datos simulados son un fallback cuando las APIs externas fallan, NO cuando el microservicio está caído

---

## 🔍 ¿Los microservicios son solo llamadas de API?

**Respuesta corta:** NO, hacen mucho más que solo llamar a APIs externas.

### Funciones adicionales de los microservicios:

#### 1. **`exchange-rate-service`** (Tipos de Cambio)

**No solo llama a APIs, también:**

✅ **Agrega múltiples proveedores:**
- Consulta 3 proveedores diferentes (ExchangeRate API, Fixer.io, Banco Central de Chile)
- Consolida todos los resultados en una sola respuesta

✅ **Normaliza formatos:**
- Cada API externa devuelve datos en formato diferente
- El microservicio los convierte a un formato uniforme (`TipoCambioItem`)

✅ **Convierte monedas base:**
- Fixer.io usa EUR como base, el microservicio convierte a USD si es necesario
- Ejemplo: `tasa_final = tasa_desde_eur / eur_to_usd`

✅ **Maneja errores por proveedor:**
- Si un proveedor falla, sigue intentando con los otros
- Devuelve lista de errores específicos por proveedor
- Agrega metadatos (qué proveedores se consultaron, fecha, etc.)

✅ **Valida y filtra:**
- Valida que las monedas sean válidas
- Filtra solo las monedas solicitadas
- Maneja casos especiales (Banco Central solo soporta USD/CLP)

**Código ejemplo:**
```python
# En main.py - NO es solo llamar a una API
proveedores = crear_proveedores(...)  # Crea múltiples proveedores

tipos_cambio_items = []
errores = {}

for proveedor in proveedores:
    resultado = proveedor.obtener_tipos_cambio(...)  # Llama a cada API
    if not resultado.get("exito"):
        errores[proveedor.codigo] = resultado.get("error")  # Registra error
        continue
    
    # Normaliza los datos de cada proveedor
    for tc in resultado.get("tipos_cambio", []):
        tipos_cambio_items.append(TipoCambioItem(...))  # Formato uniforme

# Agrega metadatos
metadata = {
    "proveedores_consultados": [p.codigo for p in proveedores],
    "fecha_consulta": date.today().isoformat(),
}

return ActualizarResponse(success=success, tipos_cambio=tipos_cambio_items, 
                         errores=errores, metadata=metadata)
```

#### 2. **`market-info-service`** (Bolsa)

**No solo llama a APIs, también:**

✅ **Implementa fallback inteligente:**
- Si Yahoo Finance falla → intenta Alpha Vantage
- Si Alpha Vantage falla → usa datos simulados
- El servicio nunca "cae", siempre devuelve algo útil

✅ **Normaliza datos de diferentes APIs:**
- Yahoo Finance y Alpha Vantage tienen formatos diferentes
- El microservicio convierte todo a `IndexItem` uniforme

✅ **Mapea símbolos:**
- Diferentes APIs usan diferentes símbolos (ej: `^IPSA` vs `IPSA`)
- El microservicio mapea correctamente según el proveedor

✅ **Genera datos históricos:**
- Implementa lógica para generar series históricas simuladas
- Función `obtener_historial_simulado()` que crea datos coherentes

✅ **Maneja rate limiting:**
- Detecta errores HTTP 429 (Too Many Requests)
- Proporciona mensajes de error específicos
- Cambia automáticamente a datos simulados si hay límites

✅ **Selección de proveedor:**
- Permite elegir qué proveedor usar (yahoo, alpha_vantage, simulado)
- Rutea las solicitudes según el proveedor seleccionado

**Código ejemplo:**
```python
# En providers.py - NO es solo llamar a una API
def obtener_mercado_por_pais(pais: str, proveedor: str):
    if proveedor == "simulado":
        return _simulados_chile()  # Lógica de fallback
    
    # Intenta API real
    quotes, error = _llamar_api_yahoo(simbolos)
    
    if error:
        return _simulados_chile()  # Fallback si falla
    
    # Normaliza datos de Yahoo Finance
    indices = []
    for symbol, q in quotes.items():
        indices.append(IndexItem(
            ultimo=float(q.get("regularMarketPrice") or 0),
            cambio=float(q.get("regularMarketChange") or 0),
            # ... normaliza formato de Yahoo a nuestro formato
        ))
    
    return MarketSummaryResponse(
        success=True,
        indices=indices,
        fuente_real=True,
        proveedor="yahoo"
    )
```

### Resumen:

| Microservicio | ¿Solo llama API? | ¿Qué más hace? |
|---------------|------------------|----------------|
| **exchange-rate-service** | ❌ NO | Agrega múltiples proveedores, normaliza formatos, convierte monedas, maneja errores, agrega metadatos |
| **market-info-service** | ❌ NO | Implementa fallback, normaliza datos, mapea símbolos, genera históricos, maneja rate limiting |

**Conclusión:**
- Los microservicios tienen **lógica de negocio** importante
- No son solo "proxies" a APIs externas
- Implementan **patrones de diseño** (Strategy para proveedores, Fallback, Normalización)
- **Agregan valor** más allá de solo hacer llamadas HTTP

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
5. **FAQ**: Aclarar diferencia entre microservicio funcionando vs APIs externas fallando
6. **Conclusión**: Resumir arquitectura híbrida (monolito + microservicios)

