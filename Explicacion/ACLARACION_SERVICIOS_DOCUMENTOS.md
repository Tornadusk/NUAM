# Aclaración: ¿Hacen lo Mismo los Dos Docker Compose?

## Respuesta Corta

**✅ SÍ, hacen exactamente lo mismo.** Ambos Docker Compose contienen el **mismo servicio** `docs-generator`. La única diferencia es que uno incluye Pulsar y el otro no.

---

## Tu Confusión Entendida

Pensabas que:
- `services/docker-compose.yml` → Para microservicio de **reportes** (del mantenedor)
- `docker-compose.yml` (raíz) → Para descargar **CSV y PDF de cada gráfico**

**Pero la realidad es diferente:**

---

## La Realidad

### Ambos Docker Compose tienen el MISMO servicio

**`docker-compose.yml` (RAÍZ):**
```yaml
services:
  pulsar:
    # ... configuración de Pulsar
  
  docs-generator:  # ← MISMO servicio
    build: ./services/docs-generator
    ports:
      - "5001:5000"
```

**`services/docker-compose.yml`:**
```yaml
services:
  docs-generator:  # ← MISMO servicio
    build: ./services/docs-generator
    ports:
      - "5001:5000"
```

**Ambos apuntan al mismo código:** `./services/docs-generator`

---

## ¿Para Qué se Usa `docs-generator`?

### ✅ Se Usa Para: Reportes del Mantenedor

**Ubicación en el código:** `calificaciones/views.py` → `exportar_datos_view()`

**URL:** `/calificaciones/exportar/<formato>/`

**Código que lo llama:**
```python
# calificaciones/views.py línea 115
resp = requests.post("http://localhost:5001/exportar", json=payload, timeout=10)
```

**Qué hace:**
- Exporta calificaciones del mantenedor en PDF, Excel, CSV
- Se llama desde el botón "Exportar" en el mantenedor de calificaciones

---

### ❌ NO se Usa Para: Gráficos

**Ubicación en el código:** `microservicio/views/graficos.py` → `api_exportar_grafico()`

**URL:** `/api/microservicio/exportar/<tipo_grafico>/<formato>/`

**Código que lo usa:**
```python
# microservicio/views/graficos.py línea 849-863
exportador = ExportadorGraficos(datos_grafico, titulo)
if formato == 'excel':
    return exportador.exportar_excel(...)
elif formato == 'csv':
    return exportador.exportar_csv(...)
elif formato == 'pdf':
    return exportador.exportar_pdf(...)
```

**Qué hace:**
- Genera archivos **directamente en Django**
- Usa la clase `ExportadorGraficos` en `microservicio/utils/exportador.py`
- **NO llama al microservicio** `docs-generator`
- **NO necesita Docker**

---

## Verificación en el Código

### Gráficos NO usan docs-generator:

```bash
# Buscar referencias a docs-generator en gráficos
grep -r "5001\|docs-generator" microservicio/views/graficos.py
# Resultado: NO HAY NINGUNA REFERENCIA
```

### Reportes del Mantenedor SÍ usan docs-generator:

```bash
# Buscar referencias a docs-generator en calificaciones
grep -r "5001\|docs-generator" calificaciones/views.py
# Resultado: SÍ HAY REFERENCIAS (líneas 105, 107, 113, 115)
```

---

## Resumen Visual

```
NUAM Exportación de Archivos
│
├── Gráficos (/microservicio/graficos/)
│   └── Exportación: ExportadorGraficos (Django directo)
│       ├── CSV ✅ (generado en Django)
│       ├── Excel ✅ (generado en Django)
│       ├── PDF ✅ (generado en Django)
│       └── HTML ✅ (generado en Django)
│       └── ❌ NO usa docs-generator
│       └── ❌ NO necesita Docker
│
└── Reportes del Mantenedor (/calificaciones/exportar/<formato>/)
    └── Exportación: exportar_datos_view() (Django)
        └── Llama a: http://localhost:5001/exportar
            └── ✅ SÍ usa docs-generator
            └── ✅ SÍ necesita Docker
            └── Genera: PDF, Excel, CSV de calificaciones
```

---

## Entonces, ¿Cuál es la Diferencia Entre los Dos Docker Compose?

### NO hay diferencia en la funcionalidad de `docs-generator`

Ambos Docker Compose tienen **exactamente el mismo servicio** `docs-generator` que hace **exactamente lo mismo**:
- Mismo código fuente (`./services/docs-generator`)
- Mismo puerto (5001)
- Misma funcionalidad (generar PDF, Excel, CSV)

### La única diferencia es:

| Aspecto | `docker-compose.yml` (RAÍZ) | `services/docker-compose.yml` |
|---------|----------------------------|-------------------------------|
| **Servicios incluidos** | Pulsar + docs-generator | Solo docs-generator |
| **Memoria requerida** | ~2GB+ | ~200-500MB |
| **Tiempo de inicio** | 60-90 segundos | 5-10 segundos |
| **Funcionalidad docs-generator** | ✅ Igual | ✅ Igual |

---

## ¿Por Qué Hay Dos Docker Compose?

**Razón:** Flexibilidad de desarrollo

1. **`docker-compose.yml` (RAÍZ):**
   - Para desarrollo completo (necesitas Pulsar + documentos)
   - Usa cuando desarrollas funcionalidades que requieren ambos servicios

2. **`services/docker-compose.yml`:**
   - Para desarrollo ligero (solo documentos)
   - Usa cuando:
     - Solo necesitas exportar reportes del mantenedor
     - Tienes poca memoria
     - NO necesitas Pulsar

---

## Conclusión

**Tu confusión era comprensible**, pero la realidad es:

- ✅ **Ambos Docker Compose hacen lo mismo** (mismo servicio `docs-generator`)
- ✅ **`docs-generator` se usa SOLO para reportes del mantenedor**
- ❌ **Los gráficos NO usan `docs-generator`** (generan archivos directamente en Django)
- ✅ **La diferencia es solo si incluyen Pulsar o no**

---

## Referencias

- **Código de Gráficos:** `microservicio/views/graficos.py` → `api_exportar_grafico()`
- **Código de Reportes:** `calificaciones/views.py` → `exportar_datos_view()`
- **Exportador de Gráficos:** `microservicio/utils/exportador.py` → `ExportadorGraficos`
- **Microservicio docs-generator:** `services/docs-generator/src/main.py`

