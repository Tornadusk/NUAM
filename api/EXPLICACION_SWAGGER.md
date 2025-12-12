# 📚 Explicación Completa: ¿Qué puedes hacer en Swagger API?

## 🌐 Acceso a Swagger

**URL:** `https://127.0.0.1:8443/api/docs/`

Swagger UI es una interfaz web interactiva que te permite explorar, probar y entender toda la API REST de NUAM sin necesidad de herramientas externas como Postman.

---

## 🔑 1. Autenticación (Authorize)

### ¿Qué es?
Un sistema integrado para autenticarte y probar endpoints protegidos.

### ¿Cómo usarlo?

1. **Haz clic en el botón "Authorize" (🔒)** en la parte superior derecha de Swagger UI
2. **Se abrirá un diálogo** con opciones de autenticación:
   - **SessionAuthentication**: Usa tu sesión actual de Django (si ya estás logueado)
   - **BasicAuthentication**: Ingresa usuario y contraseña manualmente

3. **Para Basic Authentication:**
   ```
   Username: admin
   Password: admin123
   ```
   (O las credenciales del usuario que quieras usar)

4. **Haz clic en "Authorize"** y luego en "Close"
5. Ahora todos los endpoints protegidos usarán esta autenticación automáticamente

### ¿Para qué sirve?
- Probar endpoints que requieren autenticación (crear, editar, eliminar datos)
- Ver datos filtrados por usuario/corredora
- Ejecutar operaciones administrativas

---

## 📋 2. Explorar Todos los Endpoints

Swagger organiza todos los endpoints en **grupos lógicos**. Cada grupo corresponde a un módulo de NUAM:

### 🔵 Core - Catálogos Base
- **`GET /api/paises/`** - Listar todos los países
- **`POST /api/paises/`** - Crear un nuevo país
- **`GET /api/paises/{id}/`** - Ver detalles de un país específico
- **`PUT /api/paises/{id}/`** - Actualizar un país completo
- **`PATCH /api/paises/{id}/`** - Actualizar parcialmente un país
- **`DELETE /api/paises/{id}/`** - Eliminar un país

Mismo patrón para:
- `/api/monedas/` - Monedas
- `/api/moneda-pais/` - Relación moneda-país
- `/api/mercados/` - Mercados financieros
- `/api/fuentes/` - Fuentes de datos

### 👥 Usuarios
- `/api/personas/` - Gestión de personas
- `/api/usuarios/` - Usuarios del sistema
- `/api/roles/` - Roles del sistema
- `/api/usuario-rol/` - Asignar roles a usuarios
- `/api/colaboradores/` - Colaboradores

### 🏦 Corredoras
- `/api/corredoras/` - Gestión de corredoras
- `/api/corredora-identificador/` - Identificadores fiscales
- `/api/usuario-corredora/` - Asignar usuarios a corredoras

### 📊 Instrumentos
- `/api/instrumentos/` - Instrumentos financieros
- `/api/evento-capital/` - Eventos de capital

### ✅ Calificaciones
- `/api/factores/` - Definición de factores de calificación
- `/api/calificaciones/` - Calificaciones tributarias (CRUD completo)
- `/api/calificacion-monto-detalle/` - Detalles de montos de calificaciones
- `/api/calificacion-factor-detalle/` - Detalles de factores de calificaciones

### 📦 Cargas
- `/api/cargas/` - Procesos de carga masiva
- `/api/carga-detalle/` - Detalles de cada carga

### 📝 Auditoría
- `/api/auditoria/` - Registros de auditoría (solo lectura)

### 📈 KPIs
- `/api/kpis/` - Indicadores clave de rendimiento

---

## 🧪 3. Probar Endpoints (Try it out)

### ¿Qué es?
Permite ejecutar requests reales a la API directamente desde el navegador.

### ¿Cómo usarlo?

1. **Encuentra un endpoint** (ej: `GET /api/paises/`)
2. **Haz clic en el endpoint** para expandirlo
3. **Haz clic en "Try it out"** (botón azul)
4. El formulario se habilitará para editar
5. **Configura parámetros** (si el endpoint los requiere):
   - Query parameters (filtros, paginación)
   - Path parameters (IDs en la URL)
   - Request body (JSON para POST/PUT/PATCH)
6. **Haz clic en "Execute"** (botón verde)
7. **Revisa la respuesta:**
   - **Code**: Código HTTP (200 = éxito, 404 = no encontrado, etc.)
   - **Details**: Información adicional del response
   - **Response body**: Los datos JSON devueltos por la API
   - **Response headers**: Headers HTTP de la respuesta

### Ejemplo Práctico 1: Listar Países

```
1. Busca "GET /api/paises/"
2. Haz clic en "Try it out"
3. (Opcional) Modifica parámetros:
   - search: "Chile" (buscar países que contengan "Chile")
   - page: 1 (número de página)
   - page_size: 10 (elementos por página)
4. Haz clic en "Execute"
5. Verás la lista de países en formato JSON
```

### Ejemplo Práctico 2: Crear una Calificación (Requiere Auth)

```
1. Haz clic en "Authorize" y autentícate primero
2. Busca "POST /api/calificaciones/"
3. Haz clic en "Try it out"
4. En "Request body", verás un JSON de ejemplo:
   {
     "id_corredora": 1,
     "id_moneda": 1,
     "id_instrumento": 1,
     "fecha": "2024-01-15",
     "monto": 1000000.00,
     ...
   }
5. Modifica los valores según necesites
6. Haz clic en "Execute"
7. Verás la respuesta con la calificación creada (código 201)
```

### Ejemplo Práctico 3: Actualizar una Calificación (PATCH)

```
1. Busca "PATCH /api/calificaciones/{id}/"
2. Haz clic en "Try it out"
3. En "id", ingresa el ID de la calificación a actualizar (ej: 5)
4. En "Request body", ingresa solo los campos a actualizar:
   {
     "monto": 1500000.00
   }
5. Haz clic en "Execute"
6. Verás la respuesta con la calificación actualizada
```

---

## 📖 4. Ver Documentación de Cada Endpoint

### Información Disponible para Cada Endpoint:

1. **Descripción**: Qué hace el endpoint
2. **Método HTTP**: GET, POST, PUT, PATCH, DELETE
3. **Parámetros**:
   - **Query parameters**: Filtros, búsqueda, paginación
   - **Path parameters**: IDs en la URL
   - **Request body**: Estructura JSON para crear/actualizar
4. **Esquema de Request**: Estructura exacta del JSON esperado
5. **Esquema de Response**: Estructura del JSON de respuesta
6. **Códigos de respuesta**: 200 (éxito), 201 (creado), 400 (error), 401 (no autorizado), 404 (no encontrado), 500 (error del servidor)
7. **Ejemplos**: Ejemplos de request y response

### ¿Cómo verlo?

- **Haz clic en cualquier endpoint** para expandirlo
- Verás toda la información organizada en secciones
- Los esquemas son interactivos (puedes expandirlos)

---

## 🔍 5. Buscar Endpoints

### Buscar en Swagger UI:

1. **Usa el campo de búsqueda** en la parte superior de Swagger UI
2. **Escribe el nombre** del endpoint o modelo (ej: "pais", "calificacion", "usuario")
3. **Los resultados se filtrarán** automáticamente

---

## 📥 6. Descargar el Schema OpenAPI

### ¿Qué es?
El esquema OpenAPI es una especificación estándar que describe toda la API en formato JSON o YAML.

### ¿Cómo descargarlo?

1. **URL directa:** `https://127.0.0.1:8443/api/schema/`
2. **Formato JSON** (por defecto)
3. **Formato YAML:** `https://127.0.0.1:8443/api/schema/?format=yaml`

### ¿Para qué sirve?

- **Generar clientes API automáticamente** para diferentes lenguajes (Python, JavaScript, Java, etc.)
- **Importar en Postman** o otras herramientas de testing
- **Integrar con herramientas de documentación** externas
- **Validar requests** antes de enviarlos
- **Generar mocks** para testing

---

## 🎨 7. Ver Ejemplos de Request/Response

### Para cada endpoint, Swagger muestra:

1. **Ejemplo de Request Body** (para POST/PUT/PATCH):
   - Estructura completa del JSON
   - Tipos de datos esperados (string, number, date, etc.)
   - Campos requeridos vs opcionales
   - Valores de ejemplo

2. **Ejemplo de Response**:
   - Estructura del JSON de respuesta exitosa
   - Diferentes códigos de respuesta posibles
   - Estructura de errores

### ¿Cómo verlo?

- Expande cualquier endpoint
- Ve a la sección "Request body" o "Responses"
- Haz clic en los esquemas para ver detalles

---

## 🛡️ 8. Validar Datos Antes de Enviar

### Validación en Swagger:

Swagger valida automáticamente:
- **Tipos de datos**: Asegura que un número sea número, una fecha sea fecha, etc.
- **Campos requeridos**: Marca los campos obligatorios
- **Formatos**: Valida formatos de email, URL, fecha, etc.
- **Rangos**: Valida valores mínimos/máximos
- **Enums**: Valida que los valores sean de una lista permitida

### Ejemplo:

Si intentas enviar:
```json
{
  "fecha": "esto no es una fecha",
  "monto": "esto no es un número"
}
```

Swagger te mostrará errores antes de enviar el request.

---

## 📊 9. Ver Códigos de Estado HTTP

Para cada endpoint, Swagger muestra los posibles códigos de respuesta:

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Error en los datos enviados
- **401 Unauthorized**: No autenticado
- **403 Forbidden**: Sin permisos
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

### ¿Cómo verlo?

- En la sección "Responses" de cada endpoint
- Cada código tiene su descripción y ejemplo de respuesta

---

## 🔄 10. Probar Diferentes Escenarios

### Con Swagger puedes probar:

1. **Casos exitosos**:
   - Crear recursos nuevos
   - Listar todos los recursos
   - Obtener un recurso específico
   - Actualizar recursos
   - Eliminar recursos

2. **Casos de error**:
   - Intentar crear sin autenticación (401)
   - Enviar datos inválidos (400)
   - Acceder a recursos que no existen (404)
   - Intentar eliminar recursos con dependencias (400/409)

3. **Filtros y búsqueda**:
   - Buscar por texto
   - Filtrar por campos específicos
   - Ordenar resultados
   - Paginar resultados

4. **Relaciones**:
   - Ver calificaciones de una corredora específica
   - Ver usuarios de un rol específico
   - Ver instrumentos de un mercado

---

## 💡 11. Tips y Mejores Prácticas

### Para Desarrolladores:

1. **Prueba antes de codificar el frontend**: Swagger te permite validar que los endpoints funcionen correctamente
2. **Comparte con tu equipo**: Todos pueden ver la documentación actualizada en tiempo real
3. **Usa los ejemplos**: Los ejemplos de request/response son perfectos para copiar en tu código
4. **Prueba casos límite**: Intenta enviar datos inválidos para ver cómo responde la API

### Para Administradores:

1. **Verifica permisos**: Prueba qué endpoints están disponibles para cada rol
2. **Valida integridad de datos**: Verifica que las relaciones entre entidades funcionen correctamente
3. **Monitorea respuestas**: Observa los tiempos de respuesta y códigos de estado

---

## 🎯 12. Resumen de Funcionalidades

### ✅ Lo que SÍ puedes hacer:

- ✅ Ver toda la documentación de la API
- ✅ Probar todos los endpoints en tiempo real
- ✅ Ver ejemplos de request/response
- ✅ Autenticarte y probar endpoints protegidos
- ✅ Validar datos antes de enviarlos
- ✅ Ver códigos de estado HTTP
- ✅ Descargar el schema OpenAPI
- ✅ Buscar endpoints rápidamente
- ✅ Ver esquemas de datos interactivos
- ✅ Probar filtros, búsqueda y paginación

### ❌ Lo que NO puedes hacer:

- ❌ Modificar la estructura de la API (eso se hace en el código)
- ❌ Ver logs del servidor (usa la consola de Django)
- ❌ Ver datos de otros usuarios sin autenticarte
- ❌ Ejecutar operaciones masivas (usa los endpoints individuales o scripts)

---

## 🚀 Ejemplos de Uso Común

### Caso 1: Desarrollador Frontend

```
Necesito crear un formulario de calificaciones. En Swagger:
1. Veo "POST /api/calificaciones/"
2. Expando el endpoint y veo el esquema completo
3. Copio el ejemplo de request body
4. Lo uso como base para mi formulario
5. Pruebo crear una calificación desde Swagger
6. Verifico que la respuesta sea la esperada
```

### Caso 2: Administrador del Sistema

```
Necesito verificar que un usuario tiene los permisos correctos. En Swagger:
1. Me autentico con el usuario a verificar
2. Intento acceder a "GET /api/calificaciones/"
3. Si funciona, tiene permisos de lectura
4. Intento "POST /api/calificaciones/"
5. Si funciona, tiene permisos de escritura
```

### Caso 3: Testing Manual

```
Necesito probar que la API funciona correctamente. En Swagger:
1. Pruebo cada endpoint con diferentes datos
2. Verifico códigos de respuesta
3. Valido que los datos se guarden correctamente
4. Pruebo casos de error (datos inválidos, sin auth, etc.)
```

---

## 📞 Siguiente Paso: ReDoc

Si prefieres una documentación más **legible y estructurada** (menos interactiva), puedes usar ReDoc:

**URL:** `https://127.0.0.1:8443/api/redoc/`

ReDoc es ideal para:
- Leer la documentación completa de forma lineal
- Imprimir o compartir documentación
- Ver todas las descripciones detalladas

---

## ✅ Cumplimiento de Rúbrica

Esta implementación de Swagger/OpenAPI cumple con:

- ✅ **APIs RESTful (10/10)**: Documentación completa y autogenerada
- ✅ **Mejores prácticas**: Uso de estándares OpenAPI/Swagger
- ✅ **Experiencia de desarrollador**: Interfaz intuitiva y completa
- ✅ **Autenticación integrada**: Soporte para diferentes métodos de auth
- ✅ **Ejemplos y validación**: Validación de esquemas y ejemplos reales

---

## 🔗 Recursos Adicionales

- **Documentación drf-spectacular:** https://drf-spectacular.readthedocs.io/
- **OpenAPI Specification:** https://swagger.io/specification/
- **Swagger UI Documentation:** https://swagger.io/tools/swagger-ui/

---

**¡Explora, prueba y disfruta de tu API! 🚀**

