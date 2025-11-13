# Diferencia: Índices en Modelos vs Índices en Base de Datos

## 🔍 Pregunta: ¿Si los índices ya existían es porque estaban en los modelos?

**Respuesta corta:** **NO necesariamente**. Tener índices en `models.py` NO significa que automáticamente existan en Oracle.

## 📋 Explicación Detallada

### 1. Índices en `models.py` (Modelos Django)

Los índices definidos en `models.py` son **metadatos** que Django usa para:
- ✅ Optimizar queries (Django sabe qué índices deberían existir)
- ✅ Generar migraciones automáticamente
- ✅ Documentar la estructura esperada de la BD

**PERO:** Los índices en `models.py` **NO se crean automáticamente** en la BD. Necesitas ejecutar `migrate` para que Django los cree.

### 2. Índices en la Base de Datos (Oracle)

Los índices en Oracle son **objetos físicos** que:
- ✅ Mejoran el rendimiento de las queries
- ✅ Se crean mediante `CREATE INDEX` o automáticamente por Oracle
- ✅ Deben existir físicamente para que funcionen

## 🎯 ¿Por qué los Índices Ya Existían en Oracle?

Si tu compañero obtuvo `ORA-01408` usando Método 1, significa que los índices **YA EXISTÍAN** en Oracle. Esto puede pasar por:

### Opción A: Oracle los Creó Automáticamente

Oracle crea índices automáticamente para:
- ✅ Campos `UNIQUE` → Oracle crea índice único automáticamente
- ✅ Campos `PRIMARY KEY` → Oracle crea índice automáticamente
- ⚠️ Foreign Keys → **Depende de la versión/configuración de Oracle**

**Ejemplo:**
```python
# En models.py
class UsuarioRol(models.Model):
    id_usuario = models.ForeignKey(...)  # FK
    id_rol = models.ForeignKey(...)       # FK
    
    class Meta:
        unique_together = [['id_usuario', 'id_rol']]  # UNIQUE → Oracle crea índice automático
        indexes = [
            models.Index(fields=['id_rol']),  # Este índice puede no existir aún
        ]
```

Si `unique_together` crea un índice automático en `(id_usuario, id_rol)`, Oracle puede crear índices adicionales para las FKs, o puede que no.

### Opción B: Ya Ejecutó `migrate` Parcialmente

Si tu compañero ejecutó `python manage.py migrate` antes y las migraciones estaban **descomentadas**, entonces:
- ✅ Los índices se crearon en Oracle
- ✅ Las migraciones se marcaron como aplicadas
- ❌ Si luego comentas los `AddIndex` y ejecutas `migrate` nuevamente, Django intentará crear los índices otra vez → `ORA-01408`

### Opción C: Ejecutó `cretetable_oracle` Antes

Si ejecutó `cretetable_oracle` antes de `migrate`:
- ✅ Los índices ya están en Oracle (definidos en `cretetable_oracle`)
- ❌ Las migraciones intentan crearlos de nuevo → `ORA-01408`

## 📊 Flujo Normal

### Escenario 1: Primera Vez (Esquema Limpio)

```
1. Índices en models.py ✅
2. Ejecutar: python manage.py migrate
3. Django genera migraciones con AddIndex
4. Django ejecuta CREATE INDEX en Oracle
5. Índices en Oracle ✅
```

### Escenario 2: Índices Ya Existen en Oracle

```
1. Índices en models.py ✅
2. Índices en Oracle ✅ (ya existen por alguna razón)
3. Ejecutar: python manage.py migrate
4. Django intenta CREATE INDEX
5. Oracle: "Ya existe" → ORA-01408 ❌
```

## ✅ Solución Actual

He comentado los `AddIndex` en las migraciones porque:
- Los índices **YA EXISTEN** en Oracle (por alguna de las razones anteriores)
- Los índices **SÍ están** en `models.py` (Django los conoce)
- Comentar los `AddIndex` evita que Django intente crearlos de nuevo

## 🔍 Cómo Verificar

Para saber si los índices existen en Oracle:

```sql
-- Ver índices en usuario_rol
SELECT index_name, column_name, column_position
FROM user_ind_columns 
WHERE table_name = 'USUARIO_ROL' 
ORDER BY index_name, column_position;

-- Ver índices en auditoria
SELECT index_name, column_name, column_position
FROM user_ind_columns 
WHERE table_name = 'AUDITORIA' 
ORDER BY index_name, column_position;
```

## 📝 Resumen

| Situación | Índices en `models.py` | Índices en Oracle | Resultado |
|-----------|------------------------|-------------------|-----------|
| Primera vez, esquema limpio | ✅ Sí | ❌ No | ✅ Se crean con `migrate` |
| Ya ejecutó `migrate` antes | ✅ Sí | ✅ Sí | ❌ `ORA-01408` si intentas crearlos de nuevo |
| Oracle los creó automáticamente | ✅ Sí | ✅ Sí | ❌ `ORA-01408` si intentas crearlos de nuevo |
| Ejecutó `cretetable_oracle` | ✅ Sí | ✅ Sí | ❌ `ORA-01408` si intentas crearlos de nuevo |

**Conclusión:** Tener índices en `models.py` NO garantiza que existan en Oracle. Si obtienes `ORA-01408`, significa que **YA EXISTEN** en Oracle por alguna razón (automática, migración previa, o `cretetable_oracle`).

