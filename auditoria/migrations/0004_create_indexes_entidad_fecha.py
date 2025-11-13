# Generated manually to create indexes that were missed
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auditoria', '0003_alter_auditoria_valores_antes_and_more'),
    ]

    operations = [
        # IMPORTANTE: Si obtienes ORA-01408 o ORA-06550, significa que los índices ya existen en Oracle
        # (por cretable_oracle, ejecución previa de migrate, o creación automática por Oracle).
        # Solución: COMENTAR estos RunSQL para evitar errores
        # Si los índices NO existen y necesitas crearlos, descomenta estos RunSQL:
        # migrations.RunSQL(
        #     sql="CREATE INDEX auditoria_entidad_9c3bf7_idx ON auditoria(entidad, entidad_id)",
        #     reverse_sql="DROP INDEX auditoria_entidad_9c3bf7_idx",
        # ),
        # migrations.RunSQL(
        #     sql="CREATE INDEX auditoria_fecha_b71d64_idx ON auditoria(fecha)",
        #     reverse_sql="DROP INDEX auditoria_fecha_b71d64_idx",
        # ),
    ]

