# Script PowerShell para verificar que Pulsar Admin API esté disponible
# Espera hasta que Admin API esté listo o hasta un timeout

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Verificación de Pulsar Admin API" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$maxAttempts = 30  # 30 intentos = 60 segundos (2 segundos por intento)
$attempt = 0
$url = "http://localhost:8080/admin/v2/brokers/health"

Write-Host "Verificando que el contenedor esté corriendo..." -ForegroundColor Yellow
$containerStatus = docker ps --filter "name=nuam-pulsar" --format "{{.Status}}" 2>$null

if (-not $containerStatus -or -not ($containerStatus -match "Up")) {
    Write-Host "❌ Error: Contenedor nuam-pulsar no está corriendo" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ejecuta primero:" -ForegroundColor Yellow
    Write-Host "  docker-compose up -d" -ForegroundColor White
    exit 1
}

Write-Host "✅ Contenedor está corriendo: $containerStatus" -ForegroundColor Green
Write-Host ""
Write-Host "Esperando a que Admin API esté disponible..." -ForegroundColor Yellow
Write-Host "Esto puede tardar 30-60 segundos después de iniciar el contenedor" -ForegroundColor Gray
Write-Host ""

$ready = $false
while ($attempt -lt $maxAttempts -and -not $ready) {
    $attempt++
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 2 -ErrorAction Stop -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $ready = $true
            Write-Host "✅ Admin API está disponible!" -ForegroundColor Green
            Write-Host "   Status Code: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
            break
        }
    } catch {
        # Error esperado mientras Admin API aún no está listo
        $percentComplete = [math]::Round(($attempt / $maxAttempts) * 100)
        Write-Host "   Intento $attempt/$maxAttempts ($percentComplete%)... Admin API aún no está disponible" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    Write-Host ""
    Write-Host "❌ Timeout: Admin API no está disponible después de $($maxAttempts * 2) segundos" -ForegroundColor Red
    Write-Host ""
    Write-Host "Posibles causas:" -ForegroundColor Yellow
    Write-Host "  1. Pulsar está iniciando (espera un poco más y vuelve a intentar)" -ForegroundColor White
    Write-Host "  2. Error al iniciar Pulsar (revisa logs: docker logs nuam-pulsar)" -ForegroundColor White
    Write-Host "  3. Puerto 8080 está ocupado por otro proceso" -ForegroundColor White
    Write-Host ""
    Write-Host "Para ver logs de Pulsar:" -ForegroundColor Cyan
    Write-Host "  docker logs nuam-pulsar" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ Pulsar Admin API está listo" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Puedes acceder a:" -ForegroundColor Cyan
Write-Host "  - Admin API: http://localhost:8080" -ForegroundColor White
Write-Host "  - Pulsar Service: pulsar://localhost:6650" -ForegroundColor White

