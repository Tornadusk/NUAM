#!/usr/bin/env python3
"""
Script para Exportar DDL Completo de Oracle Database
Genera: Tablas + Índices + Triggers + Secuencias + Constraints

USO:
    python exportar_ddl_python.py

REQUISITOS:
    - Oracle Instant Client instalado
    - cx_Oracle instalado: pip install cx_Oracle
    - Configuración de base de datos en settings.py o variables de entorno
"""

import os
import sys
from datetime import datetime

try:
    import cx_Oracle
except ImportError:
    print("ERROR: cx_Oracle no está instalado.")
    print("Instálalo con: pip install cx_Oracle")
    sys.exit(1)

# Configuración de conexión (ajusta según tu configuración)
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'nuam'),
    'password': os.getenv('DB_PASSWORD', 'nuam_pwd'),
    'dsn': os.getenv('DB_NAME', '127.0.0.1:1521/FREEPDB1'),
}

ARCHIVO_SALIDA = 'MODELO_EXPORTADO.DDL'


def exportar_ddl(conn, tipo_objeto, nombre_objeto):
    """Exporta el DDL de un objeto específico"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT DBMS_METADATA.GET_DDL(:tipo, :nombre) 
            FROM dual
        """, {'tipo': tipo_objeto, 'nombre': nombre_objeto})
        resultado = cursor.fetchone()
        cursor.close()
        return resultado[0] if resultado else None
    except Exception as e:
        return f"-- ERROR al exportar {tipo_objeto} {nombre_objeto}: {str(e)}\n"


def limpiar_ddl(ddl_text, usuario):
    """Limpia el DDL removiendo el esquema del usuario"""
    if not ddl_text:
        return ""
    # Remover referencias al esquema del usuario
    ddl = ddl_text.replace(f'"{usuario}".', '')
    # Normalizar espacios en blanco
    ddl = ddl.replace('\r\n', '\n')
    return ddl


def exportar_tablas(conn, usuario, archivo):
    """Exporta todas las tablas"""
    print("Exportando tablas...")
    archivo.write("\n-- ============================================================================\n")
    archivo.write("-- TABLAS\n")
    archivo.write("-- ============================================================================\n\n")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM user_tables 
        WHERE table_name NOT LIKE 'BIN$%'
        ORDER BY table_name
    """)
    
    for row in cursor:
        tabla = row[0]
        print(f"  - {tabla}")
        ddl = exportar_ddl(conn, 'TABLE', tabla)
        if ddl:
            archivo.write(f"-- Tabla: {tabla}\n\n")
            archivo.write(limpiar_ddl(ddl, usuario))
            archivo.write("\n-- ============================================================================\n\n")
    
    cursor.close()


def exportar_indices(conn, usuario, archivo):
    """Exporta todos los índices (excluyendo los de constraints)"""
    print("Exportando índices...")
    archivo.write("\n-- ============================================================================\n")
    archivo.write("-- ÍNDICES\n")
    archivo.write("-- ============================================================================\n\n")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.index_name, i.table_name
        FROM user_indexes i
        WHERE i.index_name NOT LIKE 'SYS_%'
          AND i.index_name NOT LIKE 'BIN$%'
          AND i.index_type != 'LOB'
          AND i.table_name IN (
            SELECT table_name FROM user_tables WHERE table_name NOT LIKE 'BIN$%'
          )
          AND NOT EXISTS (
            SELECT 1 
            FROM user_constraints c
            WHERE c.index_name = i.index_name
              AND c.constraint_type IN ('P', 'R')
          )
        ORDER BY i.table_name, i.index_name
    """)
    
    for row in cursor:
        indice = row[0]
        tabla = row[1]
        print(f"  - {indice} (tabla: {tabla})")
        ddl = exportar_ddl(conn, 'INDEX', indice)
        if ddl:
            archivo.write(f"-- Índice: {indice} (tabla: {tabla})\n\n")
            archivo.write(limpiar_ddl(ddl, usuario))
            archivo.write("\n-- ============================================================================\n\n")
    
    cursor.close()


def exportar_triggers(conn, usuario, archivo):
    """Exporta todos los triggers"""
    print("Exportando triggers...")
    archivo.write("\n-- ============================================================================\n")
    archivo.write("-- TRIGGERS\n")
    archivo.write("-- ============================================================================\n\n")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT trigger_name 
        FROM user_triggers 
        WHERE trigger_name NOT LIKE 'BIN$%'
        ORDER BY trigger_name
    """)
    
    for row in cursor:
        trigger = row[0]
        print(f"  - {trigger}")
        ddl = exportar_ddl(conn, 'TRIGGER', trigger)
        if ddl:
            archivo.write(f"-- Trigger: {trigger}\n\n")
            archivo.write(limpiar_ddl(ddl, usuario))
            archivo.write("\n-- ============================================================================\n\n")
    
    cursor.close()


def exportar_secuencias(conn, usuario, archivo):
    """Exporta todas las secuencias"""
    print("Exportando secuencias...")
    archivo.write("\n-- ============================================================================\n")
    archivo.write("-- SECUENCIAS\n")
    archivo.write("-- ============================================================================\n\n")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sequence_name 
        FROM user_sequences 
        WHERE sequence_name NOT LIKE 'BIN$%'
        ORDER BY sequence_name
    """)
    
    for row in cursor:
        secuencia = row[0]
        print(f"  - {secuencia}")
        ddl = exportar_ddl(conn, 'SEQUENCE', secuencia)
        if ddl:
            archivo.write(f"-- Secuencia: {secuencia}\n\n")
            archivo.write(limpiar_ddl(ddl, usuario))
            archivo.write("\n-- ============================================================================\n\n")
    
    cursor.close()


def exportar_foreign_keys(conn, usuario, archivo):
    """Exporta todas las foreign keys"""
    print("Exportando foreign keys...")
    archivo.write("\n-- ============================================================================\n")
    archivo.write("-- FOREIGN KEY CONSTRAINTS\n")
    archivo.write("-- ============================================================================\n\n")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT constraint_name, table_name
        FROM user_constraints 
        WHERE constraint_type = 'R'
          AND constraint_name NOT LIKE 'SYS_%'
          AND constraint_name NOT LIKE 'BIN$%'
        ORDER BY table_name, constraint_name
    """)
    
    for row in cursor:
        constraint = row[0]
        tabla = row[1]
        print(f"  - {constraint} (tabla: {tabla})")
        ddl = exportar_ddl(conn, 'REF_CONSTRAINT', constraint)
        if ddl:
            archivo.write(f"-- Foreign Key: {constraint} (tabla: {tabla})\n\n")
            archivo.write(limpiar_ddl(ddl, usuario))
            archivo.write("\n-- ============================================================================\n\n")
    
    cursor.close()


def mostrar_resumen(conn):
    """Muestra un resumen de los objetos exportados"""
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("RESUMEN DE OBJETOS EXPORTADOS")
    print("=" * 70)
    
    # Tablas
    cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name NOT LIKE 'BIN$%'")
    count = cursor.fetchone()[0]
    print(f"Tablas:        {count}")
    
    # Índices
    cursor.execute("""
        SELECT COUNT(*) 
        FROM user_indexes 
        WHERE index_name NOT LIKE 'SYS_%' 
          AND index_name NOT LIKE 'BIN$%'
          AND NOT EXISTS (
            SELECT 1 FROM user_constraints c
            WHERE c.index_name = user_indexes.index_name
              AND c.constraint_type IN ('P', 'R')
          )
    """)
    count = cursor.fetchone()[0]
    print(f"Índices:       {count}")
    
    # Triggers
    cursor.execute("SELECT COUNT(*) FROM user_triggers WHERE trigger_name NOT LIKE 'BIN$%'")
    count = cursor.fetchone()[0]
    print(f"Triggers:      {count}")
    
    # Secuencias
    cursor.execute("SELECT COUNT(*) FROM user_sequences WHERE sequence_name NOT LIKE 'BIN$%'")
    count = cursor.fetchone()[0]
    print(f"Secuencias:    {count}")
    
    # Foreign Keys
    cursor.execute("""
        SELECT COUNT(*) 
        FROM user_constraints 
        WHERE constraint_type = 'R'
          AND constraint_name NOT LIKE 'SYS_%'
    """)
    count = cursor.fetchone()[0]
    print(f"Foreign Keys:  {count}")
    
    print("=" * 70 + "\n")
    cursor.close()


def main():
    """Función principal"""
    print("=" * 70)
    print("EXPORTADOR DE DDL DE ORACLE DATABASE")
    print("=" * 70)
    print(f"Usuario: {DB_CONFIG['user']}")
    print(f"DSN: {DB_CONFIG['dsn']}")
    print(f"Archivo de salida: {ARCHIVO_SALIDA}")
    print("=" * 70 + "\n")
    
    try:
        # Conectar a Oracle
        print("Conectando a Oracle...")
        conn = cx_Oracle.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            dsn=DB_CONFIG['dsn']
        )
        usuario = DB_CONFIG['user'].upper()
        print(f"✓ Conectado como {usuario}\n")
        
        # Crear archivo de salida
        with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as archivo:
            # Escribir encabezado
            archivo.write("-- ============================================================================\n")
            archivo.write("-- EXPORTACIÓN DE DDL COMPLETO DE ORACLE DATABASE\n")
            archivo.write(f"-- Usuario: {usuario}\n")
            archivo.write(f"-- Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            archivo.write("-- ============================================================================\n\n")
            
            # Exportar cada tipo de objeto
            exportar_tablas(conn, usuario, archivo)
            exportar_indices(conn, usuario, archivo)
            exportar_foreign_keys(conn, usuario, archivo)
            exportar_triggers(conn, usuario, archivo)
            exportar_secuencias(conn, usuario, archivo)
            
            archivo.write("\n-- ============================================================================\n")
            archivo.write("-- Exportación completada\n")
            archivo.write(f"-- Archivo generado: {ARCHIVO_SALIDA}\n")
            archivo.write("-- ============================================================================\n")
        
        # Mostrar resumen
        mostrar_resumen(conn)
        
        # Cerrar conexión
        conn.close()
        
        print(f"✓ Exportación completada exitosamente!")
        print(f"✓ Archivo generado: {ARCHIVO_SALIDA}\n")
        
    except cx_Oracle.Error as error:
        print(f"\n✗ ERROR al conectar con Oracle:")
        print(f"  {error}\n")
        sys.exit(1)
    except Exception as error:
        print(f"\n✗ ERROR inesperado:")
        print(f"  {error}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

