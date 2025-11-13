# Generated manually to create indexes that were missed
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auditoria', '0003_alter_auditoria_valores_antes_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Crear indice en (entidad, entidad_id) directamente
            sql="CREATE INDEX auditoria_entidad_9c3bf7_idx ON auditoria(entidad, entidad_id)",
            reverse_sql="DROP INDEX auditoria_entidad_9c3bf7_idx",
        ),
        migrations.RunSQL(
            # Crear indice en fecha directamente
            sql="CREATE INDEX auditoria_fecha_b71d64_idx ON auditoria(fecha)",
            reverse_sql="DROP INDEX auditoria_fecha_b71d64_idx",
        ),
    ]

