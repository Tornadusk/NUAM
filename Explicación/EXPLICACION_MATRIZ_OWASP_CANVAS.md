# 📊 Explicación Matriz OWASP - Para Canvas

## ¿Qué es una Matriz OWASP?

**La Matriz OWASP es una herramienta de planificación** que nos ayuda a identificar y prevenir las **10 vulnerabilidades más críticas** en aplicaciones web (según OWASP Top 10).

**Estructura de la Matriz:**
- **Columnas**: 4 fases del desarrollo (Inicio → Durante → Fin → Verificación)
- **Filas**: Cada vulnerabilidad (A1-A10) con sus "conceptos a considerar"
- **Objetivo**: Planificar acciones de seguridad en cada etapa del proyecto

---

## 🎯 ¿Qué puntos tomamos en cuenta?

Para cada vulnerabilidad (A1-A10), analizamos:

1. **Conceptos a considerar**: ¿Qué podría salir mal?
2. **Inicio de desarrollo**: ¿Qué definimos antes de empezar?
3. **Acciones durante**: ¿Qué hacemos mientras programamos?
4. **Fin de desarrollo**: ¿Qué verificamos al terminar?
5. **Verificación**: ¿Cómo confirmamos que está protegido?

---

## 📝 Ejemplo: A1:2017 Inyección SQL

### **¿Qué es?**
Cuando un atacante inserta código SQL malicioso en los datos que envía, para robar o modificar información de la base de datos.

### **¿Cómo lo prevenimos en NUAM?**

#### **1. Inicio de desarrollo** ✅
- **Decisión**: Usar **solo Django ORM** (no SQL directo)
- **Regla**: Prohibir concatenar strings de usuario en consultas SQL

#### **2. Acciones durante el desarrollo** ✅
- **Implementación**: Todas las consultas usan ORM con parámetros:
  ```python
  # ✅ SEGURO (ORM con parámetros)
  calificaciones = Calificacion.objects.filter(id_corredora__in=user_corredoras)
  
  # ❌ INSEGURO (nunca hacemos esto)
  # query = f"SELECT * FROM calificacion WHERE id = {user_input}"
  ```
- **Validación**: Serializers de DRF validan todos los datos de entrada

#### **3. Fin de desarrollo** ✅
- **Verificación**: Revisar que no hay `cursor.execute()` con strings concatenados
- **Confirmación**: Todas las consultas pasan por el ORM de Django

#### **4. Verificación** ✅
- **Prueba**: Intentar inyección SQL en formularios → No funciona
- **Resultado**: El sistema está protegido porque Django ORM escapa automáticamente

---

## 🎨 Resumen para Canvas (Versión Ultra Breve)

### **Matriz OWASP = Plan de Seguridad**

**Estructura:**
- 10 vulnerabilidades críticas (A1-A10)
- 4 fases: Inicio → Durante → Fin → Verificación

**Ejemplo A1 (Inyección SQL):**
- **Problema**: Atacante inyecta código SQL malicioso
- **Solución NUAM**: Usar Django ORM (protección automática)
- **Resultado**: Sistema protegido contra inyección SQL

**Beneficio:**
- ✅ Prevención proactiva de vulnerabilidades
- ✅ Seguridad desde el diseño
- ✅ Cumplimiento con estándares OWASP

---

## 💡 Puntos Clave para Presentar

1. **¿Qué es?** → Herramienta de planificación de seguridad
2. **¿Para qué?** → Prevenir las 10 vulnerabilidades más críticas
3. **¿Cómo funciona?** → Analizamos cada vulnerabilidad en 4 fases
4. **Ejemplo práctico** → A1: Inyección SQL → Solución: Django ORM
5. **Resultado** → NUAM está protegido contra las amenazas OWASP Top 10

