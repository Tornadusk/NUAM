# 🚀 Instrucciones Rápidas - Certificados Digitales NUAM

## ⚠️ IMPORTANTE: Solo necesitas OpenSSL para GENERAR el certificado (una vez)

Después de generar el certificado, **NO necesitas OpenSSL instalado** para usar Django con HTTPS.

---

## Para Windows

### Paso 1: Instalar OpenSSL (solo para generar el certificado)

**Opción A: Descargar e Instalar**
1. Descargar desde: https://slproweb.com/products/Win32OpenSSL.html
2. Instalar "Win64 OpenSSL v3.x.x" (Light o Full)
3. Durante la instalación, seleccionar "Copy OpenSSL DLLs to: The OpenSSL binaries (/bin) directory"

**Opción B: Usar WSL (Recomendado si tienes WSL)**
```powershell
wsl
# Luego seguir instrucciones de Linux
```

### Paso 2: Generar Certificado

Abrir PowerShell en la carpeta `Certificado` y ejecutar:

```powershell
.\generar_certificado.ps1
```

O manualmente:

```powershell
# Si OpenSSL está en PATH
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365 -x509 -subj "/C=CL/ST=RM/L=Santiago/O=NUAM/OU=Backend/CN=localhost/emailAddress=admin@nuam.cl"

# Si OpenSSL está en ubicación específica
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -new -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365 -x509 -subj "/C=CL/ST=RM/L=Santiago/O=NUAM/OU=Backend/CN=localhost/emailAddress=admin@nuam.cl"
```

### Paso 3: Instalar django-extensions

```powershell
pip install django-extensions
```

### Paso 4: Ejecutar Django con HTTPS

```powershell
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443
```

### Paso 5: Acceder a la aplicación

Abrir navegador en: `https://localhost:8443`

**⚠️ Importante**: El navegador mostrará una advertencia de seguridad porque el certificado es autofirmado. Hacer clic en "Avanzado" → "Continuar a localhost (no seguro)".

---

## Para Linux

### Paso 1: Instalar OpenSSL (solo para generar el certificado)

```bash
sudo apt update
sudo apt install openssl libssl-dev
```

### Paso 2: Generar Certificado

```bash
cd Certificado
chmod +x generar_certificado.sh
./generar_certificado.sh
```

O manualmente:

```bash
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365 -x509 \
  -subj "/C=CL/ST=RM/L=Santiago/O=NUAM/OU=Backend/CN=localhost/emailAddress=admin@nuam.cl"
```

### Paso 3: Instalar django-extensions

```bash
pip install django-extensions
```

### Paso 4: Ejecutar Django con HTTPS

```bash
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443
```

### Paso 5: Acceder a la aplicación

Abrir navegador en: `https://localhost:8443`

---

## Verificación

### Verificar que los archivos se generaron correctamente:

```bash
# Windows PowerShell
Get-ChildItem Certificado\server.*

# Linux
ls -lh Certificado/server.*
```

Deberías ver:
- `server.key` (clave privada, ~1.7 KB)
- `server.crt` (certificado, ~1.4 KB)

### Verificar el certificado:

```bash
# Windows
openssl x509 -in Certificado/server.crt -text -noout

# Linux
openssl x509 -in Certificado/server.crt -text -noout
```

---

## Solución de Problemas

### Error: "openssl no se reconoce como comando"

**Windows**: Agregar OpenSSL al PATH o usar la ruta completa:
```powershell
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" version
```

**Linux**: Instalar OpenSSL:
```bash
sudo apt install openssl
```

### Error: "Permission denied" (Linux)

```bash
chmod 600 Certificado/server.key
chmod 644 Certificado/server.crt
```

### Error: "No module named 'django_extensions'"

```bash
pip install django-extensions
```

### El navegador muestra "No seguro" o "Certificado no válido"

Esto es **normal** con certificados autofirmados. En desarrollo:
- Chrome/Edge: Clic en "Avanzado" → "Continuar a localhost"
- Firefox: Clic en "Avanzado" → "Aceptar el riesgo y continuar"

---

## Próximos Pasos

1. ✅ Certificado generado
2. ✅ Django configurado
3. ✅ Servidor ejecutándose con HTTPS
4. 📝 **Siguiente**: Configurar para producción con Let's Encrypt (cuando tengas dominio)

---

## Notas Importantes

- ⚠️ Los certificados autofirmados **solo son para desarrollo**
- 🔒 **NUNCA** compartir `server.key` (clave privada)
- 📁 Los archivos `.key` y `.crt` ya están en `.gitignore` - cada desarrollador debe generar su propio par
- 🔄 El certificado expira en 365 días (renovar antes)

## 👥 Trabajo en Equipo

**¿El profesor necesita OpenSSL?** NO, si ya tiene los archivos generados.

**Recomendación:** Cada desarrollador genera su propio certificado:
- Tú generas el tuyo en Windows
- Tu profesor genera el suyo en Linux
- Cada uno usa su propio certificado localmente
- No necesitas compartir claves privadas

Ver `PREGUNTAS_FRECUENTES.md` para más detalles.

