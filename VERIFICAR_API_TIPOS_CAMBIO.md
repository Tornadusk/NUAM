# Cómo Verificar que la API de Tipos de Cambio Funciona

Esta guía te ayudará a verificar si la API key de ExchangeRate está funcionando correctamente y obteniendo datos reales.

## Método 1: Probar el Microservicio Directamente (Recomendado)

### Paso 1: Verificar que el contenedor está corriendo

```bash
docker ps | grep exchange-rate-service
```

Deberías ver algo como:
```
nuam-exchange-rate-service   Up   0.0.0.0:5100->5100/tcp
```

### Paso 2: Probar el endpoint de actualización

**En Windows (PowerShell):**
```powershell
# Probar el endpoint de actualización
curl -Method POST -Uri "http://localhost:5100/tipos-cambio/actualizar" `
     -ContentType "application/json" `
     -Body '{"monedas": ["CLP", "PEN", "COP"], "moneda_base": "USD"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**En Linux/Mac:**
```bash
curl -X POST http://localhost:5100/tipos-cambio/actualizar \
     -H "Content-Type: application/json" \
     -d '{"monedas": ["CLP", "PEN", "COP"], "moneda_base": "USD"}' | jq .
```

### Paso 3: Interpretar la Respuesta

**✅ Si funciona correctamente, verás:**
```json
{
  "success": true,
  "tipos_cambio": [
    {
      "moneda_origen": "USD",
      "moneda_destino": "CLP",
      "tasa": 950.50,
      "fecha": "2025-12-21",
      "fuente": "EXCHANGERATE_API"
    },
    {
      "moneda_origen": "USD",
      "moneda_destino": "PEN",
      "tasa": 3.75,
      "fecha": "2025-12-21",
      "fuente": "EXCHANGERATE_API"
    },
    {
      "moneda_origen": "USD",
      "moneda_destino": "COP",
      "tasa": 4100.00,
      "fecha": "2025-12-21",
      "fuente": "EXCHANGERATE_API"
    }
  ],
  "errores": {},
  "metadata": {
    "moneda_base": "USD",
    "monedas_destino": ["CLP", "PEN", "COP"],
    "proveedores_consultados": ["EXCHANGERATE_API"],
    "fecha_consulta": "2025-12-21"
  }
}
```

**❌ Si hay problemas, verás:**
```json
{
  "success": false,
  "tipos_cambio": [],
  "errores": {
    "EXCHANGERATE_API": "Error: Invalid API key"
  },
  "metadata": {
    "moneda_base": "USD",
    "monedas_destino": ["CLP", "PEN", "COP"],
    "proveedores_consultados": ["EXCHANGERATE_API"],
    "fecha_consulta": "2025-12-21"
  }
}
```

**Pistas de éxito:**
- `"success": true`
- `"tipos_cambio"` tiene al menos 1 elemento
- `"errores"` está vacío `{}`
- `"fuente": "EXCHANGERATE_API"` en los tipos de cambio
- Los valores de `tasa` son números reales (no 0 ni valores de prueba)

---

## Método 2: Verificar desde el Dashboard Web

### Paso 1: Abre el dashboard de Tipos de Cambio

1. Ve a: `https://127.0.0.1:8443/microservicio/tipos-cambio/`
2. Haz clic en el botón **"Actualizar desde APIs"**

### Paso 2: Observa el mensaje

**✅ Si funciona, verás:**
- Mensaje verde: "✓ Tipos de cambio actualizados correctamente (X tipos obtenidos)"
- Los datos se recargan automáticamente después de 2 segundos
- Los valores en las tarjetas y la tabla cambian a valores reales

**❌ Si hay problemas, verás:**
- Mensaje rojo: "Error: [descripción del error]"
- Los datos no se actualizan

---

## Método 3: Verificar en la Base de Datos

### Paso 1: Conectarte a Oracle

```bash
# En Windows
sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1

# En Linux/Mac (con Docker)
docker exec -it oracle-db sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1
```

### Paso 2: Consultar los tipos de cambio más recientes

```sql
-- Ver los últimos tipos de cambio guardados
SELECT 
    tc.id_tipo_cambio,
    tc.moneda_origen,
    tc.moneda_destino,
    tc.tasa,
    tc.fecha,
    tc.vigente_desde,
    f.nombre as fuente
FROM tipo_cambio tc
JOIN tipo_cambio_fuente f ON tc.id_fuente = f.id_fuente
WHERE tc.fecha >= SYSDATE - 1  -- Últimas 24 horas
ORDER BY tc.vigente_desde DESC;
```

**✅ Si funciona correctamente, verás:**
- Filas con `fecha` = fecha de hoy
- Valores de `tasa` reales (ej: CLP ~900-1000, PEN ~3.5-4.0, COP ~4000-4500)
- `vigente_desde` muy reciente (últimos minutos)
- `fuente` = "ExchangeRate API" o similar

**❌ Si hay problemas:**
- No hay registros con fecha de hoy
- O los valores son muy antiguos (de días anteriores)

---

## Método 4: Verificar los Logs del Contenedor

### Ver logs en tiempo real

```bash
docker logs -f nuam-exchange-rate-service
```

**✅ Si funciona, verás:**
- Llamadas exitosas: `INFO:     POST /tipos-cambio/actualizar HTTP/1.1 200 OK`
- Sin errores relacionados con API key

**❌ Si hay problemas, verás:**
- Errores HTTP 401 (Unauthorized) - API key inválida
- Errores HTTP 429 (Too Many Requests) - Límite excedido
- Mensajes de error sobre API key faltante o inválida

---

## Método 5: Ejecutar el Comando Django Directamente

### Desde la terminal

```bash
# En Windows
python manage.py obtener_tipos_cambio

# En Linux/Mac
python3 manage.py obtener_tipos_cambio
```

**✅ Si funciona, verás:**
```
Obteniendo tipos de cambio: USD -> CLP, PEN, COP

Llamando a microservicio exchange-rate-service...

✓ Guardados 3 tipos de cambio desde exchange-rate-service
```

**❌ Si hay problemas, verás:**
```
✗ Error al obtener tipos de cambio desde el microservicio: [mensaje de error]
```

---

## Verificar que la API Key está Configurada

### Verificar la variable de entorno en el contenedor

```bash
docker exec nuam-exchange-rate-service printenv | grep EXCHANGERATE_API_KEY
```

**✅ Deberías ver:**
```
EXCHANGERATE_API_KEY=effbc5f153954a92a297e710
```

**❌ Si no aparece:**
- La variable de entorno no está configurada
- Revisa `docker-compose.yml` y reinicia el contenedor:
  ```bash
  docker-compose restart exchange-rate-service
  ```

---

## Resumen Rápido - Checklist de Verificación

- [ ] Contenedor `nuam-exchange-rate-service` está corriendo (`docker ps`)
- [ ] La API key está configurada en el contenedor (`docker exec ... printenv`)
- [ ] El endpoint `/tipos-cambio/actualizar` responde con `success: true`
- [ ] La respuesta contiene tipos de cambio con `fuente: "EXCHANGERATE_API"`
- [ ] Los valores de tasa son realistas (CLP ~900-1000, PEN ~3.5-4.0, COP ~4000-4500)
- [ ] El dashboard muestra mensaje de éxito al actualizar
- [ ] La base de datos tiene registros nuevos con fecha de hoy
- [ ] El comando `obtener_tipos_cambio` se ejecuta sin errores

---

## Solución de Problemas Comunes

### Problema: "success: false" con error de API key

**Solución:**
1. Verifica que la API key esté en `docker-compose.yml`:
   ```yaml
   environment:
     - EXCHANGERATE_API_KEY=effbc5f153954a92a297e710
   ```
2. Reinicia el contenedor:
   ```bash
   docker-compose restart exchange-rate-service
   ```

### Problema: La API devuelve datos pero no se guardan en la BD

**Solución:**
1. Verifica que el comando `obtener_tipos_cambio` se ejecute correctamente
2. Revisa los logs de Django para ver errores de conexión a la BD
3. Verifica que las fuentes estén inicializadas:
   ```bash
   python manage.py inicializar_fuentes_tipos_cambio
   ```

### Problema: Los valores parecen incorrectos o muy antiguos

**Solución:**
1. Fuerza una actualización:
   ```bash
   python manage.py obtener_tipos_cambio --forzar
   ```
2. Verifica que la fecha en la respuesta sea la fecha actual
3. Si los valores son muy diferentes, puede ser que la API esté devolviendo datos históricos (raro, pero posible)

