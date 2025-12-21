# Diferencia entre Datos Simulados y Datos Reales de Tipos de Cambio

## 📋 Resumen

**NO son lo mismo.** Son tres cosas completamente diferentes:

1. **`inicializar_fuentes_tipos_cambio`**: Solo crea las FUENTES (no genera datos)
2. **`obtener_tipos_cambio`**: Obtiene datos **REALES** desde APIs externas
3. **Botón "Cargar Datos Simulados"**: Genera datos **SIMULADOS** (valores hardcodeados)

---

## 1. `inicializar_fuentes_tipos_cambio`

### ¿Qué hace?
- **Solo crea las FUENTES** de tipos de cambio en la base de datos (`TipoCambioFuente`)
- **NO genera datos** de tipos de cambio (`TipoCambio`)
- Es como crear el "catálogo" de fuentes disponibles

### Fuentes que crea:
- `EXCHANGERATE_API` - ExchangeRate API
- `FIXER_IO` - Fixer.io
- `BANCO_CENTRAL_CHILE` - Banco Central de Chile
- (NO crea la fuente `SIMULADO`)

### Cuándo se usa:
- **Una sola vez** al inicio del proyecto
- O si necesitas resetear las fuentes

### Comando:
```bash
# Mac/Linux
python3 manage.py inicializar_fuentes_tipos_cambio

# Windows
python manage.py inicializar_fuentes_tipos_cambio
```

---

## 2. `obtener_tipos_cambio`

### ¿Qué hace?
- Obtiene tipos de cambio **REALES** desde APIs externas
- Llama al microservicio `exchange-rate-service`
- El microservicio consulta APIs reales (ExchangeRate API, Fixer.io, Banco Central de Chile)
- Guarda los datos reales en la base de datos (`TipoCambio`)

### Fuentes que puede usar:
- `EXCHANGERATE_API` - Datos reales desde ExchangeRate API
- `FIXER_IO` - Datos reales desde Fixer.io
- `BANCO_CENTRAL_CHILE` - Datos reales desde Banco Central de Chile

### Requisitos:
- ✅ **Conexión a internet** (obligatorio)
- ✅ APIs configuradas (API keys configuradas en `docker-compose.yml`)
- ✅ Microservicio `exchange-rate-service` corriendo

### Cuándo se usa:
- Para obtener datos **reales y actuales** de tipos de cambio
- Puede ejecutarse periódicamente (manual o automático)
- También se ejecuta desde el botón "Actualizar desde APIs" en el dashboard

### Comando:
```bash
# Mac/Linux
python3 manage.py obtener_tipos_cambio

# Windows
python manage.py obtener_tipos_cambio
```

### Ejemplo de uso:
```bash
# Obtener de todas las fuentes activas
python manage.py obtener_tipos_cambio

# Obtener solo de ExchangeRate API
python manage.py obtener_tipos_cambio --fuente EXCHANGERATE_API

# Obtener solo CLP y PEN
python manage.py obtener_tipos_cambio --monedas CLP,PEN
```

---

## 3. Botón "Cargar Datos Simulados" / `api_generar_datos_simulados`

### ¿Qué hace?
- Genera tipos de cambio **SIMULADOS** (valores hardcodeados con variación aleatoria)
- **NO consulta APIs externas**
- Crea registros con `id_fuente.codigo == 'SIMULADO'`
- Genera datos para los últimos 12 meses (aproximadamente)

### Valores base (hardcodeados):
```python
valores_base = {
    'CLP': 950.0,   # USD/CLP
    'PEN': 3.75,    # USD/PEN
    'COP': 4100.0   # USD/COP
}
```
- Aplica variación aleatoria de ±5%
- Genera ~39 registros (3 monedas × 13 meses)

### Requisitos:
- ❌ **NO requiere conexión a internet**
- ❌ **NO requiere APIs configuradas**
- ❌ **NO requiere microservicios corriendo**
- ✅ Solo necesita la base de datos

### Cuándo se usa:
- Para **pruebas y desarrollo** cuando no hay internet
- Para tener datos de ejemplo sin depender de APIs externas
- Cuando las APIs externas están caídas o limitadas
- Para demos sin necesidad de configuración compleja

### Cómo se usa:
1. Desde el dashboard: Botón "Cargar Datos Simulados"
2. Desde API: `POST /microservicio/api/generar-datos-simulados/`

---

## 📊 Comparación

| Aspecto | `inicializar_fuentes_tipos_cambio` | `obtener_tipos_cambio` | Datos Simulados |
|---------|-----------------------------------|------------------------|-----------------|
| **Tipo de datos** | No genera datos | Datos **REALES** | Datos **SIMULADOS** |
| **Origen** | Solo crea catálogo | APIs externas reales | Valores hardcodeados |
| **Internet** | No necesario | ✅ Obligatorio | No necesario |
| **APIs configuradas** | No necesario | ✅ Obligatorio | No necesario |
| **Microservicios** | No necesario | ✅ Obligatorio | No necesario |
| **Cuándo usar** | Inicio del proyecto | Obtener datos reales | Pruebas/desarrollo |
| **Frecuencia** | Una vez | Periódicamente | Cuando se necesite |

---

## 🔄 Flujo Normal

### Primera vez (inicialización):
1. `python manage.py inicializar_fuentes_tipos_cambio` → Crea fuentes
2. `python manage.py obtener_tipos_cambio` → Obtiene datos reales
   - Si falla (sin internet/APIs), puedes usar "Cargar Datos Simulados"

### Uso normal:
1. **Opción A**: Usar datos reales
   - Botón "Actualizar desde APIs" en el dashboard
   - O `python manage.py obtener_tipos_cambio`

2. **Opción B**: Usar datos simulados (si no hay internet/APIs)
   - Botón "Cargar Datos Simulados" en el dashboard

---

## ⚠️ Importante

- **Datos simulados NO son datos reales**: Son valores aproximados con variación aleatoria
- **Datos reales requieren configuración**: APIs, internet, microservicios
- **Ambos se pueden mezclar**: Puedes tener datos reales y simulados en la misma BD
- **El dashboard muestra ambos**: Filtra por fuente para ver solo uno u otro

---

## 💡 Ejemplo de Uso

```bash
# 1. Inicializar fuentes (solo una vez)
python manage.py inicializar_fuentes_tipos_cambio

# 2. Intentar obtener datos reales
python manage.py obtener_tipos_cambio

# Si falla (sin internet/APIs), usar datos simulados desde el dashboard
# Botón "Cargar Datos Simulados"
```

---

## 📝 Notas

- Los datos simulados tienen `id_fuente.codigo == 'SIMULADO'`
- Los datos reales tienen `id_fuente.codigo` igual a la fuente usada (ej: `EXCHANGERATE_API`)
- El dashboard puede filtrar y mostrar ambos tipos
- La exportación incluye ambos tipos de datos


