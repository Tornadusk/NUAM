#!/bin/bash
# Script Bash para verificar que Pulsar Admin API esté disponible
# Espera hasta que Admin API esté listo o hasta un timeout

echo "=========================================="
echo "  Verificación de Pulsar Admin API"
echo "=========================================="
echo ""

MAX_ATTEMPTS=30  # 30 intentos = 60 segundos (2 segundos por intento)
ATTEMPT=0
URL="http://localhost:8080/admin/v2/brokers/health"

echo "Verificando que el contenedor esté corriendo..."
CONTAINER_STATUS=$(docker ps --filter "name=nuam-pulsar" --format "{{.Status}}" 2>/dev/null)

if [ -z "$CONTAINER_STATUS" ] || ! echo "$CONTAINER_STATUS" | grep -q "Up"; then
    echo "❌ Error: Contenedor nuam-pulsar no está corriendo"
    echo ""
    echo "Ejecuta primero:"
    echo "  docker-compose up -d"
    exit 1
fi

echo "✅ Contenedor está corriendo: $CONTAINER_STATUS"
echo ""
echo "Esperando a que Admin API esté disponible..."
echo "Esto puede tardar 30-60 segundos después de iniciar el contenedor"
echo ""

READY=false
while [ $ATTEMPT -lt $MAX_ATTEMPTS ] && [ "$READY" = false ]; do
    ATTEMPT=$((ATTEMPT + 1))
    
    if curl -s -f "$URL" > /dev/null 2>&1; then
        READY=true
        echo "✅ Admin API está disponible!"
        RESPONSE=$(curl -s "$URL")
        echo "   Response: $RESPONSE"
        break
    else
        # Error esperado mientras Admin API aún no está listo
        PERCENT=$((ATTEMPT * 100 / MAX_ATTEMPTS))
        echo "   Intento $ATTEMPT/$MAX_ATTEMPTS ($PERCENT%)... Admin API aún no está disponible"
        sleep 2
    fi
done

if [ "$READY" = false ]; then
    echo ""
    echo "❌ Timeout: Admin API no está disponible después de $((MAX_ATTEMPTS * 2)) segundos"
    echo ""
    echo "Posibles causas:"
    echo "  1. Pulsar está iniciando (espera un poco más y vuelve a intentar)"
    echo "  2. Error al iniciar Pulsar (revisa logs: docker logs nuam-pulsar)"
    echo "  3. Puerto 8080 está ocupado por otro proceso"
    echo ""
    echo "Para ver logs de Pulsar:"
    echo "  docker logs nuam-pulsar"
    exit 1
fi

echo ""
echo "=========================================="
echo "  ✅ Pulsar Admin API está listo"
echo "=========================================="
echo ""
echo "Puedes acceder a:"
echo "  - Admin API: http://localhost:8080"
echo "  - Pulsar Service: pulsar://localhost:6650"


