#!/bin/bash
# Script Bash para diagnosticar problemas de Pulsar
# Muestra información detallada para entender por qué se reinicia

echo "=========================================="
echo "  Diagnóstico Completo de Pulsar"
echo "=========================================="
echo ""

# 1. Estado del contenedor
echo "1. ESTADO DEL CONTENEDOR"
echo "----------------------------------------"
docker ps -a --filter "name=nuam-pulsar" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# 2. Logs recientes (últimas 50 líneas)
echo "2. LOGS RECIENTES (últimas 50 líneas)"
echo "----------------------------------------"
docker logs nuam-pulsar --tail 50 2>/dev/null || echo "No se pudieron obtener logs"
echo ""

# 3. Buscar errores específicos
echo "3. ERRORES ESPECÍFICOS"
echo "----------------------------------------"
ERRORS=$(docker logs nuam-pulsar 2>&1 | grep -i "error\|exception\|failed\|fatal\|OutOfMemory" | tail -10)
if [ -n "$ERRORS" ]; then
    echo "$ERRORS" | while IFS= read -r line; do
        echo "$line" | grep --color=always -i "error\|exception\|failed\|fatal\|OutOfMemory"
    done
else
    echo "No se encontraron errores obvios en los logs"
fi
echo ""

# 4. Verificar puertos
echo "4. PUERTOS"
echo "----------------------------------------"
echo "Puerto 6650:"
PORT6650=$(lsof -i :6650 2>/dev/null || netstat -tulpn 2>/dev/null | grep :6650)
if [ -n "$PORT6650" ]; then
    echo "$PORT6650"
else
    echo "  No hay procesos usando el puerto 6650"
fi
echo ""
echo "Puerto 8080:"
PORT8080=$(lsof -i :8080 2>/dev/null || netstat -tulpn 2>/dev/null | grep :8080)
if [ -n "$PORT8080" ]; then
    echo "$PORT8080"
else
    echo "  No hay procesos usando el puerto 8080"
fi
echo ""

# 5. Recursos del sistema
echo "5. RECURSOS DEL SISTEMA"
echo "----------------------------------------"
docker stats nuam-pulsar --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || echo "  No se pudieron obtener estadísticas"
echo ""

# 6. Verificar volúmenes
echo "6. VOLÚMENES"
echo "----------------------------------------"
docker volume ls --filter "name=pulsar" --format "table {{.Name}}\t{{.Driver}}"
echo ""

# 7. Configuración de docker-compose
echo "7. CONFIGURACIÓN DOCKER-COMPOSE"
echo "----------------------------------------"
if [ -f "../docker-compose.yml" ]; then
    echo "  docker-compose.yml encontrado"
    if grep -q "mem_limit:" ../docker-compose.yml; then
        MEM_LIMIT=$(grep "mem_limit:" ../docker-compose.yml | grep -oE "[0-9]+[a-z]*")
        echo "  Memoria límite: $MEM_LIMIT"
    fi
    if grep -q "PULSAR_MEM" ../docker-compose.yml; then
        echo "  PULSAR_MEM configurado"
    fi
else
    echo "  docker-compose.yml no encontrado"
fi
echo ""

# 8. Recomendaciones
echo "8. RECOMENDACIONES"
echo "----------------------------------------"

CONTAINER_STATUS=$(docker ps -a --filter "name=nuam-pulsar" --format "{{.Status}}" 2>/dev/null)

if echo "$CONTAINER_STATUS" | grep -q "Restarting"; then
    echo "  ⚠️  CONTENEDOR EN CICLO DE REINICIO"
    echo ""
    echo "  Ejecuta el script de solución:"
    echo "    ./solucionar_restart_loop.sh"
    echo ""
    echo "  Si el problema persiste después de ejecutar el script:"
    echo "    1. Verifica que Docker tenga suficiente memoria (mínimo 2GB, recomendado 4GB)"
    echo "    2. Aumenta mem_limit en docker-compose.yml de 2g a 3g"
    echo "    3. Revisa los logs completos: docker logs nuam-pulsar"
elif echo "$CONTAINER_STATUS" | grep -q "Up"; then
    echo "  ✅ Contenedor está corriendo"
    echo "  Espera 60 segundos y verifica Admin API con: ./verificar_pulsar.sh"
elif echo "$CONTAINER_STATUS" | grep -q "Exited"; then
    echo "  ⚠️  Contenedor se detuvo"
    echo "  Revisa los logs: docker logs nuam-pulsar"
    echo "  Ejecuta: docker-compose up -d"
else
    echo "  ❌ Contenedor no encontrado"
    echo "  Ejecuta: docker-compose up -d"
fi

echo ""
echo "=========================================="
echo "  Diagnóstico completado"
echo "=========================================="


