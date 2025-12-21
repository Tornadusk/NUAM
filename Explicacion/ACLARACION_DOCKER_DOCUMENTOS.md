# Aclaración: Docker de Documentos y su Uso

## Preguntas Frecuentes

### ¿El docker de documentos es para los gráficos?

**❌ NO.** El microservicio `docs-generator` (puerto 5001) **NO se usa para el dashboard de gráficos**.

**Dashboard de Gráficos** (`/microservicio/graficos/`):
- Genera archivos (CSV, Excel, PDF, HTML) **directamente en Django**
- Usa la clase `ExportadorGraficos` en `microservicio/utils/exportador.py`
- **NO necesita Docker**
- **NO llama al microservicio docs-generator**

**Reportes del Mantenedor** (`/calificaciones/exportar/<formato>/`):
- **SÍ usa** el microservicio `docs-generator` (puerto 5001)
- Se llama desde `calificaciones/views.py` → `exportar_datos_view()`
- **SÍ necesita Docker** corriendo

---

### ¿El docker de services es para reportes?

**✅ SÍ, parcialmente.** El docker en `services/docker-compose.yml` contiene `docs-generator`, que se usa para:

- ✅ **Reportes del Mantenedor** (`/calificaciones/exportar/<formato>/`)
  - Exportar calificaciones en PDF, Excel, CSV
  - Vista: `calificaciones/views.py` → `exportar_datos_view()`

- ❌ **NO para gráficos** - Los gráficos generan archivos directamente en Django

---

### ¿El docker de services se inicia solo?

**❌ NO.** El docker en `services/docker-compose.yml` **NO se inicia automáticamente**.

**Debes iniciarlo manualmente:**

```bash
# Opción 1: Desde la carpeta services/
cd services
docker-compose up -d

# Opción 2: Desde la raíz del proyecto (especificar el archivo)
docker-compose -f services/docker-compose.yml up -d
```

**Verificar que esté corriendo:**
```bash
docker ps | grep docs-generator
# Deberías ver: nuam-docs-generator (o docs-generator) corriendo en puerto 5001
```

---

## Resumen Visual

```
NUAM Project
│
├── Dashboard de Gráficos (/microservicio/graficos/)
│   └── Exportación: ExportadorGraficos (Django directo)
│       └── ❌ NO usa docs-generator
│
└── Reportes del Mantenedor (/calificaciones/exportar/<formato>/)
    └── Exportación: exportar_datos_view() (Django)
        └── ✅ SÍ usa docs-generator (puerto 5001)
            └── Requiere Docker corriendo
```

---

## ¿Qué Docker Compose Usar?

### Para Reportes del Mantenedor (docs-generator):

**Opción 1: Docker Compose de la raíz (recomendado)**
```bash
# Desde la raíz del proyecto
docker-compose up -d
# Inicia: Pulsar + docs-generator
```

**Opción 2: Docker Compose de services (solo docs-generator)**
```bash
# Desde la carpeta services/
cd services
docker-compose up -d
# Inicia: Solo docs-generator (sin Pulsar)
```

**Opción 3: Docker Compose dev (solo Pulsar)**
```bash
# Desde la raíz del proyecto
docker-compose -f docker-compose.dev.yml up -d
# Inicia: Solo Pulsar (sin docs-generator)
```

---

## Checklist de Uso

### Si solo necesitas Gráficos:
- [ ] Django corriendo (`runserver`)
- [ ] ❌ Docker NO necesario
- [ ] ✅ Exportación funciona directamente

### Si necesitas Reportes del Mantenedor:
- [ ] Django corriendo (`runserver`)
- [ ] ✅ Docker corriendo (`docker-compose up -d`)
- [ ] ✅ docs-generator corriendo (puerto 5001)
- [ ] ✅ Exportación funciona con microservicio

### Si necesitas ambos (Gráficos + Reportes):
- [ ] Django corriendo (`runserver`)
- [ ] ✅ Docker corriendo (`docker-compose up -d` desde la raíz)
- [ ] ✅ docs-generator corriendo (puerto 5001)
- [ ] ✅ Ambos funcionan correctamente

---

## Verificación Rápida

**Verificar que docs-generator esté corriendo:**
```bash
# Ver contenedores
docker ps | grep docs-generator

# Verificar salud del servicio
curl http://localhost:5001/health
# Debe responder: {"status": "ok", "service": "docs-generator"}
```

**Si docs-generator NO está corriendo:**
- Los reportes del mantenedor usarán métodos alternativos (fallback)
- PDF y Excel pueden fallar o usar métodos menos optimizados
- CSV funcionará normalmente (tiene fallback completo)

---

## Referencias

- **Guía de Inicio:** `Explicacion/GUIA_INICIO_PROYECTO.md`
- **Documentación de Exportación:** `calificaciones/README_EXPORTACION.md`
- **Arquitectura de Exportación:** `calificaciones/ARQUITECTURA_EXPORTACION.md`


