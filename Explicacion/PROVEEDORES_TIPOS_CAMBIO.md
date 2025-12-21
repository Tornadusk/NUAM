# Proveedores de Tipos de Cambio

## Proveedores Disponibles

Hay **3 proveedores** configurados en el microservicio `exchange-rate-service`:

### 1. ExchangeRate API (`EXCHANGERATE_API`)
- **URL**: `https://v6.exchangerate-api.com/v6`
- **Requiere API Key**: Sí (variable `EXCHANGERATE_API_KEY`)
- **Monedas soportadas**: Todas las principales (USD, CLP, PEN, COP, etc.)
- **Estado**: ✅ Configurado en `docker-compose.yml` con key: `effbc5f153954a92a297e710`

### 2. Fixer.io (`FIXER_IO`)
- **URL**: `https://api.fixer.io/latest`
- **Requiere API Key**: Sí (variable `FIXER_API_KEY`)
- **Monedas soportadas**: Todas las principales
- **Estado**: ⚠️ No configurado (falta API key en `docker-compose.yml`)

### 3. Banco Central de Chile (`BANCO_CENTRAL_CHILE`)
- **URL**: `https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx`
- **Requiere API Key**: No (público)
- **Monedas soportadas**: Solo USD -> CLP
- **Estado**: ✅ Siempre disponible (no requiere configuración)

---

## ¿Cuál se está usando actualmente?

Según los logs que viste:
```
Obteniendo tipos de cambio: USD -> CLP, PEN, COP
Llamando a microservicio exchange-rate-service...
No se guardaron nuevos tipos de cambio (ya existían o no se recibieron datos válidos)
```

El microservicio intenta usar todos los proveedores disponibles, pero:
- **ExchangeRate API**: Debería estar funcionando (tiene API key configurada)
- **Fixer.io**: No se puede usar (falta API key)
- **Banco Central de Chile**: Solo funciona para USD -> CLP

---

## Por qué aparece "ExchangeRate API" en la tabla

En la tabla veías:
- **CLP/USD**: Fuente = "ExchangeRate API" ✅ (Datos reales de la API)
- **USD/CLP, USD/PEN, USD/COP**: Fuente = "Datos Simulados" (Los datos son simulados o viejos)

Esto significa que:
1. El microservicio **sí está funcionando** para algunos casos
2. Para CLP/USD, se obtuvo un dato real de ExchangeRate API
3. Para otros pares, puede que no haya datos nuevos o que los datos existentes sean simulados

---

## Respuesta Directa

**Pregunta:** ¿Solo hay un ExchangeRate API?

**Respuesta:** No, hay **3 proveedores**:
1. ✅ **ExchangeRate API** (configurado con API key)
2. ⚠️ **Fixer.io** (no configurado, falta API key)
3. ✅ **Banco Central de Chile** (público, solo USD->CLP)

Actualmente solo **ExchangeRate API** está completamente funcional porque es el único con API key configurada.

---

## Para Usar Fixer.io (Opcional)

Si quieres agregar Fixer.io, necesitarías:

1. Obtener una API key de https://fixer.io/
2. Agregar a `docker-compose.yml`:
```yaml
environment:
  - FIXER_API_KEY=tu_api_key_aqui
```
3. Reiniciar el contenedor: `docker-compose restart exchange-rate-service`


