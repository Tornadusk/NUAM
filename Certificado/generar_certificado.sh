#!/bin/bash

# Script para generar certificado SSL autofirmado para NUAM
# Compatible con Linux y macOS

echo "=========================================="
echo "  Generador de Certificado SSL - NUAM"
echo "=========================================="
echo ""

# Verificar si OpenSSL está instalado
if ! command -v openssl &> /dev/null; then
    echo "❌ Error: OpenSSL no está instalado."
    echo "   Instala OpenSSL con: sudo apt install openssl"
    exit 1
fi

echo "✅ OpenSSL encontrado: $(openssl version)"
echo ""

# Directorio actual (donde está el script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuración del certificado
COUNTRY="CL"
STATE="RM"
CITY="Santiago"
ORGANIZATION="NUAM"
ORG_UNIT="Backend"
COMMON_NAME="localhost"
EMAIL="admin@nuam.cl"
DAYS=365
KEY_SIZE=2048

echo "Configuración del certificado:"
echo "  País: $COUNTRY"
echo "  Estado: $STATE"
echo "  Ciudad: $CITY"
echo "  Organización: $ORGANIZATION"
echo "  Unidad: $ORG_UNIT"
echo "  Nombre común: $COMMON_NAME"
echo "  Email: $EMAIL"
echo "  Válido por: $DAYS días"
echo "  Tamaño de clave: $KEY_SIZE bits"
echo ""

# Preguntar si quiere continuar
read -p "¿Continuar con la generación? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "❌ Generación cancelada."
    exit 1
fi

# Generar clave privada
echo "🔑 Generando clave privada..."
openssl genrsa -out server.key $KEY_SIZE
if [ $? -ne 0 ]; then
    echo "❌ Error al generar la clave privada."
    exit 1
fi
echo "✅ Clave privada generada: server.key"
echo ""

# Generar certificado autofirmado
echo "📜 Generando certificado autofirmado..."
openssl req -new -x509 -key server.key -out server.crt -days $DAYS \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORG_UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL"

if [ $? -ne 0 ]; then
    echo "❌ Error al generar el certificado."
    exit 1
fi
echo "✅ Certificado generado: server.crt"
echo ""

# Establecer permisos correctos
chmod 600 server.key
chmod 644 server.crt
echo "✅ Permisos configurados correctamente"
echo ""

# Mostrar información del certificado
echo "=========================================="
echo "  Información del Certificado"
echo "=========================================="
openssl x509 -in server.crt -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After)"
echo ""

# Verificar archivos
echo "=========================================="
echo "  Archivos Generados"
echo "=========================================="
ls -lh server.key server.crt
echo ""

echo "✅ ¡Certificado generado exitosamente!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Configurar Django para usar estos certificados"
echo "   2. Ejecutar: python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443"
echo "   3. Acceder a: https://localhost:8443"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Los certificados autofirmados solo son para desarrollo"
echo "   - No compartir server.key (clave privada)"
echo "   - Agregar *.key al .gitignore"
echo ""

