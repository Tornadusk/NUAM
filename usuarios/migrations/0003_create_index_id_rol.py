# Generated manually to create index that was missed
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_usuario_usernam_284c68_idx_and_more'),
    ]

    operations = [
        # IMPORTANTE: Si obtienes ORA-01408, significa que el índice ya existe en Oracle
        # (por cretable_oracle, ejecución previa de migrate, o creación automática por Oracle).
        # Solución: COMENTAR este RunSQL para evitar ORA-01408
        # Si el índice NO existe y necesitas crearlo, descomenta este RunSQL:
        migrations.RunSQL(
            # Crear índice solo si no existe (usando bloque PL/SQL para manejar excepciones)
            # Maneja tanto ORA-00955 (nombre ya usado) como ORA-01408 (columna ya indexada)
            sql="""
            BEGIN
                EXECUTE IMMEDIATE 'CREATE INDEX usuario_rol_id_rol_52d79a_idx ON usuario_rol(id_rol)';
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
            reverse_sql="DROP INDEX usuario_rol_id_rol_52d79a_idx",
        ),
    ]

