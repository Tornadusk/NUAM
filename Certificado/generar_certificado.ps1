# Script PowerShell para generar certificado SSL autofirmado para NUAM
# Compatible con Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Generador de Certificado SSL - NUAM" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si OpenSSL está instalado
$opensslPath = $null
$possiblePaths = @(
    "openssl",
    "C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
    "C:\Program Files (x86)\OpenSSL-Win64\bin\openssl.exe",
    "C:\OpenSSL-Win64\bin\openssl.exe"
)

foreach ($path in $possiblePaths) {
    try {
        $result = & $path version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $opensslPath = $path
            break
        }
    } catch {
        continue
    }
}

if (-not $opensslPath) {
    Write-Host "❌ Error: OpenSSL no está instalado o no está en el PATH." -ForegroundColor Red
    Write-Host "   Opciones:" -ForegroundColor Yellow
    Write-Host "   1. Instalar desde: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Yellow
    Write-Host "   2. Usar WSL (Windows Subsystem for Linux)" -ForegroundColor Yellow
    Write-Host "   3. Usar Git Bash (si tienes Git instalado)" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ OpenSSL encontrado: $opensslPath" -ForegroundColor Green
$version = & $opensslPath version
Write-Host "   Versión: $version" -ForegroundColor Gray
Write-Host ""

# Directorio actual (donde está el script)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Configuración del certificado
$COUNTRY = "CL"
$STATE = "RM"
$CITY = "Santiago"
$ORGANIZATION = "NUAM"
$ORG_UNIT = "Backend"
$COMMON_NAME = "localhost"
$EMAIL = "admin@nuam.cl"
$DAYS = 365
$KEY_SIZE = 2048

Write-Host "Configuración del certificado:" -ForegroundColor Cyan
Write-Host "  País: $COUNTRY"
Write-Host "  Estado: $STATE"
Write-Host "  Ciudad: $CITY"
Write-Host "  Organización: $ORGANIZATION"
Write-Host "  Unidad: $ORG_UNIT"
Write-Host "  Nombre común: $COMMON_NAME"
Write-Host "  Email: $EMAIL"
Write-Host "  Válido por: $DAYS días"
Write-Host "  Tamaño de clave: $KEY_SIZE bits"
Write-Host ""

# Preguntar si quiere continuar
$response = Read-Host "¿Continuar con la generación? (s/n)"
if ($response -notmatch "^[SsYy]") {
    Write-Host "❌ Generación cancelada." -ForegroundColor Red
    exit 1
}

# Generar clave privada
Write-Host "🔑 Generando clave privada..." -ForegroundColor Yellow
& $opensslPath genrsa -out server.key $KEY_SIZE
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al generar la clave privada." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Clave privada generada: server.key" -ForegroundColor Green
Write-Host ""

# Generar certificado autofirmado
Write-Host "📜 Generando certificado autofirmado..." -ForegroundColor Yellow
$subject = "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORG_UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL"
& $opensslPath req -new -x509 -key server.key -out server.crt -days $DAYS -subj $subject

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al generar el certificado." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Certificado generado: server.crt" -ForegroundColor Green
Write-Host ""

# Mostrar información del certificado
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Información del Certificado" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
& $opensslPath x509 -in server.crt -text -noout | Select-String -Pattern "(Subject:|Issuer:|Not Before|Not After)"
Write-Host ""

# Verificar archivos
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Archivos Generados" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Get-ChildItem server.key, server.crt | Format-Table Name, Length, LastWriteTime -AutoSize
Write-Host ""

Write-Host "✅ ¡Certificado generado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Configurar Django para usar estos certificados" -ForegroundColor White
Write-Host "   2. Ejecutar: python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443" -ForegroundColor White
Write-Host "   3. Acceder a: https://localhost:8443" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   - Los certificados autofirmados solo son para desarrollo" -ForegroundColor Yellow
Write-Host "   - No compartir server.key (clave privada)" -ForegroundColor Yellow
Write-Host "   - Agregar *.key al .gitignore" -ForegroundColor Yellow
Write-Host ""

