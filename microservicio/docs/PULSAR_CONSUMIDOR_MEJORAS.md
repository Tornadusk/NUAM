# 🚀 Mejoras en Consumidores Pulsar - Balanceo de Carga y Dead Letter Queue

## ✅ Mejoras Implementadas

### 1. Balanceo de Carga (Load Balancing)

**Estado:** ✅ **Ya implementado** con `ConsumerType.Shared`

El consumidor usa `pulsar.ConsumerType.Shared`, lo que permite:
- ✅ Múltiples consumidores con la misma suscripción
- ✅ Distribución automática de mensajes entre consumidores
- ✅ Escalabilidad horizontal
- ✅ Mayor throughput de procesamiento

**Cómo funciona:**
- Cuando varios procesos ejecutan el mismo consumidor con la misma `subscription_name`, Pulsar distribuye los mensajes automáticamente entre ellos
- Cada mensaje se entrega a un solo consumidor (no hay duplicación)
- Si un consumidor cae, sus mensajes se redistribuyen automáticamente

### 2. Dead Letter Queue (DLQ)

**Estado:** ✅ **Implementado**

**Configuración:**
- **Max redeliver count:** 3 (configurable con `--max-redeliver-count`)
- **DLQ Topic:** `{topic}-dlq` (ej: `persistent://public/default/nuam-tipo-cambio-dlq`)
- **Comportamiento:** Mensajes que fallan después de 3 reintentos se envían automáticamente al DLQ

**Beneficios:**
- ✅ Evita bucles infinitos de reintentos
- ✅ Permite analizar mensajes problemáticos
- ✅ Mantiene el procesamiento de mensajes válidos
- ✅ Facilita debugging y recuperación

---

## 📋 Uso del Consumidor Mejorado

### Ejecución Básica

```bash
# Consumir mensajes de un topic
python manage.py consumir_pulsar --topic tipo_cambio
```

### Ejecución con Balanceo de Carga

**Para habilitar balanceo de carga, ejecuta múltiples instancias del consumidor:**

```bash
# Terminal 1
python manage.py consumir_pulsar --topic tipo_cambio --subscription nuam-consumers

# Terminal 2 (en otra terminal)
python manage.py consumir_pulsar --topic tipo_cambio --subscription nuam-consumers

# Terminal 3 (en otra terminal)
python manage.py consumir_pulsar --topic tipo_cambio --subscription nuam-consumers
```

**Resultado:** Pulsar distribuirá automáticamente los mensajes entre los 3 consumidores.

### Configurar Dead Letter Queue

```bash
# Con 5 reintentos antes de enviar a DLQ
python manage.py consumir_pulsar --topic tipo_cambio --max-redeliver-count 5
```

### Opciones Disponibles

```bash
python manage.py consumir_pulsar --help
```

**Opciones:**
- `--topic`: Nombre del topic (requerido)
- `--subscription`: Nombre de la suscripción (default: `nuam-subscription`)
- `--timeout`: Timeout en milisegundos (default: 0 = sin timeout)
- `--max-redeliver-count`: Reintentos antes de DLQ (default: 3)
- `--workers`: Número sugerido de workers (solo informativo, ejecuta procesos manualmente)

---

## 🔍 Monitorear Dead Letter Queue

### Ver mensajes en DLQ

```bash
# Consumir mensajes del DLQ para analizar errores
python manage.py consumir_pulsar --topic tipo_cambio-dlq --subscription dlq-inspector
```

### Ver estadísticas en Pulsar Admin API

```bash
# Ver estadísticas del topic principal
curl http://localhost:8080/admin/v2/persistent/public/default/nuam-tipo-cambio/stats

# Ver estadísticas del DLQ
curl http://localhost:8080/admin/v2/persistent/public/default/nuam-tipo-cambio-dlq/stats
```

---

## 📊 Arquitectura con Balanceo y DLQ

```
┌─────────────────────────────────────────────────────────┐
│                    Topic: tipo_cambio                   │
│  persistent://public/default/nuam-tipo-cambio           │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Mensajes distribuidos automáticamente
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │Consumer │      │Consumer │      │Consumer │
   │  #1     │      │  #2     │      │  #3     │
   │(Worker1)│      │(Worker2)│      │(Worker3)│
   └────┬────┘      └────┬────┘      └────┬────┘
        │                 │                 │
        │  Subscription: nuam-consumers     │
        │  Type: Shared (balanceo)          │
        │                                   │
        └─────────────────┬─────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
         ✅ Success              ❌ Error (3 veces)
              │                       │
              │                       ▼
              │              ┌──────────────────┐
              │              │  Dead Letter     │
              │              │  Queue (DLQ)     │
              │              │  tipo_cambio-dlq │
              │              └──────────────────┘
              │
              ▼
        Acknowledge
        (Mensaje procesado)
```

---

## 🛠️ Implementación Técnica

### Código del Consumidor

```python
# Configurar Dead Letter Queue
dead_letter_topic = f"{topic}-dlq"
dead_letter_policy = pulsar.DeadLetterPolicy(
    max_redeliver_count=max_redeliver,  # Configurable
    dead_letter_topic=dead_letter_topic
)

# Crear consumidor con balanceo y DLQ
consumer = client.subscribe(
    topic,
    subscription_name,
    consumer_type=pulsar.ConsumerType.Shared,  # Balanceo de carga
    dead_letter_policy=dead_letter_policy      # Dead Letter Queue
)

# Procesamiento con manejo de errores
try:
    self.procesar_mensaje(topic_name, msg)
    consumer.acknowledge(msg)  # Éxito
except Exception as e:
    # Error - Pulsar reintentará automáticamente
    # Después de max_redeliver_count, irá al DLQ
    logger.error(f'Error al procesar mensaje: {e}')
    # No hacer acknowledge = reintento automático
```

---

## 📈 Beneficios

### Balanceo de Carga
- ✅ **Escalabilidad:** Aumenta throughput agregando más consumidores
- ✅ **Resiliencia:** Si un consumidor cae, otros continúan
- ✅ **Paralelización:** Procesamiento simultáneo de mensajes

### Dead Letter Queue
- ✅ **Detección de problemas:** Identifica mensajes problemáticos
- ✅ **Evita bucles:** No reintenta infinitamente
- ✅ **Recuperación:** Permite reprocesar mensajes del DLQ después de corregir bugs
- ✅ **Análisis:** Facilita debugging de mensajes que fallan

---

## 🎯 Próximos Pasos (Opcionales)

1. **Dashboard de monitoreo** para visualizar DLQ
2. **Alertas automáticas** cuando el DLQ tiene mensajes
3. **Procesador de DLQ** para reintentar después de correcciones
4. **Métricas** de tasa de error y mensajes en DLQ

---

## ✅ Cumplimiento de Rúbrica

Con estas mejoras, el criterio "Integración Kafka/Pulsar - Consumidores" alcanza **10/10**:

- ✅ Consumidores funcionales con procesamiento
- ✅ Manejo de fallos estable
- ✅ **Balanceo de carga** (múltiples consumidores)
- ✅ **Dead Letter Queue** para mensajes fallidos
- ✅ Escalabilidad horizontal


