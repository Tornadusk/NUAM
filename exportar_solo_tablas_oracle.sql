------------------------------------------------------------------------------
-- Script para Exportar SOLO TABLAS de Oracle Database
-- Genera: Solo CREATE TABLE con todas las restricciones incluidas
--
-- USO:
--   1. Conéctate a Oracle como usuario NUAM (o el usuario propietario de los objetos)
--      sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1
--   2. Ejecuta este script: @exportar_solo_tablas_oracle.sql
--   3. El resultado se guardará en: MODELO_SOLO_TABLAS.DDL
--
-- REQUISITOS:
--   - Conexión a Oracle Database
--   - Permisos de lectura en las tablas del diccionario de datos
--   - Espacio suficiente para escribir el archivo de salida
------------------------------------------------------------------------------

-- Configurar variables de entorno SQL*Plus
SET ECHO OFF
SET FEEDBACK OFF
SET HEADING OFF
SET LINESIZE 2000
SET PAGESIZE 0
SET TRIMSPOOL ON
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET SERVEROUTPUT ON SIZE UNLIMITED

-- Configurar formato de metadata para salida más limpia
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'PRETTY', true);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', true);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', false);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', false);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'TABLESPACE', false);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'CONSTRAINTS', true);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'REF_CONSTRAINTS', true);

-- Configurar el archivo de salida
SPOOL MODELO_SOLO_TABLAS.DDL

-- Encabezado del archivo
PROMPT -- ============================================================================
PROMPT -- EXPORTACIÓN DE SOLO TABLAS DE ORACLE DATABASE
PROMPT -- Usuario: &&_USER
PROMPT -- Base de Datos: &&_CONNECT_IDENTIFIER
PROMPT -- Fecha: 
SELECT TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI:SS') FROM dual;
PROMPT -- ============================================================================
PROMPT -- NOTA: Este archivo contiene SOLO las definiciones de tablas (CREATE TABLE)
PROMPT --       con todas las restricciones, claves primarias y foráneas incluidas.
PROMPT --       NO contiene datos, solo la estructura.
PROMPT -- ============================================================================
PROMPT 

-- ============================================================================
-- TABLAS (con todas las restricciones incluidas)
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- TABLAS
-- ============================================================================
PROMPT 

-- Exportar DDL de todas las tablas del usuario actual
-- Las tablas incluyen: PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, etc.
SELECT 
  '-- Tabla: ' || table_name || CHR(10) ||
  CHR(10) ||
  REPLACE(
    REPLACE(
      DBMS_METADATA.GET_DDL('TABLE', table_name),
      '"' || USER || '".',
      ''
    ),
    CHR(10) || '   ',
    CHR(10)
  ) || CHR(10) ||
  CHR(10) ||
  '-- ============================================================================' || CHR(10) ||
  CHR(10)
FROM user_tables 
WHERE table_name NOT LIKE 'BIN$%'  -- Excluir tablas en papelera
  AND table_name NOT LIKE 'DR$%'   -- Excluir tablas de índices de texto
ORDER BY table_name;

-- ============================================================================
-- FIN DEL EXPORT
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- Exportación completada
PROMPT -- Archivo generado: MODELO_SOLO_TABLAS.DDL
PROMPT -- ============================================================================

SPOOL OFF

-- Restaurar configuración normal
SET ECHO ON
SET FEEDBACK ON
SET HEADING ON
SET SERVEROUTPUT OFF

-- Mostrar resumen
PROMPT 
PROMPT ============================================================================
PROMPT RESUMEN DE TABLAS EXPORTADAS
PROMPT ============================================================================

SELECT 
  'Tablas' AS tipo,
  COUNT(*) AS cantidad
FROM user_tables 
WHERE table_name NOT LIKE 'BIN$%'
  AND table_name NOT LIKE 'DR$%'
ORDER BY tipo;

PROMPT 
PROMPT Archivo generado: MODELO_SOLO_TABLAS.DDL
PROMPT Este archivo contiene SOLO las definiciones de tablas (CREATE TABLE)
PROMPT con todas las restricciones, claves primarias y foráneas incluidas.
PROMPT ============================================================================

