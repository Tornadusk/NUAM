# Cambios en Docker para exchange-rate-service

## Resumen

Se agregó un **volumen montado** al contenedor `nuam-exchange-rate-service` en `docker-compose.yml` para habilitar **hot-reload** (recarga automática de código).

## Cambio Realizado

En `docker-compose.yml`, se agregó la sección `volumes` al servicio `exchange-rate-service`:

```yaml
exchange-rate-service:
  build: ./services/exchange-rate-service
  container_name: nuam-exchange-rate-service
  ports:
    - "5100:5100"
  environment:
    - EXCHANGERATE_API_KEY=${EXCHANGERATE_API_KEY:-effbc5f153954a92a297e710}
    - FIXER_API_KEY=${FIXER_API_KEY:-}
  volumes:
    - ./services/exchange-rate-service:/app  # ← NUEVO: Monta el código fuente
  restart: unless-stopped
  networks:
    - nuam-network
```

## ¿Qué significa esto?

### Antes:
- El código se copiaba en la imagen Docker al construir (`COPY . /app` en Dockerfile)
- Si cambiabas el código, tenías que **reconstruir la imagen** (`docker-compose build`) y **reiniciar el contenedor**

### Ahora:
- El código fuente se **monta como volumen** directamente desde tu máquina
- Cuando cambias código en `services/exchange-rate-service/`, **se refleja automáticamente** en el contenedor
- FastAPI con `reload=True` detecta cambios y **recarga automáticamente** el servicio
- No necesitas reconstruir ni reiniciar manualmente (solo esperar unos segundos)

## ¿Qué NO cambió?

- **NO** se creó un nuevo contenedor
- **NO** se cambió la configuración de red
- **NO** se cambiaron las variables de entorno
- **NO** se modificó el Dockerfile
- Solo se agregó el volumen para desarrollo

## Ventajas

1. **Desarrollo más rápido**: Cambios de código se reflejan inmediatamente
2. **Sin reconstrucción**: No necesitas `docker-compose build` cada vez
3. **Depuración más fácil**: Puedes editar código y ver cambios en tiempo real

## Desventajas

1. **Solo para desarrollo**: En producción, normalmente NO se montan volúmenes de código
2. **Rendimiento ligeramente menor**: El acceso a archivos a través de volúmenes es más lento que dentro de la imagen
3. **Dependencia del host**: El código debe estar presente en el host

## Para aplicar los cambios

Si el contenedor ya estaba corriendo, necesitas recrearlo:

```bash
docker-compose up -d exchange-rate-service
```

Esto recreará el contenedor con la nueva configuración de volumen.

## Verificar que funciona

Puedes verificar que el volumen está montado:

```bash
docker inspect nuam-exchange-rate-service | grep -A 5 "Mounts"
```

O directamente dentro del contenedor:

```bash
docker exec nuam-exchange-rate-service ls -la /app
```

Deberías ver los archivos de `services/exchange-rate-service/` listados.

