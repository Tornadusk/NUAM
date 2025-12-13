#!/bin/bash
# Script Bash para reiniciar Pulsar limpiamente
# Soluciona problemas de "exited with code 1" y volúmenes corruptos

echo "=========================================="
echo "  Reinicio Limpio de Pulsar - NUAM"
echo "=========================================="
echo ""

# 1. Detener y eliminar contenedores y volúmenes
echo "1. Deteniendo contenedores y eliminando volúmenes..."
docker-compose down -v

if [ $? -ne 0 ]; then
    echo "   ⚠️  Advertencia: Algunos recursos pueden no haberse eliminado"
fi

# 2. Verificar y eliminar volúmenes específicos de Pulsar si existen
echo "2. Eliminando volúmenes de Pulsar..."
docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Volúmenes eliminados"
else
    echo "   ℹ️  Volúmenes no existían o ya fueron eliminados"
fi

# 3. Limpiar sistema Docker (opcional)
read -p "¿Deseas limpiar el sistema Docker (elimina contenedores/volúmenes no usados)? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "3. Limpiando sistema Docker..."
    docker system prune -a --volumes -f
    echo "   ✅ Sistema limpiado"
else
    echo "3. Saltando limpieza del sistema Docker"
fi

# 4. Recrear contenedores
echo ""
echo "4. Recreando contenedores..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "   ❌ Error al recrear contenedores"
    exit 1
fi

echo "   ✅ Contenedores recreados"

# 5. Esperar unos segundos para que Pulsar inicie
echo ""
echo "5. Esperando a que Pulsar inicie (30 segundos)..."
sleep 30

# 6. Verificar estado
echo ""
echo "6. Verificando estado de Pulsar..."
CONTAINER_STATUS=$(docker ps -a --filter "name=nuam-pulsar" --format "{{.Status}}")

if echo "$CONTAINER_STATUS" | grep -q "Up"; then
    echo "   ✅ Contenedor está corriendo"
else
    echo "   ❌ Contenedor NO está corriendo: $CONTAINER_STATUS"
    echo ""
    echo "   Ver logs para más detalles:"
    echo "   docker logs nuam-pulsar"
    exit 1
fi

# 7. Verificar Admin API
echo ""
echo "7. Verificando Admin API (puerto 8080)..."
if curl -s -f http://localhost:8080/admin/v2/brokers/health > /dev/null 2>&1; then
    echo "   ✅ Admin API está disponible"
else
    echo "   ⚠️  Admin API aún no está disponible (esto es normal si acaba de iniciar)"
    echo "   Espera 30-60 segundos más y verifica manualmente:"
    echo "   curl http://localhost:8080/admin/v2/brokers/health"
fi

# 8. Mostrar logs
echo ""
echo "=========================================="
echo "  Últimas líneas de los logs:"
echo "=========================================="
docker logs --tail 50 nuam-pulsar

echo ""
echo "✅ Proceso completado!"
echo ""
echo "Para ver logs en tiempo real:"
echo "  docker logs -f nuam-pulsar"
echo ""
echo "Para verificar Admin API:"
echo "  curl http://localhost:8080/admin/v2/brokers/health"


