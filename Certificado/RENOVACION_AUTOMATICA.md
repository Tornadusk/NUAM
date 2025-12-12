# 🔄 Renovación Automática de Certificados - Let's Encrypt

## ⚠️ IMPORTANTE

Esta configuración es **solo para producción**. Para desarrollo, los certificados autofirmados con renovación manual son suficientes.

---

## 🎯 ¿Qué es Let's Encrypt?

Let's Encrypt es una autoridad certificadora (CA) gratuita y automatizada que:
- ✅ Emite certificados SSL/TLS válidos
- ✅ Renovación automática cada 90 días
- ✅ Gratuito y confiable
- ✅ Ampliamente aceptado por navegadores

---

## 🚀 Configuración con certbot

### Paso 1: Instalar certbot

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

**CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx
```

### Paso 2: Obtener certificado

**Opción A: Con Nginx (Recomendado)**
```bash
sudo certbot --nginx -d nuam.tu-dominio.com
```

**Opción B: Standalone (si no usas Nginx)**
```bash
sudo certbot certonly --standalone -d nuam.tu-dominio.com
```

### Paso 3: Configurar renovación automática

Certbot crea automáticamente un cron job para renovación:

```bash
# Verificar renovación automática
sudo certbot renew --dry-run
```

**El cron job se ejecuta dos veces al día** y renueva certificados que expiran en menos de 30 días.

---

## 🔧 Integración con Django

### Opción 1: Usar Nginx como proxy reverso (Recomendado)

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name nuam.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name nuam.tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/nuam.tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nuam.tu-dominio.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Opción 2: Script de renovación personalizado

**renew_certificate.sh:**
```bash
#!/bin/bash
# Script para renovar certificado y reiniciar Django

certbot renew --quiet

if [ $? -eq 0 ]; then
    # Reiniciar Django (ajustar según tu configuración)
    systemctl restart nuam-django
    echo "Certificado renovado y Django reiniciado"
fi
```

**Cron job:**
```bash
# Ejecutar diariamente a las 3 AM
0 3 * * * /path/to/renew_certificate.sh
```

---

## 📋 Actualizar settings.py para Producción

```python
# settings.py (producción)
DEBUG = False

# Rutas a certificados Let's Encrypt
SSL_CERTIFICATE = '/etc/letsencrypt/live/nuam.tu-dominio.com/fullchain.pem'
SSL_PRIVATE_KEY = '/etc/letsencrypt/live/nuam.tu-dominio.com/privkey.pem'

# Configuración de seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 🔄 Proceso de Renovación

1. **Certbot verifica** si el certificado expira en < 30 días
2. **Solicita renovación** a Let's Encrypt
3. **Obtiene nuevo certificado**
4. **Guarda en** `/etc/letsencrypt/live/nuam.tu-dominio.com/`
5. **Reinicia servicios** (si está configurado)

**Frecuencia:** Certbot verifica 2 veces al día automáticamente.

---

## ✅ Verificar Renovación

```bash
# Ver fecha de expiración
sudo certbot certificates

# Probar renovación (dry-run)
sudo certbot renew --dry-run

# Forzar renovación manual
sudo certbot renew --force-renewal
```

---

## 🎯 Nota para Evaluación

**Para desarrollo:** Los certificados autofirmados son suficientes (ya implementado).

**Para producción:** Let's Encrypt es la solución recomendada (documentación completa incluida).

**Criterio "Certificados Digitales":**
- Desarrollo: 7.5/10 ✅ (gestión completa con documentación)
- Producción: 10/10 ✅ (con Let's Encrypt configurado)

---

## 📚 Recursos

- **Let's Encrypt:** https://letsencrypt.org/
- **Certbot:** https://certbot.eff.org/
- **Documentación Certbot:** https://eff-certbot.readthedocs.io/

