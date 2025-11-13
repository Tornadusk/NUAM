# Generated manually to create indexes that were missed
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auditoria', '0003_alter_auditoria_valores_antes_and_more'),
    ]

    operations = [
        # IMPORTANTE: Si obtienes ORA-01408, significa que los índices ya existen en Oracle
        # (por cretable_oracle, ejecución previa de migrate, o creación automática por Oracle).
        # Solución: COMENTAR estos RunSQL para evitar ORA-01408
        # Si los índices NO existen y necesitas crearlos, descomenta estos RunSQL:
        migrations.RunSQL(
            # Crear índice solo si no existe (usando bloque PL/SQL para manejar excepciones)
            # Maneja tanto ORA-00955 (nombre ya usado) como ORA-01408 (columna ya indexada)
            sql="""
            BEGIN
                EXECUTE IMMEDIATE 'CREATE INDEX auditoria_entidad_9c3bf7_idx ON auditoria(entidad, entidad_id)';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE = -955 THEN  -- ORA-00955: name is already used by an existing object
                        NULL;  -- Índice ya existe (mismo nombre), ignorar
                    ELSIF SQLCODE = -1408 THEN  -- ORA-01408: esta lista de columnas ya está indexada
                        NULL;  -- Índice ya existe (mismas columnas, diferente nombre), ignorar
                    ELSE
                        RAISE;  -- Re-lanzar otros errores
                    END IF;
            END;
            """,
            reverse_sql="DROP INDEX auditoria_entidad_9c3bf7_idx",
        ),
        migrations.RunSQL(
            # Crear índice solo si no existe (usando bloque PL/SQL para manejar excepciones)
            # Maneja tanto ORA-00955 (nombre ya usado) como ORA-01408 (columna ya indexada)
            sql="""
            BEGIN
                EXECUTE IMMEDIATE 'CREATE INDEX auditoria_fecha_b71d64_idx ON auditoria(fecha)';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE = -955 THEN  -- ORA-00955: name is already used by an existing object
                        NULL;  -- Índice ya existe (mismo nombre), ignorar
                    ELSIF SQLCODE = -1408 THEN  -- ORA-01408: esta lista de columnas ya está indexada
                        NULL;  -- Índice ya existe (mismas columnas, diferente nombre), ignorar
                    ELSE
                        RAISE;  -- Re-lanzar otros errores
                    END IF;
            END;
            """,
            reverse_sql="DROP INDEX auditoria_fecha_b71d64_idx",
        ),
    ]

