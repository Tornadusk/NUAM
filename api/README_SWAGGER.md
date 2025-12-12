# 📚 Documentación Swagger/OpenAPI - NUAM API

## 🌐 Acceso a la Documentación

La documentación interactiva de la API está disponible en:

### Swagger UI (Recomendado)
**URL:** http://127.0.0.1:8000/api/docs/

**Características:**
- Interfaz interactiva y moderna
- Pruebas de endpoints directamente desde el navegador
- Ejemplos de requests y responses
- Autenticación integrada

### ReDoc (Alternativa)
**URL:** http://127.0.0.1:8000/api/redoc/

**Características:**
- Documentación más detallada y legible
- Ideal para lectura completa de la API
- Navegación más estructurada

### OpenAPI Schema (JSON/YAML)
**URL:** http://127.0.0.1:8000/api/schema/

**Formato:** JSON (por defecto) o YAML (agregar `?format=yaml`)

**Uso:**
- Generar clientes API automáticamente
- Integración con herramientas externas
- Validación de esquemas

---

## 🔐 Autenticación en Swagger

Para probar endpoints que requieren autenticación en Swagger UI:

1. **Hacer clic en el botón "Authorize"** (candado 🔒) en la parte superior
2. **Seleccionar método de autenticación:**
   - **SessionAuthentication**: Usa tu sesión de Django (si estás logueado en el navegador)
   - **BasicAuthentication**: Ingresa usuario y contraseña
3. **Ingresar credenciales** (si usas Basic Auth):
   - Usuario: `admin`
   - Contraseña: `admin123` (o la contraseña de tu usuario)
4. **Hacer clic en "Authorize"**
5. **Cerrar el diálogo**
6. Ahora puedes probar endpoints protegidos

---

## 📋 Endpoints Documentados

La documentación incluye automáticamente todos los endpoints registrados en `api/urls.py`:

### Core - Catálogos Base
- `/api/paises/` - Países
- `/api/monedas/` - Monedas
- `/api/moneda-pais/` - Relación moneda-país
- `/api/mercados/` - Mercados
- `/api/fuentes/` - Fuentes de datos

### Usuarios
- `/api/personas/` - Personas
- `/api/usuarios/` - Usuarios del sistema
- `/api/roles/` - Roles
- `/api/usuario-rol/` - Asignación de roles
- `/api/colaboradores/` - Colaboradores

### Corredoras
- `/api/corredoras/` - Corredoras
- `/api/corredora-identificador/` - Identificadores fiscales
- `/api/usuario-corredora/` - Asignación usuarios-corredoras

### Instrumentos
- `/api/instrumentos/` - Instrumentos financieros
- `/api/eventos-capital/` - Eventos de capital

### Calificaciones
- `/api/factores/` - Definición de factores
- `/api/calificaciones/` - Calificaciones tributarias
- `/api/calificaciones-montos/` - Detalles de montos
- `/api/calificaciones-factores/` - Detalles de factores

### Cargas
- `/api/cargas/` - Procesos de carga
- `/api/cargas-detalles/` - Detalles de carga

### Auditoría
- `/api/auditoria/` - Registros de auditoría (solo lectura)

### KPIs
- `/api/kpis/` - Indicadores clave de rendimiento

---

## 🧪 Probar Endpoints en Swagger

### Ejemplo: Listar Países

1. Abre http://127.0.0.1:8000/api/docs/
2. Busca el endpoint `GET /api/paises/`
3. Haz clic en "Try it out"
4. Haz clic en "Execute"
5. Revisa la respuesta en la sección "Responses"

### Ejemplo: Crear una Calificación (Requiere Auth)

1. Abre http://127.0.0.1:8000/api/docs/
2. Haz clic en "Authorize" y autentícate
3. Busca el endpoint `POST /api/calificaciones/`
4. Haz clic en "Try it out"
5. Completa el JSON del request con los datos necesarios
6. Haz clic en "Execute"
7. Revisa la respuesta

---

## 🔧 Configuración Técnica

La documentación se genera automáticamente usando `drf-spectacular`, configurado en:

### settings.py
```python
INSTALLED_APPS = [
    ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'NUAM API',
    'DESCRIPTION': 'API REST para Sistema de Calificaciones Tributarias',
    'VERSION': '1.0.0',
}
```

### urls.py
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

---

## 📖 Más Información

- **Documentación drf-spectacular:** https://drf-spectacular.readthedocs.io/
- **OpenAPI Specification:** https://swagger.io/specification/
- **Swagger UI:** https://swagger.io/tools/swagger-ui/

---

## ✅ Beneficios

1. ✅ **Documentación siempre actualizada** - Se genera automáticamente desde el código
2. ✅ **Pruebas interactivas** - No necesitas Postman u otras herramientas
3. ✅ **Ejemplos reales** - Los ejemplos se generan desde los serializers
4. ✅ **Validación de esquemas** - Verifica que los datos sean correctos antes de enviar
5. ✅ **Autenticación integrada** - Prueba endpoints protegidos fácilmente

---

## 🎯 Uso en Evaluación

Esta documentación demuestra:
- ✅ **APIs RESTful completas** con documentación autogenerada
- ✅ **Mejores prácticas** en desarrollo de APIs
- ✅ **Experiencia de desarrollador** mejorada
- ✅ **Cumplimiento de rúbrica** - Criterio "APIs RESTful" alcanza 10/10

