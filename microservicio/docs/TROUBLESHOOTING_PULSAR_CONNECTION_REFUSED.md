# 🔧 Troubleshooting: "Connection refused" - Pulsar No Está Corriendo

## Problema: `Connection refused` al intentar conectar con Pulsar

**Síntomas:**
- Errores en los logs: `Failed to establish connection: Connection refused`
- Mensaje: `Error Checking/Getting Partition Metadata while creating producer on persistent://public/default/nuam-tipo-cambio -- TimeOut`
- Django intenta publicar mensajes a Pulsar pero falla

**Causa:** Pulsar no está corriendo o no está disponible en `pulsar://localhost:6650`.

---

## ✅ Solución Rápida

### Paso 1: Verificar si Pulsar está corriendo

```bash
docker ps | grep pulsar
```

**Si NO aparece el contenedor:**
- Pulsar no está corriendo
- Ve al Paso 2

**Si aparece pero está "Restarting":**
- El contenedor está en ciclo de reinicio
- Ve a: `microservicio/docs/TROUBLESHOOTING_PULSAR.md` - Sección "Ciclo de Reinicio"
- Ejecuta: `scripts/solucionar_restart_loop.ps1` o `scripts/solucionar_restart_loop.sh`

**Si aparece "Up":**
- El contenedor está corriendo
- Verifica que el puerto 6650 esté mapeado correctamente
- Ve al Paso 3

---

### Paso 2: Iniciar Pulsar

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que se inició
docker ps | grep pulsar

# Esperar 60 segundos para que Pulsar termine de iniciar
sleep 60

# Verificar logs
docker logs nuam-pulsar --tail 50
```

---

### Paso 3: Verificar que el puerto 6650 esté disponible

**Windows:**
```powershell
netstat -ano | findstr :6650
```

**Linux/Mac:**
```bash
lsof -i :6650
# o
netstat -tulpn | grep :6650
```

**Si el puerto está ocupado por otro proceso:**
- Identifica el proceso (aparece en el comando anterior)
- Detén ese proceso o cambia el puerto en `docker-compose.yml`

---

### Paso 4: Verificar conectividad

```bash
# Verificar que el contenedor está escuchando en el puerto
docker port nuam-pulsar

# Debería mostrar:
# 6650/tcp -> 0.0.0.0:6650
# 8080/tcp -> 0.0.0.0:8080
```

---

## 🔍 Diagnóstico Detallado

### Verificar estado completo del contenedor

```bash
# Ver todos los contenedores (activos e inactivos)
docker ps -a | grep pulsar

# Ver información detallada del contenedor
docker inspect nuam-pulsar

# Ver logs completos
docker logs nuam-pulsar --tail 100
```

### Verificar configuración de docker-compose

Asegúrate de que `docker-compose.yml` tenga:

```yaml
services:
  pulsar:
    ports:
      - "6650:6650"    # Puerto Pulsar (productores/consumidores)
      - "8080:8080"    # Puerto Pulsar Admin (RPC)
```

---

## ⚠️ Nota Importante

**Estos errores son NORMALES si:**
- Pulsar no está corriendo (el contenedor no se ha iniciado)
- Django intenta publicar mensajes pero Pulsar está detenido

**NO son críticos:**
- Django seguirá funcionando normalmente
- Los mensajes simplemente no se publicarán a Pulsar hasta que esté disponible
- El sistema tiene fallback automático

---

## 🎯 Checklist Rápido

- [ ] ¿El contenedor `nuam-pulsar` está corriendo? (`docker ps | grep pulsar`)
- [ ] ¿El puerto 6650 está mapeado? (`docker port nuam-pulsar`)
- [ ] ¿El puerto 6650 no está ocupado por otro proceso?
- [ ] ¿Ejecutaste `docker-compose up -d`?
- [ ] ¿Esperaste 60 segundos después de iniciar para que Pulsar termine de iniciar?

---

## 💡 Soluciones Comunes

### Solución 1: Iniciar Pulsar

```bash
docker-compose up -d
sleep 60
docker logs nuam-pulsar
```

### Solución 2: Reiniciar limpiamente

```bash
# Usar el script automático
cd scripts
.\restart_pulsar.ps1   # Windows
# o
./restart_pulsar.sh    # Linux/Mac
```

### Solución 3: Si el contenedor está en ciclo de reinicio

```bash
cd scripts
.\solucionar_restart_loop.ps1   # Windows
# o
./solucionar_restart_loop.sh    # Linux/Mac
```

---

## 📝 Notas Adicionales

- Los errores de "Connection refused" **no afectan el funcionamiento de Django**
- Django puede funcionar sin Pulsar (Pulsar es opcional para notificaciones)
- Si necesitas Pulsar, simplemente inícialo con `docker-compose up -d`
- Los mensajes se publicarán automáticamente cuando Pulsar esté disponible

