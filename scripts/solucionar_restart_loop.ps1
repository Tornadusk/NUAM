# Script PowerShell para solucionar ciclo de reinicio constante de Pulsar
# Cuando el contenedor está en estado "Restarting" continuamente

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Solucionar Ciclo de Reinicio - Pulsar" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Detener el contenedor inmediatamente
Write-Host "1. Deteniendo contenedor en ciclo de reinicio..." -ForegroundColor Yellow
docker stop nuam-pulsar 2>$null
Start-Sleep -Seconds 2

# 2. Forzar eliminación del contenedor
Write-Host "2. Eliminando contenedor..." -ForegroundColor Yellow
docker rm -f nuam-pulsar 2>$null

# 3. Detener todos los servicios relacionados
Write-Host "3. Deteniendo todos los servicios de docker-compose..." -ForegroundColor Yellow
docker-compose down

# 4. Verificar y eliminar volúmenes corruptos
Write-Host "4. Eliminando volúmenes (pueden estar corruptos)..." -ForegroundColor Yellow
docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Volúmenes eliminados" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Volúmenes no existían o ya fueron eliminados" -ForegroundColor Gray
}

# 5. Limpiar contenedores huérfanos
Write-Host "5. Limpiando contenedores huérfanos..." -ForegroundColor Yellow
docker container prune -f

# 6. Mostrar los últimos logs antes de limpiar (para diagnóstico)
Write-Host ""
Write-Host "6. Últimos logs del contenedor (antes de limpiar)..." -ForegroundColor Yellow
Write-Host '   (Si el contenedor aún existe)' -ForegroundColor Gray
docker logs nuam-pulsar --tail 50 2>$null | Select-Object -Last 20

# 7. Recrear desde cero
Write-Host ""
Write-Host "7. Recreando servicios desde cero..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Error al recrear servicios" -ForegroundColor Red
    exit 1
}

Write-Host "   ✅ Servicios recreados" -ForegroundColor Green

# 8. Esperar unos segundos
Write-Host ""
Write-Host '8. Esperando a que Pulsar inicie (10 segundos)...' -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 9. Verificar estado
Write-Host ""
Write-Host "9. Verificando estado..." -ForegroundColor Yellow
$status = docker ps -a --filter "name=nuam-pulsar" --format "{{.Status}}" 2>$null

if ($status -match "Up") {
    Write-Host "   ✅ Contenedor está corriendo: $status" -ForegroundColor Green
} elseif ($status -match "Restarting") {
    Write-Host "   ⚠️  Contenedor sigue reiniciando: $status" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Esto indica un problema más profundo. Revisa los logs:" -ForegroundColor Yellow
    Write-Host "   docker logs nuam-pulsar --tail 100" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Posibles causas:" -ForegroundColor Yellow
    Write-Host "   1. Falta de memoria (aumenta mem_limit en docker-compose.yml)" -ForegroundColor White
    Write-Host "   2. Puerto 8080 o 6650 ocupado por otro proceso" -ForegroundColor White
    Write-Host "   3. Volúmenes corruptos (intenta eliminar volúmenes y recrear)" -ForegroundColor White
    Write-Host "   4. Configuración incorrecta en Pulsar" -ForegroundColor White
} else {
    Write-Host "   ❌ Contenedor en estado: $status" -ForegroundColor Red
}

# 10. Mostrar logs recientes
Write-Host ""
Write-Host "10. Logs recientes de Pulsar:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Gray
docker logs nuam-pulsar --tail 30 2>$null
Write-Host "==========================================" -ForegroundColor Gray

Write-Host ""
Write-Host "✅ Proceso completado!" -ForegroundColor Green
Write-Host ""
Write-Host "Si el problema persiste, revisa:" -ForegroundColor Cyan
Write-Host "  - Docker Desktop tiene suficiente memoria asignada" -ForegroundColor White
Write-Host "  - Los puertos 8080 y 6650 no están ocupados" -ForegroundColor White
Write-Host "  - Logs completos: docker logs nuam-pulsar" -ForegroundColor White

