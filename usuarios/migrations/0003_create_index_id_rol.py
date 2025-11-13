# Generated manually to create index that was missed
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_usuario_usernam_284c68_idx_and_more'),
    ]

    operations = [
        # IMPORTANTE: Si obtienes ORA-01408 o ORA-06550, significa que el índice ya existe en Oracle
        # (por cretable_oracle, ejecución previa de migrate, o creación automática por Oracle).
        # Solución: COMENTAR este RunSQL para evitar errores
        # Si el índice NO existe y necesitas crearlo, descomenta este RunSQL:
        # migrations.RunSQL(
        #     sql="CREATE INDEX usuario_rol_id_rol_52d79a_idx ON usuario_rol(id_rol)",
        #     reverse_sql="DROP INDEX usuario_rol_id_rol_52d79a_idx",
        # ),
    ]

