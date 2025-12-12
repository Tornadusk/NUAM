# ¿Qué hace Pulsar en NUAM y por qué es beneficioso?

## Resumen Ejecutivo

**Pulsar en NUAM es un sistema de mensajería asíncrona que permite que diferentes partes del sistema se comuniquen sin bloquearse entre sí.** Actúa como un "buzón central" donde se publican eventos y otros servicios pueden leerlos cuando están listos.

## 🔍 ¿De qué se encarga Pulsar en NUAM?

### 1. **Tipos de Cambio (Currency Exchange)**

**Situación actual sin Pulsar:**
```
Usuario guarda TipoCambio → Se guarda en BD → Fin
```

**Con Pulsar:**
```
Usuario guarda TipoCambio → Se guarda en BD → 
    → Se publica evento en Pulsar →
        → Otros servicios pueden reaccionar:
           • Actualizar caché de tipos de cambio
           • Notificar a usuarios suscritos a alertas
           • Recalcular montos en otras monedas pendientes
           • Sincronizar con sistemas externos
```

**Beneficio:** Cuando se actualiza un tipo de cambio, múltiples servicios pueden reaccionar automáticamente sin que el usuario tenga que esperar.

---

### 2. **Cargas Masivas (Bulk Uploads)**

**Situación actual sin Pulsar:**
```
Usuario sube archivo CSV → Validación → Guardar en BD → 
    → Procesar cada línea (puede tardar minutos) → 
        → Usuario espera en la pantalla → Fin
```

**Con Pulsar (Arquitectura Futura):**
```
Usuario sube archivo CSV → Validación → Guardar en BD → 
    → Publicar evento en Pulsar "carga iniciada" → 
        → Responder al usuario inmediatamente ("Procesando en segundo plano")
            → Worker consume evento desde Pulsar →
                → Procesa líneas asíncronamente →
                    → Enriquece datos con tipos de cambio →
                        → Publica evento "carga completada" →
                            → Notifica al usuario por email/dashboard
```

**Beneficios:**
- ✅ **Usuario no espera:** Puede seguir trabajando mientras se procesa
- ✅ **Escalable:** Puedes tener múltiples workers procesando cargas en paralelo
- ✅ **Resiliente:** Si un worker falla, el mensaje no se pierde (Pulsar lo guarda)
- ✅ **Rastreable:** Todos los eventos quedan registrados

---

### 3. **Actualización de Gráficos y Dashboards**

**Situación actual:**
```
Usuario actualiza calificación → Se guarda en BD →
    → Dashboard muestra datos desactualizados hasta que se recarga la página
```

**Con Pulsar:**
```
Usuario actualiza calificación → Se guarda en BD →
    → Publica evento "calificación actualizada" →
        → Dashboard escucha el evento →
            → Actualiza gráficos en tiempo real SIN recargar página
```

**Beneficio:** Dashboards más reactivos y actualizados automáticamente.

---

## 📊 Comparación: Con vs Sin Pulsar

### Escenario 1: Actualizar Tipo de Cambio

| Aspecto | Sin Pulsar | Con Pulsar |
|---------|------------|------------|
| **Tiempo de respuesta** | Usuario espera todo el proceso (1-2 seg) | Usuario recibe respuesta inmediata (< 0.1 seg) |
| **Procesos en paralelo** | Secuencial (uno tras otro) | Paralelo (múltiples servicios trabajan a la vez) |
| **Si falla un servicio** | Todo falla | Solo ese servicio falla, el resto sigue |
| **Rastreabilidad** | Solo en logs de Django | Eventos persistentes en Pulsar |

### Escenario 2: Carga Masiva de 10,000 filas

| Aspecto | Sin Pulsar | Con Pulsar |
|---------|------------|------------|
| **Experiencia usuario** | Espera 2-5 minutos viendo "Procesando..." | Recibe confirmación inmediata, notificación al terminar |
| **Rendimiento** | Un solo proceso bloquea el servidor | Múltiples workers procesan en paralelo |
| **Si falla durante proceso** | Se pierde todo el trabajo | Mensaje se guarda, puede reintentar |
| **Escalabilidad** | Difícil de escalar | Fácil: agregar más workers |

---

## 💡 Beneficios Específicos para NUAM

### 1. **Desacoplamiento de Servicios**

**Sin Pulsar:**
```python
# En views.py, todo está acoplado:
def crear_tipo_cambio(request):
    tipo_cambio.save()  # Guarda en BD
    actualizar_cache()  # Si falla esto, todo falla
    notificar_usuarios()  # Si falla esto, todo falla
    recalcular_montos()  # Si falla esto, todo falla
    return response
```

**Con Pulsar:**
```python
# views.py solo se encarga de guardar:
def crear_tipo_cambio(request):
    tipo_cambio.save()  # Guarda en BD
    # La señal automáticamente publica en Pulsar
    return response  # Responde inmediatamente

# Otros servicios consumen por separado:
# - servicio_cache.py consume y actualiza caché
# - servicio_notificaciones.py consume y envía emails
# - servicio_calculos.py consume y recalcula montos
```

**Beneficio:** Cada servicio es independiente. Si uno falla, los demás siguen funcionando.

---

### 2. **Procesamiento Asíncrono**

**Ejemplo Real:**
Imagina que un usuario sube un archivo Excel con 5,000 calificaciones que necesitan:
- Validar datos
- Consultar tipos de cambio para cada fecha
- Calcular factores de actualización
- Generar reportes
- Enviar notificaciones

**Sin Pulsar:** Todo esto sucede en la misma petición HTTP. El usuario espera 3-5 minutos.

**Con Pulsar:** 
- Usuario sube archivo → Recibe confirmación inmediata
- Procesamiento ocurre en segundo plano (workers)
- Usuario recibe notificación cuando termina
- Puede seguir trabajando mientras tanto

---

### 3. **Tolerancia a Fallos**

**Sin Pulsar:**
```
Worker procesando carga → Se cae el servidor → 
    → Se pierde el trabajo → Usuario tiene que subir archivo de nuevo
```

**Con Pulsar:**
```
Worker procesando carga → Se cae el servidor →
    → Mensaje sigue en Pulsar (no se pierde) →
        → Nuevo worker lo toma automáticamente →
            → Continúa desde donde quedó
```

**Beneficio:** Mayor confiabilidad y menos frustración para usuarios.

---

### 4. **Monitoreo y Auditoría**

Pulsar guarda todos los mensajes, entonces puedes:
- Ver qué eventos ocurrieron y cuándo
- Replay eventos si es necesario
- Auditar qué servicios procesaron qué eventos
- Detectar patrones y problemas

---

## 🎯 Casos de Uso Reales en NUAM

### Caso 1: Actualización de Tipo de Cambio en Tiempo Real

**Problema:** Cuando actualizas un tipo de cambio, hay muchas calificaciones que podrían necesitar recalcularse.

**Con Pulsar:**
1. Administrador actualiza tipo de cambio USD/CLP
2. Evento se publica en Pulsar
3. Servicio de cálculos consume el evento
4. Identifica calificaciones afectadas
5. Recalcula factores de actualización
6. Publica evento "cálculos completados"
7. Dashboard se actualiza automáticamente

**Resultado:** Todo ocurre automáticamente sin intervención manual.

---

### Caso 2: Carga Masiva con Enriquecimiento de Datos

**Problema:** Al cargar un archivo CSV, algunos datos vienen incompletos y necesitan enriquecerse con información externa.

**Con Pulsar:**
1. Operador sube CSV con 2,000 calificaciones
2. Sistema valida y guarda estructura en BD
3. Publica evento "carga iniciada" con IDs a procesar
4. Usuario recibe confirmación inmediata
5. Worker consume evento y procesa cada registro:
   - Consulta tipo de cambio para fecha específica
   - Valida datos contra APIs externas
   - Enriquece información faltante
6. Publica eventos de progreso (cada 100 registros)
7. Dashboard muestra progreso en tiempo real
8. Al finalizar, publica "carga completada"
9. Usuario recibe notificación

**Resultado:** Procesamiento eficiente, visible y no bloqueante.

---

## 🚀 Ventajas a Futuro

### Escalabilidad Horizontal

Cuando NUAM crezca y tengas muchos usuarios:
- Sin Pulsar: Necesitas un servidor más potente (escalado vertical)
- Con Pulsar: Agregas más workers (servidores más pequeños, escalado horizontal)

### Integración con Microservicios

Si en el futuro separas NUAM en microservicios:
- Servicio de Calificaciones
- Servicio de Tipos de Cambio
- Servicio de Reportes
- Servicio de Notificaciones

Pulsar los conecta a todos sin que se conozcan entre sí.

### Event-Driven Architecture

Pulsar permite evolucionar hacia una arquitectura basada en eventos, que es más flexible y mantenible a largo plazo.

---

## ❓ ¿Cuándo NO necesitas Pulsar?

Pulsar NO es necesario si:
- ✅ Tu aplicación es simple y no tiene procesos pesados
- ✅ Los usuarios pueden esperar operaciones síncronas
- ✅ No necesitas escalar horizontalmente
- ✅ No hay múltiples servicios que necesiten comunicarse

**Pero en NUAM, donde hay:**
- Cargas masivas de archivos grandes
- Necesidad de actualización en tiempo real
- Múltiples fuentes de tipos de cambio
- Procesos que pueden tardar varios minutos

**Pulsar SÍ aporta valor real.**

---

## 📝 Resumen

**Pulsar en NUAM permite:**

1. ✅ **Comunicación asíncrona** entre componentes
2. ✅ **Procesamiento en segundo plano** sin bloquear al usuario
3. ✅ **Resiliencia** ante fallos (mensajes no se pierden)
4. ✅ **Escalabilidad** horizontal (agregar más workers)
5. ✅ **Desacoplamiento** de servicios (cada uno funciona independiente)
6. ✅ **Trazabilidad** de eventos (auditoría completa)

**En pocas palabras:** Pulsar hace que NUAM sea más rápido, confiable y escalable para crecer en el futuro.

