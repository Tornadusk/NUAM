# Instalación rápida de Oracle 23c Free en Docker (Windows)

## Pasos rápidos:

### 1. Verificar Docker Desktop
Asegúrate de que Docker Desktop esté instalado y corriendo (icono en la bandeja del sistema).

Si no lo tienes: https://www.docker.com/products/docker-desktop/

### 2. Descargar imagen de Oracle (puede tardar varios minutos, ~2.5 GB)

```powershell
docker pull container-registry.oracle.com/database/free:latest
```

### 3. Iniciar el contenedor

```powershell
docker run -d -p 1521:1521 -e ORACLE_PWD=ContraseñaSegura --name oracle-db container-registry.oracle.com/database/free:latest
```

**Nota:** Cambia `ContraseñaSegura` por una contraseña robusta (será la contraseña para usuarios SYS y SYSTEM).

### 4. Verificar que está corriendo

```powershell
docker ps
```

Deberías ver el contenedor `oracle-db` en la lista con estado "Up".

### 5. Esperar a que Oracle esté listo (1-3 minutos)

```powershell
docker logs oracle-db
```

Espera hasta ver el mensaje: **"DATABASE IS READY TO USE!"** o **"The database is ready for use"**

### 6. Crear usuario NUAM

```powershell
docker exec -it oracle-db sqlplus / as sysdba
```

Dentro de SQL*Plus, ejecuta:

```sql
ALTER SESSION SET CONTAINER = FREEPDB1;

CREATE USER nuam IDENTIFIED BY nuam_pwd
   DEFAULT TABLESPACE users
   TEMPORARY TABLESPACE temp
   QUOTA UNLIMITED ON users;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE,
      CREATE TRIGGER, CREATE PROCEDURE TO nuam;
GRANT CONNECT, RESOURCE TO nuam;

ALTER PLUGGABLE DATABASE FREEPDB1 OPEN;
ALTER PLUGGABLE DATABASE FREEPDB1 SAVE STATE;

EXIT;
```

### 7. Verificar conexión

```powershell
docker exec -it oracle-db sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1
```

Si puedes conectarte, ¡estás listo! Escribe `EXIT;` para salir.

### 8. Comandos útiles

**Ver logs:**
```powershell
docker logs oracle-db
```

**Detener Oracle:**
```powershell
docker stop oracle-db
```

**Iniciar Oracle (si ya existe el contenedor):**
```powershell
docker start oracle-db
```

**Eliminar contenedor (¡cuidado, borra todos los datos!):**
```powershell
docker stop oracle-db
docker rm oracle-db
```

## ✅ Verificación rápida

Para verificar rápidamente si Oracle está funcionando:

```powershell
docker ps | findstr oracle
```

Si ves el contenedor `oracle-db` con estado "Up", está corriendo.

