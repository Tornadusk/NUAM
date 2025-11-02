  # Proyecto NUAM - Sistema de Calificaciones Tributarias

Proyecto Django con API REST para gestión de calificaciones tributarias. Conectado a Oracle Database 23c Free.

## Características

- ✅ Django 5.2.6 con Django REST Framework
- ✅ Oracle Database 23c Free como base de datos
- ✅ Panel de administración altamente personalizado
- ✅ API REST completa con 25+ endpoints (GET público, POST/PUT/DELETE con auth)
- ✅ **Mantenedor Web Interactivo** con interfaz moderna y responsive
- ✅ Modelos de datos según MODELO.DDL
- ✅ Sistema de auditoría completo
- ✅ Usuarios, roles y permisos (Admin y Operador)
- ✅ Gestión de corredoras e instrumentos financieros
- ✅ Templates frontend profesionales con Bootstrap 5
- ✅ Diseño responsive y moderno con colores marca NUAM (Rojo #FF3333)
- ✅ Logo NUAM integrado en la interfaz
- ✅ Diferenciación funcional entre Admin y Operador según roles
- ✅ Wizard multi-paso para ingreso de calificaciones
- ✅ Validación en tiempo real de cálculos tributarios
- ✅ Cargas masivas Excel/CSV con procesamiento automático

## Estructura del Proyecto

El proyecto está organizado en 8 apps Django:

| App | Descripción | Modelos principales |
|-----|-------------|---------------------|
| **core** | Catálogos base | Pais, Moneda, Mercado, Fuente |
| **usuarios** | Gestión de usuarios | Usuario, Persona, Rol, UsuarioRol, Colaborador |
| **corredoras** | Entidades financieras | Corredora, CorredoraIdentificador, UsuarioCorredora |
| **instrumentos** | Datos bursátiles | Instrumento, EventoCapital |
| **calificaciones** | Calificaciones tributarias | Calificacion, FactorDef, Detalles |
| **cargas** | Procesos de carga | Carga, CargaDetalle |
| **auditoria** | Registro de cambios | Auditoria |
| **api** | Endpoints REST | Serializers, ViewSets |

## Instalación

### Requisitos

- Python 3.9+
- Oracle Database 23c Free (local)
- Oracle Instant Client (para la conexión)

### Pasos de instalación

#### 1. Clonar el repositorio

```bash
git clone https://github.com/Tornadusk/NUAM.git
cd Nuam
```

#### 2. Activar entorno virtual

El proyecto ya tiene un venv creado con todas las dependencias instaladas.

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

**Nota:** Si el venv no existe o faltan dependencias, créelo y reinstale:

```bash
# Crear venv (solo si no existe)
python -m venv venv

# Activar venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 4. Configurar base de datos Oracle

**⚡ IMPORTANTE PARA EL DOCENTE EVALUADOR:**

El docente debe crear su propia base de datos Oracle según las instrucciones detalladas a continuación. El proyecto no proporciona acceso directo a la base de datos del estudiante.

##### Configurar Oracle Database 23c Free

Debe tener Oracle Database 23c Free instalado y seguir estos pasos para crear la base de datos del proyecto:

1. **Instalar Oracle Database 23c Free**:
   - Descargar desde: https://www.oracle.com/latam/database/free/
   - Instalar y configurar según documentación oficial

2. **Configurar servicios Oracle**:
   
   Abra **CMD como Administrador** y ejecute:
   
   ```cmd
   # Verificar servicios activos
   net start | find "Oracle"
   
   # Si no están activos, iniciarlos:
   net start OracleOraDB23Home1TNSListener
   net start OracleServiceFREE
   ```

3. **Crear usuario en Oracle**:
   
   ```cmd
   set ORACLE_SID=FREE
   sqlplus / as sysdba
   ```
   
   Dentro de SQL*Plus, ejecute:
   
   ```sql
   ALTER SESSION SET CONTAINER = FREEPDB1;
   
   CREATE USER nuam IDENTIFIED BY nuam_pwd
     DEFAULT TABLESPACE users
     TEMPORARY TABLESPACE temp
     QUOTA UNLIMITED ON users;
   
   GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE,
         CREATE TRIGGER, CREATE PROCEDURE TO nuam;
   GRANT CONNECT, RESOURCE TO nuam;
   
   ALTER SYSTEM SET local_listener='(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))' SCOPE=BOTH;
   ALTER SYSTEM REGISTER;
   ALTER PLUGGABLE DATABASE FREEPDB1 OPEN;
   ALTER PLUGGABLE DATABASE FREEPDB1 SAVE STATE;
   
   EXIT;
   ```

4. **Verificar conexión**:
   ```cmd
   sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1
   ```

5. **Configurar Django**:
   
   Edite el archivo `proyecto_nuam/settings.py`:
   - Comente la configuración de SQLite (líneas 99-104)
   - Descomente la configuración de Oracle (líneas 108-117)
   - Las credenciales ya están pre-configuradas correctamente

```python
# Comentar esto:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Descomentar esto:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'FREEPDB1',
        'USER': 'nuam',
        'PASSWORD': 'nuam_pwd',
        'HOST': '127.0.0.1',
        'PORT': '1521',
    }
}
```

#### 5. Aplicar migraciones

```bash
# Si usas el venv, usas:
# Windows: .\venv\Scripts\python.exe manage.py
# Linux/Mac: venv/bin/python manage.py

python manage.py makemigrations
python manage.py migrate
```

#### 6. Crear usuario de administración

**Opción A: Crear usuario manualmente**

```bash
python manage.py shell
```

Luego ejecute en el shell:
```python
from usuarios.models import Persona, Usuario, Rol, UsuarioRol

persona = Persona.objects.create(
    primer_nombre='Admin',
    apellido_paterno='Sistema',
    fecha_nacimiento='1990-01-01'
)

usuario = Usuario.objects.create(
    id_persona=persona,
    username='admin',
    estado='activo'
)
usuario.set_password('admin123')
usuario.save()

rol = Rol.objects.get_or_create(nombre='Administrador')[0]
UsuarioRol.objects.create(id_usuario=usuario, id_rol=rol)
```

**Opción B: Usuario ya existe**

Si el usuario 'admin' ya existe de una ejecución anterior, puede continuar al paso siguiente.

#### 7. Crear datos iniciales de ejemplo (Recomendado)

**⚠️ Importante:** Asegúrate de estar en el directorio raíz del proyecto y con el venv activado.

```bash
# Windows (PowerShell/CMD)
python create_data_initial.py

# Linux/Mac
python3 create_data_initial.py
```

**Si usas venv explícito:**
```bash
# Windows
.\venv\Scripts\python.exe create_data_initial.py

# Linux/Mac
./venv/bin/python create_data_initial.py
```

Este script **crea automáticamente** todos los datos necesarios para empezar a trabajar:

**Catálogos base:**
- Países: Chile, Perú, Colombia, USA
- Monedas: CLP, PEN, COP, USD
- Relaciones MonedaPais (ej: CLP→Chile, USD→Chile, etc.)
- Mercados bursátiles: BCS, BVL, BVC
- Fuentes de datos: SVS, SMV, SFC

**Entidades del negocio:**
- Corredoras: Banco de Chile, Banco Santander, Credicorp Capital, BTG Pactual
- Instrumentos: ADP Bolsa, Bono Peruano
- Factores F08-F37: Los 30 factores tributarios completos

**Usuarios del sistema:**
- **admin** (contraseña: `admin123`) - Rol: Administrador
- **operador** (contraseña: `op123456`) - Rol: Operador

**Roles disponibles:**
- **Administrador**: Acceso completo, gestión de usuarios, auditoría, reportes globales
- **Operador**: Acceso limitado a su corredora, gestión de calificaciones, reportes locales
- **Analista**: Análisis de datos, reportes especializados (implementación futura)
- **Consultor**: Consulta de calificaciones, acceso a reportes (implementación futura)
- **Auditor**: Acceso de solo lectura a auditoría y calificaciones (implementación futura)

> **💡 Uso del script:** El script usa `get_or_create()` de Django, lo que significa que es **seguro ejecutarlo múltiples veces**. Solo crea datos nuevos si no existen, evitando duplicados. Úsalo cada vez que necesites resetear la base de datos con datos de ejemplo.

> **📝 Nota sobre roles:** En el MVP actual, solo se implementaron permisos diferenciados para **Administrador** y **Operador**. Los demás roles (Analista, Consultor, Auditor) se crearán automáticamente para uso futuro cuando se implementen sus funcionalidades específicas.

#### 8. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Accede a:
- **Página principal:** http://127.0.0.1:8000/ (Inicio)
- **Mantenedor de Calificaciones:** http://127.0.0.1:8000/calificaciones/mantenedor/ (Requiere login)
- **Panel de administración:** http://127.0.0.1:8000/admin/ (Requiere login)
- **API REST:** http://127.0.0.1:8000/api/ (GET público, POST/PUT/DELETE con auth)
- **Login:** http://127.0.0.1:8000/accounts/login/

**Credenciales por defecto (creadas por el script):**
- **Usuario:** `admin` / **Contraseña:** `admin123` - Rol: Administrador (acceso completo)
- **Usuario:** `operador` / **Contraseña:** `op123456` - Rol: Operador (acceso limitado)

> **💡 Recomendación**: 
> 1. Primero explore el **Mantenedor** (interfaz web moderna con Bootstrap 5)
> 2. Luego revise el **Admin de Django** (administración técnica completa)
> 3. Pruebe la **API REST** desde el navegador o Postman
> 4. Todos los accesos requieren hacer login primero


## Panel de Administración

El Admin de Django está completamente configurado con:
- **Acciones masivas**: Activar, bloquear, publicar, validar registros en lote
- **Métricas contextuales**: Muestra cantidad de registros relacionados
- **Botones de edición**: Columna "✏️ Editar" visible en cada tabla
- **Acciones**: Dropdown con opciones masivas (eliminar, cambiar estado, etc.)
- **Organización**: Apps numeradas del 1 al 7 según orden lógico de uso
- **Campos completos**: Todas las tablas muestran `creado_en` y `actualizado_en` del MODELO.DDL

### Uso básico del Admin

1. **Ver registros**: Haz clic en cualquier modelo del menú lateral
2. **Crear registro**: Botón verde "Agregar [Modelo]" en la esquina superior derecha
3. **Editar registro**: Clic en el botón ✏️ Editar o en el nombre/ID del registro
4. **Eliminar registro**: Selecciona checkbox y usa acción "Eliminar seleccionados"
5. **Buscar**: Usa la barra de búsqueda superior
6. **Filtrar**: Usa los filtros del panel derecho

> **Nota importante**: El Admin de Django lee/escribe directamente desde la base de datos usando el ORM. NO usa la API REST. Son dos sistemas separados.

## API REST

La API REST **se inicia automáticamente** cuando Django arranca. No requiere configuración adicional.

### ¿Cómo funciona?

1. **Inicio automático**: Cuando ejecutas `python manage.py runserver`, Django carga todas las apps de `INSTALLED_APPS`, incluyendo `rest_framework` y `api`.
2. **Router de DRF**: El archivo `api/urls.py` registra todos los ViewSets en un `DefaultRouter()`, que automáticamente genera los endpoints REST.
3. **URLs disponibles**: Los endpoints se exponen en `/api/` (configurado en `proyecto_nuam/urls.py`).

### Endpoints principales:

#### Core - Catálogos Base
- `GET/POST /api/paises/` - Países
- `GET/POST /api/monedas/` - Monedas
- `GET/POST /api/monedas-pais/` - Relación moneda-país
- `GET/POST /api/mercados/` - Mercados
- `GET/POST /api/fuentes/` - Fuentes de datos

#### Usuarios
- `GET/POST /api/personas/` - Personas
- `GET/POST /api/usuarios/` - Usuarios del sistema
- `GET/POST /api/roles/` - Roles
- `GET/POST /api/usuarios-roles/` - Asignación de roles
- `GET/POST /api/colaboradores/` - Colaboradores

#### Corredoras
- `GET/POST /api/corredoras/` - Corredoras
- `GET/POST /api/corredoras-identificadores/` - Identificadores fiscales
- `GET/POST /api/usuarios-corredoras/` - Asignación usuarios-corredoras

#### Instrumentos
- `GET/POST /api/instrumentos/` - Instrumentos financieros
- `GET/POST /api/eventos-capital/` - Eventos de capital

#### Calificaciones
- `GET/POST /api/factores/` - Definición de factores
- `GET/POST /api/calificaciones/` - Calificaciones tributarias
- `GET/POST /api/calificaciones-montos/` - Detalles de montos
- `GET/POST /api/calificaciones-factores/` - Detalles de factores

#### Cargas
- `GET/POST /api/cargas/` - Procesos de carga
- `GET/POST /api/cargas-detalles/` - Detalles de carga

#### Auditoría
- `GET /api/auditoria/` - Registros de auditoría (solo lectura)

### Ejemplos de uso

```bash
# Listar todos los países
curl http://127.0.0.1:8000/api/paises/

# Listar corredoras activas
curl http://127.0.0.1:8000/api/corredoras/activas/

# Filtrar instrumentos por mercado
curl http://127.0.0.1:8000/api/instrumentos/?mercado=1

# Crear una nueva moneda (requiere autenticación)
curl -X POST http://127.0.0.1:8000/api/monedas/ \
  -H "Content-Type: application/json" \
  -d '{"codigo":"USD","nombre":"Dólar Estadounidense","decimales":2,"vigente":true}'
```

### Autenticación

- **GET**: No requiere autenticación (lectura pública para catálogos)
- **POST/PUT/DELETE**: Requiere autenticación de sesión Django o Basic Auth

## Mantenedor de Calificaciones

### Vista web interactiva

El proyecto incluye un **Mantenedor completo de Calificaciones Tributarias** accesible en:
```
http://localhost:8000/calificaciones/mantenedor/
```

### Características del Mantenedor

- ✅ **Interfaz responsive** con Bootstrap 5
- ✅ **Búsqueda y filtrado** por mercado, origen, período, estado
- ✅ **Vistas Resumen/Completa** para visualizar factores F08-F37
- ✅ **CRUD completo** (Crear, Leer, Actualizar, Eliminar calificaciones)
- ✅ **Wizard multi-paso** para ingreso de datos
- ✅ **Validación en tiempo real** de suma de factores
- ✅ **Paginación automática** para grandes volúmenes
- ✅ **KPIs en tiempo real** (P95 API, tiempo de carga, errores)
- ✅ **Panel de auditoría** integrado con últimos eventos
- ✅ **Cargas masivas** (x Factor y x Monto)
- ✅ **Exportación** a CSV, Excel, PDF

### Pestañas del Mantenedor

1. **Mantenedor**: Interfaz principal con filtros, tabla y acciones CRUD
2. **Cargas Masivas**: Subida de archivos Excel/CSV para importación masiva
3. **Usuarios**: Gestión de usuarios del sistema (Admin únicamente)
4. **Auditoría**: Registro de acciones realizadas en el sistema
5. **Reportes**: Exportación de datos en distintos formatos

### Flujo de trabajo

1. **Acceder**: Ingrese a `/calificaciones/mantenedor/` (requiere login)
2. **Buscar/Filtrar**: Use los filtros superiores para encontrar calificaciones
3. **Crear**: Click en "Ingresar" → Complete wizard 3 pasos → Guardar
4. **Modificar**: Seleccione una fila → Click en "Modificar" → Actualice datos
5. **Eliminar**: Seleccione una fila → Click en "Eliminar" → Confirmar
6. **Copiar**: Seleccione una fila → Click en "Copiar" → Edite y guarde

### Integración con API

El frontend utiliza JavaScript nativo (sin frameworks pesados) para comunicarse con la API REST:
- Carga de catálogos dinámicos (países, monedas, instrumentos, factores)
- Consulta de calificaciones con filtrado del lado del servidor
- Guardado/edición vía POST/PUT a `/api/calificaciones/`
- Registro de eventos de auditoría automático

## Desarrollo

### Estructura de archivos importantes

```
proyecto_nuam/
├── core/           # Catálogos base
├── usuarios/       # Gestión de usuarios
├── corredoras/     # Corredoras
├── instrumentos/   # Instrumentos
├── calificaciones/ # Calificaciones
├── cargas/         # Cargas
├── auditoria/      # Auditoría
├── api/            # API REST
└── settings.py     # Configuración principal

MODELO.DDL          # Especificación de modelo de datos
requirements.txt    # Dependencias Python
manage.py           # Script de gestión Django
```

### Comandos útiles

```bash
# Verificar estado de migraciones
python manage.py showmigrations

# Crear migraciones para una app específica
python manage.py makemigrations core

# Hacer rollback de migraciones
python manage.py migrate usuarios zero

# Acceder al shell de Django
python manage.py shell

# Crear datos de prueba
python manage.py shell
>>> from core.models import *
>>> pais = Pais.objects.create(codigo='CHL', nombre='Chile')
```

## Orden Guiado Recomendado para el Admin

Al usar el Panel de Administración, se recomienda crear datos en el siguiente orden para evitar errores de claves foráneas:

### 🔢 Secuencia Recomendada:

**1️⃣ Usuarios y Permisos**
- Crear Roles (Administrador, Operador, etc.)
- Crear Personas (datos personales)
- Crear Usuarios (asociados a Personas)
- Asignar Usuario-Rol
- Crear Colaboradores (si aplica)

**2️⃣ Catálogos Base**
- Crear Países (Chile, Perú, Colombia, etc.)
- Crear Monedas (CLP, PEN, COP, USD, etc.)
- Crear Moneda-País (relaciones)
- Crear Mercados (ACCIONES, BONOS, etc.)
- Crear Fuentes de datos

**3️⃣ Corredoras**
- Crear Corredoras (asociadas a País)
- Agregar Identificadores Fiscales (inline)
- Asignar Usuario-Corredora (relación M:N)

**4️⃣ Instrumentos**
- Crear Instrumentos (asociados a Mercado y Moneda)
- Agregar Eventos de Capital (inline)

**5️⃣ Calificaciones Tributarias**
- Revisar/Crear Factores (F08-F37)
- Crear Calificaciones (con todas las FKs)
- Agregar Detalles de Montos (inline)
- Agregar Detalles de Factores (inline)

**6️⃣ Cargas Masivas**
- Realizar Cargas por archivo
- Revisar Detalles de carga (errores)

**7️⃣ Auditoría**
- Consultar logs de cambios (solo lectura)

### 💡 Acciones Disponibles en Admin

- **Monedas**: Marcar como vigente/no vigente
- **Usuarios**: Activar/Bloquear masivamente
- **Corredoras**: Activar/Desactivar
- **Calificaciones**: Publicar, Validar, Volver a borrador

### 📊 Métricas Contextuales

Cada modelo muestra:
- Cantidad de registros relacionados
- Porcentajes de éxito en cargas
- Resúmenes de datos asociados

## Modelo de Negocio: Usuarios y Colaboradores

El sistema NUAM distingue entre **Usuarios** y **Colaboradores** según el modelo de negocio:

### Relación Usuario ↔ Colaborador (1:1 opcional)

```python
Usuario (obligatorio)
  ├── Persona (datos personales)
  ├── username, contraseña, estado
  └── Colaborador (opcional)  ← Solo si es colaborador interno
      └── gmail (email corporativo)
```

### ¿Cuándo crear un Colaborador?

**✅ Crear Colaborador:**
- Usuarios internos de la empresa NUAM
- Analistas, consultores, auditores propios
- Personal que requiere acceso a email corporativo para notificaciones

**❌ NO crear Colaborador:**
- Usuarios externos (corredoras, auditores externos)
- Roles de solo consulta
- Usuarios administrativos que no necesitan notificaciones

### Ejemplo de uso

```python
# Crear usuario normal (sin colaborador)
persona = Persona.objects.create(primer_nombre="Juan", ...)
usuario = Usuario.objects.create(id_persona=persona, username="juan", ...)

# Crear colaborador interno
persona = Persona.objects.create(primer_nombre="María", ...)
usuario = Usuario.objects.create(id_persona=persona, username="maria", ...)
Colaborador.objects.create(id_usuario=usuario, gmail="maria@nuam.cl")
```

**Nota:** El script `create_data_initial.py` crea automáticamente usuarios **admin** y **operador** ambos **como colaboradores** para facilitar las pruebas.

## Sistema de Roles y Permisos

El proyecto NUAM implementa un sistema de roles para controlar el acceso a funcionalidades según el tipo de usuario:

### Roles Implementados en MVP

#### 👑 Administrador
- **Acceso**: Completo a todo el sistema
- **Funcionalidades**:
  - ✅ Ver todas las calificaciones (sin filtros)
  - ✅ Gestionar usuarios (crear, editar, eliminar)
  - ✅ Acceso a panel de auditoría
  - ✅ Reportes globales
  - ✅ Administración completa vía Django Admin
  - ✅ Configuración de catálogos (países, monedas, mercados, etc.)

#### 🔧 Operador
- **Acceso**: Limitado a su corredora asignada
- **Funcionalidades**:
  - ✅ Ver calificaciones de su corredora
  - ✅ Crear/editar calificaciones de su corredora
  - ✅ Cargas masivas
  - ✅ Reportes locales
  - ❌ No puede gestionar usuarios
  - ❌ No puede acceder a auditoría
  - ❌ No puede ver datos de otras corredoras

### Roles para Implementación Futura

#### 📊 Analista
- Análisis de datos tributarios
- Reportes especializados y dashboards
- Visualizaciones estadísticas

#### 📋 Consultor
- Consulta de calificaciones históricas
- Acceso a reportes en modo lectura
- Sin capacidad de modificar datos

#### 🔍 Auditor
- Acceso de solo lectura a auditoría
- Revisión de cambios y transacciones
- Reportes de cumplimiento

### Matriz de Permisos (MVP)

| Funcionalidad | Administrador | Operador | Analista | Consultor | Auditor |
|---------------|---------------|----------|----------|-----------|---------|
| Mantenedor | ✅ Global | ✅ Corredora | ❌ | ❌ | ❌ |
| Cargas Masivas | ✅ | ✅ | ❌ | ❌ | ❌ |
| Gestión Usuarios | ✅ | ❌ | ❌ | ❌ | ❌ |
| Auditoría | ✅ | ❌ | ❌ | ❌ | ✅ |
| Reportes | ✅ Globales | ✅ Locales | TBD | TBD | TBD |
| Django Admin | ✅ Completo | ✅ Parcial | ❌ | ❌ | ❌ |

> **💡 Nota:** Los permisos actuales se basan en autenticación de Django (`@login_required`). La diferenciación entre Administrador y Operador se implementará en una versión futura usando el sistema de roles de Django junto con la asignación de corredoras a usuarios.

## Licencia

Proyecto académico para evaluación.

## Autor

Desarrollado como proyecto integrado.


## Nota Importante: Convención de Nomenclatura de Primary Keys

El proyecto NUAM utiliza **dos convenciones diferentes** para las Primary Keys (PK), dependiendo del tipo de tabla:

### Tablas Principales (Catálogos y Entidades de Negocio)
Las tablas principales usan **PKs con nombres descriptivos**:
- `PAIS` → `id_pais`
- `MONEDA` → `id_moneda`
- `USUARIO` → `id_usuario`
- `CALIFICACION` → `id_calificacion`
- `CORREDORA` → `id_corredora`
- `INSTRUMENTO` → `id_instrumento`
- etc.

### Tablas Intermedias (Relaciones Many-to-Many)
Las tablas que representan relaciones M:N usan **PK genérica `id`**:
- `USUARIO_ROL` → `id`
- `USUARIO_CORREDORA` → `id`
- `CALIFICACION_MONTO_DETALLE` → `id`
- `CALIFICACION_FACTOR_DETALLE` → `id`
- `CORREDORA_IDENTIFICADOR` → `id`

**Razón**: Django requiere que todos los modelos tengan una columna PK auto-incrementable. Las tablas intermedias mantienen además un `UNIQUE` constraint en las FKs para evitar duplicados en las relaciones.

> **💡 Importante**: Esta diferencia está reflejada en `MODELO.DDL` y `cretetable_oracle`. Si recreas la base de datos desde cero, las PKs se crearán automáticamente correctas.
