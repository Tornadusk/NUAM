# Diferencias entre Auditor y Consultor en el Mantenedor

## 📋 Resumen General

Tanto **Auditor** como **Consultor** son roles de **solo lectura**, pero tienen **diferencias importantes** en el acceso a funcionalidades, especialmente en la pestaña de **Auditoría**.

---

## 🎯 Menú Visible (Pestañas)

### Pestañas Disponibles

| Pestaña | Consultor | Auditor | Nota |
|---------|-----------|---------|------|
| **Mantenedor** | ✅ Sí (solo lectura) | ✅ Sí (solo lectura) | Mismo acceso, solo lectura |
| **Cargas Masivas** | ❌ No | ❌ No | Solo Admin, Operador, Analista |
| **Usuarios** | ❌ No | ❌ No | Solo Administrador |
| **Auditoría** | ❌ **No** | ✅ **Sí (acceso completo)** | **DIFERENCIA PRINCIPAL** |
| **Reportes** | ✅ Sí | ✅ Sí | Mismo acceso |

**Ubicación del código**: `templates/calificaciones/partials/_tabs_nav.html` (líneas 1-46)

**Diferencia clave**: 
- **Consultor**: NO tiene acceso a la pestaña "Auditoría"
- **Auditor**: SÍ tiene acceso completo a la pestaña "Auditoría" (puede ver todas las auditorías del sistema)

---

## 🔐 Permisos de Edición

### Ambos Roles: Solo Lectura

| Acción | Consultor | Auditor |
|--------|-----------|---------|
| **Ver calificaciones** | ✅ Solo de sus corredoras | ✅ Solo de sus corredoras |
| **Crear calificaciones** | ❌ No (solo lectura) | ❌ No (solo lectura) |
| **Editar calificaciones** | ❌ No (solo lectura) | ❌ No (solo lectura) |
| **Eliminar calificaciones** | ❌ No (solo lectura) | ❌ No (solo lectura) |
| **Carga x Factor** | ❌ No (botón oculto) | ❌ No (botón oculto) |
| **Carga x Monto** | ❌ No (botón oculto) | ❌ No (botón oculto) |
| **Descargar CSV individual** | ✅ Sí | ✅ Sí |
| **Exportar Reportes** | ✅ Sí | ✅ Sí |

**Ubicación del código**: 
- Backend: `api/views.py` líneas 512-514 y 594-598
- Frontend: `templates/calificaciones/partials/_tabla.html` líneas 16-45

---

## 🔍 Diferencia Principal: Acceso a Auditoría

### Consultor

**Acceso a Auditoría**: ❌ NO tiene acceso

- No ve la pestaña "Auditoría" en el menú
- No puede ver el registro de cambios del sistema
- Solo puede ver calificaciones (en modo solo lectura)

**Código de validación**: `calificaciones/views.py` línea 62
```python
can_view_auditoria = bool(is_administrador or is_auditor)
# Consultor NO está incluido
```

### Auditor

**Acceso a Auditoría**: ✅ SÍ tiene acceso completo

- Ve la pestaña "Auditoría" en el menú
- Puede ver TODAS las auditorías del sistema (sin filtros por corredora)
- Puede ver el registro completo de cambios (INSERT, UPDATE, DELETE) en todas las entidades
- La pestaña "Auditoría" es la activa por defecto cuando ingresa al sistema

**Código de validación**: `calificaciones/views.py` línea 62
```python
can_view_auditoria = bool(is_administrador or is_auditor)
# Auditor SÍ está incluido
```

**Ubicación del código**: `templates/calificaciones/partials/_tabs_nav.html` líneas 30-37

---

## 📊 Comparación Detallada de Funcionalidades

### 1. Mantenedor (Pestaña Principal)

| Funcionalidad | Consultor | Auditor |
|---------------|-----------|---------|
| **Ver calificaciones** | ✅ Solo de sus corredoras | ✅ Solo de sus corredoras |
| **Filtrar por mercado/origen/período** | ✅ Sí | ✅ Sí |
| **Vista Resumen/Completa** | ✅ Sí | ✅ Sí |
| **Modo Solo Lectura** | ✅ Badge visible | ✅ Badge visible |
| **Descargar CSV individual** | ✅ Sí | ✅ Sí |
| **Crear/Editar/Eliminar** | ❌ No (botones ocultos) | ❌ No (botones ocultos) |
| **Carga x Factor/Monto** | ❌ No (botones ocultos) | ❌ No (botones ocultos) |

**Nota**: Ambos roles ven exactamente lo mismo en la pestaña Mantenedor: calificaciones en modo solo lectura.

### 2. Cargas Masivas

| Funcionalidad | Consultor | Auditor |
|---------------|-----------|---------|
| **Acceso a pestaña** | ❌ No | ❌ No |
| **Carga x Factor** | ❌ No disponible | ❌ No disponible |
| **Carga x Monto** | ❌ No disponible | ❌ No disponible |

**Nota**: Ninguno de los dos roles tiene acceso a cargas masivas (solo Admin, Operador, Analista).

### 3. Auditoría (DIFERENCIA PRINCIPAL)

| Funcionalidad | Consultor | Auditor |
|---------------|-----------|---------|
| **Acceso a pestaña** | ❌ **NO** | ✅ **SÍ** |
| **Ver auditoría completa** | ❌ No | ✅ Sí (TODAS las auditorías) |
| **Ver auditoría filtrada** | ❌ No | ✅ Sí (puede filtrar por entidad) |
| **Ver cambios en calificaciones** | ❌ No | ✅ Sí (de todas las corredoras) |
| **Ver cambios en cargas** | ❌ No | ✅ Sí |
| **Ver cambios en usuarios** | ❌ No | ✅ Sí |
| **Ver auditoría reciente** | ✅ Sí (en panel KPIs) | ✅ Sí (en panel KPIs + pestaña completa) |

**Ubicación del código**: 
- Template: `templates/calificaciones/partials/_auditoria.html`
- Backend: `api/views.py` líneas 2320-2352 (`AuditoriaViewSet.get_queryset`)

**Diferencia clave en el backend**:
```python
def get_queryset(self):
    # Auditor: Puede ver toda la auditoría (solo lectura, sin filtros)
    if is_auditor:
        # No aplicar filtros, puede ver toda la auditoría
        pass
    # Consultor: No tiene acceso (la pestaña no se muestra)
```

### 4. Reportes

| Funcionalidad | Consultor | Auditor |
|---------------|-----------|---------|
| **Exportar CSV** | ✅ Sí | ✅ Sí |
| **Exportar Excel** | ✅ Sí | ✅ Sí |
| **Exportar PDF** | ✅ Sí | ✅ Sí |

**Nota**: Ambos roles tienen acceso completo a los reportes. No hay diferencia funcional.

---

## 🎨 Diferencias Visuales en la Interfaz

### 1. Badge "Modo Solo Lectura"

**Ambos roles** ven el badge "Modo Solo Lectura" en lugar de los botones de acción:

```
[Mantenedor] [Cargas Masivas] [Reportes]

[Modo Solo Lectura] | [Descargar CSV]
```

**Ubicación**: `templates/calificaciones/partials/_tabla.html` líneas 16-19

### 2. Pestaña de Auditoría

**Consultor**:
```
[Mantenedor] [Reportes]
            ↑ No ve "Auditoría"
```

**Auditor**:
```
[Mantenedor] [Auditoría] [Reportes]
                    ↑ Ve esta pestaña
```

**Ubicación**: `templates/calificaciones/partials/_tabs_nav.html` líneas 30-37

### 3. Pestaña Activa por Defecto

**Consultor**: La pestaña "Mantenedor" está activa por defecto
**Auditor**: La pestaña "Auditoría" está activa por defecto (si no es admin)

**Código**: `calificaciones/views.py` línea 73
```python
default_active_tab = 'auditoria' if (is_auditor and not is_administrador) else 'mantenedor'
```

---

## 📝 Ejemplos Prácticos

### Escenario 1: Ver Calificaciones

**Situación**: Un Consultor y un Auditor tienen acceso a la corredora "Banco de Chile".

1. **Consultor** ingresa al sistema:
   - ✅ Ve calificaciones de "Banco de Chile" (solo lectura)
   - ❌ No ve pestaña "Auditoría"
   - ✅ Ve pestaña "Reportes" (puede exportar)

2. **Auditor** ingresa al sistema:
   - ✅ Ve calificaciones de "Banco de Chile" (solo lectura)
   - ✅ Ve pestaña "Auditoría" (acceso completo a TODAS las auditorías)
   - ✅ Ve pestaña "Reportes" (puede exportar)
   - 🔄 La pestaña "Auditoría" está activa por defecto

### Escenario 2: Revisar Cambios en el Sistema

**Situación**: Se crearon 10 calificaciones y se modificaron 5.

1. **Consultor**:
   - ❌ NO puede ver la pestaña "Auditoría"
   - ✅ Puede ver las calificaciones finales (pero no quién las creó/modificó)
   - ✅ Ve "Auditoría Reciente" en el panel KPIs (últimos 5 registros)

2. **Auditor**:
   - ✅ Puede ver la pestaña "Auditoría"
   - ✅ Puede ver TODOS los registros de auditoría (los 10 INSERT y 5 UPDATE)
   - ✅ Puede ver quién creó/modificó cada calificación
   - ✅ Puede ver cambios en otras entidades (CARGA, USUARIO, etc.)
   - ✅ Puede filtrar por entidad, fecha, usuario, etc.

---

## 🔄 Flujo de Trabajo Típico

### Consultor

1. Login → 2. Mantenedor (solo lectura) → 3. Filtrar calificaciones → 4. Exportar Reportes → 5. Análisis externo

**Propósito**: Consultar y analizar datos sin poder modificarlos.

### Auditor

1. Login → 2. **Auditoría** (pestaña activa por defecto) → 3. Revisar cambios en el sistema → 4. Ver Mantenedor (solo lectura) → 5. Exportar Reportes

**Propósito**: Revisar trazabilidad y cumplimiento de cambios en el sistema.

---

## 📊 Tabla Comparativa Resumen

| Característica | Consultor | Auditor |
|----------------|-----------|---------|
| **Ver calificaciones** | ✅ Solo de sus corredoras | ✅ Solo de sus corredoras |
| **Crear calificaciones** | ❌ No (solo lectura) | ❌ No (solo lectura) |
| **Editar calificaciones** | ❌ No (solo lectura) | ❌ No (solo lectura) |
| **Eliminar calificaciones** | ❌ No (solo lectura) | ❌ No (solo lectura) |
| **Cargas masivas** | ❌ No | ❌ No |
| **Reportes** | ✅ Sí | ✅ Sí |
| **Auditoría (pestaña completa)** | ❌ **NO** | ✅ **SÍ (TODAS las auditorías)** |
| **Auditoría Reciente (panel KPIs)** | ✅ Sí (últimos 5) | ✅ Sí (últimos 5) |
| **Pestaña activa por defecto** | Mantenedor | **Auditoría** |

---

## 🔍 Código de Validación Detallado

### Validación de Permisos para Crear/Editar/Eliminar

**Ubicación**: `api/views.py` líneas 512-514 y 594-598

```python
def _can_edit_calificacion(self, calificacion, usuario):
    # Consultor y Auditor: Solo lectura (NO pueden editar)
    if 'consultor' in user_roles or 'auditor' in user_roles:
        return False

def perform_create(self, serializer):
    # Consultor y Auditor: Solo lectura (NO pueden crear)
    if 'consultor' in user_roles or 'auditor' in user_roles:
        raise permissions.PermissionDenied(
            "No tienes permiso para crear calificaciones. Tu rol es de solo lectura."
        )
```

### Validación de Acceso a Auditoría

**Ubicación**: `calificaciones/views.py` línea 62

```python
can_view_auditoria = bool(is_administrador or is_auditor)
# Consultor NO está incluido, por lo que can_view_auditoria = False
```

### Filtrado de Auditoría para Auditor

**Ubicación**: `api/views.py` líneas 2329-2332

```python
def get_queryset(self):
    # Auditor: Puede ver toda la auditoría (solo lectura, sin filtros)
    if is_auditor:
        # No aplicar filtros, puede ver toda la auditoría
        pass  # Retorna TODAS las auditorías
    # Otros usuarios (excepto admin): Solo auditoría de sus corredoras
```

---

## 💡 Casos de Uso

### ¿Cuándo usar Consultor?

- Usuarios externos que necesitan consultar datos sin modificarlos
- Analistas que solo necesitan visualizar y exportar información
- Stakeholders que revisan calificaciones para reportes
- Consultores que necesitan datos para análisis externos
- Usuarios que NO necesitan ver el historial de cambios

### ¿Cuándo usar Auditor?

- Usuarios responsables de cumplimiento y trazabilidad
- Supervisores que revisan quién hizo qué cambios en el sistema
- Auditores internos/externos que necesitan ver el historial completo
- Personal de compliance que revisa cambios en calificaciones
- Usuarios que necesitan ver el registro completo de auditoría (no solo calificaciones)

---

## 🎯 Diferencias Clave Resumidas

### Consultor

- ✅ Puede ver calificaciones (solo lectura)
- ✅ Puede exportar reportes
- ❌ **NO puede ver la pestaña "Auditoría"**
- ✅ Ve "Auditoría Reciente" en el panel KPIs (últimos 5)

### Auditor

- ✅ Puede ver calificaciones (solo lectura)
- ✅ Puede exportar reportes
- ✅ **Puede ver la pestaña "Auditoría" completa (TODAS las auditorías)**
- ✅ Ve "Auditoría Reciente" en el panel KPIs (últimos 5)
- 🔄 La pestaña "Auditoría" es la activa por defecto

---

## 📁 Archivos Relevantes

### Templates

- `templates/calificaciones/partials/_tabs_nav.html`: Define qué pestañas se muestran
- `templates/calificaciones/partials/_tabla.html`: Define el badge "Modo Solo Lectura"
- `templates/calificaciones/partials/_auditoria.html`: Pestaña de auditoría (solo Auditor)
- `templates/calificaciones/partials/_reportes.html`: Pestaña de reportes

### Backend

- `calificaciones/views.py`: Define variables de contexto (`can_view_auditoria`, `is_read_only`, `default_active_tab`)
- `api/views.py`: 
  - `CalificacionViewSet._can_edit_calificacion()`: Valida permisos de edición
  - `CalificacionViewSet.perform_create()`: Bloquea creación para Consultor y Auditor
  - `AuditoriaViewSet.get_queryset()`: Filtra auditoría (Auditor ve todo)

---

## ✅ Checklist de Diferencias

- [x] **Menú visual**: Consultor NO ve "Auditoría", Auditor SÍ la ve
- [x] **Pestaña activa por defecto**: Consultor → Mantenedor, Auditor → Auditoría
- [x] **Acceso a Auditoría completa**: Consultor NO, Auditor SÍ (sin filtros)
- [x] **Ver calificaciones**: Ambos pueden ver (solo lectura)
- [x] **Crear/Editar/Eliminar**: Ninguno puede (solo lectura)
- [x] **Cargas masivas**: Ninguno tiene acceso
- [x] **Reportes**: Ambos tienen acceso completo
- [x] **Auditoría Reciente (KPIs)**: Ambos ven los últimos 5 registros

---

## 🔐 Nivel de Acceso a Datos

### Consultor

**Puede ver**:
- Calificaciones de sus corredoras asignadas (solo lectura)
- Reportes de sus corredoras (exportación)
- Auditoría Reciente (últimos 5 registros en panel KPIs)

**NO puede ver**:
- Pestaña completa de Auditoría
- Historial completo de cambios
- Auditoría de otras corredoras (excepto en panel KPIs limitado)

### Auditor

**Puede ver**:
- Calificaciones de sus corredoras asignadas (solo lectura)
- Reportes de sus corredoras (exportación)
- **TODA la Auditoría del sistema** (sin filtros por corredora):
  - Auditoría de TODAS las calificaciones (todas las corredoras)
  - Auditoría de cargas masivas
  - Auditoría de cambios en usuarios
  - Auditoría de cambios en instrumentos
  - Historial completo con filtros por entidad, fecha, usuario

**NO puede**:
- Modificar ninguna calificación (solo lectura)
- Crear o eliminar datos

---

## 💡 Resumen de Propósito

### Consultor

**Propósito**: Usuario que consulta y analiza datos para reportes externos, sin necesidad de ver el historial de cambios.

**Ideal para**:
- Análisis de datos para reportes externos
- Consultas puntuales sobre calificaciones
- Usuarios que solo necesitan visualizar y exportar información

### Auditor

**Propósito**: Usuario que revisa cumplimiento y trazabilidad, necesita ver el historial completo de cambios en el sistema.

**Ideal para**:
- Revisión de cumplimiento normativo
- Auditorías internas/externas
- Trazabilidad de quién hizo qué cambios
- Cumplimiento de políticas de seguridad

---

*Última actualización: 2025-01-14*

