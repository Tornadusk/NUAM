# 🚀 Guía de Inicio Rápido - NUAM

## ⚠️ Si no ves datos en los gráficos del dashboard

**Problema:** Los gráficos están vacíos o muestran "No hay datos disponibles"

**Solución:** Necesitas poblar la base de datos con datos de ejemplo.

---

## 📋 Pasos para tener datos en los gráficos

### 1️⃣ Verificar que las migraciones estén aplicadas

```bash
# Windows (PowerShell)
python manage.py migrate

# Mac/Linux
python3 manage.py migrate
```

Esto crea todas las tablas necesarias en la base de datos.

### 2️⃣ Ejecutar el script de datos iniciales

```bash
# Windows (PowerShell)
python create_data_initial.py

# Mac/Linux
python3 create_data_initial.py
```

Este script crea:
- ✅ 4 Países (Chile, Perú, Colombia, USA)
- ✅ 4 Monedas (CLP, PEN, COP, USD)
- ✅ 3 Mercados (BCS, BVL, BVC)
- ✅ 3 Fuentes (SVS, SMV, SFC)
- ✅ 4 Corredoras (Banco de Chile, Santander, Credicorp, BTG Pactual)
- ✅ 5 Roles (Administrador, Operador, Analista, Consultor, Auditor)
- ✅ 30 Factores (F08-F37)
- ✅ 5 Usuarios de ejemplo (admin, operador, analista, consultor, auditor)
- ✅ 4 Instrumentos de ejemplo
- ✅ **15 Calificaciones de ejemplo** (necesarias para los gráficos)
- ✅ **8 Cargas de ejemplo** (necesarias para los gráficos)
- ✅ Tipos de cambio de ejemplo

### 3️⃣ Verificar que el servidor Django esté corriendo

```bash
# Windows (PowerShell)
python manage.py runserver

# Mac/Linux
python3 manage.py runserver
```

### 4️⃣ Acceder al dashboard de gráficos

Abre en tu navegador:
- **Dashboard de gráficos:** http://127.0.0.1:8000/microservicio/graficos/
- **Login:** http://127.0.0.1:8000/accounts/login/

**Credenciales de prueba:**
- Usuario: `admin` / Contraseña: `admin123`
- Usuario: `operador` / Contraseña: `op123456`

---

## 🔍 Verificar que los datos se crearon correctamente

Puedes verificar en el admin de Django:
- **Admin:** http://127.0.0.1:8000/admin/
- Usuario: `admin` / Contraseña: `admin123`

O ejecuta en Python:

```python
python manage.py shell
```

```python
from calificaciones.models import Calificacion
from cargas.models import Carga
from corredoras.models import Corredora

print(f"Calificaciones: {Calificacion.objects.count()}")
print(f"Cargas: {Carga.objects.count()}")
print(f"Corredoras: {Corredora.objects.count()}")
```

Deberías ver:
- Calificaciones: 15
- Cargas: 8
- Corredoras: 4

---

## ⚙️ Servicios opcionales (no necesarios para los gráficos básicos)

### Apache Pulsar (Opcional - para notificaciones en tiempo real)
```bash
# Con Docker (recomendado)
docker-compose up -d pulsar

# Verificar que está corriendo
docker ps | grep pulsar
```

### Microservicio de PDF (Opcional - para generar comprobantes)
```bash
# Con Docker
docker-compose up -d docs-generator

# Verificar que está corriendo
docker ps | grep docs-generator
```

**Nota:** Estos servicios son opcionales. Los gráficos funcionan sin ellos, pero algunas funcionalidades avanzadas (como notificaciones Pulsar o generación de PDFs) no estarán disponibles.

---

## ❓ Problemas comunes

### Error: "No module named 'django'"
**Solución:** Activa el entorno virtual:
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

### Error: "ORA-00955: este nombre ya lo está utilizando otro objeto existente"
**Solución:** Las tablas ya existen. Ejecuta:
```bash
python manage.py migrate --fake-initial
```

### Los gráficos siguen vacíos después de ejecutar el script
**Solución:** 
1. Verifica que el script se ejecutó sin errores
2. Verifica que estás logueado con un usuario que tiene acceso a las corredoras
3. Si eres operador/analista, verifica que tu usuario tenga una corredora asignada
4. Recarga la página (Ctrl+F5 o Cmd+Shift+R)

---

## 📞 ¿Necesitas ayuda?

Si después de seguir estos pasos los gráficos siguen sin mostrar datos, verifica:
1. ✅ Las migraciones se aplicaron correctamente
2. ✅ El script `create_data_initial.py` se ejecutó sin errores
3. ✅ Estás logueado con un usuario válido
4. ✅ El servidor Django está corriendo
5. ✅ La base de datos está configurada correctamente en `settings.py`

