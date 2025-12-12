# 📦 Guía de Archivos Docker Compose en NUAM

## Resumen de Archivos

NUAM tiene **3 archivos docker-compose** diferentes para diferentes propósitos:

### ✅ 1. `docker-compose.yml` (RAÍZ) - ⭐ USAR ESTE PARA DESARROLLO

**Ubicación:** `/docker-compose.yml` (en la raíz del proyecto)

**Servicios incluidos:**
- ✅ **Pulsar** (Apache Pulsar para mensajería)
  - Puerto 6650: Productores/Consumidores
  - Puerto 8080: Admin API
  - Container: `nuam-pulsar`
- ✅ **docs-generator** (Microservicio FastAPI para generar documentos)
  - Puerto 5001
  - Container: `nuam-docs-generator`

**Cuándo usarlo:**
- ✅ Desarrollo normal
- ✅ Cuando necesites Pulsar Admin API
- ✅ Cuando necesites generar documentos (PDF, Excel, CSV)
- ✅ **Este es el archivo que TODOS deben usar por defecto**

**Comandos:**
```bash
# Levantar todos los servicios
docker-compose up -d

# Ver estado
docker ps

# Ver logs
docker logs nuam-pulsar
docker logs nuam-docs-generator

# Detener todo
docker-compose down
```

---

### ❌ 2. `services/docker-compose.yml` - Solo docs-generator

**Ubicación:** `/services/docker-compose.yml`

**Servicios incluidos:**
- ✅ docs-generator (FastAPI)
- ❌ **NO incluye Pulsar**

**Cuándo usarlo:**
- Solo si **NO necesitas Pulsar** y solo quieres el generador de documentos
- **NO recomendado** para desarrollo normal

**Comandos:**
```bash
# Desde la raíz del proyecto
docker-compose -f services/docker-compose.yml up -d
```

---

### ⚠️ 3. `docker-compose.dev.yml` - Archivo alternativo

**Ubicación:** `/docker-compose.dev.yml` (en la raíz del proyecto)

**Servicios incluidos:**
- ✅ Pulsar (pero con nombre diferente: `nuam-pulsar-dev`)
- ❌ NO incluye docs-generator

**Cuándo usarlo:**
- Solo si quieres un ambiente completamente separado para pruebas
- **NO necesario** para desarrollo normal

**Comandos:**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

---

## ❓ ¿Cuál usar?

### Para desarrollo normal (RECOMENDADO):

```bash
# Usa el docker-compose.yml de la raíz
docker-compose up -d

# ⚠️ IMPORTANTE: El contenedor inicia inmediatamente, pero Admin API puede tardar 30-60 segundos
# Usa el script de verificación para esperar automáticamente:
cd scripts
.\verificar_pulsar.ps1   # Windows
# o
chmod +x verificar_pulsar.sh && ./verificar_pulsar.sh   # Linux/Mac
```

Esto levanta:
- ✅ Pulsar (Admin API en puerto 8080) - **Nota: tarda 30-60 segundos en estar disponible**
- ✅ docs-generator (puerto 5001)

### Si tu compañero no tiene Admin API disponible:

1. **Verifica que está usando el archivo correcto:**
   ```bash
   # Asegúrate de estar en la raíz del proyecto
   pwd  # Debería mostrar: .../Nuam
   
   # Verifica qué servicios están corriendo
   docker ps
   ```

2. **Si no está corriendo Pulsar, levanta todos los servicios:**
   ```bash
   # Desde la raíz del proyecto
   docker-compose up -d
   ```

3. **Verifica que Pulsar esté corriendo:**
   ```bash
   docker ps | grep pulsar
   # Debería mostrar: nuam-pulsar
   ```

4. **Verifica que Admin API esté disponible:**
   ```bash
   curl http://localhost:8080/admin/v2/brokers/health
   # Debería responder con: {"status": "ok"} o similar
   ```

5. **Si sigue fallando, reinicia limpiamente:**
   ```bash
   # Usa el script automático
   cd scripts
   .\restart_pulsar.ps1  # Windows
   # o
   ./restart_pulsar.sh   # Linux/Mac
   ```

---

## 🔍 Troubleshooting

### Problema: "Pulsar Admin API no disponible"

**Posibles causas:**
1. ❌ No estás usando el `docker-compose.yml` correcto
2. ❌ Pulsar no está corriendo
3. ❌ Pulsar está iniciando (espera 30-60 segundos)
4. ❌ Puerto 8080 está ocupado

**Solución:**
```bash
# 1. Asegúrate de estar en la raíz
cd /ruta/al/proyecto/Nuam

# 2. Detén todo
docker-compose down -v

# 3. Levanta de nuevo
docker-compose up -d

# 4. Espera 60 segundos
sleep 60

# 5. Verifica
docker logs nuam-pulsar
curl http://localhost:8080/admin/v2/brokers/health
```

### Problema: "Conflicto de nombres de contenedores"

Si has usado `docker-compose.dev.yml`, puede que tengas un contenedor llamado `nuam-pulsar-dev` en lugar de `nuam-pulsar`.

**Solución:**
```bash
# Detener todos los contenedores de Pulsar
docker stop nuam-pulsar nuam-pulsar-dev 2>/dev/null || true
docker rm nuam-pulsar nuam-pulsar-dev 2>/dev/null || true

# Usar el docker-compose.yml principal
docker-compose up -d
```

---

## 📝 Notas Importantes

1. **Todos los servicios deben usar el mismo network (`nuam-network`)** para poder comunicarse
2. **Los volúmenes son persistentes** - si borras volúmenes con `-v`, perderás datos
3. **`restart: unless-stopped`** hace que los servicios se reinicien automáticamente si se caen
4. **El puerto 8080 debe estar libre** para que Admin API funcione

---

## 🎯 Resumen Rápido

```bash
# ✅ PARA DESARROLLO NORMAL (RECOMENDADO):
docker-compose up -d          # Desde la raíz del proyecto

# ✅ VERIFICAR:
docker ps                     # Debería mostrar nuam-pulsar y nuam-docs-generator
curl http://localhost:8080/admin/v2/brokers/health  # Debería responder OK

# ✅ SI ALGO FALLA:
cd scripts
.\restart_pulsar.ps1          # Windows
# o
./restart_pulsar.sh           # Linux/Mac
```

