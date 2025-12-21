# Cambio: Botón "Actualizar desde APIs" ahora usa --forzar

## Cambio Realizado

El botón **"Actualizar desde APIs"** en el dashboard ahora ejecuta automáticamente con `--forzar`.

---

## ¿Por qué este cambio?

### Antes (comportamiento antiguo):

```javascript
forzar: false  // No forzaba actualización
```

**Problema**: Si ya había datos para hoy, mostraba el mensaje "No se guardaron nuevos tipos de cambio (ya existían)" y no actualizaba nada.

**Experiencia del usuario**: Hace clic en "Actualizar" → No pasa nada (confuso)

---

### Ahora (comportamiento nuevo):

```javascript
forzar: true  // Fuerza actualización
```

**Ventaja**: Siempre actualiza los datos cuando el usuario hace clic en "Actualizar", incluso si ya existen.

**Experiencia del usuario**: Hace clic en "Actualizar" → Los datos se actualizan (esperado)

---

## Comparación

| Acción | Antes | Ahora |
|--------|-------|-------|
| **Clic en "Actualizar desde APIs"** | `forzar: false` → Puede que no actualice | `forzar: true` → Siempre actualiza ✅ |
| **Comando manual** | `python manage.py obtener_tipos_cambio` → No actualiza si existen | `python manage.py obtener_tipos_cambio --forzar` → Siempre actualiza |

---

## Razón del Cambio

Cuando un usuario hace clic en un botón que dice **"Actualizar desde APIs"**, espera que los datos se actualicen, no que le digan "ya existen".

Es el comportamiento esperado e intuitivo.

---

## Código Modificado

**Archivo:** `templates/static/js/microservicio/tipos_cambio.js`

**Línea 434:**
```javascript
// Antes:
forzar: false

// Ahora:
forzar: true  // Forzar actualización cuando el usuario hace clic en "Actualizar"
```

---

## Impacto

✅ **Positivo**: Los usuarios obtienen datos actualizados cuando hacen clic en "Actualizar"  
✅ **Esperado**: Comportamiento más intuitivo  
⚠️ **Nota**: Puede crear más registros en la BD (pero eso es normal con `update_or_create`)

---

## Resumen

**Pregunta del usuario:** "Al poner actualizar, no sería bueno que se ejecutara `--forzar`?"

**Respuesta:** ✅ **Sí, tienes razón.** El cambio ya está aplicado.

Ahora cuando hagas clic en **"Actualizar desde APIs"**, se ejecutará automáticamente con `--forzar`, actualizando los datos incluso si ya existen para hoy.



