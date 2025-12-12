# Certificados Digitales - NUAM

Este directorio contiene los certificados SSL/TLS y scripts para generar certificados digitales para NUAM.

## 📋 Índice

- [Requisitos](#requisitos)
- [Generación de Certificados](#generación-de-certificados)
- [Configuración en Django](#configuración-en-django)
- [Uso en Desarrollo](#uso-en-desarrollo)
- [Uso en Producción](#uso-en-producción)
- [Trabajo en Equipo](#trabajo-en-equipo)
- [Troubleshooting](#troubleshooting)

## 🔧 Requisitos

### Windows

**⚠️ IMPORTANTE**: Solo necesitas OpenSSL para **GENERAR** el certificado (una vez). Después de generarlo, NO necesitas OpenSSL instalado para usar el certificado.

1. **Opción 1: OpenSSL para Windows** (Recomendado)
   - Descargar desde: https://slproweb.com/products/Win32OpenSSL.html
   - Instalar la versión "Win64 OpenSSL v3.x.x Light" (suficiente para generar certificados)
   - Durante la instalación, seleccionar "Copy OpenSSL DLLs to: The OpenSSL binaries (/bin) directory"
   - Agregar OpenSSL al PATH del sistema (opcional, pero recomendado)

2. **Opción 2: WSL (Windows Subsystem for Linux)**
   - Instalar WSL desde Microsoft Store
   - Usar los scripts de Linux dentro de WSL
   - No necesitas instalar OpenSSL en Windows

3. **Opción 3: Pedirle a tu profesor que lo genere**
   - Tu profesor puede generar el certificado en Linux
   - Te pasa los archivos `server.crt` y `server.key`
   - Los certificados son compatibles entre Windows y Linux

### Linux

```bash
# Instalar OpenSSL
sudo apt install openssl

# Instalar versión development (headers)
sudo apt install libssl-dev

# Verificar instalación
openssl version -a
```

## 🔐 Generación de Certificados

### Método 1: Script Automático (Recomendado)

#### Windows (PowerShell)

```powershell
# Ejecutar desde la carpeta Certificado
.\generar_certificado.ps1
```

#### Linux/Mac

```bash
# Ejecutar desde la carpeta Certificado
chmod +x generar_certificado.sh
./generar_certificado.sh
```

### Método 2: Manual

#### Paso 1: Generar Clave Privada

```bash
# Generar clave privada RSA de 2048 bits
openssl genrsa -out private.key 2048

# O con passphrase (más seguro)
openssl genrsa -aes256 -out private.key 2048
```

#### Paso 2: Generar Certificado Autofirmado

```bash
# Generar certificado autofirmado válido por 365 días
openssl req -new -x509 -key private.key -out certificate.crt -days 365
```

Durante la generación, se pedirán los siguientes datos:
- **Country Name (2 letter code)**: `CL` (Chile)
- **State or Province Name**: `RM` (Región Metropolitana)
- **Locality Name**: `Santiago`
- **Organization Name**: `NUAM`
- **Organizational Unit Name**: `Backend`
- **Common Name**: `localhost` o `127.0.0.1` (para desarrollo)
- **Email Address**: `admin@nuam.cl`

#### Paso 3: Generar en un Solo Paso (Más Rápido)

```bash
# Generar clave y certificado en un solo comando
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365 -x509 \
  -subj "/C=CL/ST=RM/L=Santiago/O=NUAM/OU=Backend/CN=localhost/emailAddress=admin@nuam.cl"
```

### Verificar Certificado

```bash
# Ver detalles del certificado
openssl x509 -in certificate.crt -text -noout

# Verificar validez
openssl x509 -in certificate.crt -noout -dates
```

## ⚙️ Configuración en Django

### 1. Instalar django-extensions (Opcional pero recomendado)

```bash
pip install django-extensions
```

Agregar a `INSTALLED_APPS` en `settings.py`:

```python
INSTALLED_APPS = [
    # ... otras apps
    'django_extensions',  # Para runserver_plus con SSL
]
```

### 2. Configurar Settings

Agregar al final de `proyecto_nuam/settings.py`:

```python
# ============================================================
# CONFIGURACIÓN SSL/HTTPS
# ============================================================

# Rutas a los certificados (relativas a BASE_DIR)
SSL_CERTIFICATE = BASE_DIR / 'Certificado' / 'server.crt'
SSL_PRIVATE_KEY = BASE_DIR / 'Certificado' / 'server.key'

# Configuración de seguridad HTTPS
if not DEBUG:
    # En producción, forzar HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # En desarrollo, permitir HTTP pero mostrar advertencias
    SECURE_SSL_REDIRECT = False
```

### 3. Actualizar ALLOWED_HOSTS

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'nuam.local']
```

## 🚀 Uso en Desarrollo

### Opción 1: Django con django-extensions (Recomendado)

```bash
# Ejecutar servidor con SSL
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 0.0.0.0:8443
```

Acceder a: `https://localhost:8443`

### Opción 2: Usar Nginx como Proxy Reverso

Ver `nginx.conf.example` en esta carpeta.

### Opción 3: Usar Gunicorn con SSL

```bash
gunicorn proyecto_nuam.wsgi:application \
  --bind 0.0.0.0:8443 \
  --keyfile Certificado/server.key \
  --certfile Certificado/server.crt
```

## 🌐 Uso en Producción

### Certificados Válidos

Para producción, usar certificados de una Autoridad Certificadora (CA) confiable:

1. **Let's Encrypt (Gratuito)**
   ```bash
   sudo apt install certbot
   sudo certbot certonly --standalone -d tu-dominio.com
   ```

2. **Comerciales**: Comprar certificado de DigiCert, GlobalSign, etc.

### Configuración Nginx

Ver `nginx.production.conf.example` para configuración completa.

## 🔍 Troubleshooting

### Error: "certificate verify failed"

**Solución**: Los certificados autofirmados no son confiables por defecto. En desarrollo:
- Chrome/Edge: Hacer clic en "Avanzado" → "Continuar a localhost"
- Firefox: Hacer clic en "Avanzado" → "Aceptar el riesgo"

### Error: "OpenSSL no encontrado"

**Windows**:
```powershell
# Verificar si está instalado
openssl version

# Si no está, agregar al PATH o usar ruta completa
C:\Program Files\OpenSSL-Win64\bin\openssl.exe version
```

**Linux**:
```bash
sudo apt update
sudo apt install openssl libssl-dev
```

### Error: "Permission denied" en Linux

```bash
# Dar permisos correctos a los archivos
chmod 600 private.key
chmod 644 certificate.crt
```

### El navegador muestra "No seguro"

Esto es normal con certificados autofirmados. En desarrollo, aceptar la excepción.
En producción, usar certificados de una CA confiable.

## 📚 Recursos Adicionales

- [Documentación OpenSSL](https://www.openssl.org/docs/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Let's Encrypt](https://letsencrypt.org/)

## 📝 Notas Importantes

1. **Certificados Autofirmados**: Solo para desarrollo. No usar en producción.
2. **Claves Privadas**: Nunca compartir o subir a repositorios públicos.
3. **Renovación**: Los certificados expiran. Renovar antes de la fecha de expiración.
4. **Seguridad**: Mantener las claves privadas con permisos restrictivos (600).

## 🔐 Archivos Generados

Después de generar los certificados, deberías tener:

```
Certificado/
├── server.key           # Clave privada (NO COMPARTIR, NO SUBIR AL REPO)
├── server.crt           # Certificado para servidor (SÍ se puede subir)
└── README.md            # Este archivo
```

**⚠️ IMPORTANTE**: 
- ✅ `server.crt` **SÍ se puede subir** al repositorio (es público)
- ❌ `server.key` **NUNCA subir** al repositorio (ya está en `.gitignore`)
- 🔒 Las claves privadas están protegidas automáticamente

## 👥 Trabajo en Equipo

### ⚠️ Por qué NO subir la clave privada al repositorio

**Razones de seguridad:**
1. La clave privada (`server.key`) es como una contraseña maestra
2. Quien la tiene puede hacerse pasar por tu servidor
3. Los repositorios Git guardan historial (aunque borres el archivo después)
4. Es una mala práctica de seguridad compartir claves privadas

### ✅ Opción Recomendada: Cada desarrollador genera su propio certificado

**Ventajas:**
- ✅ Cada uno tiene su propia clave privada (más seguro)
- ✅ No necesitas compartir archivos sensibles
- ✅ Los certificados autofirmados son solo para desarrollo
- ✅ Funciona igual en Windows y Linux
- ✅ Es la práctica recomendada en la industria

**Proceso:**
1. Tú generas tu certificado en Windows: `.\generar_certificado.ps1`
2. Tu profesor genera su certificado en Linux: `./generar_certificado.sh`
3. Cada uno usa su propio certificado localmente
4. No necesitas compartir `server.key` (clave privada)

**En el repositorio:**
- ✅ Subir scripts de generación (`.ps1`, `.sh`)
- ✅ Subir documentación
- ✅ Subir `server.crt` (opcional, puede regenerarse)
- ❌ NO subir `server.key` (ya protegido en `.gitignore`)

### ⚠️ Si REALMENTE necesitas compartir el certificado

Si por alguna razón necesitas que tu profesor use el mismo certificado:

1. **Comparte `server.key` por un canal seguro:**
   - ✅ USB/Disco externo (más seguro)
   - ✅ Mensajería cifrada (Signal, WhatsApp)
   - ❌ NUNCA por Git/GitHub
   - ❌ NUNCA por email sin cifrar

2. **Tu profesor copia `server.key` a su carpeta `Certificado/`**

**Ver `COMPARTIR_CERTIFICADO.md` para más detalles sobre cómo compartir de forma segura.**

**Pero recuerda:** Para desarrollo local, cada uno puede tener su propio certificado sin problemas. Los certificados autofirmados son solo para desarrollo y no afecta la funcionalidad.

### ❓ ¿Si cada uno tiene un certificado diferente, funcionará?

**Respuesta: SÍ, absolutamente.** ✅

Cada certificado autofirmado funciona **independientemente**. No necesitan ser iguales. Lo importante es que cada uno tenga su par `server.crt` + `server.key` que coincidan entre sí.

**Ver `COMO_FUNCIONAN_CERTIFICADOS.md` y `EXPLICACION_SIMPLE.md` para más detalles.**

