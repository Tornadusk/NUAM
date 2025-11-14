# 🔒 Patrones de Seguridad Implementados en Proyecto NUAM

## 📋 Resumen Ejecutivo

El código implementa **múltiples patrones de seguridad avanzados** que protegen contra vulnerabilidades conocidas según OWASP Top 10 y mejores prácticas de Django. A continuación se detallan los patrones implementados y los que requieren mejora.

---

## ✅ PATRONES DE SEGURIDAD IMPLEMENTADOS

### 1. **Protección contra Inyección SQL (A01:2021 - Broken Access Control)**

**✅ IMPLEMENTADO**

Django ORM protege automáticamente contra SQL Injection mediante:
- **Parameterized Queries**: Todas las consultas usan parámetros preparados
- **ORM Abstraction**: No se ejecuta SQL directo (excepto en casos controlados)

**Evidencia**:
```python
# api/views.py - Todas las consultas usan ORM
corredoras = UsuarioCorredora.objects.filter(id_usuario=usuario_obj).values_list('id_corredora_id', flat=True)
calificaciones = Calificacion.objects.filter(id_corredora__in=user_corredoras)
```

**Archivo**: `api/views.py` (líneas 437-613, 2223-2300)

---

### 2. **Autenticación y Autorización (A01:2021 - Broken Access Control)**

**✅ IMPLEMENTADO**

#### **Autenticación**:
- **SessionAuthentication**: Autenticación basada en sesiones de Django
- **BasicAuthentication**: Autenticación HTTP Basic (REST Framework)

**Evidencia**:
```python
# proyecto_nuam/settings.py (líneas 179-182)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}
```

#### **Autorización RBAC (Role-Based Access Control)**:
- **Permisos por rol**: Administrador, Operador, Analista, Consultor, Auditor
- **Row-Level Security**: Usuarios solo ven datos de sus corredoras asignadas

**Evidencia**:
```python
# api/views.py (líneas 489-543)
def _can_edit_calificacion(self, calificacion, usuario):
    """
    Verificar si el usuario puede editar una calificación específica
    Reglas:
    - Admin/Superuser: Puede editar todas
    - Operador: Solo puede editar las que él mismo creó
    - Analista: Puede editar todas de su corredora
    - Consultor: NO puede editar (solo lectura)
    - Auditor: NO puede editar (solo lectura)
    """
```

#### **Permisos en Endpoints**:
- **IsAuthenticatedOrReadOnly**: GET público, POST/PUT/DELETE requieren autenticación

**Evidencia**:
```python
# api/views.py (múltiples ViewSets)
permission_classes = [permissions.IsAuthenticatedOrReadOnly]
```

**Archivos**:
- `proyecto_nuam/settings.py` (líneas 176-182)
- `api/views.py` (líneas 437-543, 595-613, 658-699)

---

### 3. **Protección CSRF (A03:2021 - Injection)**

**✅ IMPLEMENTADO**

**Middleware CSRF activo**:
```python
# proyecto_nuam/settings.py (línea 57)
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]
```

**Protección en Frontend**:
```javascript
// templates/static/js/mantenedor/core.js
export function fetchWithCSRF(url, options = {}) {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }
}
```

**⚠️ NOTA**: Verificar que todos los formularios HTML incluyan `{% csrf_token %}`

**Archivos**:
- `proyecto_nuam/settings.py` (línea 57)
- `templates/static/js/mantenedor/core.js` (líneas 42-69)

---

### 4. **Protección XSS (A03:2021 - Injection)**

**✅ IMPLEMENTADO**

Django protege automáticamente contra XSS mediante:
- **Auto-escape**: Todos los templates escapan HTML por defecto
- **Safe filter**: Solo se marca explícitamente contenido seguro

**Evidencia**:
```python
# Django templates escapan automáticamente
{{ user.nombre }}  # Se escapa automáticamente
{{ user_roles_json|safe }}  # Solo se marca como safe explícitamente (JSON para JS)
```

**Validación en CSV Export**:
```javascript
// templates/static/js/mantenedor/core.js (líneas 151-159)
const escapeCell = (cell) => {
    // Escapar comillas dobles
    value = value.replace(/"/g, '""');
    // Encerrar en comillas si contiene delimitador o comillas
    if (needsQuote) {
        value = `"${value}"`;
    }
};
```

**Archivos**:
- Django templates (auto-escape por defecto)
- `templates/static/js/mantenedor/core.js` (líneas 151-159)

---

### 5. **Row-Level Security (RLS)**

**✅ IMPLEMENTADO**

**Filtrado por Corredora del Usuario**:
```python
# api/views.py (líneas 510-525)
def get_queryset(self):
    queryset = super().get_queryset()
    usuario = self.request.user
    
    # Admin/Superuser puede ver todas
    if self._is_admin_or_superuser(usuario):
        return queryset
    
    # Otros usuarios solo ven sus corredoras
    user_corredoras = self._get_user_corredoras(usuario)
    if user_corredoras:
        queryset = queryset.filter(id_corredora__in=user_corredoras)
    else:
        queryset = queryset.none()  # No tiene corredoras = no ve nada
    
    return queryset
```

**Validación en Creación/Actualización**:
```python
# api/views.py (líneas 549-596)
def perform_create(self, serializer):
    usuario = self.request.user
    user_corredoras = self._get_user_corredoras(usuario)
    
    # Validar que la corredora pertenece al usuario
    if serializer.validated_data['id_corredora'].id_corredora not in user_corredoras:
        raise permissions.PermissionDenied("No tiene permisos para crear calificaciones en esta corredora")
```

**Archivo**: `api/views.py` (líneas 437-613, 2223-2300)

---

### 6. **Auditoría Completa (A09:2021 - Security Logging and Monitoring)**

**✅ IMPLEMENTADO**

**Tabla de Auditoría**:
```python
# auditoria/models.py
class Auditoria(models.Model):
    actor_id = models.ForeignKey('usuarios.Usuario', ...)
    entidad = models.CharField(...)  # 'CALIFICACION', 'CARGA', etc.
    entidad_id = models.BigIntegerField()
    accion = models.CharField(...)  # 'INSERT', 'UPDATE', 'DELETE'
    fecha = models.DateTimeField(auto_now_add=True)
    valores_antes = OracleJSONField(...)  # Snapshot antes del cambio
    valores_despues = OracleJSONField(...)  # Snapshot después del cambio
```

**Registro Automático**:
```python
# api/views.py (en CalificacionViewSet)
Auditoria.objects.create(
    actor_id=usuario,
    entidad='CALIFICACION',
    entidad_id=calificacion.id_calificacion,
    accion='UPDATE',
    fuente='API',
    valores_antes={'campo': 'valor_anterior'},
    valores_despues={'campo': 'valor_nuevo'}
)
```

**Archivos**:
- `auditoria/models.py` (líneas 5-50)
- `api/views.py` (múltiples lugares donde se registra auditoría)

---

### 7. **Validación de Entrada (A03:2021 - Injection)**

**✅ IMPLEMENTADO**

#### **Validación de Archivos**:
```python
# api/views.py (líneas 1147-1152)
file = request.FILES['file']
is_excel = file.name.endswith('.xlsx') or file.name.endswith('.xls')
is_csv = file.name.endswith('.csv')

if not (is_csv or is_excel):
    return Response({'error': 'El archivo debe ser CSV o Excel (.xlsx, .xls)'}, 
                    status=status.HTTP_400_BAD_REQUEST)
```

#### **Validación de Headers**:
```python
# api/views.py (líneas 1279-1300)
required_alias_groups = [
    ('corredora',),
    ('instrumento', 'instrumento_codigo'),
    ('fuente', 'fuente_codigo'),
    ('moneda', 'moneda_codigo'),
    ('ejercicio',),
    ('fecha_pago', 'fecha'),
    ('secuencia_evento', 'secuencia')
]

# Validar headers requeridos
missing_headers = []
for alias_group in required_alias_groups:
    found = False
    for alias in alias_group:
        if normalize_header(alias) in [normalize_header(h) for h in raw_headers]:
            found = True
            break
    if not found:
        missing_headers.append(alias_group[0])
```

#### **Validación de Modelos Django**:
```python
# calificaciones/models.py
class Calificacion(models.Model):
    ejercicio = models.IntegerField()  # Validación de tipo automática
    fecha_pago = models.DateField()    # Validación de formato automática
    # ...
    
    class Meta:
        unique_together = [['id_corredora', 'id_instrumento', 'ejercicio', 'secuencia_evento']]
```

**Archivos**:
- `api/views.py` (líneas 1140-1350, 1761-1950)
- Modelos Django (validación automática)

---

### 8. **Hashing de Contraseñas (A07:2021 - Identification and Authentication Failures)**

**✅ IMPLEMENTADO**

Django usa **PBKDF2** por defecto con:
- **Salt único** por contraseña
- **Iteraciones**: 260,000 (ajustable)

**Evidencia**:
```python
# Django automáticamente hashea contraseñas
user.set_password('password')  # Se hashea automáticamente
user.check_password('password')  # Verifica hash automáticamente
```

**Validadores de Contraseña**:
```python
# proyecto_nuam/settings.py (líneas 122-135)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

**Archivo**: `proyecto_nuam/settings.py` (líneas 122-135)

---

### 9. **Protección Clickjacking (A05:2021 - Security Misconfiguration)**

**✅ IMPLEMENTADO**

**Middleware X-Frame-Options**:
```python
# proyecto_nuam/settings.py (línea 60)
MIDDLEWARE = [
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ...
]
```

Esto establece automáticamente el header `X-Frame-Options: DENY` para prevenir que la página sea embebida en iframes.

**Archivo**: `proyecto_nuam/settings.py` (línea 60)

---

### 10. **Protección Security Headers (A05:2021 - Security Misconfiguration)**

**✅ PARCIALMENTE IMPLEMENTADO**

**SecurityMiddleware activo**:
```python
# proyecto_nuam/settings.py (línea 54)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ...
]
```

Este middleware agrega varios headers de seguridad, pero se recomienda configurar explícitamente en producción.

**Recomendaciones para producción**:
```python
# settings.py (agregar en producción)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**Archivo**: `proyecto_nuam/settings.py` (línea 54)

---

### 11. **Validación de Tipo de Datos**

**✅ IMPLEMENTADO**

**Validación de Tipos en CSV/Excel Import**:
```python
# api/views.py (líneas 1216-1221)
elif isinstance(value, (int, float)) and header.lower() in ['ejercicio', 'linea']:
    # Mantener números para ejercicio y linea
    row_dict[header] = str(int(value))
elif isinstance(value, datetime):
    # Formatear fecha como YYYY-MM-DD
    row_dict[header] = value.strftime('%Y-%m-%d')
```

**Archivo**: `api/views.py` (líneas 1207-1221)

---

### 12. **Transacciones Atómicas (Integridad de Datos)**

**✅ IMPLEMENTADO**

**Uso de transacciones para garantizar consistencia**:
```python
# api/views.py (líneas 856-891)
with transaction.atomic():
    # Eliminar factores antiguos
    CalificacionFactorDetalle.objects.filter(id_calificacion=calificacion).delete()
    
    # Guardar factores calculados
    for codigo, factor in factores_calculados.items():
        CalificacionFactorDetalle.objects.create(...)
    
    # Actualizar calificación
    calificacion.save()
```

**Archivo**: `api/views.py` (múltiples lugares con `transaction.atomic()`)

---

## ⚠️ PATRONES QUE REQUIEREN MEJORA

### 1. **Configuración de Producción**

**❌ NO IMPLEMENTADO (Solo Desarrollo)**

```python
# proyecto_nuam/settings.py (líneas 24, 27, 29)
SECRET_KEY = 'django-insecure-...'  # ⚠️ Hardcodeado
DEBUG = True  # ⚠️ Debe ser False en producción
ALLOWED_HOSTS = []  # ⚠️ Debe incluir dominios de producción
```

**Recomendaciones**:
```python
# Usar variables de entorno
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',')])
```

---

### 2. **Rate Limiting**

**❌ NO IMPLEMENTADO**

Se recomienda agregar rate limiting para prevenir:
- Brute force attacks
- DoS attacks
- API abuse

**Recomendación**:
```python
# Instalar django-ratelimit
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

### 3. **Validación de Tamaño de Archivo**

**⚠️ PARCIALMENTE IMPLEMENTADO**

Se valida el tipo de archivo pero no el tamaño máximo.

**Recomendación**:
```python
# api/views.py - upload_factores()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

if file.size > MAX_FILE_SIZE:
    return Response({'error': f'El archivo excede el tamaño máximo de {MAX_FILE_SIZE / 1024 / 1024} MB'}, 
                    status=status.HTTP_400_BAD_REQUEST)
```

---

### 4. **Validación MIME Type**

**⚠️ PARCIALMENTE IMPLEMENTADO**

Se valida por extensión pero no por MIME type real del archivo.

**Recomendación**:
```python
import magic

file_mime = magic.from_buffer(file.read(1024), mime=True)
if file_mime not in ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
    return Response({'error': 'Tipo de archivo no permitido'}, 
                    status=status.HTTP_400_BAD_REQUEST)
```

---

### 5. **CSRF Token en Templates**

**⚠️ VERIFICAR**

Verificar que todos los formularios HTML incluyan `{% csrf_token %}`.

**Archivos a revisar**:
- `templates/calificaciones/partials/_modals_*.html`
- `templates/registration/login.html`

---

## 📊 RESUMEN DE PATRONES IMPLEMENTADOS

| Patrón de Seguridad | Estado | Archivo(s) |
|---------------------|--------|------------|
| Protección SQL Injection | ✅ Implementado | Django ORM (todos los archivos) |
| Autenticación y Autorización | ✅ Implementado | `settings.py`, `api/views.py` |
| RBAC (Role-Based Access Control) | ✅ Implementado | `api/views.py` (líneas 437-543) |
| Row-Level Security | ✅ Implementado | `api/views.py` (líneas 510-525) |
| Protección CSRF | ✅ Implementado | `settings.py`, `core.js` |
| Protección XSS | ✅ Implementado | Django auto-escape |
| Validación de Entrada | ✅ Implementado | `api/views.py` (líneas 1140-1350) |
| Hashing de Contraseñas | ✅ Implementado | Django PBKDF2 (automático) |
| Protección Clickjacking | ✅ Implementado | `settings.py` (línea 60) |
| Auditoría Completa | ✅ Implementado | `auditoria/models.py`, `api/views.py` |
| Transacciones Atómicas | ✅ Implementado | `api/views.py` (múltiples lugares) |
| Security Headers | ⚠️ Parcial | `settings.py` (requiere configuración producción) |
| Rate Limiting | ❌ No implementado | Requiere instalación |
| Validación Tamaño Archivo | ❌ No implementado | Requiere agregar |
| Validación MIME Type | ❌ No implementado | Requiere agregar |

---

## ✅ CONCLUSIÓN

**El código implementa múltiples patrones de seguridad avanzados** que protegen contra vulnerabilidades conocidas:

1. ✅ **Protección contra SQL Injection** (Django ORM)
2. ✅ **Autenticación y Autorización RBAC**
3. ✅ **Row-Level Security** (filtrado por corredora)
4. ✅ **Protección CSRF y XSS**
5. ✅ **Validación de entrada**
6. ✅ **Hashing seguro de contraseñas**
7. ✅ **Auditoría completa**
8. ✅ **Transacciones atómicas**

**Recomendaciones para producción**:
- Configurar variables de entorno para `SECRET_KEY` y `DEBUG`
- Agregar rate limiting
- Validar tamaño y MIME type de archivos
- Configurar security headers explícitamente
- Verificar `{% csrf_token %}` en todos los formularios

**Evaluación**: **8/10** - Implementación sólida con mejoras recomendadas para producción.

---

**Archivos Principales**:
- `proyecto_nuam/settings.py` (configuración de seguridad)
- `api/views.py` (permisos, validaciones, auditoría)
- `auditoria/models.py` (modelo de auditoría)
- `templates/static/js/mantenedor/core.js` (CSRF protection en frontend)

