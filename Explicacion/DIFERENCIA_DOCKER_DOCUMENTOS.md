# Diferencia Entre los Dos Docker Compose de Documentos

NUAM tiene **dos archivos Docker Compose** que incluyen `docs-generator`. Esta guía explica las diferencias y cuándo usar cada uno.

---

## Comparación Rápida

| Aspecto | `docker-compose.yml` (RAÍZ) | `services/docker-compose.yml` |
|---------|----------------------------|-------------------------------|
| **Ubicación** | Raíz del proyecto | Carpeta `services/` |
| **Contiene** | Pulsar + docs-generator | Solo docs-generator |
| **Puertos** | 6650, 8080 (Pulsar) + 5001 (docs-generator) | Solo 5001 (docs-generator) |
| **Memoria** | Más memoria (2GB para Pulsar) | Menos memoria (solo docs-generator) |
| **Cuándo usar** | Desarrollo completo | Solo desarrollo de docs-generator |

---

## 1. `docker-compose.yml` (RAÍZ) - Completo

**Ubicación:** `/docker-compose.yml` (en la raíz del proyecto)

**Contiene:**
```yaml
services:
  pulsar:
    # Apache Pulsar (puertos 6650, 8080)
  
  docs-generator:
    # Microservicio de documentos (puerto 5001)
```

**Características:**
- ✅ **Incluye Pulsar** (sistema de mensajería)
- ✅ **Incluye docs-generator** (microservicio de documentos)
- ✅ **Configuración completa** para desarrollo completo
- ✅ **Red compartida** (`nuam-network`) entre servicios
- ✅ **Dependencias configuradas** (docs-generator depende de Pulsar)

**Memoria requerida:**
- Pulsar: 2GB límite, 1GB reservado
- docs-generator: Sin límite específico (usa lo que necesita)

**Puertos expuestos:**
- `6650`: Pulsar (productores/consumidores)
- `8080`: Pulsar Admin API
- `5001`: docs-generator (microservicio de documentos)

**Comando para iniciar:**
```bash
# Desde la raíz del proyecto
docker-compose up -d
```

**Cuándo usar:**
- ✅ Desarrollo completo de NUAM
- ✅ Necesitas Pulsar Y docs-generator
- ✅ Quieres probar integración completa
- ✅ Tienes suficiente memoria (mínimo 2GB para Docker)

---

## 2. `services/docker-compose.yml` - Solo Documentos

**Ubicación:** `/services/docker-compose.yml` (dentro de la carpeta `services/`)

**Contiene:**
```yaml
services:
  docs-generator:
    # Solo microservicio de documentos (puerto 5001)
```

**Características:**
- ✅ **Solo docs-generator** (sin Pulsar)
- ✅ **Menor consumo de memoria** (no necesita Pulsar)
- ✅ **Inicio más rápido** (solo un servicio)
- ✅ **Ideal para desarrollo aislado** del microservicio de documentos

**Memoria requerida:**
- docs-generator: Sin límite específico (usa lo que necesita)
- **Total:** Mucho menos que el docker-compose completo

**Puertos expuestos:**
- `5001`: docs-generator (microservicio de documentos)

**Comando para iniciar:**
```bash
# Opción 1: Desde la carpeta services/
cd services
docker-compose up -d

# Opción 2: Desde la raíz del proyecto
docker-compose -f services/docker-compose.yml up -d
```

**Cuándo usar:**
- ✅ Solo necesitas generar documentos (reportes del mantenedor)
- ✅ NO necesitas Pulsar
- ✅ Tienes poca memoria disponible
- ✅ Estás desarrollando solo el microservicio docs-generator
- ✅ Quieres un inicio más rápido

---

## Comparación Detallada

### Configuración de Servicios

**`docker-compose.yml` (RAÍZ):**
```yaml
services:
  pulsar:
    image: apachepulsar/pulsar:3.2.0
    container_name: nuam-pulsar
    ports:
      - "6650:6650"
      - "8080:8080"
    mem_limit: 2g
    mem_reservation: 1g
    # ... más configuración
  
  docs-generator:
    build: ./services/docs-generator
    container_name: nuam-docs-generator
    ports:
      - "5001:5000"
    depends_on:
      - pulsar  # Depende de Pulsar
    # ... más configuración
```

**`services/docker-compose.yml`:**
```yaml
services:
  docs-generator:
    build: ./services/docs-generator
    ports:
      - "5001:5000"
    # NO tiene dependencias
    # NO tiene Pulsar
```

### Diferencias Clave

1. **Dependencias:**
   - **Raíz:** docs-generator depende de Pulsar (`depends_on: - pulsar`)
   - **Services:** No tiene dependencias

2. **Redes:**
   - **Raíz:** Ambos servicios en la misma red (`nuam-network`)
   - **Services:** Solo docs-generator (red por defecto)

3. **Memoria:**
   - **Raíz:** ~2GB+ (Pulsar + docs-generator)
   - **Services:** ~200-500MB (solo docs-generator)

4. **Tiempo de inicio:**
   - **Raíz:** ~60-90 segundos (Pulsar tarda en iniciar)
   - **Services:** ~5-10 segundos (solo docs-generator)

---

## ¿Cuál Debo Usar?

### Usa `docker-compose.yml` (RAÍZ) si:

- ✅ Necesitas **Pulsar Y docs-generator**
- ✅ Estás desarrollando **funcionalidades completas** de NUAM
- ✅ Quieres probar la **integración completa**
- ✅ Tienes **suficiente memoria** (mínimo 2GB para Docker)
- ✅ Necesitas el **dashboard de Pulsar** (`/microservicio/pulsar/`)

**Ejemplo de uso:**
```bash
# Desarrollo completo
docker-compose up -d
# Inicia: Pulsar + docs-generator
# Puedes usar: Dashboard Pulsar + Reportes del Mantenedor
```

---

### Usa `services/docker-compose.yml` si:

- ✅ **Solo necesitas** generar documentos (reportes del mantenedor)
- ✅ **NO necesitas** Pulsar
- ✅ Tienes **poca memoria** disponible
- ✅ Estás desarrollando **solo el microservicio** docs-generator
- ✅ Quieres un **inicio más rápido**

**Ejemplo de uso:**
```bash
# Solo documentos
cd services
docker-compose up -d
# Inicia: Solo docs-generator
# Puedes usar: Reportes del Mantenedor (pero NO dashboard Pulsar)
```

---

## Escenarios de Uso

### Escenario 1: Desarrollo Completo
```bash
# Necesitas todo: Pulsar + docs-generator
docker-compose up -d  # Desde la raíz
```
**Resultado:** Pulsar (6650, 8080) + docs-generator (5001) corriendo

---

### Escenario 2: Solo Reportes del Mantenedor
```bash
# Solo necesitas exportar documentos
cd services
docker-compose up -d
```
**Resultado:** Solo docs-generator (5001) corriendo

---

### Escenario 3: Solo Pulsar (sin documentos)
```bash
# Solo necesitas Pulsar
docker-compose -f docker-compose.dev.yml up -d  # Desde la raíz
```
**Resultado:** Solo Pulsar (6650, 8080) corriendo

---

## Verificación

### Verificar qué está corriendo:

```bash
# Ver todos los contenedores
docker ps

# Ver solo docs-generator
docker ps | grep docs-generator

# Ver solo Pulsar
docker ps | grep pulsar
```

### Verificar puertos:

```bash
# Verificar docs-generator
curl http://localhost:5001/health
# Debe responder: {"status": "ok", "service": "docs-generator"}

# Verificar Pulsar (solo si usaste docker-compose.yml de la raíz)
curl http://localhost:8080/admin/v2/brokers/health
# Debe responder: {"status": "ok"} o similar
```

---

## Resumen Visual

```
NUAM Docker Compose Options
│
├── docker-compose.yml (RAÍZ) ⭐ RECOMENDADO
│   ├── pulsar (6650, 8080)
│   └── docs-generator (5001)
│   └── ✅ Desarrollo completo
│
├── services/docker-compose.yml
│   └── docs-generator (5001)
│   └── ✅ Solo documentos (sin Pulsar)
│
└── docker-compose.dev.yml
    └── pulsar (6650, 8080)
    └── ✅ Solo Pulsar (sin docs-generator)
```

---

## Recomendación

**Para la mayoría de casos:** Usa `docker-compose.yml` de la raíz.

**Razones:**
- ✅ Tiene todo lo necesario (Pulsar + docs-generator)
- ✅ Configuración completa y probada
- ✅ Permite usar todas las funcionalidades de NUAM
- ✅ Es el archivo principal del proyecto

**Solo usa `services/docker-compose.yml` si:**
- Tienes problemas de memoria
- Solo necesitas documentos y NO necesitas Pulsar
- Estás desarrollando específicamente el microservicio docs-generator

---

## Referencias

- **Guía de Inicio:** `Explicacion/GUIA_INICIO_PROYECTO.md`
- **Aclaración Docker Documentos:** `Explicacion/ACLARACION_DOCKER_DOCUMENTOS.md`
- **README Principal:** `readme.md`

