"""
Script para verificar si los indices existen en Oracle
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_nuam.settings')
django.setup()

from django.db import connection

# Verificar indices en usuario_rol y auditoria
cursor = connection.cursor()

print("=" * 60)
print("VERIFICACION DE INDICES EN ORACLE")
print("=" * 60)

# Verificar indice en usuario_rol
print("\n1. Indices en USUARIO_ROL:")
cursor.execute("""
    SELECT index_name, column_name 
    FROM user_ind_columns 
    WHERE table_name = 'USUARIO_ROL' 
    AND index_name NOT LIKE 'SYS%'
    ORDER BY index_name, column_position
""")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"   [OK] {row[0]} en {row[1]}")
else:
    print("   [X] No se encontraron indices")

# Verificar indice esperado: usuario_rol_id_rol_52d79a_idx
cursor.execute("""
    SELECT COUNT(*) 
    FROM user_indexes 
    WHERE index_name = 'USUARIO_ROL_ID_ROL_52D79A_IDX'
    AND table_name = 'USUARIO_ROL'
""")
count = cursor.fetchone()[0]
if count > 0:
    print(f"   [OK] Indice usuario_rol_id_rol_52d79a_idx EXISTE (creado por migraciones)")
else:
    print(f"   [X] Indice usuario_rol_id_rol_52d79a_idx NO EXISTE (deberia crearse con migraciones)")

# Verificar indices en auditoria
print("\n2. Indices en AUDITORIA:")
cursor.execute("""
    SELECT index_name, column_name 
    FROM user_ind_columns 
    WHERE table_name = 'AUDITORIA' 
    AND index_name NOT LIKE 'SYS%'
    ORDER BY index_name, column_position
""")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"   [OK] {row[0]} en {row[1]}")
else:
    print("   [X] No se encontraron indices")

# Verificar indices esperados
expected_indices = [
    ('AUDITORIA_ENTIDAD_9C3BF7_IDX', 'entidad, entidad_id'),
    ('AUDITORIA_FECHA_B71D64_IDX', 'fecha'),
]

print("\n3. Verificacion de indices esperados (creados por migraciones):")
for index_name, columns in expected_indices:
    cursor.execute(f"""
        SELECT COUNT(*) 
        FROM user_indexes 
        WHERE index_name = '{index_name}'
        AND table_name = 'AUDITORIA'
    """)
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"   [OK] Indice {index_name} EXISTE (creado por migraciones)")
    else:
        print(f"   [X] Indice {index_name} NO EXISTE (deberia crearse con migraciones)")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("Si los indices EXISTEN -> Las migraciones funcionaron correctamente [OK]")
print("Si los indices NO EXISTEN -> Las migraciones no se ejecutaron o fallaron [X]")
print("=" * 60)
