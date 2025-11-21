------------------------------------------------------------------------------
-- Script para Exportar DDL Completo de Oracle Database
-- Genera: Tablas + Índices + Triggers + Secuencias + Constraints
--
-- USO:
--   1. Conéctate a Oracle como usuario NUAM (o el usuario propietario de los objetos)
--      sqlplus nuam/nuam_pwd@//localhost:1521/FREEPDB1
--   2. Ejecuta este script: @exportar_ddl_oracle.sql
--   3. El resultado se guardará en: MODELO_EXPORTADO.DDL
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

-- Configurar el archivo de salida
SPOOL MODELO_EXPORTADO.DDL

-- Encabezado del archivo
PROMPT -- ============================================================================
PROMPT -- EXPORTACIÓN DE DDL COMPLETO DE ORACLE DATABASE
PROMPT -- Usuario: &&_USER
PROMPT -- Base de Datos: &&_CONNECT_IDENTIFIER
PROMPT -- Fecha: 
SELECT TO_CHAR(SYSDATE, 'DD/MM/YYYY HH24:MI:SS') FROM dual;
PROMPT -- ============================================================================
PROMPT 

-- ============================================================================
-- SECCIÓN 1: SECUENCIAS (primero, porque las tablas pueden depender de ellas)
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- SECUENCIAS
PROMPT -- ============================================================================
PROMPT 

SELECT 
  '-- Secuencia: ' || sequence_name || CHR(10) ||
  CHR(10) ||
  REPLACE(
    REPLACE(
      DBMS_METADATA.GET_DDL('SEQUENCE', sequence_name),
      '"' || USER || '".',
      ''
    ),
    CHR(10) || '   ',
    CHR(10)
  ) || CHR(10) ||
  CHR(10)
FROM user_sequences 
WHERE sequence_name NOT LIKE 'BIN$%'  -- Excluir secuencias en papelera
ORDER BY sequence_name;

-- ============================================================================
-- SECCIÓN 2: TABLAS
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- TABLAS
-- ============================================================================
PROMPT 

-- Exportar DDL de todas las tablas del usuario actual
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
  CHR(10)
FROM user_tables 
WHERE table_name NOT LIKE 'BIN$%'  -- Excluir tablas en papelera
  AND table_name NOT LIKE 'DR$%'   -- Excluir tablas de índices de texto
ORDER BY table_name;

-- ============================================================================
-- SECCIÓN 3: ÍNDICES (no asociados a constraints)
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- ÍNDICES
PROMPT -- ============================================================================
PROMPT 

-- Exportar índices que NO son de constraints (PK/FK ya están en las tablas)
SELECT 
  '-- Índice: ' || ui.index_name || CHR(10) ||
  CHR(10) ||
  REPLACE(
    REPLACE(DBMS_METADATA.GET_DDL('INDEX', ui.index_name), '"' || USER || '".', ''),
    CHR(10) || '   ', CHR(10)
  ) || CHR(10) ||
  CHR(10) ||
  '-- ============================================================================' || CHR(10) ||
  CHR(10)
FROM user_indexes ui
WHERE ui.index_name NOT LIKE 'SYS_%'  -- Excluir índices del sistema
  AND ui.index_name NOT LIKE 'BIN$%'  -- Excluir índices en papelera
  AND ui.index_type != 'LOB'          -- Excluir índices LOB
  AND ui.index_type != 'DOMAIN'       -- Excluir índices de dominio
  AND ui.table_name IN (
    SELECT table_name FROM user_tables WHERE table_name NOT LIKE 'BIN$%'
  )
  AND NOT EXISTS (
    SELECT 1 
    FROM user_constraints c
    WHERE c.index_name = ui.index_name
      AND c.constraint_type IN ('P', 'R')  -- Excluir índices de PK/FK
  )
ORDER BY ui.table_name, ui.index_name;

-- ============================================================================
-- SECCIÓN 4: FOREIGN KEY CONSTRAINTS (si necesitas exportarlas por separado)
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- FOREIGN KEY CONSTRAINTS
PROMPT -- ============================================================================
PROMPT 

SELECT 
  '-- Foreign Key: ' || c.constraint_name || CHR(10) ||
  CHR(10) ||
  REPLACE(
    REPLACE(DBMS_METADATA.GET_DDL('REF_CONSTRAINT', c.constraint_name), '"' || USER || '".', ''),
    CHR(10) || '   ', CHR(10)
  ) || CHR(10) ||
  CHR(10) ||
  '-- ============================================================================' || CHR(10) ||
  CHR(10)
FROM user_constraints c
WHERE c.constraint_type = 'R'  -- Foreign Key
  AND c.constraint_name NOT LIKE 'SYS_%'
  AND c.constraint_name NOT LIKE 'BIN$%'
ORDER BY c.table_name, c.constraint_name;

-- ============================================================================
-- SECCIÓN 5: TRIGGERS
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- TRIGGERS
PROMPT -- ============================================================================
PROMPT 

SELECT 
  '-- Trigger: ' || trigger_name || CHR(10) ||
  CHR(10) ||
  REPLACE(
    REPLACE(DBMS_METADATA.GET_DDL('TRIGGER', trigger_name), '"' || USER || '".', ''),
    CHR(10) || '   ', CHR(10)
  ) || CHR(10) ||
  CHR(10) ||
  '-- ============================================================================' || CHR(10) ||
  CHR(10)
FROM user_triggers 
WHERE trigger_name NOT LIKE 'BIN$%'  -- Excluir triggers en papelera
ORDER BY trigger_name;

-- ============================================================================
-- FIN DEL EXPORT
-- ============================================================================
PROMPT -- ============================================================================
PROMPT -- Exportación completada
PROMPT -- Archivo generado: MODELO_EXPORTADO.DDL
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
PROMPT RESUMEN DE OBJETOS EXPORTADOS
PROMPT ============================================================================

SELECT 
  'Tablas' AS tipo,
  COUNT(*) AS cantidad
FROM user_tables 
WHERE table_name NOT LIKE 'BIN$%'
  AND table_name NOT LIKE 'DR$%'   -- Excluir tablas de índices de texto
UNION ALL
SELECT 
  'Índices' AS tipo,
  COUNT(*) AS cantidad
FROM user_indexes ui
WHERE ui.index_name NOT LIKE 'SYS_%' 
  AND ui.index_name NOT LIKE 'BIN$%'
  AND ui.index_type != 'LOB'          -- Excluir índices LOB
  AND ui.index_type != 'DOMAIN'       -- Excluir índices de dominio
  AND ui.table_name IN (
    SELECT table_name FROM user_tables WHERE table_name NOT LIKE 'BIN$%'
  )
  AND NOT EXISTS (
    SELECT 1 
    FROM user_constraints c
    WHERE c.index_name = ui.index_name
      AND c.constraint_type IN ('P', 'R')
  )
UNION ALL
SELECT 
  'Triggers' AS tipo,
  COUNT(*) AS cantidad
FROM user_triggers 
WHERE trigger_name NOT LIKE 'BIN$%'
UNION ALL
SELECT 
  'Secuencias' AS tipo,
  COUNT(*) AS cantidad
FROM user_sequences 
WHERE sequence_name NOT LIKE 'BIN$%'
UNION ALL
SELECT 
  'Foreign Keys' AS tipo,
  COUNT(*) AS cantidad
FROM user_constraints c
WHERE c.constraint_type = 'R'
  AND c.constraint_name NOT LIKE 'SYS_%'
  AND c.constraint_name NOT LIKE 'BIN$%'
ORDER BY tipo;

PROMPT 
PROMPT Archivo generado: MODELO_EXPORTADO.DDL
PROMPT Revisa el contenido en el archivo para ver el DDL completo.
PROMPT ============================================================================
