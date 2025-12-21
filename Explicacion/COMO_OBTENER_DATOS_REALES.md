# Cómo Obtener Más Datos Reales de ExchangeRate API

## Problema

Solo tienes **1 dato real** de ExchangeRate API (CLP/USD del 2025-12-15), pero necesitas más datos para USD/CLP, USD/PEN, USD/COP.

---

## Diagnóstico

### ¿Por qué solo hay un dato real?

**Posibles razones:**

1. **ExchangeRate API solo devolvió CLP/USD** en alguna ejecución previa
2. **La fecha del dato es vieja** (2025-12-15) porque no se han obtenido datos nuevos
3. **Los datos para hoy son todos simulados** porque la API falló o no se ejecutó correctamente

---

## Solución: Forzar Actualización

### Paso 1: Ejecutar comando con --forzar

```bash
python manage.py obtener_tipos_cambio --forzar
```

Esto **actualizará** los datos incluso si ya existen para hoy.

### Paso 2: Verificar que el microservicio esté funcionando

```bash
# Verificar contenedor
docker-compose ps exchange-rate-service

# Ver logs del microservicio
docker-compose logs exchange-rate-service --tail=50
```

### Paso 3: Probar el microservicio directamente

```bash
# Probar endpoint del microservicio
curl -X POST http://localhost:5100/tipos-cambio/actualizar \
  -H "Content-Type: application/json" \
  -d '{"monedas": ["CLP", "PEN", "COP"], "moneda_base": "USD"}'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "tipos_cambio": [
    {
      "moneda_origen": "USD",
      "moneda_destino": "CLP",
      "tasa": 910.38,
      "fecha": "2025-12-21",
      "fuente": "EXCHANGERATE_API"
    },
    {
      "moneda_origen": "USD",
      "moneda_destino": "PEN",
      "tasa": 3.59,
      "fecha": "2025-12-21",
      "fuente": "EXCHANGERATE_API"
    },
    {
      "moneda_origen": "USD",
      "moneda_destino": "COP",
      "tasa": 4116.37,
      "fecha": "2025-12-21",
      "fuente": "EXCHANGERATE_API"
    }
  ],
  "errores": {},
  "metadata": {
    "moneda_base": "USD",
    "monedas_destino": ["CLP", "PEN", "COP"],
    "proveedores_consultados": ["EXCHANGERATE_API", "BANCO_CENTRAL_CHILE"],
    "fecha_consulta": "2025-12-21"
  }
}
```

---

## Verificar Datos en la Base de Datos

### Usar el script de verificación

```bash
python verificar_datos_tipos_cambio.py
```

Este script mostrará:
- Cuántos registros hay para hoy
- Cuántos son simulados vs reales
- Los últimos datos de ExchangeRate API

### Usar Django shell

```python
python manage.py shell

>>> from microservicio.models import TipoCambio, TipoCambioFuente
>>> from django.utils import timezone
>>> hoy = timezone.now().date()
>>> 
>>> # Ver datos reales de hoy
>>> fuente_real = TipoCambioFuente.objects.filter(codigo__icontains='EXCHANGERATE').first()
>>> if fuente_real:
...     reales = TipoCambio.objects.filter(fecha=hoy, id_fuente=fuente_real)
...     print(f"Datos reales para hoy: {reales.count()}")
...     for tc in reales:
...         print(f"  {tc.moneda_origen}/{tc.moneda_destino}: {tc.tasa}")
```

---

## Si ExchangeRate API No Funciona

### Verificar API Key

La API key está configurada en `docker-compose.yml`:
```yaml
environment:
  - EXCHANGERATE_API_KEY=${EXCHANGERATE_API_KEY:-effbc5f153954a92a297e710}
```

### Probar la API directamente

```bash
curl "https://v6.exchangerate-api.com/v6/effbc5f153954a92a297e710/latest/USD"
```

**Debería devolver:**
```json
{
  "result": "success",
  "conversion_rates": {
    "USD": 1.0,
    "CLP": 910.38,
    "PEN": 3.59,
    "COP": 4116.37,
    ...
  }
}
```

Si devuelve error, la API key puede estar expirada o tener límites.

---

## Solución Completa

### 1. Eliminar datos simulados (opcional)

Si quieres solo datos reales, puedes eliminar los simulados:

```python
python manage.py shell

>>> from microservicio.models import TipoCambio, TipoCambioFuente
>>> fuente_simulado = TipoCambioFuente.objects.filter(codigo='SIMULADO').first()
>>> if fuente_simulado:
...     TipoCambio.objects.filter(id_fuente=fuente_simulado).delete()
...     print("Datos simulados eliminados")
```

### 2. Forzar actualización

```bash
python manage.py obtener_tipos_cambio --forzar
```

### 3. Verificar resultados

```bash
python verificar_datos_tipos_cambio.py
```

---

## Resumen de Comandos

| Acción | Comando |
|--------|---------|
| **Forzar actualización** | `python manage.py obtener_tipos_cambio --forzar` |
| **Ver datos en BD** | `python verificar_datos_tipos_cambio.py` |
| **Probar microservicio** | `curl -X POST http://localhost:5100/tipos-cambio/actualizar -H "Content-Type: application/json" -d '{"monedas": ["CLP", "PEN", "COP"]}'` |
| **Ver logs del microservicio** | `docker-compose logs exchange-rate-service --tail=50` |
| **Verificar contenedor** | `docker-compose ps exchange-rate-service` |

---

## Esperado Después de Actualizar

Después de ejecutar `--forzar`, deberías tener:

- ✅ **USD/CLP** desde ExchangeRate API (fecha: hoy)
- ✅ **USD/PEN** desde ExchangeRate API (fecha: hoy)
- ✅ **USD/COP** desde ExchangeRate API (fecha: hoy)
- ✅ Posiblemente **USD/CLP** desde Banco Central de Chile (solo para CLP)

**Total esperado: 3-4 registros reales** para hoy.

