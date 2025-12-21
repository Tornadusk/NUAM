# ¿Funcionan las exportaciones si el Docker está apagado?

## Respuesta Corta

**NO.** Las exportaciones de archivos (PDF, Excel, HTML) **NO funcionarán** si el Docker está apagado porque dependen de los microservicios.

---

## Explicación Detallada

### ¿Cómo funciona la exportación?

La exportación hace esto:

1. **Django obtiene datos de la BD** (lee `TipoCambio.objects.filter(...)`)
2. **Django llama al microservicio** para generar el archivo
3. **El microservicio genera el PDF/Excel/HTML** usando las librerías (`reportlab`, `openpyxl`, `jinja2`)
4. **El microservicio devuelve el archivo** a Django
5. **Django envía el archivo** al navegador

### Flujo de Exportación

```
┌─────────────────────────────────────────┐
│  Usuario clic "Exportar PDF/Excel/HTML" │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  GET /api/exportar/tipos_cambio/pdf/     │
│  (Django endpoint)                       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  TipoCambio.objects.filter(...)          │
│  Lee datos de la BASE DE DATOS          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  exportar_tipos_cambio(datos, formato)   │
│  (Cliente HTTP)                          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  POST http://localhost:5100/exportar/pdf │
│  (Llama al microservicio)               │
│                                         │
│  ¿Docker corriendo?                     │
│  ┌─────────┐      ┌─────────┐          │
│  │   SÍ    │      │   NO    │          │
│  └────┬────┘      └────┬────┘          │
│       │                │                │
│       ▼                ▼                │
│  ✅ Genera archivo  ❌ Error 502        │
│  con reportlab         Connection       │
│  /openpyxl/jinja2      Refused          │
└─────────────────────────────────────────┘
```

---

## Comportamiento por Escenario

### Escenario 1: Docker APAGADO + Intentar Exportar

**Resultado:**
- ❌ **Error 502 Bad Gateway** o **Connection Refused**
- ❌ No se genera el archivo
- ⚠️ Mensaje de error en el navegador

**Ejemplo:**
```
1. Docker exchange-rate-service está DETENIDO
2. Usuario clic "Exportar PDF" en Tipos de Cambio
3. Django intenta llamar a http://localhost:5100/exportar/pdf
4. ❌ Error: Connection refused / 502 Bad Gateway
5. Usuario ve error en el navegador
```

---

### Escenario 2: Docker ENCENDIDO + Exportar

**Resultado:**
- ✅ **Funciona correctamente**
- ✅ Se genera el archivo (PDF/Excel/HTML)
- ✅ El archivo se descarga en el navegador

**Ejemplo:**
```
1. Docker exchange-rate-service está CORRIENDO
2. Usuario clic "Exportar PDF" en Tipos de Cambio
3. Django llama a http://localhost:5100/exportar/pdf
4. ✅ Microservicio genera PDF con reportlab
5. ✅ Usuario descarga el archivo
```

---

## Comparación: Dashboard vs Exportación

| Funcionalidad | ¿Lee de BD? | ¿Llama al Microservicio? | ¿Funciona sin Docker? |
|---------------|-------------|--------------------------|----------------------|
| **Ver dashboard** | ✅ SÍ | ❌ NO | ✅ **SÍ funciona** |
| **Actualizar datos** | ❌ NO | ✅ SÍ | ❌ **NO funciona** |
| **Exportar PDF/Excel/HTML** | ✅ SÍ (lee datos) | ✅ SÍ (genera archivo) | ❌ **NO funciona** |

---

## Código Relevante

### Django llama al microservicio:

```python
# microservicio/services/exchange_rate_client.py
def exportar_tipos_cambio(tipos_cambio, formato, titulo):
    base_url = "http://localhost:5100"  # Microservicio
    url = f"{base_url}/exportar/{formato}"
    
    resp = requests.post(url, json=payload, timeout=30)
    # ❌ Si Docker está apagado: Connection refused
    return resp
```

### El microservicio genera el archivo:

```python
# services/exchange-rate-service/main.py
@app.post("/exportar/{formato}")
def exportar_tipos_cambio(formato, request: ExportarRequest):
    if formato == "pdf":
        return generar_pdf(request.tipos_cambio, request.titulo)
    elif formato == "excel":
        return generar_excel(request.tipos_cambio, request.titulo)
    elif formato == "html":
        return generar_html(request.tipos_cambio, request.titulo)
```

---

## ¿Por qué se diseñó así?

**Razón:** Separación de responsabilidades (arquitectura de microservicios)

- **Django**: Lee datos de la BD y maneja la UI
- **Microservicio**: Genera archivos (PDF/Excel/HTML) con librerías especializadas

**Ventajas:**
- ✅ Microservicio puede usar Python moderno y librerías actualizadas
- ✅ Generación de archivos no sobrecarga Django
- ✅ Fácil escalar el microservicio independientemente

**Desventajas:**
- ❌ Requiere Docker corriendo para exportar

---

## Solución Temporal (si no puedes usar Docker)

Si necesitas exportar sin Docker, tendrías que:

1. **Modificar el código** para generar archivos directamente en Django
2. **Usar las mismas librerías** (`reportlab`, `openpyxl`, `jinja2`) en Django
3. **Duplicar la lógica** de generación (no recomendado)

**No recomendado** porque:
- Pierdes la arquitectura de microservicios
- Duplicas código
- Aumenta la complejidad de Django

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿Funcionan exportaciones sin Docker? | ❌ **NO** |
| ¿Por qué no funcionan? | Necesitan llamar al microservicio para generar archivos |
| ¿Qué error veré? | 502 Bad Gateway o Connection Refused |
| ¿El dashboard funciona sin Docker? | ✅ **SÍ** (lee de BD) |
| ¿La actualización funciona sin Docker? | ❌ **NO** (necesita microservicio) |

---

## Recomendación

**Para que todo funcione correctamente:**

```bash
# Asegúrate de que el Docker esté corriendo antes de exportar
docker-compose ps exchange-rate-service
# Debe mostrar STATUS: Up

# Si está detenido, inícialo:
docker-compose up -d exchange-rate-service
```

**Orden de dependencias:**

1. ✅ **Dashboard**: No necesita Docker (lee de BD)
2. ❌ **Actualizar datos**: Necesita Docker
3. ❌ **Exportar archivos**: Necesita Docker

---

## Conclusión

**Las exportaciones requieren que el Docker esté corriendo** porque el microservicio es quien genera los archivos (PDF, Excel, HTML). Sin Docker, verás un error de conexión.

Si necesitas exportar, asegúrate de que `exchange-rate-service` esté corriendo:
```bash
docker-compose ps exchange-rate-service
docker-compose up -d exchange-rate-service  # Si está detenido
```

