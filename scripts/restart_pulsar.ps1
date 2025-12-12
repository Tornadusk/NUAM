# Script PowerShell para reiniciar Pulsar limpiamente
# Soluciona problemas de "exited with code 1" y volúmenes corruptos

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Reinicio Limpio de Pulsar - NUAM" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Detener y eliminar contenedores y volúmenes
Write-Host "1. Deteniendo contenedores y eliminando volúmenes..." -ForegroundColor Yellow
docker-compose down -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️  Advertencia: Algunos recursos pueden no haberse eliminado" -ForegroundColor Yellow
}

# 2. Verificar y eliminar volúmenes específicos de Pulsar si existen
Write-Host "2. Eliminando volúmenes de Pulsar..." -ForegroundColor Yellow
docker volume rm nuam_pulsar-data nuam_pulsar-conf 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Volúmenes eliminados" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Volúmenes no existían o ya fueron eliminados" -ForegroundColor Gray
}

# 3. Limpiar sistema Docker (opcional)
$response = Read-Host "¿Deseas limpiar el sistema Docker (elimina contenedores/volúmenes no usados)? (s/n)"
if ($response -match "^[SsYy]") {
    Write-Host "3. Limpiando sistema Docker..." -ForegroundColor Yellow
    docker system prune -a --volumes -f
    Write-Host "   ✅ Sistema limpiado" -ForegroundColor Green
} else {
    Write-Host "3. Saltando limpieza del sistema Docker" -ForegroundColor Gray
}

# 4. Recrear contenedores
Write-Host ""
Write-Host "4. Recreando contenedores..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Error al recrear contenedores" -ForegroundColor Red
    exit 1
}

Write-Host "   ✅ Contenedores recreados" -ForegroundColor Green

# 5. Esperar unos segundos para que Pulsar inicie
Write-Host ""
Write-Host "5. Esperando a que Pulsar inicie (30 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 6. Verificar estado
Write-Host ""
Write-Host "6. Verificando estado de Pulsar..." -ForegroundColor Yellow
$containerStatus = docker ps -a --filter "name=nuam-pulsar" --format "{{.Status}}"

if ($containerStatus -match "Up") {
    Write-Host "   ✅ Contenedor está corriendo" -ForegroundColor Green
} else {
    Write-Host "   ❌ Contenedor NO está corriendo: $containerStatus" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Ver logs para más detalles:" -ForegroundColor Yellow
    Write-Host "   docker logs nuam-pulsar" -ForegroundColor Cyan
    exit 1
}

# 7. Verificar Admin API
Write-Host ""
Write-Host "7. Verificando Admin API (puerto 8080)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/admin/v2/brokers/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Admin API está disponible" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Admin API respondió con código: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Admin API aún no está disponible (esto es normal si acaba de iniciar)" -ForegroundColor Yellow
    Write-Host "   Espera 30-60 segundos más y verifica manualmente:" -ForegroundColor Yellow
    Write-Host "   curl http://localhost:8080/admin/v2/brokers/health" -ForegroundColor Cyan
}

# 8. Mostrar logs
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Últimas líneas de los logs:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
docker logs --tail 50 nuam-pulsar

Write-Host ""
Write-Host "✅ Proceso completado!" -ForegroundColor Green
Write-Host ""
Write-Host "Para ver logs en tiempo real:" -ForegroundColor Cyan
Write-Host "  docker logs -f nuam-pulsar" -ForegroundColor White
Write-Host ""
Write-Host "Para verificar Admin API:" -ForegroundColor Cyan
Write-Host "  curl http://localhost:8080/admin/v2/brokers/health" -ForegroundColor White

