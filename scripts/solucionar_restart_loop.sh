#!/bin/bash
# Script Bash para solucionar ciclo de reinicio constante de Pulsar
# Cuando el contenedor está en estado "Restarting" continuamente

echo "=========================================="
echo "  Solucionar Ciclo de Reinicio - Pulsar"
echo "=========================================="
echo ""

# 1. Detener el contenedor inmediatamente
echo "1. Deteniendo contenedor en ciclo de reinicio..."
docker stop nuam-pulsar 2>/dev/null
sleep 2

# 2. Forzar eliminación del contenedor
echo "2. Eliminando contenedor..."
docker rm -f nuam-pulsar 2>/dev/null

# 3. Detener todos los servicios relacionados
echo "3. Deteniendo todos los servicios de docker-compose..."
docker-compose down

# 4. Verificar y eliminar volúmenes corruptos
echo "4. Eliminando volúmenes (pueden estar corruptos)..."
if docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>/dev/null; then
    echo "   ✅ Volúmenes eliminados"
else
    echo "   ℹ️  Volúmenes no existían o ya fueron eliminados"
fi

# 5. Limpiar contenedores huérfanos
echo "5. Limpiando contenedores huérfanos..."
docker container prune -f

# 6. Mostrar los últimos logs antes de limpiar (para diagnóstico)
echo ""
echo "6. Últimos logs del contenedor (antes de limpiar)..."
echo "   (Si el contenedor aún existe)"
docker logs nuam-pulsar --tail 20 2>/dev/null || true

# 7. Recrear desde cero
echo ""
echo "7. Recreando servicios desde cero..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "   ❌ Error al recrear servicios"
    exit 1
fi

echo "   ✅ Servicios recreados"

# 8. Esperar unos segundos
echo ""
echo "8. Esperando a que Pulsar inicie (10 segundos)..."
sleep 10

# 9. Verificar estado
echo ""
echo "9. Verificando estado..."
STATUS=$(docker ps -a --filter "name=nuam-pulsar" --format "{{.Status}}" 2>/dev/null)

if echo "$STATUS" | grep -q "Up"; then
    echo "   ✅ Contenedor está corriendo: $STATUS"
elif echo "$STATUS" | grep -q "Restarting"; then
    echo "   ⚠️  Contenedor sigue reiniciando: $STATUS"
    echo ""
    echo "   Esto indica un problema más profundo. Revisa los logs:"
    echo "   docker logs nuam-pulsar --tail 100"
    echo ""
    echo "   Posibles causas:"
    echo "   1. Falta de memoria (aumenta mem_limit en docker-compose.yml)"
    echo "   2. Puerto 8080 o 6650 ocupado por otro proceso"
    echo "   3. Volúmenes corruptos (intenta eliminar volúmenes y recrear)"
    echo "   4. Configuración incorrecta en Pulsar"
else
    echo "   ❌ Contenedor en estado: $STATUS"
fi

# 10. Mostrar logs recientes
echo ""
echo "10. Logs recientes de Pulsar:"
echo "=========================================="
docker logs nuam-pulsar --tail 30 2>/dev/null || true
echo "=========================================="

echo ""
echo "✅ Proceso completado!"
echo ""
echo "Si el problema persiste, revisa:"
echo "  - Docker Desktop tiene suficiente memoria asignada"
echo "  - Los puertos 8080 y 6650 no están ocupados"
echo "  - Logs completos: docker logs nuam-pulsar"

