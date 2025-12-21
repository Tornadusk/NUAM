# Comandos para Probar Exportación Sin Docker

## Paso 1: Detener el microservicio

```bash
docker-compose stop exchange-rate-service
```

O si quieres detener todos los microservicios:

```bash
docker-compose stop exchange-rate-service market-info-service
```

## Paso 2: Verificar que está detenido

```bash
docker-compose ps exchange-rate-service
```

Debe mostrar `STATUS: Exited` o `STATUS: Stopped`

## Paso 3: Probar exportación en el navegador

1. Abre el dashboard de Tipos de Cambio
2. Haz clic en "Exportar PDF" (o Excel/HTML)
3. Deberías ver un error: **502 Bad Gateway** o **Connection Refused**

## Paso 4: Ver logs de Django (opcional)

```bash
# Ver logs de Django para confirmar el error
python manage.py runserver_plus --cert-file server.crt --key-file server.key 0.0.0.0:8443
```

O si ya está corriendo, busca en la consola:
- `Connection refused`
- `502 Bad Gateway`
- `requests.exceptions.ConnectionError`

## Paso 5: Volver a iniciar (cuando termines de probar)

```bash
docker-compose up -d exchange-rate-service
```

Verificar que esté corriendo:

```bash
docker-compose ps exchange-rate-service
```

Debe mostrar `STATUS: Up`

---

## Comandos Rápidos

```bash
# Detener
docker-compose stop exchange-rate-service

# Verificar estado
docker-compose ps exchange-rate-service

# Reiniciar
docker-compose up -d exchange-rate-service

# Ver logs del microservicio (para debug)
docker-compose logs exchange-rate-service --tail=50
```

