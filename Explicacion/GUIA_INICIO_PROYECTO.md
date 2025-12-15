# Guía de Inicio del Proyecto NUAM

Esta guía explica cómo iniciar correctamente el proyecto NUAM, qué hace cada Docker Compose, y qué servicios necesitan Docker.

## 📋 Índice

- [¿Qué hace cada Docker Compose?](#qué-hace-cada-docker-compose)
- [Microservicios y sus Dependencias](#microservicios-y-sus-dependencias)
- [Orden Correcto de Inicio](#orden-correcto-de-inicio)
- [Checklist de Inicio](#checklist-de-inicio)
- [Preguntas Frecuentes](#preguntas-frecuentes)

---

## ¿Qué hace cada Docker Compose?

NUAM tiene **3 archivos Docker Compose** diferentes, cada uno con un propósito específico:

### 1. `docker-compose.yml` (RAÍZ - ⭐ Principal)

**Ubicación:** En la raíz del proyecto (`/docker-compose.yml`)

**Propósito:** Servicios principales para desarrollo completo

**Contiene:**
- `pulsar`: Apache Pulsar (sistema de mensajería)
- `docs-generator`: Microservicio FastAPI para generar PDFs/Excel/CSV

**Cuándo usar:**
- ✅ Desarrollo normal cuando necesitas Pulsar + docs-generator
- ✅ Cuando quieres usar el dashboard de Pulsar (`/microservicio/pulsar/`)
- ✅ Cuando necesitas exportar documentos (PDF, Excel, CSV)

**Comando:**
```bash
# Desde la raíz del proyecto
docker-compose up -d
```

**Puertos:**
- `6650`: Pulsar (productores/consumidores)
- `8080`: Pulsar Admin API
- `5001`: docs-generator (microservicio de documentos)

---

### 2. `docker-compose.dev.yml` (RAÍZ - Alternativo)

**Ubicación:** En la raíz del proyecto (`/docker-compose.dev.yml`)

**Propósito:** Versión alternativa para desarrollo con menos memoria

**Contiene:**
- `pulsar`: Apache Pulsar con configuración de memoria reducida

**Cuándo usar:**
- ✅ Si tienes problemas de memoria en Docker Desktop
- ✅ Si solo necesitas Pulsar (no necesitas docs-generator)
- ✅ Para desarrollo ligero

**Comando:**
```bash
# Desde la raíz del proyecto
docker-compose -f docker-compose.dev.yml up -d
```

**Puertos:**
- `6650`: Pulsar (productores/consumidores)
- `8080`: Pulsar Admin API

---

### 3. `services/docker-compose.yml` (CARPETA SERVICES)

**Ubicación:** En la carpeta `services/` (`/services/docker-compose.yml`)

**Propósito:** Solo el microservicio de documentos (sin Pulsar)

**Contiene:**
- `docs-generator`: Microservicio FastAPI

**⚠️ IMPORTANTE:** Este Docker Compose **NO se inicia automáticamente**. Debes ejecutarlo manualmente.

**Cuándo usar:**
- ✅ Si tu compañero está trabajando solo en docs-generator
- ✅ Si no necesitas Pulsar pero sí necesitas generar documentos (reportes del mantenedor)
- ✅ Para desarrollo aislado del microservicio de documentos

**Comando:**
```bash
# Desde la carpeta services/
cd services
docker-compose up -d
```

**Puertos:**
- `5001`: docs-generator (microservicio de documentos)

**¿Para qué se usa docs-generator?**
- ✅ **Reportes del Mantenedor** (`/calificaciones/exportar/<formato>/`) - Exportar calificaciones en PDF, Excel, CSV
- ❌ **NO se usa para gráficos** - El dashboard de gráficos (`/microservicio/graficos/`) genera archivos directamente en Django sin usar este microservicio

---

## Microservicios y sus Dependencias

### Microservicios que **NO necesitan Docker**

Estos microservicios son parte de Django y funcionan directamente con `python manage.py runserver`:

#### 1. **Gráficos** (`/microservicio/graficos/`)
- **URL:** `http://localhost:8000/microservicio/graficos/`
- **Dependencias:** Solo Django + Base de datos
- **Docker:** ❌ No necesario
- **Descripción:** Dashboard de gráficos y métricas de calificaciones
- **Exportación:** Genera archivos (CSV, Excel, PDF, HTML) directamente en Django usando `ExportadorGraficos` - **NO usa docs-generator**

#### 2. **Tipos de Cambio** (`/microservicio/tipos-cambio/`)
- **URL:** `http://localhost:8000/microservicio/tipos-cambio/`
- **Dependencias:** Solo Django + Base de datos
- **Docker:** ❌ No necesario
- **Descripción:** Dashboard de tipos de cambio (CLP, PEN, COP, USD)
- **⚠️ IMPORTANTE:** Requiere inicializar fuentes en la BD (ver `SOLUCION_TIPOS_CAMBIO.md`)

#### 3. **Tests** (`/microservicio/testing/`)
- **URL:** `http://localhost:8000/microservicio/testing/`
- **Dependencias:** Solo Django
- **Docker:** ❌ No necesario
- **Descripción:** Dashboard para ejecutar tests desde la interfaz web

---

### Microservicios que **SÍ necesitan Docker**

Estos microservicios requieren servicios externos corriendo en Docker:

#### 1. **Pulsar Dashboard** (`/microservicio/pulsar/`)
- **URL:** `http://localhost:8000/microservicio/pulsar/`
- **Dependencias:** Django + Pulsar (Docker)
- **Docker:** ✅ Requiere `docker-compose up -d` (usar `docker-compose.yml` de la raíz)
- **Descripción:** Dashboard para visualizar estado de Pulsar, topics y mensajes

#### 2. **docs-generator** (Microservicio FastAPI)
- **URL:** `http://localhost:5001/health`
- **Dependencias:** Docker
- **Docker:** ✅ Requiere `docker-compose up -d` (usar `docker-compose.yml` de la raíz o `services/docker-compose.yml`)
- **Descripción:** Microservicio para generar PDFs, Excel y CSV
- **Uso:** Se llama desde Django cuando exportas **reportes del mantenedor** (`/calificaciones/exportar/<formato>/`)
- **⚠️ NO se usa para gráficos:** El dashboard de gráficos genera archivos directamente en Django sin usar este microservicio
- **⚠️ NO se inicia solo:** Debes ejecutar `docker-compose up -d` manualmente

---

## Orden Correcto de Inicio

### Paso 1: Preparar el Entorno

```bash
# 1. Activar entorno virtual
source venv/bin/activate     # Linux/Mac
# o
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# 2. Verificar que las dependencias estén instaladas
pip install -r requirements.txt
```

### Paso 2: Iniciar Docker (si necesitas Pulsar o docs-generator)

**⚠️ IMPORTANTE:** Solo necesitas Docker si vas a usar:
- Dashboard de Pulsar (`/microservicio/pulsar/`)
- Exportación de documentos (PDF, Excel, CSV)

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que los servicios estén corriendo
docker ps

# Deberías ver:
# - nuam-pulsar (puerto 6650 y 8080)
# - nuam-docs-generator (puerto 5001)
```

**Nota:** Pulsar Admin API puede tardar 30-60 segundos en estar disponible después de iniciar el contenedor.

### Paso 3: Aplicar Migraciones y Cargar Datos Iniciales

```bash
# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales (países, monedas, usuarios, etc.)
python create_data_initial.py
```

### Paso 4: Inicializar Tipos de Cambio (SOLO LA PRIMERA VEZ)

**⚠️ IMPORTANTE:** Este paso es necesario para que el microservicio de tipos de cambio funcione.

```bash
# Crear fuentes de tipos de cambio en la BD
python manage.py inicializar_fuentes_tipos_cambio

# Obtener tipos de cambio desde las APIs externas
python manage.py obtener_tipos_cambio
```

**Ver `SOLUCION_TIPOS_CAMBIO.md` para más detalles.**

### Paso 5: Iniciar Django

**Opción A: HTTP (Desarrollo simple)**
```bash
python manage.py runserver
```

**Opción B: HTTPS (Con certificado SSL)**
```bash
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443
```

**Nota:** Para HTTPS, primero debes generar los certificados (ver `readme.md` sección "Paso 7: Configurar Certificados SSL/HTTPS").

---

## Checklist de Inicio

Usa este checklist para asegurarte de que todo esté configurado correctamente:

### Preparación Básica
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos configurada en `settings.py`
- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Datos iniciales cargados (`python create_data_initial.py`)

### Docker (Solo si necesitas Pulsar/docs-generator)
- [ ] Docker Desktop instalado y corriendo
- [ ] `docker-compose up -d` ejecutado desde la raíz
- [ ] Contenedores corriendo (`docker ps` muestra `nuam-pulsar` y `nuam-docs-generator`)
- [ ] Pulsar Admin API disponible (esperar 60 segundos y verificar con `curl http://localhost:8080/admin/v2/brokers/health`)

### Microservicio de Tipos de Cambio (Solo si lo vas a usar)
- [ ] Fuentes inicializadas (`python manage.py inicializar_fuentes_tipos_cambio`)
- [ ] Tipos de cambio obtenidos (`python manage.py obtener_tipos_cambio`)
- [ ] Dashboard accesible en `/microservicio/tipos-cambio/`

### Django
- [ ] Django corriendo (`runserver` o `runserver_plus`)
- [ ] Aplicación accesible en `http://localhost:8000/` o `https://127.0.0.1:8443/`
- [ ] Login funcionando (usuario: `admin`, contraseña: `admin123`)

---

## Preguntas Frecuentes

### ¿Cuál Docker Compose debo usar?

**Respuesta corta:** Usa `docker-compose.yml` de la raíz del proyecto.

**Respuesta detallada:**
- **Desarrollo normal:** `docker-compose.yml` (raíz) - Tiene Pulsar + docs-generator
- **Problemas de memoria:** `docker-compose.dev.yml` (raíz) - Solo Pulsar con menos memoria
- **Solo docs-generator:** `services/docker-compose.yml` - Solo el microservicio de documentos

### ¿Necesito Docker para iniciar el proyecto?

**No necesariamente.** Solo necesitas Docker si vas a usar:
- Dashboard de Pulsar (`/microservicio/pulsar/`)
- Exportación de documentos (PDF, Excel, CSV)

Los demás microservicios (Gráficos, Tipos de Cambio, Tests) funcionan sin Docker.

### ¿Por qué el microservicio de tipos de cambio no muestra datos?

**Causa:** No se han inicializado las fuentes en la base de datos ni se han obtenido tipos de cambio.

**Solución:** Ejecuta:
```bash
python manage.py inicializar_fuentes_tipos_cambio
python manage.py obtener_tipos_cambio
```

Ver `SOLUCION_TIPOS_CAMBIO.md` para más detalles.

### ¿Puedo usar solo `runserver` sin HTTPS?

**Sí.** HTTPS es opcional para desarrollo. Solo necesitas HTTPS si:
- Quieres probar la funcionalidad de certificados SSL
- Estás preparando para producción
- Necesitas cumplir con requisitos de seguridad específicos

### ¿Qué pasa si Docker no está corriendo?

**Depende del microservicio:**
- **Gráficos, Tipos de Cambio, Tests:** Funcionan normalmente
- **Pulsar Dashboard:** Mostrará "Pulsar no disponible" pero Django seguirá funcionando
- **Exportación de documentos:** Fallará al intentar generar PDFs/Excel/CSV, pero Django usará métodos alternativos (fallback)

### ¿Cómo verifico que todo está funcionando?

1. **Docker:** `docker ps` debe mostrar los contenedores corriendo
2. **Django:** Accede a `http://localhost:8000/` y deberías ver la página de inicio
3. **Pulsar:** Accede a `/microservicio/pulsar/` y debería mostrar "ONLINE"
4. **Tipos de Cambio:** Accede a `/microservicio/tipos-cambio/` y debería mostrar datos

---

## Diagrama de Dependencias

```
NUAM Project
│
├── Django (runserver)
│   │
│   ├── Microservicio Gráficos ──────────────┐
│   ├── Microservicio Tipos de Cambio ───────┤ No necesitan Docker
│   └── Microservicio Tests ─────────────────┘
│
└── Docker (docker-compose up -d)
    │
    ├── Pulsar (puerto 6650, 8080)
    │   └── Microservicio Pulsar Dashboard ────┐ Necesitan Docker
    │                                           │
    └── docs-generator (puerto 5001) ──────────┘
        └── Exportación de documentos (PDF/Excel/CSV)
```

---

## Referencias

- **README Principal:** `readme.md`
- **Solución Tipos de Cambio:** `Explicacion/SOLUCION_TIPOS_CAMBIO.md`
- **Configuración Tipos de Cambio:** `microservicio/docs/CONFIGURACION_TIPOS_CAMBIO.md`
- **Troubleshooting Pulsar:** `microservicio/docs/TROUBLESHOOTING_PULSAR.md`

