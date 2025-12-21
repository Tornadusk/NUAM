# ¿--forzar actualiza los datos simulados?

## Respuesta Corta

**NO.** El comando `obtener_tipos_cambio --forzar` **solo actualiza los datos REALES** que vienen del microservicio. Los datos simulados **NO se tocan**.

---

## Explicación Detallada

### ¿Qué hace `--forzar`?

El comando `obtener_tipos_cambio --forzar`:

1. ✅ Llama al microservicio `exchange-rate-service`
2. ✅ Obtiene datos de APIs reales (ExchangeRate API, Banco Central de Chile, etc.)
3. ✅ Actualiza los datos **solo de esas fuentes reales** en la BD
4. ❌ **NO toca los datos simulados** (fuente `SIMULADO`)

### ¿Por qué no actualiza los simulados?

**Razón 1: Fuentes diferentes**
- Los datos reales vienen con fuente `EXCHANGERATE_API`, `BANCO_CENTRAL_CHILE`, etc.
- Los datos simulados tienen fuente `SIMULADO`
- El comando solo guarda lo que el microservicio devuelve (que nunca incluye `SIMULADO`)

**Razón 2: Origen diferente**
- Los datos reales se obtienen del microservicio `exchange-rate-service`
- Los datos simulados se generan con el endpoint `api_generar_datos_simulados` (botón "Cargar Datos Simulados")

**Razón 3: Lógica del código**
```python
# En _guardar_tipos_cambio():
# Solo actualiza si la fuente coincide con lo que viene del microservicio
# Los datos simulados tienen fuente 'SIMULADO' que nunca viene del microservicio
```

---

## Comportamiento Actual

### Con `--forzar`:

| Tipo de Dato | ¿Se actualiza? | Fuente |
|--------------|----------------|--------|
| **USD/CLP desde ExchangeRate API** | ✅ SÍ | `EXCHANGERATE_API` |
| **USD/PEN desde ExchangeRate API** | ✅ SÍ | `EXCHANGERATE_API` |
| **USD/COP desde ExchangeRate API** | ✅ SÍ | `EXCHANGERATE_API` |
| **USD/CLP desde Banco Central Chile** | ✅ SÍ | `BANCO_CENTRAL_CHILE` |
| **USD/CLP Simulado** | ❌ NO | `SIMULADO` |
| **USD/PEN Simulado** | ❌ NO | `SIMULADO` |
| **USD/COP Simulado** | ❌ NO | `SIMULADO` |

---

## Solución: Eliminar Simulados Antes de Actualizar

Si quieres que solo queden datos reales después de actualizar:

### Opción 1: Script automático

```bash
python eliminar_simulados_hoy.py
python manage.py obtener_tipos_cambio --forzar
```

### Opción 2: Manualmente

```python
python manage.py shell

>>> from microservicio.models import TipoCambio, TipoCambioFuente
>>> from django.utils import timezone
>>> 
>>> # Eliminar simulados de hoy
>>> fuente_simulado = TipoCambioFuente.objects.filter(codigo='SIMULADO').first()
>>> if fuente_simulado:
...     hoy = timezone.now().date()
...     eliminados = TipoCambio.objects.filter(fecha=hoy, id_fuente=fuente_simulado).delete()
...     print(f"Eliminados {eliminados[0]} registros simulados")
```

Luego ejecutar:
```bash
python manage.py obtener_tipos_cambio --forzar
```

---

## ¿Debería `--forzar` eliminar simulados automáticamente?

**Opción A: NO (comportamiento actual)**
- ✅ Mantiene separación clara entre datos reales y simulados
- ✅ El usuario controla cuándo eliminar simulados
- ✅ No elimina datos que el usuario puede querer conservar

**Opción B: SÍ (modificar código)**
- ✅ Simplifica el flujo (un solo comando)
- ❌ Puede eliminar datos que el usuario quiere conservar
- ❌ Menos control para el usuario

**Recomendación:** Mantener el comportamiento actual (Opción A) porque:
- Los datos simulados pueden ser útiles para pruebas
- El usuario puede decidir cuándo eliminarlos
- Ya existe un script (`eliminar_simulados_hoy.py`) para hacerlo fácilmente

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿`--forzar` actualiza datos simulados? | ❌ NO |
| ¿`--forzar` actualiza datos reales? | ✅ SÍ |
| ¿Cómo eliminar simulados? | Usar `eliminar_simulados_hoy.py` o manualmente |
| ¿Debería `--forzar` eliminar simulados? | No recomendado (mantener control del usuario) |

---

## Flujo Recomendado

Si quieres **solo datos reales actualizados**:

```bash
# 1. Eliminar simulados de hoy
python eliminar_simulados_hoy.py

# 2. Actualizar datos reales
python manage.py obtener_tipos_cambio --forzar

# O desde el dashboard:
# 1. No usar el botón "Cargar Datos Simulados"
# 2. Usar solo el botón "Actualizar desde APIs" (ahora con --forzar automático)
```


