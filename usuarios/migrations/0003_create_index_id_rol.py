# Generated manually to create index that was missed
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_usuario_usernam_284c68_idx_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Crear indice directamente (si ya existe, fallará con ORA-01408 pero lo ignoramos)
            sql="CREATE INDEX usuario_rol_id_rol_52d79a_idx ON usuario_rol(id_rol)",
            reverse_sql="DROP INDEX usuario_rol_id_rol_52d79a_idx",
            # Estado inicial: el índice no existe, pero si existe (de cretable_oracle), esta migración fallará
            # Para evitar el error, ejecuta esta migración solo si no usaste cretable_oracle
        ),
    ]

