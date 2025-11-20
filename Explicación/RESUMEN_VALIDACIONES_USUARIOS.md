# 📋 Resumen de Validaciones Implementadas para Usuarios

## 🎯 Alcance

Todas las validaciones se implementaron tanto en **Backend** (Django REST Framework serializers) como en **Frontend** (HTML5 + JavaScript), garantizando validación en múltiples capas de seguridad.

---

## ✅ 1. VALIDACIONES DE DATOS PERSONALES (Persona)

### 📅 **Fecha de Nacimiento** (`fecha_nacimiento`)

**Ubicación**: `api/serializers.py` - `PersonaSerializer.validate_fecha_nacimiento()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **No puede ser futura** | ✅ | ✅ | "La fecha de nacimiento no puede ser superior a la fecha actual." |
| **Edad mínima: 18 años** | ✅ | ✅ | "La fecha de nacimiento debe ser de al menos 18 años atrás." |
| **Edad máxima: 120 años** | ✅ | ❌ | "La fecha de nacimiento no puede ser anterior a 120 años." |

**Implementación Frontend**:
- HTML5: Atributo `max` dinámicamente establecido a 18 años atrás desde hoy
- JavaScript: Validación antes de enviar el formulario
- UI: Texto de ayuda visible: "Debe ser al menos 18 años atrás y no puede ser futura"

**Ejemplo**:
- ❌ `2026-12-31` → Error: No puede ser futura
- ❌ `2010-01-01` → Error: Menos de 18 años
- ✅ `2000-01-01` → Válido

---

### 📝 **Primer Nombre** (`primer_nombre`)

**Ubicación**: `api/serializers.py` - `PersonaSerializer.validate_primer_nombre()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **No puede estar vacío** | ✅ | ✅ (HTML5 `required`) | "El primer nombre no puede estar vacío." |
| **Longitud mínima: 2 caracteres** | ✅ | ❌ | "El primer nombre debe tener al menos 2 caracteres." |
| **No puede ser solo números** | ✅ | ❌ | "El primer nombre no puede ser solo números." |
| **Trim automático** | ✅ | ❌ | - |

**Ejemplo**:
- ❌ `""` → Error: No puede estar vacío
- ❌ `"a"` → Error: Menos de 2 caracteres
- ❌ `"123"` → Error: Solo números
- ✅ `"Juan"` → Válido
- ✅ `" María "` → Válido (se trimea a "María")

---

### 📝 **Segundo Nombre** (`segundo_nombre` - Opcional)

**Ubicación**: `api/serializers.py` - `PersonaSerializer.validate_segundo_nombre()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **Es opcional** | ✅ | ✅ | - |
| **Si se proporciona: mínimo 2 caracteres** | ✅ | ❌ | "El segundo nombre debe tener al menos 2 caracteres." |
| **Si se proporciona: no solo números** | ✅ | ❌ | "El segundo nombre no puede ser solo números." |

**Ejemplo**:
- ✅ `""` → Válido (opcional)
- ❌ `"1"` → Error: Menos de 2 caracteres
- ❌ `"123"` → Error: Solo números
- ✅ `"Carlos"` → Válido

---

### 📝 **Apellido Paterno** (`apellido_paterno`)

**Ubicación**: `api/serializers.py` - `PersonaSerializer.validate_apellido_paterno()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **No puede estar vacío** | ✅ | ✅ (HTML5 `required`) | "El apellido paterno no puede estar vacío." |
| **Longitud mínima: 2 caracteres** | ✅ | ❌ | "El apellido paterno debe tener al menos 2 caracteres." |
| **No puede ser solo números** | ✅ | ❌ | "El apellido paterno no puede ser solo números." |

**Ejemplo**:
- ❌ `""` → Error: No puede estar vacío
- ❌ `"1"` → Error: Menos de 2 caracteres
- ❌ `"123"` → Error: Solo números
- ✅ `"García"` → Válido

---

### 📝 **Apellido Materno** (`apellido_materno` - Opcional)

**Ubicación**: `api/serializers.py` - `PersonaSerializer.validate_apellido_materno()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **Es opcional** | ✅ | ✅ | - |
| **Si se proporciona: mínimo 2 caracteres** | ✅ | ❌ | "El apellido materno debe tener al menos 2 caracteres." |
| **Si se proporciona: no solo números** | ✅ | ❌ | "El apellido materno no puede ser solo números." |

**Ejemplo**:
- ✅ `""` → Válido (opcional)
- ❌ `"1"` → Error: Menos de 2 caracteres
- ❌ `"123"` → Error: Solo números
- ✅ `"López"` → Válido

---

### 🌍 **Nacionalidad** (`nacionalidad` - Opcional)

**Ubicación**: `api/serializers.py` - `PersonaSerializer.validate_nacionalidad()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **Es opcional** | ✅ | ✅ | - |
| **Si se proporciona: exactamente 3 caracteres** | ✅ | ❌ | "La nacionalidad debe ser un código ISO-3 de 3 caracteres (ej: CHL, PER, COL)." |
| **Si se proporciona: solo letras** | ✅ | ❌ | "La nacionalidad solo puede contener letras (código ISO-3)." |
| **Convertir a mayúsculas automáticamente** | ✅ | ❌ | - |

**Ejemplo**:
- ✅ `""` → Válido (opcional)
- ❌ `"CH"` → Error: Menos de 3 caracteres
- ❌ `"CHL1"` → Error: Más de 3 caracteres
- ❌ `"CH1"` → Error: Contiene números
- ✅ `"chl"` → Válido (se convierte a "CHL")
- ✅ `"CHL"` → Válido

---

## ✅ 2. VALIDACIONES DE DATOS DE USUARIO (Usuario)

### 👤 **Username** (`username`)

**Ubicación**: `api/serializers.py` - `UsuarioCreateSerializer.validate_username()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **No puede estar vacío** | ✅ | ✅ (HTML5 `required`) | "El username no puede estar vacío." |
| **Longitud mínima: 3 caracteres** | ✅ | ✅ | "El username debe tener al menos 3 caracteres." |
| **Longitud máxima: 60 caracteres** | ✅ | ✅ | "El username no puede tener más de 60 caracteres." |
| **Solo letras, números, guiones (-) y guiones bajos (_)** | ✅ | ✅ | "El username solo puede contener letras, números, guiones (-) y guiones bajos (_)." |
| **Trim automático** | ✅ | ✅ | - |
| **Debe ser único** | ✅ (BD) | ❌ | Error de base de datos si existe |

**Implementación Frontend**:
- HTML5: `minlength="3"`, `maxlength="60"`, `pattern="[a-zA-Z0-9_-]+"`
- JavaScript: Validación antes de enviar el formulario
- UI: Texto de ayuda visible con ejemplos

**Ejemplo**:
- ❌ `"ab"` → Error: Menos de 3 caracteres
- ❌ `"usuario@123"` → Error: Contiene caracteres no permitidos (@)
- ❌ `"usuario muy largo que supera los 60 caracteres permitidos..."` → Error: Más de 60 caracteres
- ✅ `"usuario_123"` → Válido
- ✅ `"admin-test"` → Válido

---

### 🔒 **Contraseña** (`password`)

**Ubicación**: `api/serializers.py` - `UsuarioCreateSerializer.validate_password()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **No puede estar vacía** | ✅ | ✅ (HTML5 `required`) | "La contraseña es obligatoria." |
| **Longitud mínima: 6 caracteres** | ✅ | ✅ | "La contraseña debe tener al menos 6 caracteres." |
| **Acepta cualquier combinación** | ✅ | ✅ | - |

**Nota**: Se eliminaron las validaciones que rechazaban contraseñas solo numéricas o solo letras, por lo que ahora acepta cualquier combinación siempre que tenga al menos 6 caracteres.

**Implementación Frontend**:
- HTML5: `minlength="6"` en ambos campos (contraseña y confirmación)
- JavaScript: Validación antes de enviar el formulario
- UI: Texto de ayuda visible: "Mínimo 6 caracteres"

**Ejemplo**:
- ❌ `"12345"` → Error: Menos de 6 caracteres
- ✅ `"123456"` → Válido (solo números)
- ✅ `"password"` → Válido (solo letras)
- ✅ `"pass123"` → Válido (mixto)
- ✅ `"1234567"` → Válido

---

### 🔒 **Confirmar Contraseña** (`passwordConfirm`)

**Ubicación**: `templates/static/js/mantenedor/usuarios.js` - `guardarUsuario()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **Debe coincidir con la contraseña** | ❌ | ✅ | "Las contraseñas no coinciden." |
| **Mínimo 6 caracteres** | ❌ | ✅ (HTML5 `minlength="6"`) | - |

**Implementación Frontend**:
- HTML5: `required`, `minlength="6"`
- JavaScript: Validación antes de enviar el formulario
- UI: Mensaje de error visible debajo del campo

**Ejemplo**:
- ❌ `password="123456"`, `confirm="654321"` → Error: No coinciden
- ✅ `password="123456"`, `confirm="123456"` → Válido

---

## ✅ 3. VALIDACIONES DE COLABORADOR (Opcional)

### 📧 **Email Gmail** (`gmail`)

**Ubicación**: `templates/static/js/mantenedor/usuarios.js` - `guardarUsuario()`

| Validación | Backend | Frontend | Mensaje de Error |
|------------|---------|----------|------------------|
| **Es opcional (solo si se marca como colaborador)** | ✅ | ✅ | - |
| **Si se proporciona: debe ser Gmail** | ✅ (BD) | ✅ | "El email debe ser una cuenta de Gmail válida (ej: usuario@gmail.com)" |
| **Formato: `usuario@gmail.com`** | ✅ | ✅ | - |

**Implementación Frontend**:
- HTML5: `type="email"`, `pattern="[a-zA-Z0-9._%+-]+@gmail\.com$"`
- JavaScript: Validación con regex antes de enviar
- UI: Texto de ayuda visible con ejemplo

**Ejemplo**:
- ✅ `""` → Válido (si no es colaborador)
- ❌ `"usuario@yahoo.com"` → Error: No es Gmail
- ❌ `"usuario@gmail"` → Error: Formato incorrecto
- ✅ `"usuario@gmail.com"` → Válido

---

## 🔄 4. MEJORA EN MANEJO DE ERRORES

### 📊 **Visualización de Errores**

**Ubicación**: `templates/static/js/mantenedor/usuarios.js` - `mostrarErroresValidacion()`

**Características**:
1. ✅ **Errores mostrados directamente en los campos** usando `invalid-feedback` de Bootstrap
2. ✅ **Campos con error resaltados** con clase `is-invalid` (borde rojo)
3. ✅ **Scroll automático al primer campo con error** y foco automático
4. ✅ **Mensajes de error legibles** en lugar de JSON crudo
5. ✅ **Mapeo automático** entre campos del backend y del formulario
6. ✅ **Limpieza de errores previos** antes de mostrar nuevos

**Antes**:
```
❌ Error al crear usuario: Error al crear persona: {"primer_nombre":["El primer nombre no puede ser solo números."],...}
```

**Ahora**:
1. Los campos se resaltan en rojo
2. Mensajes bajo cada campo: "El primer nombre no puede ser solo números."
3. Alerta clara:
   ```
   ❌ Error al crear persona:
   
   • Primer Nombre: El primer nombre no puede ser solo números.
   • Segundo Nombre: El segundo nombre no puede ser solo números.
   
   Por favor, corrige los errores indicados y vuelve a intentar.
   ```

---

## 📊 Resumen Tabular

| Campo | Validaciones | Backend | Frontend | Opcional |
|-------|--------------|---------|----------|----------|
| **Fecha Nacimiento** | No futura, 18-120 años | ✅ | ✅ | ❌ |
| **Primer Nombre** | Min 2 chars, no solo números | ✅ | ✅ | ❌ |
| **Segundo Nombre** | Si existe: min 2 chars, no solo números | ✅ | ❌ | ✅ |
| **Apellido Paterno** | Min 2 chars, no solo números | ✅ | ✅ | ❌ |
| **Apellido Materno** | Si existe: min 2 chars, no solo números | ✅ | ❌ | ✅ |
| **Nacionalidad** | Si existe: 3 chars, solo letras, ISO-3 | ✅ | ❌ | ✅ |
| **Username** | 3-60 chars, solo letras/números/-/_ | ✅ | ✅ | ❌ |
| **Contraseña** | Min 6 chars | ✅ | ✅ | ❌ |
| **Confirmar Contraseña** | Debe coincidir, min 6 chars | ❌ | ✅ | ❌ |
| **Email Gmail** | Si existe: formato @gmail.com | ✅ | ✅ | ✅ |

---

## 🎯 Prioridad de Validaciones

Las validaciones se ejecutan en este orden:

1. **Username** (PRIMERO)
   - Longitud mínima/máxima
   - Caracteres permitidos

2. **Contraseña** (SEGUNDO)
   - Longitud mínima

3. **Confirmar Contraseña** (TERCERO)
   - Coincidencia

4. **Fecha de Nacimiento** (CUARTO)
   - No futura
   - Edad mínima/máxima

5. **Email Gmail** (QUINTO, si aplica)
   - Formato Gmail

6. **Datos Personales** (SEXTO, en backend)
   - Nombres y apellidos
   - Nacionalidad

---

## 🔒 Seguridad

### Backend (Django)
- ✅ **Validación en serializers**: Se ejecuta SIEMPRE, incluso si se omite el frontend
- ✅ **Validación de unicidad**: `username` debe ser único (validación de BD)
- ✅ **Escape de datos**: Django automáticamente previene SQL injection

### Frontend (JavaScript)
- ✅ **Validación preventiva**: Evita enviar datos inválidos al servidor
- ✅ **Mejor UX**: Mensajes inmediatos sin esperar respuesta del servidor
- ✅ **HTML5 validation**: Validación nativa del navegador como primera capa

---

## 📝 Notas Importantes

1. **Validaciones duplicadas**: Tanto backend como frontend validan los mismos campos para seguridad en múltiples capas.

2. **Errores del backend**: Si el backend rechaza datos que pasaron el frontend, los errores se muestran de forma amigable en los campos correspondientes.

3. **Trim automático**: Los campos de texto se trimean automáticamente en el backend (eliminación de espacios iniciales y finales).

4. **Conversión automática**: La nacionalidad se convierte automáticamente a mayúsculas en el backend.

5. **Contraseñas**: Solo se valida longitud mínima (6 caracteres). Se acepta cualquier combinación de caracteres (números, letras, símbolos).

---

*Última actualización: 2025-01-14*

