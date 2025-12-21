# Respuestas sobre Exportaciones y Proveedores

## 1. ¿Solo hay un ExchangeRate API?

**No, hay 3 proveedores:**

| Proveedor | Estado | API Key | Monedas |
|-----------|--------|---------|---------|
| **ExchangeRate API** | ✅ Activo | ✅ Configurada (`effbc5f153954a92a297e710`) | Todas (USD, CLP, PEN, COP, etc.) |
| **Fixer.io** | ⚠️ Inactivo | ❌ No configurada | Todas |
| **Banco Central de Chile** | ✅ Activo | No requiere | Solo USD → CLP |

**Respuesta corta:** Actualmente solo **ExchangeRate API** está completamente funcional porque es el único con API key configurada.

Ver: `Explicacion/PROVEEDORES_TIPOS_CAMBIO.md` para más detalles.

---

## 2. PDF muestra datos, HTML no muestra datos

**Problema identificado y corregido:** ✅

El template HTML de Jinja2 no estaba manejando correctamente el formato Django de los datos. 

**Corrección aplicada:**
- El template ahora detecta si los datos vienen en formato Django (`'Par de Monedas'`, `'Tasa'`, etc.)
- Maneja ambos formatos correctamente usando `tc.get(header)` en lugar de acceso directo

**Archivo modificado:** `services/exchange-rate-service/exportador.py`

**Próximo paso:** Reconstruir el contenedor para aplicar los cambios:
```bash
docker-compose restart exchange-rate-service
# O si es necesario reconstruir:
docker-compose up -d --build exchange-rate-service
```

---

## 3. Errores de Pulsar

Los errores que ves son **normales** si:
- Pulsar está iniciando (puede tardar 30-60 segundos)
- Pulsar no está corriendo

**Ejemplo de errores (normales durante inicio):**
```
Pulsar Admin API no disponible: Admin API respondió con código 500
Error de conexión con Pulsar Admin API para topic carga_masiva
```

**Si quieres verificar:**
```bash
docker-compose ps nuam-pulsar
docker-compose logs nuam-pulsar
```

**Si Pulsar no es crítico para exportaciones**, puedes ignorar estos errores ya que las exportaciones funcionan sin Pulsar.

---

## 4. ¿Todas las exportaciones vienen del Docker de tipo de cambio?

**Respuesta:** Depende del tipo de datos:

### Tipos de Cambio: ✅ SÍ
- **Todas las exportaciones (PDF, Excel, HTML, CSV)** vienen del microservicio `exchange-rate-service` (Docker)
- El contenedor está corriendo en el puerto `5100`
- Django llama a: `http://localhost:5100/exportar/{formato}`

### Bolsa de Valores: ⚠️ Parcialmente
- **Microservicio listo**: `market-info-service` tiene los endpoints `/exportar/pdf`, `/exportar/excel`, `/exportar/html`
- **Integración Django**: ❌ Falta agregar el caso en `api_exportar_grafico()`
- **Estado**: El microservicio está en Docker, pero Django aún no lo está usando para exportación

**Resumen:**

| Datos | Exportación | Origen |
|-------|-------------|--------|
| Tipos de Cambio | PDF, Excel, HTML, CSV | ✅ Docker (`exchange-rate-service`) |
| Bolsa | PDF, Excel, HTML | ⚠️ Docker listo, falta integración Django |

---

## Resumen de Correcciones Aplicadas

1. ✅ **Template HTML corregido** para manejar formato Django correctamente
2. ✅ **Documentación de proveedores** creada
3. ✅ **Errores de Pulsar** explicados (normales durante inicio)
4. ✅ **Estado de exportaciones** aclarado

---

## Para Probar las Correcciones

1. **Reconstruir/Reiniciar el microservicio:**
   ```bash
   docker-compose restart exchange-rate-service
   # O si hay cambios en el código:
   docker-compose up -d --build exchange-rate-service
   ```

2. **Probar exportación HTML:**
   - Ir a "Tipos de Cambio" en el dashboard
   - Hacer clic en el botón "HTML"
   - Verificar que el archivo descargado tenga datos en la tabla

3. **Verificar que PDF siga funcionando:**
   - Exportar a PDF
   - Confirmar que los datos se muestren correctamente



