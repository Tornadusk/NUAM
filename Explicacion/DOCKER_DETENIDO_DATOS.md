# ¿Qué pasa si detienes el Docker del microservicio?

## Respuesta Corta

**SÍ.** Si detienes el contenedor `exchange-rate-service`, seguirás viendo los datos que están en la base de datos, **incluidos los simulados** si existen.

---

## ¿Por qué?

### El dashboard lee de la BASE DE DATOS, no del microservicio

El dashboard hace esto:

```python
# En api_tipos_cambio_por_pais():
tipos_cambio = TipoCambio.objects.filter(...)  # Lee de la BD
```

**No llama al microservicio** para mostrar datos, solo lee de la base de datos.

### El microservicio solo se usa para ACTUALIZAR

El microservicio solo se llama cuando:
- Haces clic en **"Actualizar desde APIs"** → llama a `obtener_tipos_cambio` → llama al microservicio
- O ejecutas manualmente: `python manage.py obtener_tipos_cambio`

---

## Comportamiento por Escenario

### Escenario 1: Docker detenido + Datos simulados en BD

**Resultado:**
- ✅ **SÍ verás los datos simulados** en el dashboard
- ✅ El dashboard funciona normal
- ❌ El botón "Actualizar desde APIs" fallará (502 Bad Gateway)

**Ejemplo:**
```
1. Tienes datos simulados de hoy en la BD
2. Detienes: docker-compose stop exchange-rate-service
3. Abres el dashboard → VES los datos simulados ✅
4. Clic en "Actualizar desde APIs" → Error 502 ❌
```

---

### Escenario 2: Docker detenido + Solo datos reales en BD

**Resultado:**
- ✅ **SÍ verás los datos reales** (los que ya estaban guardados)
- ✅ El dashboard funciona normal
- ❌ No podrás obtener datos nuevos (el botón fallará)

**Ejemplo:**
```
1. Tienes datos reales de ayer en la BD
2. Detienes: docker-compose stop exchange-rate-service
3. Abres el dashboard → VES los datos reales de ayer ✅
4. Clic en "Actualizar desde APIs" → Error 502 ❌
```

---

### Escenario 3: Docker corriendo + Datos simulados en BD

**Resultado:**
- ⚠️ **Verás los datos simulados** (porque son más recientes)
- ✅ El botón "Actualizar desde APIs" funciona
- ✅ Podrás obtener datos reales nuevos

**Solución:**
```bash
# Eliminar simulados y obtener reales
python eliminar_simulados_hoy.py
# O desde el dashboard: clic en "Actualizar desde APIs"
```

---

## Comparación

| Acción | Con Docker Corriendo | Con Docker Detenido |
|--------|---------------------|---------------------|
| **Ver datos en dashboard** | ✅ Funciona (lee de BD) | ✅ Funciona (lee de BD) |
| **"Actualizar desde APIs"** | ✅ Funciona | ❌ Error 502 |
| **Datos simulados** | ⚠️ Se muestran si están en BD | ✅ Se muestran si están en BD |
| **Datos reales** | ✅ Se muestran si están en BD | ✅ Se muestran si están en BD |
| **Obtener datos nuevos** | ✅ Funciona | ❌ No funciona |

---

## Flujo del Dashboard

```
┌─────────────────────────────────────────┐
│         Usuario abre dashboard          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  GET /api/tipos-cambio-por-pais/        │
│  (No llama al microservicio)            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  TipoCambio.objects.filter(...)         │
│  Lee directamente de la BASE DE DATOS   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Devuelve datos (reales + simulados)    │
│  Ordenados por fecha más reciente       │
└─────────────────────────────────────────┘
```

---

## Flujo de Actualización

```
┌─────────────────────────────────────────┐
│  Usuario clic "Actualizar desde APIs"   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  POST /api/obtener-tipos-cambio/        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  obtener_tipos_cambio --forzar          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  ¿Docker corriendo?                     │
│  ┌─────────┐      ┌─────────┐          │
│  │   SÍ    │      │   NO    │          │
│  └────┬────┘      └────┬────┘          │
│       │                │                │
│       ▼                ▼                │
│  ✅ Llama a         ❌ Error 502        │
│  exchange-rate-        (Bad Gateway)    │
│  service                               │
└─────────────────────────────────────────┘
```

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿Veré datos simulados si detengo Docker? | ✅ **SÍ**, si están en la BD |
| ¿Veré datos reales si detengo Docker? | ✅ **SÍ**, si están en la BD |
| ¿Funcionará el dashboard? | ✅ **SÍ**, lee de la BD |
| ¿Funcionará "Actualizar desde APIs"? | ❌ **NO**, necesita el Docker |
| ¿Qué datos se muestran primero? | Los más recientes (ordenados por `vigente_desde`) |

---

## Recomendación

Si quieres ver **solo datos reales**:

1. **No uses el botón "Cargar Datos Simulados"**
2. **Usa solo "Actualizar desde APIs"** (con Docker corriendo)
3. **O elimina simulados manualmente**: `python eliminar_simulados_hoy.py`

El dashboard **siempre muestra lo que hay en la BD**, independientemente de si el Docker está corriendo o no.


