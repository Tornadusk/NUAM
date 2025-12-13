# 🔧 Troubleshooting: Dashboard de Tipos de Cambio

## Problema: No se pueden ver los tipos de cambio en el dashboard

---

## ✅ Diagnóstico Paso a Paso

### 1. Verificar que puedes acceder al dashboard

**URL del dashboard:**
- `http://127.0.0.1:8000/microservicio/tipos-cambio/` (HTTP)
- `https://127.0.0.1:8443/microservicio/tipos-cambio/` (HTTPS)

**Si ves un error de acceso denegado:**
- Verifica que tu usuario tenga uno de estos roles: **Administrador**, **Analista** o **Operador**
- Si no tienes el rol correcto, un administrador debe asignártelo

---

### 2. Verificar que hay datos en la base de datos

```bash
# Desde la raíz del proyecto
python manage.py shell
```

En el shell de Python:
```python
from microservicio.models import TipoCambio, TipoCambioFuente

# Verificar cuántos tipos de cambio hay
print(f"Total tipos de cambio: {TipoCambio.objects.count()}")

# Verificar fuentes
print(f"Total fuentes: {TipoCambioFuente.objects.count()}")
for fuente in TipoCambioFuente.objects.all():
    print(f"  - {fuente.codigo}: {fuente.nombre} (activa: {fuente.activa})")

# Ver los tipos de cambio más recientes
recientes = TipoCambio.objects.order_by('-fecha', '-vigente_desde')[:10]
for tc in recientes:
    print(f"  {tc.moneda_origen}/{tc.moneda_destino}: {tc.tasa} ({tc.fecha})")
```

**Si no hay datos:**
- Ver sección "Cargar datos iniciales" más abajo

---

### 3. Verificar que el botón "Tipos de Cambio" aparece en la navegación

**El botón debería aparecer si tienes uno de estos roles:**
- Administrador
- Analista
- Operador

**Si NO aparece el botón:**
1. Verifica tu rol en el sistema:
   - Ve a `/admin/usuarios/usuariorol/` (si eres admin)
   - O pide a un administrador que verifique tu rol

2. Verifica que estés autenticado:
   - Debes estar logueado en NUAM
   - Ve a `/accounts/login/` si no estás autenticado

---

### 4. Verificar errores en la consola del navegador

1. Abre el dashboard de tipos de cambio
2. Abre las herramientas de desarrollador (F12 o Cmd+Option+I)
3. Ve a la pestaña **Console**
4. Busca errores en rojo

**Errores comunes:**

#### Error: `Failed to fetch` o `NetworkError`
- **Causa:** Django no está corriendo o la URL es incorrecta
- **Solución:** 
  ```bash
  # Verifica que Django esté corriendo
  python manage.py runserver
  # o
  python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443
  ```

#### Error: `401 Unauthorized` o `403 Forbidden`
- **Causa:** No estás autenticado o no tienes permisos
- **Solución:** 
  - Cierra sesión y vuelve a iniciar sesión
  - Verifica que tengas el rol correcto (Administrador, Analista u Operador)

#### Error: `null is not an object (reading 'parentElement')`
- **Causa:** Error en el código JavaScript del gráfico histórico
- **Solución:** Este error ya está corregido. Actualiza tu código:
  ```bash
  git pull
  # o actualiza el archivo templates/microservicio/tipos_cambio/dashboard.html
  ```

---

### 5. Verificar errores en el backend (logs de Django)

Mira la consola donde está corriendo Django. Busca errores cuando accedes al dashboard.

**Errores comunes:**

#### `DoesNotExist: Pais matching query does not exist`
- **Causa:** No hay países configurados en la base de datos
- **Solución:**
  ```bash
  python create_data_initial.py
  ```

#### `DatabaseError` o errores de Oracle
- **Causa:** Problemas de conexión a la base de datos
- **Solución:** Verifica que Oracle esté corriendo y que las credenciales en `settings.py` sean correctas

---

## 📥 Cargar Datos Iniciales

Si no hay tipos de cambio en la base de datos, necesitas:

### Paso 1: Inicializar fuentes de tipos de cambio

```bash
python manage.py inicializar_fuentes_tipos_cambio
```

Esto crea las fuentes:
- ExchangeRate-API (si tienes API key)
- Fixer.io (si tienes API key)
- Banco Central de Chile (público, sin API key)

### Paso 2: Obtener tipos de cambio desde APIs externas

```bash
# Obtener tipos de cambio (usa todas las fuentes activas)
python manage.py obtener_tipos_cambio

# O forzar actualización
python manage.py obtener_tipos_cambio --forzar
```

**⚠️ IMPORTANTE:** Para usar APIs externas (ExchangeRate-API, Fixer.io), necesitas:
1. Obtener una API key gratuita desde sus sitios web
2. Configurarla en la base de datos:
   ```python
   python manage.py shell
   ```
   ```python
   from microservicio.models import TipoCambioFuente
   
   # Configurar API key de ExchangeRate-API
   fuente = TipoCambioFuente.objects.get(codigo='EXCHANGERATE_API')
   fuente.api_key = 'TU_API_KEY_AQUI'
   fuente.activa = True
   fuente.save()
   ```

**Alternativa:** Si no tienes API keys, puedes insertar datos manualmente:
```python
python manage.py shell
```
```python
from microservicio.models import TipoCambio, TipoCambioFuente
from datetime import date
from decimal import Decimal

# Obtener fuente (usa Banco Central si no tienes API keys)
fuente = TipoCambioFuente.objects.filter(activa=True).first()
if not fuente:
    print("Error: No hay fuentes activas. Ejecuta: python manage.py inicializar_fuentes_tipos_cambio")
else:
    # Insertar ejemplo: USD/CLP
    TipoCambio.objects.create(
        id_fuente=fuente,
        moneda_origen='USD',
        moneda_destino='CLP',
        tasa=Decimal('950.50'),
        fecha=date.today()
    )
    print("Tipo de cambio insertado exitosamente")
```

---

## 🔍 Verificar Endpoints de la API

Puedes probar directamente los endpoints de la API:

```bash
# Si estás autenticado en el navegador, abre en una nueva pestaña:

# Todos los tipos de cambio
http://127.0.0.1:8000/microservicio/api/tipos-cambio-por-pais/

# Tipos de cambio de Chile
http://127.0.0.1:8000/microservicio/api/tipos-cambio-por-pais/CHL/

# Tipos de cambio actuales
http://127.0.0.1:8000/microservicio/api/tipos-cambio-actuales/
```

**Si estos endpoints devuelven datos pero el dashboard no:**
- Es un problema del frontend (JavaScript)
- Revisa la consola del navegador para errores

**Si estos endpoints no devuelven datos:**
- Es un problema del backend o de la base de datos
- Verifica que haya datos (paso 2)
- Verifica que la API esté funcionando

---

## 🎯 Checklist Rápido

- [ ] ¿Estás autenticado en NUAM?
- [ ] ¿Tienes uno de estos roles: Administrador, Analista u Operador?
- [ ] ¿Ves el botón "Tipos de Cambio" en la barra de navegación?
- [ ] ¿Django está corriendo?
- [ ] ¿Hay datos en la tabla `tipo_cambio`? (ver paso 2)
- [ ] ¿Hay fuentes activas? (ver paso 2)
- [ ] ¿Hay errores en la consola del navegador?
- [ ] ¿Hay errores en los logs de Django?

---

## 💡 Soluciones Comunes

### Solución 1: Recargar datos

```bash
# Desde la raíz del proyecto
python manage.py obtener_tipos_cambio --forzar
```

### Solución 2: Limpiar caché del navegador

- **Chrome/Edge:** Ctrl+Shift+Delete (Windows) o Cmd+Shift+Delete (Mac)
- O usa **Ctrl+F5** (Windows) o **Cmd+Shift+R** (Mac) para forzar recarga

### Solución 3: Verificar roles

```bash
python manage.py shell
```
```python
from usuarios.models import Usuario, UsuarioRol
from django.contrib.auth.models import User

# Verificar usuario
usuario_django = User.objects.get(username='TU_USUARIO')
usuario_nuam = Usuario.objects.get(username=usuario_django.username)
roles = UsuarioRol.objects.filter(id_usuario=usuario_nuam)
for rol in roles:
    print(f"Rol: {rol.id_rol.nombre}")
```

### Solución 4: Revisar logs completos de Django

Si hay errores, busca en la consola donde corre Django mensajes como:
- `ERROR`
- `Exception`
- `Traceback`

---

## 🆘 Si Nada Funciona

1. **Verifica que tienes la última versión del código:**
   ```bash
   git pull
   ```

2. **Verifica migraciones:**
   ```bash
   python manage.py migrate
   ```

3. **Reinicia Django:**
   - Detén el servidor (Ctrl+C)
   - Vuelve a iniciarlo

4. **Pide ayuda a un compañero:**
   - Comparte los errores de la consola del navegador
   - Comparte los logs de Django
   - Indica qué pasos ya probaste

---

## 📝 Notas Adicionales

- El dashboard muestra tipos de cambio de los **últimos 30 días**
- Si insertas datos antiguos (más de 30 días), no aparecerán en el dashboard
- El dashboard agrupa por **par de monedas** (ej: USD/CLP, USD/PEN)
- Necesitas datos de **al menos un par de monedas** para ver algo en el dashboard


