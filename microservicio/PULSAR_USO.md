# Guía de Uso de Apache Pulsar en NUAM

## Resumen

Apache Pulsar está integrado en el proyecto NUAM para permitir comunicación asíncrona entre microservicios. Actualmente se utiliza para:

1. **Tipos de Cambio**: Publicar eventos cuando se actualizan tipos de cambio
2. **Cargas Masivas**: Notificar inicio de cargas masivas para enriquecimiento de datos
3. **Actualización de Gráficos**: Notificar cambios que requieren actualizar dashboards

## Configuración

### Variables de Entorno (opcional)

Puedes configurar Pulsar mediante variables de entorno o usar los valores por defecto en `settings.py`:

```bash
# .env
PULSAR_SERVICE_URL=pulsar://localhost:6650
PULSAR_ADMIN_URL=http://localhost:8080
PULSAR_ENABLED=True
PULSAR_OPERATION_TIMEOUT=30
```

### Deshabilitar Pulsar

Si quieres deshabilitar Pulsar temporalmente (útil para desarrollo o si no tienes Pulsar instalado):

```bash
# .env
PULSAR_ENABLED=False
```

Cuando está deshabilitado, las funciones de publicación no generan errores, solo registran warnings en los logs.

## Uso en el Código

### Publicar Mensajes Manualmente

```python
from microservicio.pulsar_client import (
    publicar_tipo_cambio,
    publicar_carga_masiva,
    publicar_actualizacion_graficos,
    publicar_mensaje
)

# Publicar tipo de cambio
publicar_tipo_cambio(
    id_fuente=1,
    moneda_origen='USD',
    moneda_destino='CLP',
    tasa=950.5,
    fecha='2025-12-11'
)

# Publicar carga masiva
publicar_carga_masiva(
    id_carga=123,
    tipo='masiva',
    nombre_archivo='datos.xlsx',
    filas_total=1000,
    usuario_id=5
)

# Publicar mensaje personalizado
publicar_mensaje(
    topic_name='tipo_cambio',
    mensaje={'evento': 'custom', 'datos': 'valor'},
    propiedades={'priority': 'high'}
)
```

### Publicación Automática (Señales)

Las señales de Django publican automáticamente mensajes cuando:

- **TipoCambio**: Se crea un nuevo tipo de cambio → Publica en topic `tipo_cambio`
- **Carga**: Se crea una carga masiva → Publica en topic `carga_masiva`

No necesitas hacer nada especial, funciona automáticamente cuando guardas estos modelos.

## Consumir Mensajes

### Usando el Management Command

```bash
# Consumir mensajes de tipos de cambio
python manage.py consumir_pulsar --topic tipo_cambio

# Consumir mensajes de cargas masivas
python manage.py consumir_pulsar --topic carga_masiva

# Con timeout (se detiene después de 30 segundos sin mensajes)
python manage.py consumir_pulsar --topic tipo_cambio --timeout 30000

# Con nombre de suscripción personalizado
python manage.py consumir_pulsar --topic tipo_cambio --subscription mi-suscripcion
```

### Implementar tu Propio Consumidor

```python
from microservicio.pulsar_client import get_pulsar_client
from django.conf import settings
import json

client = get_pulsar_client()
if client:
    topic = settings.PULSAR_TOPICS['tipo_cambio']
    consumer = client.subscribe(
        topic,
        'mi-suscripcion',
        consumer_type=pulsar.ConsumerType.Shared
    )
    
    while True:
        msg = consumer.receive()
        data = json.loads(msg.data().decode('utf-8'))
        # Procesar mensaje
        print(f"Recibido: {data}")
        consumer.acknowledge(msg)
```

## Topics Configurados

Los topics disponibles están definidos en `settings.PULSAR_TOPICS`:

- `tipo_cambio`: `persistent://public/default/nuam-tipo-cambio`
- `carga_masiva`: `persistent://public/default/nuam-carga-masiva`
- `enriquecimiento_datos`: `persistent://public/default/nuam-enriquecimiento`
- `actualizacion_graficos`: `persistent://public/default/nuam-actualizacion-graficos`

## Verificar que Pulsar Funciona

### 1. Verificar que el contenedor está corriendo

```bash
docker-compose ps
```

Deberías ver `nuam-pulsar` con status `Up` y `healthy`.

### 2. Probar la conexión desde Django

```python
# En el shell de Django: python manage.py shell
from microservicio.pulsar_client import get_pulsar_client

client = get_pulsar_client()
if client:
    print("✓ Pulsar conectado correctamente")
else:
    print("✗ Error al conectar con Pulsar")
```

### 3. Publicar un mensaje de prueba

```python
from microservicio.pulsar_client import publicar_tipo_cambio

resultado = publicar_tipo_cambio(
    id_fuente=1,
    moneda_origen='USD',
    moneda_destino='CLP',
    tasa=950.5,
    fecha='2025-12-11'
)
print(f"Publicado: {resultado}")
```

### 4. Consumir mensajes

En otra terminal:

```bash
python manage.py consumir_pulsar --topic tipo_cambio
```

Luego publica un mensaje desde Django y deberías verlo en el consumidor.

## Troubleshooting

### Error: "pulsar-client no está instalado"

```bash
pip install pulsar-client==3.8.0
```

### Error: "No se pudo conectar con Pulsar"

1. Verifica que Pulsar está corriendo: `docker-compose ps`
2. Verifica la URL en `settings.PULSAR_SERVICE_URL`
3. Si usas Docker, asegúrate de que `PULSAR_SERVICE_URL=pulsar://localhost:6650`

### Los mensajes no se publican

1. Verifica que `PULSAR_ENABLED=True` en settings
2. Revisa los logs de Django para ver errores
3. Prueba publicar manualmente desde el shell

### El consumidor no recibe mensajes

1. Verifica que el topic existe: `curl http://localhost:8080/admin/v2/persistent/public/default/nuam-tipo-cambio/stats`
2. Asegúrate de que el consumidor está usando la misma suscripción o una nueva
3. Verifica que los mensajes se están publicando (revisa logs)

## Próximos Pasos

Para extender la integración:

1. **Agregar más topics**: Edita `settings.PULSAR_TOPICS`
2. **Crear procesadores de mensajes**: Implementa lógica en `management/commands/consumir_pulsar.py`
3. **Agregar más señales**: Crea nuevas señales en `microservicio/signals.py`
4. **Webhooks**: Usa Pulsar Functions para notificar a servicios externos

## Referencias

- [Documentación Apache Pulsar](https://pulsar.apache.org/docs/)
- [Cliente Python Pulsar](https://pulsar.apache.org/docs/client-libraries-python/)
- [Docker Compose para Pulsar](https://pulsar.apache.org/docs/getting-started-standalone/)

