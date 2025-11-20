# Diferencias entre Analista y Operador en el Mantenedor

## 📋 Resumen General

Aunque **Analista** y **Operador** tienen acceso a las mismas pestañas del menú (Mantenedor, Cargas Masivas, Reportes), existen **diferencias importantes** en los permisos de edición y acceso a funcionalidades. La diferencia principal está en **qué calificaciones pueden editar**.

---

## 🎯 Menú Visible (Pestañas)

### Pestañas Disponibles para Ambos Roles

| Pestaña | Operador | Analista | Nota |
|---------|----------|----------|------|
| **Mantenedor** | ✅ Sí | ✅ Sí | Mismo acceso |
| **Cargas Masivas** | ✅ Sí | ✅ Sí | Mismo acceso |
| **Usuarios** | ❌ No | ❌ No | Solo Administrador |
| **Auditoría** | ❌ No | ❌ No | Solo Administrador y Auditor |
| **Reportes** | ✅ Sí | ✅ Sí (con badge "Avanzado") | Analista ve badge "Avanzado" |

**Ubicación del código**: `templates/calificaciones/partials/_tabs_nav.html` (líneas 1-46)

**Nota importante**: Ambos roles ven exactamente las mismas pestañas, con la única diferencia visual de que **Analista** ve un badge azul "**Avanzado**" en la pestaña de Reportes.

---

## 🔐 Permisos de Edición (Diferencia Principal)

### Operador

**Puede editar**: Solo las calificaciones que él mismo creó

**Código de validación**: `api/views.py` líneas 520-522
```python
# Si es operador, solo puede editar las que él mismo creó
if 'operador' in user_roles:
    return calificacion.creado_por_id == usuario_obj.id_usuario
```

**Ejemplo práctico**:
- Operador crea Calificación ID 1 → ✅ Puede editarla
- Otro Operador crea Calificación ID 2 → ❌ NO puede editarla (aunque pertenezca a la misma corredora)
- Admin crea Calificación ID 3 en la misma corredora → ❌ NO puede editarla

### Analista

**Puede editar**: TODAS las calificaciones de sus corredoras asignadas (sin importar quién las creó)

**Código de validación**: `api/views.py` líneas 524-525
```python
# Analista, supervisor, admin de corredora, u otros roles pueden editar todas de su corredora
return True  # Si pertenece a una corredora del usuario
```

**Ejemplo práctico**:
- Operador crea Calificación ID 1 → ✅ Analista puede editarla
- Otro Analista crea Calificación ID 2 → ✅ Analista puede editarla
- Admin crea Calificación ID 3 en la misma corredora → ✅ Analista puede editarla
- Cualquier calificación de sus corredoras → ✅ Puede editarla

---

## 📊 Comparación Detallada de Funcionalidades

### 1. Mantenedor (Pestaña Principal)

| Funcionalidad | Operador | Analista |
|---------------|----------|----------|
| **Ver calificaciones** | ✅ Solo de sus corredoras | ✅ Solo de sus corredoras |
| **Crear calificaciones** | ✅ Sí | ✅ Sí |
| **Editar calificaciones** | ✅ Solo las que él creó | ✅ TODAS de sus corredoras |
| **Eliminar calificaciones** | ✅ Solo las que él creó | ✅ TODAS de sus corredoras |
| **Copiar calificaciones** | ✅ Sí | ✅ Sí |
| **Filtrar por mercado/origen/período** | ✅ Sí | ✅ Sí |
| **Vista Resumen/Completa** | ✅ Sí | ✅ Sí |
| **Descargar CSV individual** | ✅ Sí | ✅ Sí |

**Ubicación del código**: 
- Frontend: `templates/static/js/mantenedor/calificaciones.js` líneas 216-256
- Backend: `api/views.py` líneas 489-528 (`_can_edit_calificacion`)

### 2. Cargas Masivas

| Funcionalidad | Operador | Analista |
|---------------|----------|----------|
| **Carga x Factor** | ✅ Sí | ✅ Sí |
| **Carga x Monto** | ✅ Sí | ✅ Sí |
| **Calcular Factores** | ✅ Sí | ✅ Sí |
| **Ver preview antes de grabar** | ✅ Sí | ✅ Sí |

**Ubicación del código**: `templates/calificaciones/partials/_cargas_masivas.html`

**Nota**: Ambos roles tienen acceso completo a las cargas masivas. No hay diferencia funcional en esta pestaña.

### 3. Reportes

| Funcionalidad | Operador | Analista |
|---------------|----------|----------|
| **Exportar CSV** | ✅ Sí | ✅ Sí |
| **Exportar Excel** | ✅ Sí | ✅ Sí |
| **Exportar PDF** | ✅ Sí | ✅ Sí |
| **Badge "Avanzado"** | ❌ No | ✅ Sí (solo visual) |

**Ubicación del código**: 
- Badge: `templates/calificaciones/partials/_tabs_nav.html` línea 43
- Funcionalidad: `templates/calificaciones/partials/_reportes.html`

**Nota importante**: Actualmente, la funcionalidad de exportación es **idéntica** para ambos roles. El badge "Avanzado" es solo una **indicación visual** de que el Analista tiene un rol de mayor jerarquía, pero no desbloquea funcionalidades adicionales en este momento.

---

## 🔍 Diferencias en el Backend (API)

### Validación de Permisos

**Ubicación**: `api/views.py` - Método `_can_edit_calificacion` (líneas 489-528)

```python
def _can_edit_calificacion(self, calificacion, usuario):
    # ... validaciones de admin ...
    
    # Si es operador, solo puede editar las que él mismo creó
    if 'operador' in user_roles:
        return calificacion.creado_por_id == usuario_obj.id_usuario
    
    # Analista, supervisor, admin de corredora, u otros roles pueden editar todas de su corredora
    return True  # Si pertenece a una corredora del usuario
```

### Filtrado de Calificaciones

**Ambos roles** ven solo las calificaciones de sus corredoras asignadas:

```python
# FILTRO DE SEGURIDAD: Solo mostrar calificaciones de las corredoras del usuario
if not self._is_admin_or_superuser(self.request.user):
    user_corredoras = self._get_user_corredoras(self.request.user)
    if user_corredoras:
        queryset = queryset.filter(id_corredora_id__in=user_corredoras)
```

**Ubicación**: `api/views.py` líneas 545-554

---

## 🎨 Diferencias Visuales en la Interfaz

### 1. Pestaña de Reportes

**Operador**: Ve "Reportes" sin badge
```
[📄 Reportes]
```

**Analista**: Ve "Reportes" con badge "Avanzado" azul
```
[📄 Reportes] [Avanzado]
```

**Ubicación**: `templates/calificaciones/partials/_tabs_nav.html` línea 43
```html
<i class="fas fa-file-alt me-1"></i> Reportes
{% if is_analista %}<span class="badge bg-info ms-1">Avanzado</span>{% endif %}
```

### 2. Botones en la Tabla

**Ambos roles** ven los mismos botones:
- ✅ Botón "Ingresar" (verde)
- ✅ Botón "Modificar" (naranja) - **Comportamiento diferente**
- ✅ Botón "Eliminar" (rojo) - **Comportamiento diferente**
- ✅ Botón "Copiar" (azul claro)
- ✅ Botones "Carga x Factor" y "Carga x Monto" (gris)
- ✅ Botón "Descargar CSV" (azul)

**La diferencia está en el comportamiento**:
- **Operador**: Al hacer clic en "Modificar" o "Eliminar", el sistema valida que la calificación sea suya.
- **Analista**: Puede modificar o eliminar cualquier calificación de sus corredoras (sin validar quién la creó).

---

## 📝 Ejemplos Prácticos

### Escenario 1: Creación de Calificaciones

**Situación**: Un Operador y un Analista tienen acceso a la misma corredora (Banco de Chile).

1. **Operador** crea Calificación ID 1:
   - ✅ Operador puede editarla
   - ✅ Analista puede editarla

2. **Analista** crea Calificación ID 2:
   - ❌ Operador NO puede editarla (no la creó él)
   - ✅ Analista puede editarla

3. **Admin** crea Calificación ID 3:
   - ❌ Operador NO puede editarla (no la creó él)
   - ✅ Analista puede editarla (pertenece a su corredora)

### Escenario 2: Carga Masiva

**Situación**: Ambos suben un archivo CSV con 100 calificaciones.

1. **Operador** carga el archivo:
   - Las 100 calificaciones se crean con `creado_por = operador`
   - ✅ Operador puede editar las 100
   - ✅ Analista puede editar las 100 (pertenecen a su corredora)

2. **Analista** carga el archivo:
   - Las 100 calificaciones se crean con `creado_por = analista`
   - ❌ Operador NO puede editar ninguna (no las creó él)
   - ✅ Analista puede editar las 100

---

## 🔄 Flujo de Trabajo Típico

### Operador

1. Login → 2. Mantenedor → 3. Crear/Editar calificaciones propias → 4. Cargas Masivas → 5. Reportes

**Limitación**: Solo puede modificar lo que él mismo crea.

### Analista

1. Login → 2. Mantenedor → 3. Revisar y ajustar TODAS las calificaciones de su corredora → 4. Cargas Masivas → 5. Reportes Avanzados

**Ventaja**: Puede corregir o ajustar calificaciones creadas por Operadores u otros Analistas.

---

## ⚠️ Restricciones Comunes

Ambos roles comparten las siguientes restricciones:

1. **Solo ven calificaciones de sus corredoras asignadas**
   - No pueden ver calificaciones de otras corredoras
   - Si un usuario no tiene corredoras asignadas, no ve ninguna calificación

2. **No pueden acceder a la pestaña "Usuarios"**
   - Solo Administrador puede gestionar usuarios

3. **No pueden acceder a la pestaña "Auditoría"**
   - Solo Administrador y Auditor tienen acceso

4. **No pueden eliminar calificaciones de otros usuarios fuera de sus corredoras**
   - El filtro de corredora se aplica primero, antes de la validación de permisos

---

## 📊 Tabla Comparativa Resumen

| Característica | Operador | Analista |
|----------------|----------|----------|
| **Ver calificaciones** | Solo de sus corredoras | Solo de sus corredoras |
| **Crear calificaciones** | ✅ Sí | ✅ Sí |
| **Editar calificaciones** | Solo las que él creó | ✅ TODAS de sus corredoras |
| **Eliminar calificaciones** | Solo las que él creó | ✅ TODAS de sus corredoras |
| **Cargas masivas** | ✅ Sí | ✅ Sí |
| **Reportes** | ✅ Sí | ✅ Sí (con badge "Avanzado") |
| **Auditoría** | ❌ No | ❌ No |
| **Gestión de usuarios** | ❌ No | ❌ No |

---

## 🎯 Casos de Uso

### ¿Cuándo usar Operador?

- Usuarios que solo ingresan sus propios datos
- Flujo de trabajo donde cada usuario es responsable de sus propias calificaciones
- Evitar que usuarios modifiquen datos creados por otros
- Mayor control y trazabilidad (cada calificación tiene un creador claro)

### ¿Cuándo usar Analista?

- Usuarios que revisan y ajustan calificaciones creadas por múltiples Operadores
- Flujo de trabajo colaborativo donde un supervisor revisa el trabajo de su equipo
- Necesidad de corregir errores en calificaciones creadas por otros
- Análisis y ajuste de datos de toda la corredora

---

## 🔍 Código de Validación Detallado

### Validación en el Backend (`api/views.py`)

```python
def _can_edit_calificacion(self, calificacion, usuario):
    """
    Verificar si el usuario puede editar una calificación específica
    Reglas:
    - Admin/Superuser: Puede editar todas
    - Operador: Solo puede editar las que él mismo creó  ← DIFERENCIA CLAVE
    - Analista: Puede editar todas de su corredora        ← DIFERENCIA CLAVE
    - Consultor: NO puede editar (solo lectura)
    - Auditor: NO puede editar (solo lectura)
    """
    # ... código de validación ...
    
    # Si es operador, solo puede editar las que él mismo creó
    if 'operador' in user_roles:
        return calificacion.creado_por_id == usuario_obj.id_usuario
    
    # Analista puede editar todas de su corredora
    return True
```

### Validación en el Frontend (`calificaciones.js`)

El frontend no valida directamente, pero muestra/oculta botones según roles. La validación real se hace en el backend cuando se intenta actualizar o eliminar.

---

## 📁 Archivos Relevantes

### Templates

- `templates/calificaciones/partials/_tabs_nav.html`: Define qué pestañas se muestran
- `templates/calificaciones/partials/_tabla.html`: Define qué botones se muestran
- `templates/calificaciones/partials/_cargas_masivas.html`: Pestaña de cargas masivas
- `templates/calificaciones/partials/_reportes.html`: Pestaña de reportes

### Backend

- `calificaciones/views.py`: Define variables de contexto (is_operador, is_analista)
- `api/views.py`: Contiene la lógica de validación de permisos (`_can_edit_calificacion`)

### Frontend JavaScript

- `templates/static/js/mantenedor/calificaciones.js`: Renderiza botones según roles
- `templates/static/js/mantenedor/cargas.js`: Maneja cargas masivas

---

## ✅ Checklist de Diferencias

- [x] **Menú visual**: Ambos ven las mismas pestañas
- [x] **Badge "Avanzado"**: Solo Analista lo ve en Reportes
- [x] **Edición de calificaciones**: Operador solo las propias, Analista todas de su corredora
- [x] **Eliminación de calificaciones**: Operador solo las propias, Analista todas de su corredora
- [x] **Creación de calificaciones**: Ambos pueden crear
- [x] **Cargas masivas**: Ambos tienen acceso completo
- [x] **Reportes**: Ambos tienen acceso completo (Analista tiene badge visual)
- [x] **Auditoría**: Ninguno tiene acceso
- [x] **Gestión de usuarios**: Ninguno tiene acceso

---

## 💡 Recomendaciones

1. **Para Operadores**: Ideal para entrada de datos inicial donde cada usuario es responsable de sus propias calificaciones.

2. **Para Analistas**: Ideal para revisión, corrección y ajuste de calificaciones creadas por múltiples Operadores en una corredora.

3. **Flujo recomendado**:
   - Operadores crean calificaciones iniciales
   - Analistas revisan y ajustan todas las calificaciones de la corredora
   - Administradores supervisan todo el proceso

---

*Última actualización: 2025-01-14*

