# Estructura de Base de Datos y Optimización - Criterios de Evaluación

## 📊 Criterio 1: Estructura adecuada de la base de datos

**Destacado:** La estructura de la base de datos es óptima, incluye relaciones correctas, índices y modelos eficientes para cada tipo de datos.

### ✅ **Ubicaciones en el proyecto donde se cumple:**

#### **1. Modelos Django (`*/models.py`)**

**Relaciones correctas implementadas:**

##### **Foreign Keys con `on_delete` apropiado:**
- `RESTRICT`: Previene eliminación si hay dependencias (integridad referencial)
  - **`calificaciones/models.py`** (líneas 42-95):
    - `Calificacion.id_corredora` → `RESTRICT` (no se puede eliminar corredora con calificaciones)
    - `Calificacion.id_instrumento` → `RESTRICT`
    - `Calificacion.id_fuente` → `RESTRICT`
    - `Calificacion.id_moneda` → `RESTRICT`
    - `Calificacion.creado_por` / `actualizado_por` → `RESTRICT`
  
  - **`corredoras/models.py`** (línea 16):
    - `Corredora.id_pais` → `RESTRICT` (no se puede eliminar país con corredoras)
  
  - **`usuarios/models.py`** (línea 38):
    - `Usuario.id_persona` → `RESTRICT` (no se puede eliminar persona con usuario)

- `CASCADE`: Elimina registros relacionados automáticamente
  - **`corredoras/models.py`** (línea 35):
    - `CorredoraIdentificador.id_corredora` → `CASCADE` (se eliminan identificadores al eliminar corredora)
  
  - **`usuarios/models.py`** (línea 96):
    - `UsuarioRol.id_usuario` → `CASCADE` (se eliminan roles al eliminar usuario)

- `SET_NULL`: Mantiene el registro pero deja FK en null
  - **`calificaciones/models.py`** (líneas 57-63):
    - `Calificacion.id_evento` → `SET_NULL` (opcional, puede ser null)
  
  - **`auditoria/models.py`** (líneas 7-13):
    - `Auditoria.actor_id` → `SET_NULL` (mantiene auditoría aunque se elimine usuario)
  
  - **`cargas/models.py`** (líneas 72-78):
    - `CargaDetalle.id_calificacion` → `SET_NULL` (mantiene detalle aunque se elimine calificación)

##### **OneToOneField para relaciones 1:1:**
- **`usuarios/models.py`** (líneas 120-126):
  - `Colaborador.id_usuario` → `OneToOneField` con `unique=True` (1 usuario = 1 colaborador máximo)

##### **Constraints de integridad:**
- **`unique_together`** para evitar duplicados:
  - **`calificaciones/models.py`** (línea 104):
    - `Calificacion`: `(id_corredora, id_instrumento, ejercicio, secuencia_evento)` → Evita calificaciones duplicadas
  
  - **`calificaciones/models.py`** (línea 134):
    - `CalificacionMontoDetalle`: `(id_calificacion, id_factor)` → Un factor por calificación
  
  - **`calificaciones/models.py`** (línea 163):
    - `CalificacionFactorDetalle`: `(id_calificacion, id_factor)` → Un factor por calificación
  
  - **`usuarios/models.py`** (línea 105):
    - `UsuarioRol`: `(id_usuario, id_rol)` → Un usuario no puede tener el mismo rol dos veces
  
  - **`corredoras/models.py`** (línea 47):
    - `CorredoraIdentificador`: `(tipo, numero, id_pais)` → Evita identificadores duplicados
  
  - **`corredoras/models.py`** (línea 77):
    - `UsuarioCorredora`: `(id_usuario, id_corredora)` → Evita asignaciones duplicadas
  
  - **`cargas/models.py`** (líneas 87-90):
    - `CargaDetalle`: `(id_carga, linea)` y `(id_carga, hash_linea)` → Evita líneas duplicadas

#### **2. Documentación del esquema (`MODELO.DDL`)**

**Archivo:** `MODELO.DDL` (líneas 1-390)

- Define **8 ENUMS** para valores controlados (EstadoCorredora, EstadoUsuario, EstadoCalificacion, etc.)
- Define **21 tablas** con relaciones explícitas
- Especifica **índices** en secciones dedicadas
- Documenta **constraints** UNIQUE y FOREIGN KEY
- Incluye comentarios explicativos para cada tabla

**Ejemplos de estructura óptima:**
- **Tabla `calificacion`** (líneas 206-235):
  - 4 Foreign Keys (id_corredora, id_instrumento, id_fuente, id_evento)
  - Constraint UNIQUE compuesto (4 campos)
  - Índices en todos los FKs
  - Campo `estado` con ENUM (EstadoCalificacion)

- **Tabla `auditoria`** (líneas 336-354):
  - Foreign Key con SET_NULL (actor_id)
  - Índice compuesto `(entidad, entidad_id)` para búsquedas eficientes
  - Índice en `fecha` para consultas temporales
  - Campos JSON para valores antes/después

#### **3. Script SQL de creación (`cretetable_oracle`)**

**Archivo:** `cretetable_oracle` (453 líneas)

- **CREATE TABLE** con tipos de datos apropiados (VARCHAR2, NUMBER, DATE, TIMESTAMP, BOOLEAN)
- **CONSTRAINTS** explícitos (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)
- **ÍNDICES** creados explícitamente con nombres descriptivos:
  - `ix_usuario_persona` (línea 138)
  - `ix_aud_entidad` (línea 409)
  - `ix_aud_fecha` (línea 410)
  - `ix_calif_*` (múltiples índices para calificaciones)
- **CHECK constraints** para validar ENUMs (líneas 135, 156, etc.)

---

## 🚀 Criterio 2: Optimización y normalización

**Destacado:** Las bases de datos cumplen con principios avanzados de normalización y optimización, asegurando un rendimiento excelente.

### ✅ **Ubicaciones en el proyecto donde se cumple:**

#### **1. Normalización (Forma Normal 3NF - Tercera Forma Normal)**

##### **Separación de entidades:**
- **Persona vs Usuario** (`usuarios/models.py`):
  - `Persona` (líneas 6-33): Datos personales (nombre, apellidos, fecha nacimiento)
  - `Usuario` (líneas 36-77): Credenciales y estado (username, password, estado)
  - **Beneficio:** Permite reutilizar Persona para otros propósitos (clientes, contactos, etc.)

- **Calificación vs Detalles** (`calificaciones/models.py`):
  - `Calificacion` (líneas 40-112): Entidad principal
  - `CalificacionMontoDetalle` (líneas 113-141): Montos desnormalizados
  - `CalificacionFactorDetalle` (líneas 144-172): Factores desnormalizados
  - **Beneficio:** Permite almacenar 30 factores/montos por calificación sin crear 30 columnas

##### **Tablas intermedias para relaciones M:N:**
- **`UsuarioRol`** (`usuarios/models.py`, líneas 95-115):
  - Relación M:N entre Usuario y Rol
  - Evita redundancia (un usuario puede tener múltiples roles)
  
- **`UsuarioCorredora`** (`corredoras/models.py`, líneas 57-84):
  - Relación M:N entre Usuario y Corredora
  - Campo `es_principal` para marcar corredora principal

- **`MonedaPais`** (`core/models.py`):
  - Relación M:N entre Moneda y País
  - Permite múltiples monedas por país con fechas de vigencia

##### **Eliminación de redundancia:**
- **`CorredoraIdentificador`** separado de `Corredora`:
  - Permite múltiples identificadores por corredora (RUT, RUC, NIT)
  - Evita columnas duplicadas (rut, ruc, nit) en tabla principal

- **`Colaborador`** separado de `Usuario`:
  - Relación 1:1 opcional (solo usuarios internos son colaboradores)
  - Evita campo email en Usuario que no siempre se usa

#### **2. Optimización de rendimiento**

##### **Índices en campos de búsqueda frecuente:**

**Índices simples:**
- **`corredoras/models.py`** (línea 25):
  - `Corredora.nombre` → Índice para búsquedas por nombre
  
- **`auditoria/models.py`** (líneas 45-46):
  - `Auditoria.fecha` → Índice para consultas temporales
  - `Auditoria.(entidad, entidad_id)` → Índice compuesto para búsquedas por entidad

- **`cargas/models.py`** (línea 53):
  - `Carga.estado` → Índice para filtrar cargas por estado

- **`usuarios/models.py`** (línea 23):
  - `Persona.(apellido_paterno, apellido_materno)` → Índice compuesto para búsquedas por apellidos

**Índices automáticos por Foreign Keys:**
- Oracle crea automáticamente índices en todas las Foreign Keys
- Mejora rendimiento de JOINs y consultas con WHERE en FKs

**Índices únicos:**
- `unique_together` crea índices únicos automáticamente
- Ejemplo: `Calificacion.(id_corredora, id_instrumento, ejercicio, secuencia_evento)` → Índice único compuesto

##### **Optimización de queries con `select_related` y `prefetch_related`:**

**Archivo:** `api/views.py`

- **Línea 433** (`CalificacionViewSet.list()`):
  ```python
  queryset = Calificacion.objects.all().prefetch_related(
      'calificacionfactordetalle_set', 
      'calificacionmontodetalle_set'
  )
  ```
  **Beneficio:** Reduce queries N+1 al cargar detalles de factores/montos

- **Líneas 532-536** (`CalificacionViewSet.retrieve()`):
  ```python
  queryset = queryset.prefetch_related(
      'calificacionfactordetalle_set__id_factor',
      'calificacionmontodetalle_set__id_factor'
  ).select_related(
      'id_corredora', 'id_instrumento', 'id_fuente', 'id_evento'
  )
  ```
  **Beneficio:** 
  - `prefetch_related` carga detalles de factores/montos en una query separada
  - `select_related` hace JOINs para cargar relaciones 1:1 y N:1 en una sola query

- **`usuarios/context_processors.py`** (línea 27):
  ```python
  usuario_obj = Usuario.objects.select_related('id_persona', 'colaborador').get(...)
  ```
  **Beneficio:** Carga Persona y Colaborador en una sola query en lugar de 3 queries separadas

##### **Tipos de datos apropiados:**
- **`BigAutoField`** para PKs de tablas grandes (`calificacion`, `auditoria`, `carga`)
- **`DecimalField(max_digits=20, decimal_places=8)`** para valores monetarios precisos
- **`CharField`** con `max_length` apropiado para strings cortos
- **`TextField`** para descripciones largas (sin límite de longitud)
- **`BooleanField`** para flags simples
- **`DateField`** / `DateTimeField`** para fechas con timezone

##### **Campos calculados y propiedades:**
- **`Persona.nombre_completo`** (`usuarios/models.py`, líneas 29-33):
  - Propiedad `@property` que concatena nombres y apellidos
  - No se almacena en BD (evita redundancia)

##### **Campos de auditoría automáticos:**
- **`creado_en`** / **`actualizado_en`** en todas las tablas:
  - `auto_now_add=True` para `creado_en`
  - `auto_now=True` para `actualizado_en`
  - Trazabilidad automática sin lógica adicional

#### **3. Estrategias de optimización implementadas**

##### **Índices compuestos para consultas complejas:**
- `Calificacion`: `(id_corredora, id_instrumento, ejercicio, secuencia_evento)` → Búsquedas exactas eficientes
- `Auditoria`: `(entidad, entidad_id)` → Búsquedas por entidad específica
- `CargaDetalle`: `(id_carga, linea)` y `(id_carga, hash_linea)` → Validación de duplicados rápida

##### **Campos indexados para filtros frecuentes:**
- `Auditoria.fecha` → Consultas por rango de fechas
- `Carga.estado` → Filtrado de cargas por estado
- `Corredora.nombre` → Búsquedas por nombre

##### **Reducción de queries con prefetch:**
- `CalificacionViewSet` usa `prefetch_related` para cargar 30 factores/montos en 2 queries en lugar de 30+
- `Usuario.objects.select_related('id_persona', 'colaborador')` en context processor

---

## 📁 Archivos del proyecto donde se demuestra:

### **1. Estructura de Base de Datos:**

| Archivo | Líneas | Contenido |
|---------|--------|-----------|
| `MODELO.DDL` | 1-390 | Esquema completo con relaciones, índices y constraints |
| `cretetable_oracle` | 1-453 | Script SQL con creación de tablas, índices y constraints |
| `usuarios/models.py` | Todo | Modelos Persona, Usuario, Rol, UsuarioRol, Colaborador |
| `calificaciones/models.py` | Todo | Modelos Calificacion, FactorDef, CalificacionMontoDetalle, CalificacionFactorDetalle |
| `corredoras/models.py` | Todo | Modelos Corredora, CorredoraIdentificador, UsuarioCorredora |
| `cargas/models.py` | Todo | Modelos Carga, CargaDetalle |
| `auditoria/models.py` | Todo | Modelo Auditoria |
| `core/models.py` | Todo | Modelos Pais, Moneda, Mercado, Fuente, MonedaPais |

### **2. Optimización y Normalización:**

| Archivo | Líneas | Contenido |
|---------|--------|-----------|
| `api/views.py` | 433, 532-536 | `prefetch_related` y `select_related` en queries |
| `usuarios/context_processors.py` | 27 | `select_related` para optimizar context processor |
| `*/models.py` | Varias | Índices definidos en `Meta.indexes` |
| `MODELO.DDL` | Todo | Índices documentados en secciones `indexes {}` |
| `cretetable_oracle` | Varias | `CREATE INDEX` explícitos |

---

## ✅ Resumen de cumplimiento:

### **Criterio 1: Estructura adecuada de la base de datos** ✅

✅ **Relaciones correctas:**
- 21 Foreign Keys con `on_delete` apropiado (RESTRICT, CASCADE, SET_NULL)
- 1 OneToOneField con constraint único
- 8 Constraints `unique_together` para evitar duplicados

✅ **Índices eficientes:**
- Índices en todos los Foreign Keys (automáticos en Oracle)
- Índices en campos de búsqueda frecuente (nombre, fecha, estado)
- Índices compuestos para consultas complejas

✅ **Tipos de datos apropiados:**
- BigAutoField para PKs grandes
- DecimalField para valores monetarios
- CharField/TextField según longitud
- BooleanField para flags
- DateField/DateTimeField para fechas

### **Criterio 2: Optimización y normalización** ✅

✅ **Normalización (3NF):**
- Separación Persona/Usuario (evita redundancia)
- Separación Calificación/Detalles (estructura flexible)
- Tablas intermedias para relaciones M:N (UsuarioRol, UsuarioCorredora)
- Eliminación de redundancia (CorredoraIdentificador separado)

✅ **Optimización de rendimiento:**
- `select_related` para JOINs eficientes (1 query en lugar de N)
- `prefetch_related` para relaciones reversas (2 queries en lugar de N+1)
- Índices en campos de búsqueda frecuente
- Índices compuestos para consultas complejas
- Campos calculados (`@property`) para evitar redundancia

✅ **Campos de auditoría automáticos:**
- `creado_en` / `actualizado_en` en todas las tablas
- Trazabilidad automática sin lógica adicional

---

**Conclusión:** El proyecto cumple completamente ambos criterios de evaluación con una estructura de base de datos óptima y optimizaciones avanzadas implementadas en múltiples capas (modelos, queries, índices).

