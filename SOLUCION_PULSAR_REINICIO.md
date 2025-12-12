# ✅ Solución: Pulsar en Ciclo de Reinicio Constante

## Problema Identificado

El contenedor de Pulsar estaba en ciclo de reinicio constante debido a un error en la configuración de `docker-compose.yml`.

### Error en los logs:
```
Error: Could not find or load main class "-Xms512m
Caused by: java.lang.ClassNotFoundException: "-Xms512m
```

### Causa Raíz:

La variable de entorno `PULSAR_MEM` tenía **comillas dentro del valor**, lo que causaba que Java interpretara las opciones JVM incorrectamente.

**Configuración INCORRECTA:**
```yaml
environment:
  - PULSAR_MEM="-Xms512m -Xmx1024m -XX:MaxDirectMemorySize=512m"  # ❌ Comillas dentro del valor
```

**Configuración CORRECTA:**
```yaml
environment:
  - PULSAR_MEM=-Xms512m -Xmx1024m -XX:MaxDirectMemorySize=512m  # ✅ Sin comillas dentro
```

**Razón:** Docker Compose ya maneja las comillas automáticamente cuando pasas variables de entorno. Las comillas dentro del valor causan que se interpreten literalmente, haciendo que Java trate de ejecutar `"-Xms512m` como si fuera una clase.

---

## ✅ Solución Aplicada

1. ✅ Corregida la configuración en `docker-compose.yml`
2. ✅ Eliminados volúmenes corruptos
3. ✅ Recreados los contenedores desde cero

---

## 🧪 Verificación

Después de aplicar la corrección, verifica que Pulsar esté corriendo:

```bash
# Verificar estado
docker ps | grep pulsar

# Debería mostrar:
# nuam-pulsar   Up X minutes   ...

# Verificar logs (sin errores de "ClassNotFoundException")
docker logs nuam-pulsar --tail 50

# Verificar Admin API (después de 60 segundos)
curl http://localhost:8080/admin/v2/brokers/health
```

---

## 📝 Nota Importante

Si alguien más tiene este problema:

1. **Actualiza el código:**
   ```bash
   git pull
   ```

2. **Si ya tienes el contenedor corriendo con la configuración incorrecta:**
   ```bash
   # Detener y eliminar
   docker-compose down -v
   
   # Eliminar volúmenes específicos
   docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>/dev/null || true
   
   # Recrear con la configuración corregida
   docker-compose up -d
   
   # Esperar 60 segundos
   sleep 60
   
   # Verificar
   docker ps | grep pulsar
   docker logs nuam-pulsar --tail 30
   ```

---

## 🔍 Si el Problema Persiste

Si después de aplicar esta corrección el contenedor sigue reiniciándose:

1. **Verifica memoria de Docker Desktop:**
   - Settings → Resources → Advanced
   - Mínimo 2GB, recomendado 4GB

2. **Ejecuta el script de diagnóstico:**
   ```bash
   cd scripts
   .\diagnosticar_pulsar.ps1   # Windows
   # o
   ./diagnosticar_pulsar.sh    # Linux/Mac
   ```

3. **Ejecuta el script de solución:**
   ```bash
   cd scripts
   .\solucionar_restart_loop.ps1   # Windows
   # o
   ./solucionar_restart_loop.sh    # Linux/Mac
   ```

4. **Revisa logs completos:**
   ```bash
   docker logs nuam-pulsar --tail 200
   ```

---

## ✅ Estado Final

- ✅ Configuración corregida en `docker-compose.yml`
- ✅ Scripts de diagnóstico y solución creados
- ✅ Documentación actualizada

El problema debería estar resuelto ahora. Si tu compañero actualiza el código con `git pull`, debería funcionar correctamente.

