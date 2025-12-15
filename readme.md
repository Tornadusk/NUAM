# Proyecto NUAM - Sistema de Calificaciones Tributarias

Proyecto Django con API REST para gestión de calificaciones tributarias. Conectado a Oracle Database 23c Free.

# Integrantes
-Victor Manuel Gangas García
-Darby Beltran
-Fernando Pizarro

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

## 📚 Documentación y Recursos

Para comprender y utilizar el sistema NUAM, se recomienda consultar los siguientes recursos:

### Manual de Usuario
- **📖 Manual de Usuario**: Consulta el archivo `Manual de Usuario.docx` incluido en el repositorio para obtener una guía completa sobre el manejo de la interfaz, funcionalidades del sistema y procedimientos operativos.

### Videos Tutoriales
- **🎥 Tutorial de instalación de Nuam Linux/Mac – Paso a paso**: [Ver video](https://www.youtube.com/watch?v=gFuCFgRHXZk)
- **🎥 NUAM - Explicación del Menú Administrador**: [Ver video](https://www.youtube.com/watch?v=XK5sFWuF-yQ) - Guía detallada sobre las funcionalidades del panel de administración y navegación del sistema.

### Documentación Técnica y de Diseño
- **📄 Proyecto Integrado Ev3.docx**: Este documento contiene toda la documentación del proyecto incluyendo:
  - Lógica de trabajo empleada en NUAM
  - Diagramas de arquitectura y flujo
  - Requerimientos funcionales y no funcionales
  - Historias de usuario
  - Mockups y prototipos de interfaz
  - Flujo del prototipo y casos de uso
  - Especificaciones técnicas del sistema

> **💡 Recomendación**: Se sugiere revisar primero el Manual de Usuario para familiarizarse con la interfaz, luego los videos tutoriales para procedimientos específicos, y finalmente el documento "Proyecto Integrado Ev3.docx" para entender la arquitectura completa y la lógica de negocio implementada.

## Guía de instalación (paso a paso)

Índice rápido:
- Paso 1: Preparar entorno
- Paso 2: Instalar y levantar Oracle (Docker/Windows)
- Paso 3: Instalar Apache Pulsar con Docker (Opcional)
- Paso 4: Configurar `settings.py`
- Paso 5: Aplicar migraciones
- Paso 6: Cargar datos iniciales
- Paso 7: Configurar Certificados SSL/HTTPS (Opcional)
- Paso 8: Inicializar Microservicio de Tipos de Cambio (Opcional)
- Paso 9: Ejecutar servidor
- Tutorial de instalación recomendado: [Tutorial de instalación de Nuam Linux/Mac – Paso a paso](https://www.youtube.com/watch?v=gFuCFgRHXZk)

**📚 Guías adicionales:**
- **Orden de inicio y Docker:** Ver `Explicacion/GUIA_INICIO_PROYECTO.md` para entender qué hace cada Docker Compose y cómo iniciar correctamente el proyecto
- **Problemas con tipos de cambio:** Ver `Explicacion/SOLUCION_TIPOS_CAMBIO.md` si el microservicio de tipos de cambio no muestra datos

### “Resumen paso a paso: sección de instalación con los detalles específicos.”

### Paso 1: Preparar entorno
```bash
# 1. Clona el repositorio
git clone https://github.com/Tornadusk/NUAM.git
cd NUAM

# 2. Crea y activa el entorno virtual
python3 -m venv venv   # Mac/Linux
python -m venv venv    # Windows

source venv/bin/activate     # Mac/Linux
# ./venv/Scripts/Activate.ps1   # Windows PowerShell
# ./venv/Scripts/activate.bat   # Windows CMD

# 3. Instala las dependencias de Python
pip install -r requirements.txt

# Nota: django-extensions está incluido en requirements.txt
# Se usa opcionalmente para HTTPS con runserver_plus
# Si no lo necesitas, Django funcionará normalmente sin él
```

### Paso 2: Instalar y levantar Oracle (elige UNA opción)
- Docker (Mac/Linux) → ver sección “Instalación y configuración de Oracle (Opción A)” más abajo
- Nativo Windows → ver sección “Instalación y configuración de Oracle (Opción B)” más abajo

### Paso 3: Instalar Apache Pulsar con Docker (Opcional - para microservicios)

**⚠️ IMPORTANTE:** Este paso es **opcional** y solo necesario si vas a usar los microservicios con Pulsar (productores/consumidores de mensajes).

#### Opción A: Docker (⭐ RECOMENDADO - Funciona en Windows y Linux)

**Requisito previo:** Tener Docker Desktop instalado y corriendo.

**Windows:**
- Descarga e instala Docker Desktop desde: https://www.docker.com/products/docker-desktop/
- Asegúrate de que Docker Desktop esté corriendo (icono en la bandeja del sistema)

**Linux:**
```bash
# Instalar Docker (si no lo tienes)
sudo apt-get update
sudo apt-get install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

# Agregar tu usuario al grupo docker (para no usar sudo)
sudo usermod -aG docker $USER
# Cierra sesión y vuelve a iniciar para que tome efecto
```

**Levantar Pulsar y servicios:**
```bash
# En la raíz del proyecto NUAM
# Esto levanta Pulsar + docs-generator (microservicio de documentos)
docker-compose up -d

# Verificar que todos los servicios están corriendo
docker ps

# Deberías ver:
# - nuam-pulsar (puerto 6650 y 8080)
# - nuam-docs-generator (puerto 5001)

# ⚠️ IMPORTANTE: Admin API puede tardar 30-60 segundos en estar disponible
# El contenedor inicia inmediatamente, pero Admin API necesita tiempo para iniciar

# Opción 1: Verificar manualmente (esperar 60 segundos y luego verificar)
sleep 60  # Linux/Mac - o espera manualmente en Windows
curl http://localhost:8080/admin/v2/brokers/health
# Debería responder: {"status": "ok"} o similar

# Opción 2: Usar script automático (espera hasta que Admin API esté listo)
cd scripts
.\verificar_pulsar.ps1   # Windows PowerShell
# o
chmod +x verificar_pulsar.sh && ./verificar_pulsar.sh   # Linux/Mac

# Ver logs de Pulsar
docker logs nuam-pulsar

# Ver logs de docs-generator
docker logs nuam-docs-generator
```

**⚠️ IMPORTANTE:** Usa el `docker-compose.yml` de la **RAÍZ del proyecto** (contiene Pulsar + docs-generator + exchange-rate-service).
- ✅ `docker-compose.yml` (raíz) → Usa este para desarrollo completo (levanta **Pulsar**, **docs-generator** y el microservicio de **tipos de cambio** `exchange-rate-service` en el puerto 5100)
- ❌ `services/docker-compose.yml` → Solo docs-generator (no tiene Pulsar)
- ❌ `docker-compose.dev.yml` → Archivo alternativo (no necesario si usas el principal)

**Verificar instalación:**
- Pulsar debería estar disponible en:
  - **Puerto 6650**: Para productores/consumidores
  - **Puerto 8080**: Admin API (http://localhost:8080)

**Detener Pulsar:**
```bash
docker-compose down
```

**⚠️ Troubleshooting:** Si Pulsar se apaga constantemente, está en ciclo de reinicio ("Restarting"), o no puedes acceder a Pulsar Admin (puerto 8080), consulta `microservicio/docs/TROUBLESHOOTING_PULSAR.md` para soluciones detalladas a problemas comunes.

**🔄 Si el contenedor está en ciclo de reinicio constante:**
```bash
cd scripts
.\solucionar_restart_loop.ps1   # Windows
# o
chmod +x solucionar_restart_loop.sh && ./solucionar_restart_loop.sh   # Linux/Mac
```

#### Opción B: WSL2 + Instalación nativa (Solo Windows - NO recomendado para evaluación)

⚠️ **Solo si NO puedes usar Docker**. Requiere más pasos y puede dar problemas.

**Prerequisitos:**
1. Instalar WSL2:
   ```powershell
   # En PowerShell como Administrador
   wsl --install -d Ubuntu
   ```
2. Reiniciar la computadora
3. Descargar Pulsar desde: https://archive.apache.org/dist/pulsar/pulsar-4.1.1/
   - Seleccionar el archivo `.tar.gz` (aproximadamente 234MB)
4. Descomprimir y ejecutar (en WSL):
   ```bash
   cd /ruta/donde/descomprimiste/apache-pulsar-4.1.1
   bin/pulsar standalone
   ```

#### Opción C: Instalación nativa en Linux (Solo Linux - NO recomendado para evaluación)

⚠️ **Solo si NO puedes usar Docker**.

```bash
# 1. Descargar Pulsar
cd /tmp
wget https://archive.apache.org/dist/pulsar/pulsar-4.1.1/apache-pulsar-4.1.1-bin.tar.gz

# 2. Descomprimir
tar -xzf apache-pulsar-4.1.1-bin.tar.gz
cd apache-pulsar-4.1.1

# 3. Ejecutar en modo standalone
bin/pulsar standalone
```

**💡 Recomendación:**
- **Para desarrollo/evaluación:** Usa **Opción A (Docker)** - Es la más fácil y funciona igual en Windows y Linux
- **Para producción:** Usa un cluster de Pulsar (NO standalone) con configuración dedicada

### Paso 4: Configurar conexión en `proyecto_nuam/settings.py`
- La configuración de Oracle ya está pre-configurada en `settings.py` con las credenciales correctas.

### Paso 5: Aplicar migraciones (después de tener la BD arriba)

**⚠️ IMPORTANTE: Elige UNO de los dos métodos siguientes**

**🚨 ADVERTENCIA CRÍTICA:**
Si ejecutas `cretetable_oracle` primero y luego intentas usar `migrate`, obtendrás el error **`ORA-00955: este nombre ya lo está utilizando otro objeto existente`** porque Django intentará crear tablas/objetos que ya existen. Por esta razón, **se recomienda encarecidamente usar solo `migrate` (Método 1)** para crear la base de datos desde cero.

#### **Método 1: Solo migraciones de Django (⭐ RECOMENDADO - Para desarrollo y producción)**

Este método usa **SOLO** las migraciones de Django para crear la base de datos:

```bash
python3 manage.py migrate   # Mac/Linux
python manage.py migrate    # Windows
```

- ✅ Django crea todas las tablas e índices automáticamente mediante migraciones
- ✅ Fácil de mantener cuando cambias modelos (solo `makemigrations` + `migrate`)
- ✅ No necesitas modificar scripts SQL manualmente
- ✅ **NO ejecutes `cretable_oracle`** - Django lo hace todo
- ✅ **Evita conflictos** - No hay riesgo de `ORA-00955` por objetos duplicados
- ⚠️ **Si obtienes `ORA-01408`**: Algunos índices ya existen en tu base de datos (Oracle puede crear índices automáticamente para Foreign Keys). Ve a la migración que falla, comenta el `AddIndex` correspondiente (está marcado con el nombre del índice) y vuelve a ejecutar `migrate`. Django no intentará crearlos de nuevo.

#### **Método 2: cretable_oracle + migraciones (Solo si realmente necesitas DDL manual)**
⚠️ **NO recomendado a menos que tengas un motivo específico** (ej: políticas de empresa que requieren DDL manual).

Si decides usar este método:
1. **Primero, ejecuta `cretetable_oracle` en Oracle** (crea todas las tablas e índices)
2. **Luego, marca las migraciones como aplicadas usando `--fake` por app**:
```bash
# Marcar migraciones de apps de negocio como aplicadas (las tablas ya existen)
python manage.py migrate usuarios --fake
python manage.py migrate auditoria --fake
python manage.py migrate core --fake
python manage.py migrate instrumentos --fake
python manage.py migrate corredoras --fake
python manage.py migrate calificaciones --fake
python manage.py migrate cargas --fake

# Aplicar migraciones restantes de Django (auth, sessions, etc.)
python manage.py migrate
```
- ⚠️ **Requiere sincronización manual** - Debes mantener `cretetable_oracle` actualizado con los modelos
- ⚠️ **Más propenso a errores** - Si `cretetable_oracle` y los modelos difieren, tendrás problemas

**¿Cuándo usar `makemigrations`?**
- Solo si modificas modelos y necesitas generar nuevas migraciones
- **Para clonar y levantar el proyecto desde cero: NO necesitas ejecutar `makemigrations`** - Solo ejecuta `migrate` y Django creará todo automáticamente
- **Si obtienes `ORA-01408`**: Algunos índices ya existen en tu base de datos (Oracle puede crear índices automáticamente para Foreign Keys). Ve a la migración que falla, comenta el `AddIndex` correspondiente (está marcado con el nombre del índice) y vuelve a ejecutar `migrate`. Django no intentará crearlos de nuevo.

### Paso 6: Cargar datos iniciales (idempotente)
```bash
python3 create_data_initial.py   # Mac/Linux
python create_data_initial.py    # Windows
```

Este script crea automáticamente:
- Catálogos base (países, monedas, mercados, fuentes)
- Usuarios de ejemplo: `admin` (contraseña: `admin123`), `operador` (contraseña: `op123456`)
- Corredoras, instrumentos y factores tributarios
- **Fuentes de tipos de cambio** (inicializa automáticamente usando `inicializar_fuentes_tipos_cambio`)
- Ver sección "Crear datos iniciales" más abajo para más detalles

### Paso 7: Configurar Certificados SSL/HTTPS (Opcional para desarrollo, Recomendado para seguridad)

**📋 Nota para evaluación:** El uso de HTTPS es opcional para levantar el proyecto en desarrollo, pero la implementación de SSL y certificados digitales está completamente disponible, documentada y funcional, cumpliendo con los criterios de seguridad definidos en la rúbrica. En producción, HTTPS es obligatorio para proteger la información sensible.

📝 **Para verificación de cifrado y cumplimiento de rúbrica:** Ver `Certificado/VERIFICACION_CIFRADO.md`

🔄 **Renovación automática de certificados:** Para producción, el proyecto incluye documentación completa sobre renovación automática de certificados usando Let's Encrypt y Certbot. Ver `Certificado/RENOVACION_AUTOMATICA.md` y `Certificado/COMO_FUNCIONA_RENOVACION_AUTOMATICA.md` para más detalles.

**⚠️ IMPORTANTE:** Solo necesitas esto si quieres usar HTTPS en desarrollo. Para producción usa certificados de una CA confiable.

#### Verificar si OpenSSL está instalado

**Windows:**
```powershell
openssl version
# Si aparece un error, OpenSSL no está instalado
```

**Linux/Mac:**
```bash
openssl version
# Si aparece un error, instala OpenSSL
```

#### Instalar OpenSSL (si no está instalado)

**Windows:**
1. Descargar desde: https://slproweb.com/products/Win32OpenSSL.html
2. Instalar "Win64 OpenSSL v3.x.x Light" (suficiente)
3. Durante la instalación, seleccionar "Copy OpenSSL DLLs to: The OpenSSL binaries (/bin) directory"

**Linux:**
```bash
sudo apt update
sudo apt install openssl libssl-dev
```

#### Generar certificado autofirmado

**Windows (PowerShell):**
```powershell
cd Certificado
.\generar_certificado.ps1
```

**Nota:** El script se ejecuta desde dentro de la carpeta `Certificado` y genera los archivos `server.key` y `server.crt` directamente en esa carpeta.

**Linux/Mac:**
```bash
cd Certificado
chmod +x generar_certificado.sh
./generar_certificado.sh
```

**O manualmente (si OpenSSL está en PATH):**

**Opción A: Desde la raíz del proyecto:**
```bash
# Windows/Linux/Mac (comando único)
openssl req -new -newkey rsa:2048 -nodes -keyout Certificado/server.key -out Certificado/server.crt -days 365 -x509 -subj "/C=CL/ST=RM/L=Santiago/O=NUAM/OU=Backend/CN=localhost/emailAddress=admin@nuam.cl"
```

**Opción B: Desde la carpeta Certificado:**
```bash
cd Certificado
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365 -x509 -subj "/C=CL/ST=RM/L=Santiago/O=NUAM/OU=Backend/CN=localhost/emailAddress=admin@nuam.cl"
```

Esto creará **AMBOS archivos juntos** (son un par inseparable) en la carpeta `Certificado/`:
- `Certificado/server.crt` (certificado público)
- `Certificado/server.key` (clave privada)

**⚠️ IMPORTANTE:** 
- Debes generar **AMBOS** archivos juntos. No puedes usar un `server.crt` existente con un `server.key` diferente.
- Ambos archivos están en `.gitignore` - cada desarrollador debe generar su propio par.
- Si usas un `server.crt` de otra persona con tu `server.key`, **FALLARÁ** con error "key does not match certificate".

Ver `Certificado/IMPORTANTE_PAR_CERTIFICADO.md` para más detalles.

#### Tabla resumen: Certificados SSL

| Aspecto | Detalles |
|---------|----------|
| **¿Necesito OpenSSL?** | Solo para GENERAR el certificado (una vez). Después no necesitas OpenSSL instalado |
| **¿Dónde se guarda?** | `Certificado/server.crt` y `Certificado/server.key` |
| **¿Se sube al repositorio?** | ❌ **NO** - Ambos (`server.crt` y `server.key`) están en `.gitignore`. Cada desarrollador debe generar su propio par |
| **⚠️ IMPORTANTE** | Cada desarrollador debe generar **AMBOS archivos juntos** usando el script. El `server.crt` y `server.key` son un par inseparable - si usas un `server.crt` de otra persona con tu `server.key`, **FALLARÁ** con error "key does not match certificate" |
| **¿Funciona automáticamente?** | ❌ NO. Debes usar `runserver_plus` con `--cert-file` y `--key-file` explícitamente |
| **¿Funciona en Windows y Linux?** | SÍ, los certificados son compatibles. Cada desarrollador puede generar el suyo |
| **¿Si cada uno tiene un certificado diferente?** | SÍ funciona. Cada certificado es independiente |
| **¿Para qué sirve?** | Solo para desarrollo local con HTTPS. En producción usa certificados de una CA confiable |

📝 **Más detalles:** Ver `Certificado/README.md` y `Certificado/INSTRUCCIONES_RAPIDAS.md`

### Paso 8: Inicializar Microservicio de Tipos de Cambio (Opcional - Solo si vas a usar el dashboard de tipos de cambio)

**⚠️ IMPORTANTE:** Este paso es necesario **solo si vas a usar el microservicio de tipos de cambio** (`/microservicio/tipos-cambio/`).

El microservicio de tipos de cambio requiere que las fuentes estén inicializadas en la base de datos antes de poder obtener datos.

**✅ Las fuentes se inicializan automáticamente** cuando ejecutas `create_data_initial.py` (Paso 6). No necesitas ejecutar `inicializar_fuentes_tipos_cambio` manualmente si ya ejecutaste el script de datos iniciales.

**Si NO ejecutaste `create_data_initial.py` o necesitas reinicializar las fuentes:**

```bash
# Inicializar fuentes de tipos de cambio manualmente
python manage.py inicializar_fuentes_tipos_cambio
```

**Para obtener tipos de cambio reales desde APIs externas:**

```bash
# Obtener tipos de cambio desde APIs externas (requiere conexión a internet)
python manage.py obtener_tipos_cambio
```

**Nota:** 
- Banco Central de Chile no requiere API key y funciona automáticamente
- Para ExchangeRate API y Fixer.io, puedes configurar API keys opcionales desde el admin (`/admin/microservicio/tipocambiofuente/`)
- `obtener_tipos_cambio` **NO se ejecuta automáticamente** - debes ejecutarlo manualmente o configurar una tarea programada (cron) para actualizaciones periódicas

**📝 Para más detalles:** Ver `Explicacion/SOLUCION_TIPOS_CAMBIO.md` si el microservicio no muestra datos.

### Paso 9: Ejecutar servidor

#### Opción A: Servidor HTTP normal (por defecto)

**⚠️ Seguridad:** HTTP no cifra la comunicación. Los datos (contraseñas, tokens, información sensible) viajan en texto plano. **Recomendado solo para desarrollo local sin datos sensibles.**

**Respuesta directa:** ¿Es más seguro usar HTTPS? **SÍ, definitivamente.** HTTPS cifra toda la comunicación, protegiendo contraseñas, tokens de sesión y datos sensibles. En producción, HTTPS es obligatorio. En desarrollo, es opcional pero recomendado.
```bash
python3 manage.py runserver   # Mac/Linux
python manage.py runserver    # Windows
```

Accesos:
- Login: http://127.0.0.1:8000/accounts/login/
- Mantenedor: http://127.0.0.1:8000/calificaciones/mantenedor/
- Admin: http://127.0.0.1:8000/admin/

#### Opción B: Servidor HTTPS (requiere certificado generado - **más seguro**)

**✅ Seguridad:** HTTPS cifra toda la comunicación entre el navegador y el servidor. **Recomendado para desarrollo con datos sensibles y obligatorio en producción.**

**⚠️ IMPORTANTE:** Los certificados **NO funcionan automáticamente**. Debes usar el comando `runserver_plus` con los archivos generados. Django no detecta automáticamente los certificados.

**Prerrequisito:** Haber completado el Paso 7 (generar certificado - AMBOS archivos: `server.crt` y `server.key`)

**Nota:** `django-extensions`, `Werkzeug` y `pyOpenSSL` ya están incluidos en `requirements.txt` (líneas 23-25) y se instalan automáticamente al ejecutar `pip install -r requirements.txt`. Si por alguna razón no están instalados, ejecuta:
```bash
pip install django-extensions Werkzeug pyOpenSSL
```

**Ejecutar con HTTPS:**

**Opción A: Desarrollo local (recomendado)**
```bash
# Windows/Linux/Mac
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443
```
Django mostrará: `Development server is running at https://127.0.0.1:8443/`

**Opción B: Acceso desde otras máquinas en la red local**
```bash
# Windows/Linux/Mac
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 0.0.0.0:8443
```
Django mostrará: `Development server is running at https://0.0.0.0:8443/`
**Nota:** Aunque el servidor escucha en `0.0.0.0`, debes acceder desde el navegador usando `127.0.0.1` o `localhost`.

Accesos (ambas opciones):
- Login: **https://127.0.0.1:8443/accounts/login/** o **https://localhost:8443/accounts/login/**
- Mantenedor: **https://127.0.0.1:8443/calificaciones/mantenedor/** o **https://localhost:8443/calificaciones/mantenedor/**
- Admin: **https://127.0.0.1:8443/admin/** o **https://localhost:8443/admin/**

**⚠️ Nota:** El navegador mostrará una advertencia de seguridad porque el certificado es autofirmado. Esto es normal en desarrollo. Hacer clic en "Avanzado" → "Continuar a localhost (no seguro)".

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

### Recomendación
- Consulta la documentación oficial como primera referencia.
- Si tienes dudas sobre la instalación en Linux o Mac, revisa el video “Tutorial de instalación de Nuam Linux/Mac – Paso a paso” (enlace en el índice rápido).
- Apóyate en la IA si aparece algún error durante la instalación.
- Recuerda leer todos los puntos y opciones antes de probar precipitadamente

### Pasos de instalación

#### 1. Clonar el repositorio

```bash
git clone https://github.com/Tornadusk/NUAM.git
cd NUAM
```

#### 2. Crear y activar tu entorno virtual

El entorno virtual (venv) no se versiona en Git. Crea y activa el tuyo, luego instala dependencias:

```bash
# Crear venv (si no existe)
python3 -m venv venv   # Mac/Linux
python -m venv venv    # Windows

# Activar venv
source venv/bin/activate     # Mac/Linux
# .\venv\Scripts\Activate.ps1   # Windows PowerShell
# venv\Scripts\activate.bat     # Windows CMD

# Instalar dependencias
pip install -r requirements.txt
```

#### 4. Instalación y configuración de Oracle por sistema operativo

Paso 1: Instalación

Elige la opción que corresponda a tu sistema operativo.

Opción A: Docker (Recomendado para Mac/Linux)

Este método usa Docker, que es la forma más sencilla de ejecutar Oracle en entornos Mac y Linux. Asegúrate de tener Docker Desktop instalado y en ejecución.

```bash
# 1. Descarga la imagen
docker pull container-registry.oracle.com/database/free:latest

# 2. Inicia el contenedor (cambia ContraseñaSegura por una contraseña robusta para SYS/SYSTEM)
docker run -d \
  -p 1521:1521 \
  -e ORACLE_PWD=ContraseñaSegura \
  --name oracle-db \
  container-registry.oracle.com/database/free:latest

# 3. Verifica que esté activo (la BD puede tardar 1-2 minutos en estar lista)
docker ps
```

Opción B: Instalación Nativa (Windows)

1) Instalar Oracle:
- Descargar desde: https://www.oracle.com/latam/database/free/
- Instalar y configurar según la documentación oficial.

2) Iniciar servicios Oracle (CMD como Administrador):

```cmd
:: Verificar servicios activos
net start | find "Oracle"

:: Si no están activos, iniciarlos (los nombres pueden variar)
net start OracleOraDB23Home1TNSListener
net start OracleServiceFREE
```

Paso 2: Crear Usuario (Comandos SQL)

Conéctate como administrador (sysdba).

- Para Docker (Mac/Linux):

```bash
docker exec -it oracle-db sqlplus / as sysdba
```

- Para Windows (nativo):

```cmd
set ORACLE_SID=FREE
sqlplus / as sysdba
```

Una vez dentro de SQL*Plus, ejecuta:

```sql
-- Conectar a la Pluggable Database (PDB)
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Crear el usuario 'nuam'
CREATE USER nuam IDENTIFIED BY nuam_pwd
   DEFAULT TABLESPACE users
   TEMPORARY TABLESPACE temp
   QUOTA UNLIMITED ON users;

-- Asignar permisos básicos y de creación
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE,
      CREATE TRIGGER, CREATE PROCEDURE TO nuam;
GRANT CONNECT, RESOURCE TO nuam;

-- Asegurar que la PDB se abra al iniciar la DB
ALTER PLUGGABLE DATABASE FREEPDB1 OPEN;
ALTER PLUGGABLE DATABASE FREEPDB1 SAVE STATE;

EXIT;
```

Paso 3: Verificar Conexión

- Docker (Mac/Linux):

```bash
docker exec -it oracle-db sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1
```

- Windows (nativo):

```cmd
sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1
```

Si la conexión es exitosa, ¡estás listo!

#### 5. Aplicar migraciones

> **📝 Nota:** Para una guía rápida, consulta la sección "Guía rápida de instalación" al inicio del README.

**¿Cómo funciona `migrate`?**

Django lee la configuración en `proyecto_nuam/settings.py` donde Oracle ya está configurado como base de datos por defecto.

El comando `python manage.py migrate` lee los **modelos Django** (archivos `models.py` de cada app) y genera automáticamente el DDL SQL para crear todas las tablas en la base de datos configurada. **No necesita** `cretetable_oracle` ni `MODELO.DDL` para crear tablas; Django lo hace automáticamente desde los modelos.

**Escenario 1: Esquema limpio (recomendado para desarrollo nuevo)**

```bash
python manage.py migrate            # Crea todas las tablas en Oracle
```

**Escenario 2: Ya tienes tablas creadas manualmente (por `cretetable_oracle`)**

⚠️ **ADVERTENCIA**: Si ejecutaste `cretetable_oracle` primero y luego intentas usar `migrate` directamente, obtendrás el error **`ORA-00955: este nombre ya lo está utilizando otro objeto existente`** porque Django intentará crear objetos que ya existen. **Se recomienda usar el Método 1** (crear la BD solo con `migrate`) para evitar este problema.

Si ya ejecutaste `cretetable_oracle` y las tablas ya existen, tienes dos opciones:

**Opción A: Borrar todo y empezar desde cero (⭐ Recomendado)**
```bash
# Borrar todas las tablas manualmente desde SQL*Plus
# Luego ejecutar:
python manage.py migrate
```
Esta opción te permite empezar limpio y usar solo `migrate`, evitando futuros conflictos.

**Opción B: Marcar migraciones como aplicadas (usando `--fake` por app)**
Si por alguna razón necesitas mantener las tablas existentes:
```bash
# Marcar migraciones de apps de negocio como aplicadas (las tablas ya existen)
python manage.py migrate usuarios --fake
python manage.py migrate auditoria --fake
python manage.py migrate core --fake
python manage.py migrate instrumentos --fake
python manage.py migrate corredoras --fake
python manage.py migrate calificaciones --fake
python manage.py migrate cargas --fake

# Aplicar migraciones restantes de Django (auth, sessions, etc.)
python manage.py migrate
```
Esta opción requiere que `cretetable_oracle` esté perfectamente sincronizado con los modelos Django.

**💡 Nota importante:**

- `--fake-initial` solo se usa si ya creaste tablas manualmente y quieres que Django las reconozca como "ya creadas"
- `MODELO.DDL` y `cretetable_oracle` son solo documentación/referencia. Django no los usa para crear tablas

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
python3 create_data_initial.py   # Mac/Linux (dentro de venv)
python create_data_initial.py    # Windows (dentro de venv)
```

Este script **crea automáticamente** todos los datos necesarios para empezar a trabajar:

**Catálogos base:**
- Países: Chile, Perú, Colombia, USA
- Monedas: CLP, PEN, COP, USD
- Relaciones MonedaPais (ej: CLP→Chile, USD→Chile, etc.)
- Mercados bursátiles: BCS, BVL, BVC
- Fuentes de datos: SVS, SMV, SFC
- **Fuentes de tipos de cambio**: ExchangeRate API, Fixer.io, Banco Central de Chile (inicializadas automáticamente usando `inicializar_fuentes_tipos_cambio`)

**Entidades del negocio:**
- Corredoras: Banco de Chile, Banco Santander, Credicorp Capital, BTG Pactual
- Instrumentos: ADP Bolsa, Bono Peruano
- Factores F08-F37: Los 30 factores tributarios completos

**Usuarios del sistema:**
- **admin** (contraseña: `admin123`) - Rol: Administrador
- **operador** (contraseña: `op123456`) - Rol: Operador

**Roles creados en BD (Todos Implementados):**
- **Administrador**: ✅ Implementado funcionalmente (menú + permisos)
- **Operador**: ✅ Implementado funcionalmente (menú + permisos)
- **Analista**: ✅ Implementado funcionalmente (menú + permisos)
- **Consultor**: ✅ Implementado funcionalmente (menú + permisos, solo lectura)
- **Auditor**: ✅ Implementado funcionalmente (menú + permisos, solo lectura de auditoría)

**Usuarios de ejemplo creados:**
- **admin** (contraseña: `admin123`) - Rol: Administrador ✅
- **operador** (contraseña: `op123456`) - Rol: Operador ✅
- **analista** (contraseña: `analista123`) - Rol: Analista ✅
- **consultor** (contraseña: `consultor123`) - Rol: Consultor ✅
- **auditor** (contraseña: `auditor123`) - Rol: Auditor ✅

> **💡 Uso del script:** El script usa `get_or_create()` de Django, lo que significa que es **seguro ejecutarlo múltiples veces**. Solo crea datos nuevos si no existen, evitando duplicados. Úsalo cada vez que necesites resetear la base de datos con datos de ejemplo.

> **📝 Nota importante sobre roles:** 
> - **Todos los roles** tienen menú diferenciado y permisos específicos implementados.
> - Cada rol ve solo las pestañas y funciones que tiene permitidas según su nivel de acceso.
> - Consultor y Auditor tienen acceso de solo lectura (no pueden crear, editar o eliminar calificaciones).
> - Para más detalles, consulta la sección "Sistema de Roles y Permisos" más abajo.

#### 8. Ejecutar servidor de desarrollo

##### Opción A: Servidor HTTP (por defecto)

```bash
python3 manage.py runserver   # Mac/Linux (dentro de venv)
python manage.py runserver    # Windows (dentro de venv)
```

Accede a:
- **Página principal:** http://127.0.0.1:8000/ (Inicio)
- **Mantenedor de Calificaciones:** http://127.0.0.1:8000/calificaciones/mantenedor/ (Requiere login)
- **Panel de administración:** http://127.0.0.1:8000/admin/ (Requiere login)
- **API REST:** http://127.0.0.1:8000/api/ (GET público, POST/PUT/DELETE con auth)
- **Login:** http://127.0.0.1:8000/accounts/login/

##### Opción B: Servidor HTTPS (requiere certificado - ver Paso 7)

**⚠️ IMPORTANTE:** Los certificados **NO funcionan automáticamente**. Debes usar el comando `runserver_plus` con los archivos generados. Django no detecta automáticamente los certificados.

**Prerrequisito:** Haber generado el certificado en el Paso 7 (AMBOS archivos: `server.crt` y `server.key`)

**Nota:** `django-extensions` ya está incluido en `requirements.txt` (línea 23) y se instala automáticamente al ejecutar `pip install -r requirements.txt`. Si por alguna razón no está instalado:
```bash
pip install django-extensions
```

**Ejecutar con HTTPS:**

**Opción A: Desarrollo local (recomendado)**
```bash
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443
```
Django mostrará: `Development server is running at https://127.0.0.1:8443/`

**Opción B: Acceso desde otras máquinas en la red local**
```bash
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 0.0.0.0:8443
```
Django mostrará: `Development server is running at https://0.0.0.0:8443/`
**Nota:** Aunque el servidor escucha en `0.0.0.0`, debes acceder desde el navegador usando `127.0.0.1` o `localhost`.

Accede a (ambas opciones):
- **Página principal:** https://127.0.0.1:8443/ o https://localhost:8443/ (Inicio)
- **Mantenedor de Calificaciones:** https://localhost:8443/calificaciones/mantenedor/ (Requiere login)
- **Panel de administración:** https://localhost:8443/admin/ (Requiere login)
- **API REST:** https://localhost:8443/api/ (GET público, POST/PUT/DELETE con auth)
- **Login:** https://localhost:8443/accounts/login/

**⚠️ Nota:** El navegador mostrará una advertencia de seguridad porque el certificado es autofirmado. Esto es normal en desarrollo. Hacer clic en "Avanzado" → "Continuar a localhost (no seguro)".

> Si el servidor muestra errores de conexión a Oracle (listener/BBDD caída), levántala primero:
>
> ```cmd
> lsnrctl status               # Ver estado del listener
> lsnrctl services             # Ver servicios publicados (freepdb1 READY)
> sqlplus / as sysdba          # Abrir SQL*Plus
> -- dentro de SQL*Plus
> STARTUP                      # Inicia la instancia si estaba inactiva
> ALTER PLUGGABLE DATABASE FREEPDB1 OPEN;   -- abre el PDB
> ALTER PLUGGABLE DATABASE FREEPDB1 SAVE STATE;
> EXIT;
> ```

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

### 📚 Documentación Interactiva (Swagger/OpenAPI)

La API incluye **documentación interactiva autogenerada** usando Swagger/OpenAPI:

- **Swagger UI:** http://127.0.0.1:8000/api/docs/ (interfaz interactiva)
- **ReDoc:** http://127.0.0.1:8000/api/redoc/ (documentación alternativa)
- **Schema OpenAPI:** http://127.0.0.1:8000/api/schema/ (JSON/YAML del esquema)

**Características:**
- ✅ Documentación automática de todos los endpoints
- ✅ Ejemplos de requests y responses
- ✅ Pruebas interactivas directamente desde el navegador
- ✅ Esquemas de validación
- ✅ Autenticación integrada (Session, Basic Auth)

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

### 🧪 Tests

El proyecto incluye tests unitarios y de integración usando pytest:

**Ejecutar tests:**
```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Tests específicos
pytest tests/test_api_core.py
pytest tests/test_models.py
```

**Estructura de tests:**
- `tests/test_models.py` - Tests unitarios para modelos
- `tests/test_api_core.py` - Tests de integración para APIs de Core
- `tests/test_api_usuarios.py` - Tests de integración para APIs de Usuarios
- `tests/conftest.py` - Fixtures compartidos

Ver `tests/README.md` para más detalles.

## Microservicios

El proyecto NUAM incluye varios microservicios especializados que proporcionan funcionalidades específicas a través de dashboards web interactivos. Estos microservicios están organizados en una barra de navegación secundaria visible según los permisos del usuario.

**📚 Guías relacionadas:**
- **Orden de inicio y Docker:** `Explicacion/GUIA_INICIO_PROYECTO.md` - Explica qué hace cada Docker Compose y qué microservicios necesitan Docker
- **Solución tipos de cambio:** `Explicacion/SOLUCION_TIPOS_CAMBIO.md` - Si el microservicio de tipos de cambio no muestra datos

### Tabla Descriptiva de Microservicios

| Microservicio | URL/Tipo | Descripción | Roles Permitidos | Funcionalidades Principales |
|---------------|----------|-------------|-------------------|----------------------------|
| **📊 Gráficos** | `/microservicio/graficos/`<br>(Dashboard Web) | Dashboard de visualización de métricas y estadísticas operativas del sistema | Administrador, Operador | • Estadísticas generales (calificaciones, corredoras, instrumentos)<br>• Gráficos por país, moneda, corredora<br>• KPIs operativos (tiempo de carga, errores)<br>• Cargas por corredora<br>• Exportación a CSV, Excel, PDF, HTML<br>• Filtrado por corredora (Operador ve solo su corredora) |
| **💱 Tipos de Cambio** | `/microservicio/tipos-cambio/`<br>(Dashboard Web) | Dashboard de monitoreo de tipos de cambio de monedas en tiempo real | Administrador, Analista, Operador | • Tipos de cambio actuales (CHL, PER, COL, USA)<br>• Histórico de tasas de cambio<br>• Estadísticas y tendencias<br>• Integración con APIs externas (ExchangeRate API, Fixer.io, Banco Central de Chile)<br>• Actualización automática de tasas |
| **📡 Pulsar** | `/microservicio/pulsar/`<br>(Dashboard Web) | Visualización de mensajes y estado de Apache Pulsar (sistema de mensajería asíncrona) | Administrador | • Estado de conexión con Pulsar<br>• Lista de topics y estadísticas<br>• Mensajes recientes del sistema<br>• Contador de mensajes (24H)<br>• Publicación de mensajes de prueba<br>• Interfaz estilo "holográfico/hacker" |
| **🧪 Tests** | `/microservicio/testing/`<br>(Dashboard Web) | Dashboard para ejecutar y visualizar tests desde la interfaz web | Administrador | • Ejecución de tests con pytest<br>• Visualización de resultados en tiempo real<br>• Cobertura de código<br>• Lista de tests disponibles<br>• Modo verbose<br>• Manejo de errores (especialmente Oracle) |
| **📚 Swagger API** | `/api/docs/`<br>(Dashboard Web) | Documentación interactiva de la API REST usando Swagger/OpenAPI | Administrador | • Documentación automática de todos los endpoints<br>• Pruebas interactivas desde el navegador<br>• Ejemplos de requests y responses<br>• Autenticación integrada (Session, Basic Auth)<br>• Esquemas de validación<br>• Descarga de schema OpenAPI (JSON/YAML) |
| **📄 Generador de Documentos** | `http://localhost:5001`<br>(Servicio Backend FastAPI) | Microservicio para generación de documentos en múltiples formatos (PDF, CSV, Excel) | Todos (consumido por Django) | • Generación de PDFs (comprobantes tributarios, reportes)<br>• Exportación a CSV con encoding UTF-8-BOM<br>• Exportación a Excel (.xlsx) con formato estructurado<br>• Templates HTML con Jinja2<br>• Endpoint `/health` para monitoreo<br>• Fallback automático a métodos locales si el servicio está offline<br>• Ejecuta en Docker (puerto 5001) |

### Acceso a Microservicios

Los microservicios están disponibles en la **segunda barra de navegación** (barra horizontal debajo del menú principal), visible solo para usuarios con los permisos adecuados:

- **Administrador**: Ve todos los microservicios (Gráficos, Tipos de Cambio, Pulsar, Tests, Swagger API)
- **Operador**: Ve Gráficos y Tipos de Cambio
- **Analista**: Ve Gráficos y Tipos de Cambio
- **Consultor**: No tiene acceso a microservicios
- **Auditor**: No tiene acceso a microservicios

### Características Comunes

- ✅ **Interfaz web moderna**: Dashboards con Bootstrap 5 y Chart.js
- ✅ **Control de acceso basado en roles**: Cada microservicio valida permisos antes de permitir acceso
- ✅ **Datos dinámicos**: Toda la información se carga desde la base de datos en tiempo real
- ✅ **Responsive**: Adaptados para dispositivos móviles y tablets
- ✅ **Integración con Pulsar**: Los microservicios pueden publicar eventos a Apache Pulsar para notificaciones asíncronas

### Notas Técnicas

- **Dashboards Web**: Los microservicios de visualización (Gráficos, Tipos de Cambio, Pulsar, Tests, Swagger) están implementados como vistas Django con decoradores de autenticación y control de roles
- **Servicio Backend**: El microservicio de Generación de Documentos es un servicio FastAPI independiente que se ejecuta en Docker
- **APIs Internas**: Utilizan Django REST Framework para exponer APIs internas
- **Carga de Datos**: Los datos se cargan mediante JavaScript `fetch` para una experiencia fluida
- **Exportación con Fallback**: La exportación de datos (CSV, Excel, PDF) puede usar el microservicio externo (FastAPI) con fallback automático a métodos locales si el servicio está offline

### Levantar el Microservicio de Documentos

El microservicio de Generación de Documentos se ejecuta en Docker y es opcional. Si el servicio está offline, Django automáticamente usa métodos locales para generar documentos.

**⚠️ IMPORTANTE:** Usa el `docker-compose.yml` de la **RAÍZ** para levantar todos los servicios juntos (Pulsar + docs-generator).

**Levantar los servicios de Docker (Pulsar + Documentos + Tipos de Cambio):**
```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que estén corriendo
docker ps | grep nuam-pulsar               # Broker Pulsar (mensajería)
docker ps | grep nuam-docs-generator       # Microservicio de documentos (FastAPI)
docker ps | grep nuam-exchange-rate-service # Microservicio de tipos de cambio (FastAPI, puerto 5100)
```

**Verificar salud del servicio:**
```bash
curl http://localhost:5001/health
# Debe responder: {"status": "ok", "service": "docs-generator"}
```

**Detener el servicio:**
```bash
docker-compose down
```

---

### Troubleshooting: Dashboard de Tipos de Cambio

Si no puedes ver los tipos de cambio en el dashboard, consulta las guías completas:
- 📖 `Explicacion/SOLUCION_TIPOS_CAMBIO.md` - Solución paso a paso para problemas comunes
- 📖 `microservicio/docs/TROUBLESHOOTING_TIPOS_CAMBIO.md` - Troubleshooting técnico detallado

**Problemas comunes:**
- ❌ No hay datos en la base de datos → Ejecuta: `python manage.py inicializar_fuentes_tipos_cambio` y luego `python manage.py obtener_tipos_cambio`
- ❌ No aparece el botón "Tipos de Cambio" → Verifica que tengas rol: Administrador, Analista u Operador
- ❌ Error en el dashboard → Revisa la consola del navegador (F12) para errores JavaScript

**📚 Para entender el orden correcto de inicio y qué Docker Compose usar:** Ver `Explicacion/GUIA_INICIO_PROYECTO.md`

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

**Pestañas visibles según roles:**
1. **Mantenedor**: 
   - ✅ Visible para: Administrador, Operador, Analista, Consultor, Auditor
   - 🔒 Permisos: CRUD completo (Admin, Operador, Analista) / Solo lectura (Consultor, Auditor)

2. **Cargas Masivas**: 
   - ✅ Visible para: Administrador, Operador, Analista
   - ❌ Oculto para: Consultor, Auditor

3. **Usuarios**: 
   - ✅ Visible para: Administrador únicamente
   - ❌ Oculto para: Operador, Analista, Consultor, Auditor

4. **Auditoría**: 
   - ✅ Visible para: Administrador, Auditor
   - ❌ Oculto para: Operador, Analista, Consultor

5. **Reportes**: 
   - ✅ Visible para: Todos los roles
   - 🔒 Permisos: Reportes avanzados (Analista) / Reportes estándar (otros roles)

> **💡 Nota sobre visibilidad:** Los tabs se muestran/ocultan automáticamente según el rol del usuario. Los roles **Consultor** y **Auditor** tienen acceso de solo lectura (sin botones de edición/eliminación).

### Flujo de trabajo

1. **Acceder**: Ingrese a `/calificaciones/mantenedor/` (requiere login)
2. **Buscar/Filtrar**: Use los filtros superiores para encontrar calificaciones
3. **Crear**: Click en "Ingresar" → Complete wizard 3 pasos → Guardar
4. **Modificar**: Seleccione una fila → Click en "Modificar" → Actualice datos
5. **Eliminar**: Seleccione una fila → Click en "Eliminar" → Confirmar
6. **Copiar**: Seleccione una fila → Click en "Copiar" → Edite y guarde

### Estados de Calificación

Las calificaciones tienen 4 estados posibles según el modelo de negocio:

| Estado | Descripción | Cuándo se usa |
|--------|-------------|---------------|
| **borrador** | Estado inicial al crear una calificación | **Default** - Se aplica automáticamente al crear |
| **validada** | Calificación revisada y verificada | Cambiar manualmente desde Admin o mediante flujo de validación |
| **publicada** | Calificación publicada y visible | Solo después de validar |
| **pendiente** | Calificación en revisión | Intermedio entre borrador y validada |

**⚠️ Cambiar estado:**
- Desde el **Admin de Django**: edite la calificación y modifique el campo "Estado"
- Desde el **Mantenedor**: actualmente solo crea calificaciones en estado "borrador"
- API REST: puede actualizar cualquier campo incluyendo `estado` mediante `PUT /api/calificaciones/{id}/`

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

### Exportar DDL (Estructura de Base de Datos)

El proyecto incluye scripts para exportar la estructura completa de la base de datos Oracle (tablas, índices, triggers, secuencias).

#### Scripts Disponibles

1. **`exportar_solo_tablas_oracle.sql`**: Exporta solo las definiciones de tablas (`CREATE TABLE`) con todas las restricciones incluidas.
2. **`exportar_ddl_oracle.sql`**: Exporta estructura completa (tablas, índices, triggers, secuencias).

#### Uso en Windows

##### Opción 1: Exportar solo tablas (recomendado)

```powershell
# Conectarse a Oracle y ejecutar script
sqlplus usuario/password@localhost:1521/FREEPDB1 @exportar_solo_tablas_oracle.sql

# Ejemplo con usuario NUAM
sqlplus NUAM/NUAM@localhost:1521/FREEPDB1 @exportar_solo_tablas_oracle.sql
```

**Salida:** El script genera el archivo `MODELO_SOLO_TABLAS.DDL` en el directorio actual.

##### Opción 2: Exportar estructura completa

```powershell
# Exportar todo (tablas + índices + triggers + secuencias)
sqlplus usuario/password@localhost:1521/FREEPDB1 @exportar_ddl_oracle.sql
```

**Salida:** El script genera archivos separados por tipo:
- `MODELO_TABLAS.DDL`
- `MODELO_INDICES.DDL`
- `MODELO_TRIGGERS.DDL`
- `MODELO_SECUENCIAS.DDL`

##### Opción 3: Ejecutar desde PowerShell con parámetros

```powershell
# Navegar al directorio del proyecto
cd "V:\Base de datos\django\Nuam"

# Ejecutar script SQL*Plus
$env:ORACLE_HOME = "C:\oracle\product\19.0.0\dbhome_1"  # Ajustar según tu instalación
$env:PATH = "$env:ORACLE_HOME\bin;$env:PATH"

sqlplus NUAM/NUAM@localhost:1521/FREEPDB1 @exportar_solo_tablas_oracle.sql
```

#### Uso en Linux

##### Opción 1: Exportar solo tablas (recomendado)

```bash
# Conectarse a Oracle y ejecutar script
sqlplus usuario/password@localhost:1521/FREEPDB1 @exportar_solo_tablas_oracle.sql

# Ejemplo con usuario NUAM
sqlplus NUAM/NUAM@localhost:1521/FREEPDB1 @exportar_solo_tablas_oracle.sql
```

**Salida:** El script genera el archivo `MODELO_SOLO_TABLAS.DDL` en el directorio actual.

##### Opción 2: Exportar estructura completa

```bash
# Exportar todo (tablas + índices + triggers + secuencias)
sqlplus usuario/password@localhost:1521/FREEPDB1 @exportar_ddl_oracle.sql
```

##### Opción 3: Ejecutar desde bash con configuración de entorno

```bash
# Configurar variables de entorno de Oracle (ajustar según tu instalación)
export ORACLE_HOME=/opt/oracle/product/19c/dbhome_1
export PATH=$ORACLE_HOME/bin:$PATH
export ORACLE_SID=FREEPDB1

# Navegar al directorio del proyecto
cd /ruta/al/proyecto/Nuam

# Ejecutar script
sqlplus NUAM/NUAM@localhost:1521/FREEPDB1 @exportar_solo_tablas_oracle.sql
```

#### Notas Importantes

- **Archivos generados**: Los scripts generan archivos en el directorio actual donde se ejecuta SQL*Plus.
- **Formato de salida**: Los archivos incluyen solo la estructura (DDL), NO contienen datos.
- **Renombrar archivo**: Después de exportar, puedes renombrar `MODELO_SOLO_TABLAS.DDL` a `MODELO.DDL` si prefieres mantener ese nombre.
- **Conexión**: Asegúrate de que Oracle esté corriendo y que la cadena de conexión sea correcta (`host:port/service_name`).
- **Permisos**: El usuario debe tener permisos para consultar las vistas del diccionario de datos (`user_tables`, `user_indexes`, etc.).

#### Verificar Exportación

Después de ejecutar el script, verifica que el archivo se haya generado correctamente:

```bash
# Windows (PowerShell)
Get-Content MODELO_SOLO_TABLAS.DDL | Select-Object -First 20

# Linux/Mac
head -20 MODELO_SOLO_TABLAS.DDL
```

El archivo debe comenzar con:
```sql
-- ============================================================================
-- EXPORTACIÓN DE SOLO TABLAS DE ORACLE DATABASE
-- Usuario: NUAM
-- Base de Datos: //localhost:1521/FREEPDB1
-- Fecha: ...
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

El proyecto NUAM implementa un sistema de roles para controlar el acceso a funcionalidades según el tipo de usuario.

### ⚠️ Estado Actual de Implementación

**✅ Roles Implementados Funcionalmente:**
- **Administrador**: Acceso completo con menú diferenciado ✅
- **Operador**: Acceso limitado por corredora con menú diferenciado ✅
- **Analista**: Acceso a Mantenedor, Cargas Masivas y Reportes avanzados ✅
- **Consultor**: Solo lectura de calificaciones y reportes (sin edición) ✅
- **Auditor**: Solo lectura de auditoría completa y reportes ✅

> **💡 Nota Importante:** Todos los roles ahora tienen **menú diferenciado y permisos específicos implementados**. Cada rol ve solo las pestañas y funciones que tiene permitidas según su nivel de acceso.

### Roles Implementados en MVP

#### 👑 Administrador
- **Identificación**: Usuario con `is_staff=True` o rol "Administrador"
- **Acceso**: Completo a todo el sistema
- **Menú Visible**:
  - ✅ Mantenedor (todas las calificaciones)
  - ✅ Cargas Masivas
  - ✅ **Usuarios** (tab exclusivo de Admin)
  - ✅ **Auditoría** (tab exclusivo de Admin)
  - ✅ Reportes (globales)
- **Funcionalidades**:
  - ✅ Ver todas las calificaciones (sin filtros por corredora)
  - ✅ Gestionar usuarios (crear, editar, eliminar)
  - ✅ Acceso a panel de auditoría completo
  - ✅ Reportes globales
  - ✅ Administración completa vía Django Admin
  - ✅ Configuración de catálogos (países, monedas, mercados, etc.)
  - ✅ Editar/eliminar cualquier calificación

#### 🔧 Operador
- **Identificación**: Usuario con `is_staff=False` y rol "Operador"
- **Acceso**: Limitado a su corredora asignada
- **Menú Visible**:
  - ✅ Mantenedor (solo su corredora)
  - ✅ Cargas Masivas
  - ❌ Usuarios (oculto)
  - ❌ Auditoría (oculto)
  - ✅ Reportes (locales de su corredora)
- **Funcionalidades**:
  - ✅ Ver calificaciones de su corredora (filtrado automático)
  - ✅ Crear calificaciones para su corredora
  - ✅ Editar/eliminar solo las calificaciones que él mismo creó
  - ✅ Cargas masivas (solo para su corredora)
  - ✅ Reportes locales
  - ❌ No puede gestionar usuarios
  - ❌ No puede acceder a auditoría completa (solo ve eventos de su corredora en auditoría reciente)
  - ❌ No puede ver datos de otras corredoras

#### 📊 Analista
- **Identificación**: Usuario con rol "Analista"
- **Acceso**: Limitado a sus corredoras asignadas
- **Menú Visible**:
  - ✅ Mantenedor (sus corredoras)
  - ✅ Cargas Masivas
  - ❌ Usuarios (oculto)
  - ❌ Auditoría (oculto)
  - ✅ Reportes (avanzados, con badge "Avanzado")
- **Funcionalidades**:
  - ✅ Ver calificaciones de sus corredoras (filtrado automático)
  - ✅ Crear/editar/eliminar calificaciones de sus corredoras
  - ✅ Cargas masivas (para sus corredoras)
  - ✅ Reportes avanzados (análisis de datos tributarios)
  - ✅ Análisis de datos y visualizaciones estadísticas
  - ❌ No puede gestionar usuarios
  - ❌ No puede acceder a auditoría completa

#### 📋 Consultor
- **Identificación**: Usuario con rol "Consultor"
- **Acceso**: Solo lectura de todas las corredoras asignadas
- **Menú Visible**:
  - ✅ Mantenedor (solo lectura, sin botones de edición)
  - ❌ Cargas Masivas (oculto)
  - ❌ Usuarios (oculto)
  - ❌ Auditoría (oculto)
  - ✅ Reportes (solo lectura)
- **Funcionalidades**:
  - ✅ Ver calificaciones de sus corredoras (filtrado automático)
  - ✅ Consulta de calificaciones históricas
  - ✅ Acceso a reportes en modo lectura
  - ✅ Descargar CSV de calificaciones
  - ❌ **NO puede crear, editar o eliminar calificaciones** (solo lectura)
  - ❌ No puede realizar cargas masivas
  - ❌ No puede gestionar usuarios
  - ❌ No puede acceder a auditoría completa

#### 🔍 Auditor
- **Identificación**: Usuario con rol "Auditor"
- **Acceso**: Solo lectura de auditoría completa y reportes
- **Menú Visible**:
  - ✅ Mantenedor (solo lectura, sin botones de edición)
  - ❌ Cargas Masivas (oculto)
  - ❌ Usuarios (oculto)
  - ✅ **Auditoría** (tab visible, acceso completo)
  - ✅ Reportes (solo lectura)
- **Funcionalidades**:
  - ✅ Ver calificaciones de todas las corredoras (acceso completo a auditoría)
  - ✅ Acceso de solo lectura a auditoría completa (sin filtros por corredora)
  - ✅ Revisión de cambios y transacciones
  - ✅ Reportes de cumplimiento
  - ✅ Descargar CSV de calificaciones
  - ❌ **NO puede crear, editar o eliminar calificaciones** (solo lectura)
  - ❌ No puede realizar cargas masivas
  - ❌ No puede gestionar usuarios

### Matriz de Permisos (Estado Actual)

| Funcionalidad | Administrador | Operador | Analista | Consultor | Auditor |
|---------------|---------------|----------|----------|-----------|---------|
| **Mantenedor** | ✅ Global (CRUD) | ✅ Corredora (CRUD limitado) | ✅ Corredoras (CRUD) | ✅ Solo Lectura | ✅ Solo Lectura |
| **Cargas Masivas** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Gestión Usuarios** | ✅ (Tab visible) | ❌ (Tab oculto) | ❌ (Tab oculto) | ❌ (Tab oculto) | ❌ (Tab oculto) |
| **Auditoría** | ✅ (Tab visible, completo) | ❌ (Tab oculto) | ❌ (Tab oculto) | ❌ (Tab oculto) | ✅ (Tab visible, solo lectura) |
| **Reportes** | ✅ Globales | ✅ Locales | ✅ Avanzados | ✅ Solo Lectura | ✅ Solo Lectura |
| **Django Admin** | ✅ Completo | ✅ Parcial | ✅ Parcial | ❌ | ❌ |
| **Editar Calificaciones** | ✅ Todas | ✅ Solo las creadas | ✅ Todas de su corredora | ❌ | ❌ |
| **Crear Calificaciones** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Eliminar Calificaciones** | ✅ | ✅ Solo las creadas | ✅ Todas de su corredora | ❌ | ❌ |

**Leyenda:**
- ✅ **Implementado**: Funcionalidad completa con menú diferenciado
- ❌ **No disponible**: Funcionalidad oculta o bloqueada

### Implementación Técnica

**Frontend (Templates):**
- Los tabs se muestran/ocultan según roles en `_tabs_nav.html`:
  - Mantenedor: Visible para Admin, Operador, Analista, Consultor
  - Cargas Masivas: Visible para Admin, Operador, Analista
  - Usuarios: Solo visible para Administrador
  - Auditoría: Visible para Administrador y Auditor
  - Reportes: Visible para todos los roles
- Las variables de roles (`is_administrador`, `is_operador`, `is_analista`, `is_consultor`, `is_auditor`) vienen de `calificaciones/views.py`
- Los botones de edición se ocultan para Consultor y Auditor en `_tabla.html`
- Los roles se pasan al JavaScript mediante `window.USER_ROLES` para controlar permisos en tiempo real

**Backend (API):**
- `CalificacionViewSet.get_queryset()`: Filtra por corredora si no es admin (todos los roles no-admin ven solo sus corredoras)
- `CalificacionViewSet.perform_create()`: Consultor y Auditor no pueden crear (solo lectura)
- `CalificacionViewSet.perform_update()`: Valida permisos:
  - Admin: Puede editar todas
  - Operador: Solo edita las que creó
  - Analista: Puede editar todas de su corredora
  - Consultor y Auditor: No pueden editar (solo lectura)
- `CalificacionViewSet.perform_destroy()`: Valida permisos (misma lógica que `perform_update`)
- `AuditoriaViewSet.get_queryset()`: 
  - Admin: Ve toda la auditoría
  - Auditor: Ve toda la auditoría (sin filtros)
  - Otros roles: Ven auditoría de sus corredoras

**Base de Datos:**
- Los roles se crean en `create_data_initial.py` (líneas 178-195)
- Se crean usuarios de ejemplo para todos los roles:
  - `admin` (contraseña: `admin123`) - Rol: Administrador
  - `operador` (contraseña: `op123456`) - Rol: Operador
  - `analista` (contraseña: `analista123`) - Rol: Analista
  - `consultor` (contraseña: `consultor123`) - Rol: Consultor
  - `auditor` (contraseña: `auditor123`) - Rol: Auditor
- Todos los usuarios tienen corredoras asignadas para poder ver calificaciones

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

> **⚠️ Actualización MVP**: El campo `requerido` fue agregado a la tabla `FACTOR_DEF` para marcar factores obligatorios según reglas de negocio. El campo ya está incluido en `MODELO.DDL` y `cretetable_oracle`, por lo que si recreas la base de datos desde cero, se creará automáticamente.
