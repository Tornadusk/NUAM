# Guía de Instalación de Apache Pulsar para NUAM

## ⚠️ IMPORTANTE

**Pulsar es OPCIONAL** - Solo necesario si vas a implementar:
- Productores de mensajes (p. ej., cuando se completa una carga masiva)
- Consumidores de mensajes (p. ej., microservicio de enriquecimiento de cargas)
- Integración con microservicios

Si solo vas a usar el **microservicio de gráficos/métricas** (que se conecta directamente a la BD), **NO necesitas Pulsar**.

## ¿Por qué Docker?

✅ **Ventajas:**
- Funciona igual en Windows, Linux y Mac
- No requiere instalación manual
- Tu profesor puede ejecutarlo fácilmente con `docker-compose up`
- Configuración lista en el repositorio
- Fácil de detener/iniciar

❌ **Desventajas de instalación nativa:**
- Requiere WSL2 en Windows (más complejo)
- Diferentes instrucciones para cada SO
- Puede dar problemas de configuración
- Tu profesor tendría que instalarlo manualmente

## Instalación con Docker (RECOMENDADO)

### Windows

1. **Instalar Docker Desktop:**
   - Descarga desde: https://www.docker.com/products/docker-desktop/
   - Instala y reinicia la computadora
   - Asegúrate de que Docker Desktop esté corriendo (icono en la bandeja)

2. **Levantar Pulsar:**
   ```powershell
   # En la raíz del proyecto NUAM
   docker-compose up -d
   ```

3. **Verificar:**
   ```powershell
   docker ps
   # Deberías ver el contenedor "nuam-pulsar" corriendo
   ```

### Linux/Mac

1. **Instalar Docker (si no lo tienes):**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose -y
   
   # Agregar tu usuario al grupo docker
   sudo usermod -aG docker $USER
   # Cierra sesión y vuelve a iniciar
   ```

2. **Levantar Pulsar:**
   ```bash
   docker-compose up -d
   ```

3. **Verificar:**
   ```bash
   docker ps
   docker logs nuam-pulsar
   ```

## Configuración

### Puertos

- **6650**: Puerto Pulsar (productores/consumidores)
- **8080**: Puerto Admin API (http://localhost:8080)

### Verificar que funciona

```bash
# Ver logs
docker logs nuam-pulsar

# Deberías ver algo como:
# "Successfully started the Pulsar standalone service."
```

Accede a: http://localhost:8080/admin/v3/clusters

## Comandos útiles

```bash
# Iniciar Pulsar
docker-compose up -d

# Detener Pulsar
docker-compose down

# Ver logs en tiempo real
docker logs -f nuam-pulsar

# Reiniciar Pulsar
docker-compose restart

# Ver estado
docker ps | grep pulsar
```

## Solución de problemas

### Error: "Cannot connect to Docker daemon"

**Windows:**
- Asegúrate de que Docker Desktop esté corriendo
- Reinicia Docker Desktop

**Linux:**
- Verifica que Docker esté corriendo: `sudo systemctl status docker`
- Inicia Docker: `sudo systemctl start docker`
- Verifica permisos: `sudo usermod -aG docker $USER` (y cierra sesión)

### Error: "Port already in use"

```bash
# Ver qué está usando el puerto
# Windows PowerShell
netstat -ano | findstr :6650

# Linux/Mac
lsof -i :6650

# Cambiar el puerto en docker-compose.yml si es necesario
```

### Contenedor no inicia

```bash
# Ver logs detallados
docker logs nuam-pulsar

# Reiniciar desde cero
docker-compose down
docker-compose up -d
```

## Alternativas (NO recomendadas para evaluación)

### WSL2 + Instalación nativa (Windows)

⚠️ Solo si NO puedes usar Docker.

1. Instalar WSL2:
   ```powershell
   wsl --install -d Ubuntu
   ```

2. Reiniciar computadora

3. Descargar Pulsar 4.1.1:
   - URL: https://archive.apache.org/dist/pulsar/pulsar-4.1.1/
   - Archivo: `apache-pulsar-4.1.1-bin.tar.gz` (~234MB)

4. En WSL:
   ```bash
   tar -xzf apache-pulsar-4.1.1-bin.tar.gz
   cd apache-pulsar-4.1.1
   bin/pulsar standalone
   ```

### Instalación nativa en Linux

⚠️ Solo si NO puedes usar Docker.

```bash
cd /tmp
wget https://archive.apache.org/dist/pulsar/pulsar-4.1.1/apache-pulsar-4.1.1-bin.tar.gz
tar -xzf apache-pulsar-4.1.1-bin.tar.gz
cd apache-pulsar-4.1.1
bin/pulsar standalone
```

## Para tu profesor (revisión en Linux)

Tu profesor solo necesita:

1. Tener Docker instalado
2. Ejecutar: `docker-compose up -d`
3. Verificar: `docker ps`

**Eso es todo.** No necesita instalar Pulsar manualmente.

## Integración con Django

Cuando implementes los productores/consumidores, usa:

```python
# En settings.py (agregar cuando implementes Pulsar)
PULSAR_SERVICE_URL = 'pulsar://localhost:6650'
PULSAR_ADMIN_URL = 'http://localhost:8080'
```

## Recursos

- Documentación oficial: https://pulsar.apache.org/docs/
- Docker Hub: https://hub.docker.com/r/apachepulsar/pulsar


