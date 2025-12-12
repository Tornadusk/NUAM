# 🔧 Troubleshooting: Pulsar se Apaga o No Está Disponible

## Problema: Pulsar Admin no está disponible o Pulsar se apaga constantemente

## ⚠️ ERROR CRÍTICO: `nuam-pulsar exited with code 1`

**Síntomas:**
- El contenedor se detiene inmediatamente después de iniciar
- Logs muestran `Exception: java.lang.IllegalThreadStateException` y mensajes de shutdown
- Error: "Pulsar Admin API no disponible"
- El contenedor aparece como detenido en Docker Desktop

**Causa más común:** Volúmenes de datos corruptos o configuración incorrecta.

**Solución rápida:**
```bash
# 1. Detener y eliminar contenedores y volúmenes
docker-compose down -v

# 2. Eliminar volúmenes de Pulsar específicamente (opcional, más agresivo)
docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>/dev/null || true

# 3. Limpiar sistema Docker
docker system prune -f

# 4. Recrear desde cero
docker-compose up -d

# 5. Ver logs en tiempo real para verificar que inicia correctamente
docker logs -f nuam-pulsar
```

**Si sigue fallando, ver errores anteriores en los logs:**
```bash
# Ver TODOS los logs desde el inicio (no solo los últimos)
docker logs nuam-pulsar 2>&1 | head -200

# O buscar errores específicos
docker logs nuam-pulsar 2>&1 | grep -i "error\|exception\|failed\|fatal"
```

---

## ✅ Diagnóstico Paso a Paso

### 1. Verificar que Docker Desktop esté corriendo

**Windows:**
- Busca el icono de Docker en la bandeja del sistema (área de notificaciones)
- Si no está visible, abre Docker Desktop manualmente
- Espera a que Docker Desktop termine de iniciar (icono deja de animarse)

**Linux:**
```bash
# Verificar que Docker está corriendo
sudo systemctl status docker

# Si no está corriendo, iniciarlo
sudo systemctl start docker
```

---

### 2. Verificar que el contenedor está corriendo

```bash
# Ver todos los contenedores (activos e inactivos)
docker ps -a

# Deberías ver algo como:
# CONTAINER ID   IMAGE                        STATUS
# abc123def456   apachepulsar/pulsar:3.2.0    Up 5 minutes
```

**Si el contenedor NO aparece o está "Exited":**
```bash
# Ver los logs del contenedor para entender por qué se detuvo
docker logs nuam-pulsar

# O si el contenedor tiene otro nombre
docker ps -a  # Ver todos los contenedores
docker logs <CONTAINER_ID>  # Reemplazar con el ID real
```

---

### 3. Verificar que los puertos no estén ocupados

**Windows (PowerShell):**
```powershell
# Verificar puerto 6650
netstat -ano | findstr :6650

# Verificar puerto 8080
netstat -ano | findstr :8080
```

**Linux/Mac:**
```bash
# Verificar puerto 6650
lsof -i :6650
# o
sudo netstat -tulpn | grep :6650

# Verificar puerto 8080
lsof -i :8080
# o
sudo netstat -tulpn | grep :8080
```

**Si los puertos están ocupados:**
- Identifica qué proceso está usando el puerto (aparece en el comando)
- Detén ese proceso o cambia los puertos en `docker-compose.yml`

---

### 4. Verificar los logs de Pulsar para errores

```bash
# Ver logs en tiempo real (últimas 100 líneas)
docker logs --tail 100 nuam-pulsar

# Ver logs completos
docker logs nuam-pulsar

# Seguir logs en tiempo real
docker logs -f nuam-pulsar
```

**Errores comunes a buscar:**
- `OutOfMemoryError` o `java.lang.OutOfMemoryError`
- `Address already in use` (puertos ocupados)
- `Cannot bind to address` (problemas de red)
- `Permission denied` (problemas de permisos)

---

### 5. Verificar recursos del sistema

**Windows:**
- Abre el Administrador de Tareas (Ctrl+Shift+Esc)
- Verifica uso de CPU, RAM y disco
- Pulsar necesita al menos **1-2 GB de RAM** disponible

**Linux:**
```bash
# Ver uso de memoria
free -h

# Ver uso de CPU
top
# o
htop
```

---

## 🔄 Soluciones Comunes

### Solución 1: Pulsar se detiene por falta de memoria

**Síntomas:**
- Logs muestran `OutOfMemoryError`
- El contenedor se detiene poco después de iniciar
- Uso de memoria muy alto antes de detenerse

**Solución:**

Editar `docker-compose.yml` para aumentar memoria:

```yaml
services:
  pulsar:
    image: apachepulsar/pulsar:3.2.0
    container_name: nuam-pulsar
    ports:
      - "6650:6650"
      - "8080:8080"
    command: bin/pulsar standalone
    environment:
      - PULSAR_MEM="-Xms512m -Xmx1g -XX:MaxDirectMemorySize=512m"
    volumes:
      - pulsar-data:/pulsar/data
      - pulsar-conf:/pulsar/conf
    # ... resto de la configuración
```

**Reiniciar:**
```bash
docker-compose down
docker-compose up -d
```

---

### Solución 2: Puertos ocupados

**Síntomas:**
- Error: `bind: address already in use`
- El contenedor no puede iniciar

**Solución A: Cambiar puertos en docker-compose.yml**

```yaml
services:
  pulsar:
    # ...
    ports:
      - "6651:6650"    # Cambiado de 6650 a 6651
      - "8081:8080"    # Cambiado de 8080 a 8081
```

**Actualizar settings.py:**
```python
PULSAR_SERVICE_URL = config('PULSAR_SERVICE_URL', default='pulsar://localhost:6651')
PULSAR_ADMIN_URL = config('PULSAR_ADMIN_URL', default='http://localhost:8081')
```

**Solución B: Detener el proceso que usa el puerto**

**Windows:**
```powershell
# Encontrar el proceso (reemplazar <PID> con el número que aparece en netstat)
taskkill /PID <PID> /F
```

**Linux:**
```bash
# Encontrar el proceso
sudo lsof -i :8080

# Detener el proceso (reemplazar <PID>)
sudo kill -9 <PID>
```

---

### Solución 3: Contenedor se detiene inmediatamente (`exited with code 1`)

**Síntomas:**
- El contenedor inicia pero se detiene en segundos
- Estado: `Exited (1)` o similar
- Logs muestran `java.lang.IllegalThreadStateException` y shutdown anormal

**⚠️ Este es el error más común - Causado por volúmenes corruptos o problemas de inicialización**

**Diagnóstico:**
```bash
# Ver logs completos desde el inicio (buscar el error REAL, no solo el shutdown)
docker logs nuam-pulsar 2>&1 | head -100

# Verificar errores específicos
docker logs nuam-pulsar 2>&1 | grep -i "error\|exception\|failed\|fatal" | head -20
```

**Solución A: Limpiar volúmenes y recrear (⭐ RECOMENDADO)**

```bash
# 1. Detener y eliminar contenedores y volúmenes
docker-compose down -v

# 2. Verificar que los volúmenes se eliminaron
docker volume ls | grep pulsar
# No debería mostrar volúmenes de pulsar

# 3. Limpiar sistema Docker (elimina contenedores, imágenes y volúmenes no usados)
docker system prune -a --volumes -f

# 4. Recrear todo desde cero
docker-compose up -d

# 5. Ver logs en tiempo real (esperar 30-60 segundos para que Pulsar inicie completamente)
docker logs -f nuam-pulsar
```

**Solución B: Si Solución A no funciona, aumentar memoria y recursos**

Editar `docker-compose.yml`:

```yaml
services:
  pulsar:
    image: apachepulsar/pulsar:3.2.0
    container_name: nuam-pulsar
    ports:
      - "6650:6650"
      - "8080:8080"
    command: bin/pulsar standalone
    environment:
      - PULSAR_MEM="-Xms512m -Xmx1024m -XX:MaxDirectMemorySize=512m"
      - PULSAR_GC="-XX:+UseG1GC -XX:MaxGCPauseMillis=10"
    volumes:
      - pulsar-data:/pulsar/data
      - pulsar-conf:/pulsar/conf
    healthcheck:
      test: ["CMD", "bin/pulsar-admin", "brokers", "healthcheck"]
      interval: 30s  # Aumentado para dar más tiempo
      timeout: 10s
      retries: 10
      start_period: 60s  # Esperar 60 segundos antes de empezar health checks
    mem_limit: 2g  # Límite de memoria
    mem_reservation: 1g  # Reserva mínima
    networks:
      - nuam-network
```

Luego:
```bash
docker-compose down -v
docker-compose up -d
docker logs -f nuam-pulsar
```

**Solución C: Usar versión diferente de Pulsar (última opción)**

Si nada funciona, intentar con una versión más reciente:

```yaml
services:
  pulsar:
    image: apachepulsar/pulsar:3.3.0  # O la última versión disponible
    # ... resto igual
```

---

### Solución 4: Docker Desktop no está corriendo (Windows)

**Síntomas:**
- Error: `Cannot connect to the Docker daemon`
- `docker ps` no funciona

**Solución:**
1. Abre Docker Desktop manualmente
2. Espera a que termine de inicializar (icono deja de animarse)
3. Verifica que esté corriendo: `docker ps`

**Si Docker Desktop no inicia:**
- Reinicia Docker Desktop
- Verifica que WSL2 esté habilitado (Docker Desktop requiere WSL2 en Windows)
- Revisa los logs de Docker Desktop (Settings → Troubleshoot)

---

### Solución 5: Problemas de permisos (Linux)

**Síntomas:**
- Error: `Permission denied`
- No puedes ejecutar comandos docker sin `sudo`

**Solución:**
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar que funciona sin sudo
docker ps
```

---

### Solución 6: Pulsar Admin API no responde (puerto 8080)

**Síntomas:**
- El contenedor está corriendo
- Pero `http://localhost:8080` no responde

**Verificación:**
```bash
# Verificar que el puerto está escuchando
curl http://localhost:8080/admin/v2/brokers/health

# O abrir en navegador:
# http://localhost:8080/admin/v2/brokers/health
```

**Si no responde:**

1. **Verificar que el contenedor está realmente corriendo:**
   ```bash
   docker ps | grep pulsar
   ```

2. **Verificar que el puerto está mapeado correctamente:**
   ```bash
   docker port nuam-pulsar
   # Debe mostrar: 8080/tcp -> 0.0.0.0:8080
   ```

3. **Reiniciar el contenedor:**
   ```bash
   docker restart nuam-pulsar
   docker logs -f nuam-pulsar
   ```

4. **Si sigue sin funcionar, verificar logs:**
   ```bash
   docker logs nuam-pulsar | grep -i "admin\|8080\|error"
   ```

---

## 🚀 Script de Reinicio Automático

### Windows (PowerShell)

```powershell
# Desde la raíz del proyecto
cd scripts
.\restart_pulsar.ps1
```

### Linux/Mac (Bash)

```bash
# Desde la raíz del proyecto
cd scripts
chmod +x restart_pulsar.sh
./restart_pulsar.sh
```

Este script:
1. Detiene y elimina contenedores y volúmenes
2. Limpia volúmenes corruptos de Pulsar
3. Opcionalmente limpia el sistema Docker
4. Recrea los contenedores
5. Verifica que Pulsar esté corriendo
6. Verifica que Admin API esté disponible

---

## 🚀 Comandos Útiles de Diagnóstico

### Ver estado completo de Docker

```bash
# Ver contenedores activos
docker ps

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Ver uso de recursos
docker stats nuam-pulsar

# Ver información del contenedor
docker inspect nuam-pulsar
```

### Limpiar y empezar desde cero

```bash
# Detener y eliminar contenedores, redes y volúmenes
docker-compose down -v

# Eliminar imágenes (opcional)
docker rmi apachepulsar/pulsar:3.2.0

# Limpiar sistema Docker (elimina contenedores, imágenes, volúmenes no usados)
docker system prune -a --volumes

# Recrear desde cero
docker-compose up -d

# Ver logs
docker logs -f nuam-pulsar
```

### Verificar conectividad desde Django

```bash
# Probar conexión desde Python (dentro del venv)
python manage.py shell

>>> from django.conf import settings
>>> import requests
>>> 
>>> # Probar Admin API
>>> response = requests.get(f"{settings.PULSAR_ADMIN_URL}/admin/v2/brokers/health")
>>> print(response.status_code)  # Debe ser 200
>>> print(response.text)
```

---

## ✅ Checklist de Verificación

Usa este checklist para diagnosticar el problema:

- [ ] Docker Desktop está corriendo (Windows) o Docker está activo (Linux)
- [ ] El contenedor `nuam-pulsar` aparece en `docker ps`
- [ ] Los puertos 6650 y 8080 no están ocupados por otro proceso
- [ ] El contenedor tiene suficientes recursos (RAM, CPU)
- [ ] Los logs no muestran errores críticos (`docker logs nuam-pulsar`)
- [ ] `http://localhost:8080/admin/v2/brokers/health` responde (debe devolver JSON)
- [ ] `settings.PULSAR_SERVICE_URL` y `settings.PULSAR_ADMIN_URL` son correctos
- [ ] No hay problemas de permisos (Linux)

---

## 📝 Verificación Final

**Si todo está bien, deberías poder:**

1. **Ver el contenedor corriendo:**
   ```bash
   docker ps | grep pulsar
   ```

2. **Acceder a la Admin API:**
   ```bash
   curl http://localhost:8080/admin/v2/brokers/health
   # Debe responder: {"status":"ok"}
   ```

3. **Ver topics en el dashboard de Pulsar:**
   - Abrir: `http://127.0.0.1:8000/microservicio/pulsar/`
   - Debe mostrar el estado de conexión como "Conectado"

4. **Verificar desde Django:**
   ```bash
   python manage.py shell
   >>> from microservicio.pulsar import get_pulsar_client
   >>> client = get_pulsar_client()
   >>> print("Cliente Pulsar:", client)  # No debe ser None
   ```

---

## 🆘 Si Nada Funciona

Si después de intentar todas las soluciones Pulsar sigue sin funcionar:

1. **Verificar versión de Docker:**
   ```bash
   docker --version
   docker-compose --version
   ```
   - Docker debe ser >= 20.10
   - Docker Compose debe ser >= 2.0

2. **Reinstalar Docker Desktop (Windows):**
   - Descargar última versión desde: https://www.docker.com/products/docker-desktop/
   - Desinstalar versión anterior
   - Instalar nueva versión
   - Reiniciar computadora

3. **Probar con una configuración mínima:**

   Crear `docker-compose.test.yml`:
   ```yaml
   version: '3.8'
   services:
     pulsar:
       image: apachepulsar/pulsar:3.2.0
       container_name: nuam-pulsar-test
       ports:
         - "6650:6650"
         - "8080:8080"
       command: bin/pulsar standalone
   ```

   Ejecutar:
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   docker logs -f nuam-pulsar-test
   ```

4. **Contactar soporte o revisar documentación oficial:**
   - Documentación Pulsar: https://pulsar.apache.org/docs/
   - Docker Hub: https://hub.docker.com/r/apachepulsar/pulsar

---

## 📚 Referencias

- `docker-compose.yml` - Configuración de Pulsar
- `proyecto_nuam/settings.py` - Configuración de conexión
- `microservicio/pulsar/client.py` - Cliente Pulsar de Django
- Documentación oficial: https://pulsar.apache.org/docs/

