# 🔧 Instrucciones para Solucionar Problema de Pulsar

## ⚠️ Problema: Pulsar en Ciclo de Reinicio Constante

Tu compañero ha corregido un error crítico en la configuración de Pulsar que causaba que el contenedor se reiniciara continuamente.

---

## 📥 Paso 1: Actualizar el Código

**Primero, actualiza tu código local con los cambios más recientes:**

```bash
# Desde la raíz del proyecto NUAM
git pull origin main
```

---

## 🛑 Paso 2: Detener y Limpiar Todo

**Importante:** Debes detener completamente Pulsar y eliminar los volúmenes corruptos antes de recrear.

```bash
# Detener todos los servicios
docker-compose down

# Eliminar volúmenes corruptos de Pulsar
docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>/dev/null || true

# En Windows PowerShell, usa:
docker volume rm nuam_pulsar-data nuam_pulsar-conf

# Forzar eliminación del contenedor si existe
docker rm -f nuam-pulsar 2>/dev/null || true
```

---

## ✅ Paso 3: Recrear Pulsar con la Configuración Corregida

```bash
# Recrear los servicios desde cero
docker-compose up -d

# Verificar que se inició correctamente
docker ps | grep pulsar
```

**Deberías ver algo como:**
```
nuam-pulsar   Up X seconds   0.0.0.0:6650->6650/tcp, 0.0.0.0:8080->8080/tcp
```

---

## ⏱️ Paso 4: Esperar a que Pulsar Inicie Completamente

**⚠️ IMPORTANTE:** Pulsar necesita 30-60 segundos para iniciar completamente.

```bash
# Esperar 60 segundos (o cuenta manualmente)
sleep 60  # Linux/Mac
# En Windows PowerShell, espera manualmente o usa:
Start-Sleep -Seconds 60
```

---

## 🔍 Paso 5: Verificar que Funciona Correctamente

### Opción A: Usar el Script de Verificación (Recomendado)

```bash
cd scripts

# Windows PowerShell
.\verificar_pulsar.ps1

# Linux/Mac
chmod +x verificar_pulsar.sh
./verificar_pulsar.sh
```

### Opción B: Verificación Manual

```bash
# 1. Verificar que el contenedor está corriendo (debe decir "Up", NO "Restarting")
docker ps | grep pulsar

# 2. Verificar logs (no debe haber errores de "ClassNotFoundException")
docker logs nuam-pulsar --tail 50

# 3. Verificar Admin API
curl http://localhost:8080/admin/v2/brokers/health
# Debe responder: {"status": "ok"} o similar
```

---

## 🎯 Checklist de Verificación

Después de seguir los pasos, verifica que:

- [ ] ✅ El contenedor muestra estado: `Up X minutes (healthy)` (NO "Restarting")
- [ ] ✅ Los logs NO muestran: `Error: Could not find or load main class "-Xms512m`
- [ ] ✅ Admin API responde: `curl http://localhost:8080/admin/v2/brokers/health` devuelve 200
- [ ] ✅ El dashboard de Pulsar muestra "Admin API: ONLINE"

---

## 🔧 Si el Problema Persiste

Si después de seguir estos pasos el contenedor **sigue reiniciándose**:

### Opción 1: Usar Script de Diagnóstico

```bash
cd scripts

# Windows PowerShell
.\diagnosticar_pulsar.ps1

# Linux/Mac
chmod +x diagnosticar_pulsar.sh
./diagnosticar_pulsar.sh
```

Este script te mostrará información detallada sobre qué está causando el problema.

### Opción 2: Usar Script de Solución Completa

```bash
cd scripts

# Windows PowerShell
.\solucionar_restart_loop.ps1

# Linux/Mac
chmod +x solucionar_restart_loop.sh
./solucionar_restart_loop.sh
```

Este script:
1. Fuerza la detención del contenedor
2. Elimina volúmenes corruptos
3. Limpia todo
4. Recrea desde cero
5. Verifica el estado

### Opción 3: Verificar Recursos del Sistema

**Si el problema persiste, puede ser falta de memoria:**

1. **Verifica memoria de Docker Desktop:**
   - Abre Docker Desktop
   - Settings → Resources → Advanced
   - Asegúrate de tener **mínimo 2GB** asignados (recomendado **4GB**)

2. **Aumenta memoria en docker-compose.yml (si es necesario):**
   ```yaml
   services:
     pulsar:
       mem_limit: 3g  # Aumentar de 2g a 3g
       mem_reservation: 2g  # Aumentar de 1g a 2g
   ```

---

## 📝 Resumen Rápido

```bash
# 1. Actualizar código
git pull origin main

# 2. Detener y limpiar
docker-compose down
docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>/dev/null || true
docker rm -f nuam-pulsar 2>/dev/null || true

# 3. Recrear
docker-compose up -d

# 4. Esperar 60 segundos

# 5. Verificar
cd scripts
.\verificar_pulsar.ps1   # Windows
# o
./verificar_pulsar.sh    # Linux/Mac
```

---

## ✅ Qué Debería Pasar

Después de seguir estos pasos:

1. ✅ El contenedor debe iniciar sin errores
2. ✅ Debe quedarse en estado "Up" (no "Restarting")
3. ✅ Admin API debe estar disponible después de 60 segundos
4. ✅ El dashboard de Pulsar debe mostrar "Admin API: ONLINE"

---

## 🆘 Si Necesitas Ayuda

Si después de seguir todos estos pasos el problema persiste:

1. **Ejecuta el script de diagnóstico:**
   ```bash
   cd scripts
   .\diagnosticar_pulsar.ps1   # Windows
   ```

2. **Copia los logs completos:**
   ```bash
   docker logs nuam-pulsar > pulsar_logs.txt
   ```

3. **Comparte:**
   - Salida del script de diagnóstico
   - Logs de Pulsar
   - Estado del contenedor (`docker ps -a | grep pulsar`)

---

## 📚 Documentación Adicional

Para más información sobre troubleshooting de Pulsar:
- `microservicio/docs/TROUBLESHOOTING_PULSAR.md` - Guía completa
- `microservicio/docs/TROUBLESHOOTING_PULSAR_CONNECTION_REFUSED.md` - Errores de conexión
- `SOLUCION_PULSAR_REINICIO.md` - Explicación del problema y solución

