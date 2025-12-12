# Script PowerShell para diagnosticar problemas de Pulsar
# Muestra información detallada para entender por qué se reinicia

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Diagnóstico Completo de Pulsar" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Estado del contenedor
Write-Host "1. ESTADO DEL CONTENEDOR" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$containerStatus = docker ps -a --filter "name=nuam-pulsar" --format "{{.Status}}" 2>$null
$containerInfo = docker ps -a --filter "name=nuam-pulsar" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
Write-Host $containerInfo
Write-Host ""

# 2. Logs recientes (últimas 50 líneas)
Write-Host "2. LOGS RECIENTES (últimas 50 líneas)" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
docker logs nuam-pulsar --tail 50 2>$null
Write-Host ""

# 3. Buscar errores específicos
Write-Host "3. ERRORES ESPECÍFICOS" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$logs = docker logs nuam-pulsar 2>&1
$errorLines = $logs | Select-String -Pattern "error|exception|failed|fatal|OutOfMemory" -CaseSensitive:$false | Select-Object -Last 10
if ($errorLines) {
    $errorLines | ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
} else {
    Write-Host "No se encontraron errores obvios en los logs" -ForegroundColor Green
}
Write-Host ""

# 4. Verificar puertos
Write-Host "4. PUERTOS" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "Puerto 6650:" -ForegroundColor White
$port6650 = netstat -ano | findstr ":6650"
if ($port6650) {
    Write-Host $port6650 -ForegroundColor Yellow
} else {
    Write-Host "  No hay procesos usando el puerto 6650" -ForegroundColor Green
}
Write-Host ""
Write-Host "Puerto 8080:" -ForegroundColor White
$port8080 = netstat -ano | findstr ":8080"
if ($port8080) {
    Write-Host $port8080 -ForegroundColor Yellow
} else {
    Write-Host "  No hay procesos usando el puerto 8080" -ForegroundColor Green
}
Write-Host ""

# 5. Recursos del sistema
Write-Host "5. RECURSOS DEL SISTEMA" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$stats = docker stats nuam-pulsar --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>$null
if ($stats) {
    Write-Host $stats
} else {
    Write-Host "  No se pudieron obtener estadísticas (el contenedor puede no estar corriendo)" -ForegroundColor Yellow
}
Write-Host ""

# 6. Verificar volúmenes
Write-Host "6. VOLÚMENES" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$volumes = docker volume ls --filter "name=pulsar" --format "table {{.Name}}\t{{.Driver}}"
Write-Host $volumes
Write-Host ""

# 7. Configuración de docker-compose
Write-Host "7. CONFIGURACIÓN DOCKER-COMPOSE" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
if (Test-Path "../docker-compose.yml") {
    Write-Host "  docker-compose.yml encontrado" -ForegroundColor Green
    $composeContent = Get-Content "../docker-compose.yml" -Raw
    if ($composeContent -match "mem_limit:\s*(\d+)") {
        Write-Host "  Memoria límite: $($matches[1])" -ForegroundColor White
    }
    if ($composeContent -match "PULSAR_MEM") {
        Write-Host "  PULSAR_MEM configurado" -ForegroundColor White
    }
} else {
    Write-Host "  docker-compose.yml no encontrado" -ForegroundColor Red
}
Write-Host ""

# 8. Recomendaciones
Write-Host "8. RECOMENDACIONES" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

if ($containerStatus -match "Restarting") {
    Write-Host "  ⚠️  CONTENEDOR EN CICLO DE REINICIO" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Ejecuta el script de solución:" -ForegroundColor Yellow
    Write-Host "    .\solucionar_restart_loop.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Si el problema persiste después de ejecutar el script:" -ForegroundColor Yellow
    Write-Host "    1. Verifica que Docker Desktop tenga suficiente memoria (mínimo 2GB, recomendado 4GB)" -ForegroundColor White
    Write-Host "    2. Aumenta mem_limit en docker-compose.yml de 2g a 3g" -ForegroundColor White
    Write-Host "    3. Revisa los logs completos: docker logs nuam-pulsar" -ForegroundColor White
} elseif ($containerStatus -match "Up") {
    Write-Host "  ✅ Contenedor está corriendo" -ForegroundColor Green
    Write-Host "  Espera 60 segundos y verifica Admin API con: .\verificar_pulsar.ps1" -ForegroundColor White
} elseif ($containerStatus -match "Exited") {
    Write-Host "  ⚠️  Contenedor se detuvo" -ForegroundColor Yellow
    Write-Host "  Revisa los logs: docker logs nuam-pulsar" -ForegroundColor White
    Write-Host "  Ejecuta: docker-compose up -d" -ForegroundColor White
} else {
    Write-Host "  ❌ Contenedor no encontrado" -ForegroundColor Red
    Write-Host "  Ejecuta: docker-compose up -d" -ForegroundColor White
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Diagnóstico completado" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

