# Solución: Microservicio de Tipos de Cambio No Funciona

Esta guía explica por qué el microservicio de tipos de cambio no muestra datos y cómo solucionarlo.

## 🔍 Problema

**Síntomas:**
- El dashboard de tipos de cambio (`/microservicio/tipos-cambio/`) está vacío
- No se muestran tipos de cambio para ningún país
- El gráfico histórico no tiene datos
- Los mensajes dicen "No hay datos disponibles"

**Causa Raíz:**
El microservicio de tipos de cambio requiere que:
1. **Las fuentes estén inicializadas** en la base de datos (tabla `tipo_cambio_fuente`)
2. **Se hayan obtenido tipos de cambio** ejecutando el comando `obtener_tipos_cambio`
3. **NO requiere Docker** (es parte de Django, no un microservicio separado)

---

## ✅ Solución Paso a Paso

### Paso 1: Verificar que Django Esté Corriendo

```bash
# Asegúrate de que Django esté corriendo
python manage.py runserver
# o
python manage.py runserver_plus --cert-file Certificado/server.crt --key-file Certificado/server.key 127.0.0.1:8443
```

### Paso 2: Inicializar Fuentes de Tipos de Cambio

Este comando crea las fuentes básicas en la base de datos:
- ExchangeRate API
- Fixer.io
- Banco Central de Chile

```bash
python manage.py inicializar_fuentes_tipos_cambio
```

**Salida esperada:**
```
✓ Creada: EXCHANGERATE_API
✓ Creada: FIXER_IO
✓ Creada: BANCO_CENTRAL_CHILE

============================================================
Resumen:
  Creadas: 3
  Actualizadas: 0
  Total fuentes: 3
============================================================
IMPORTANTE:
  - Configura las API keys en el admin: /admin/microservicio/tipocambiofuente/
  - Para ExchangeRate API: https://www.exchangerate-api.com/
  - Para Fixer.io: https://fixer.io/
  - Banco Central de Chile no requiere API key

  Ejecuta: python manage.py obtener_tipos_cambio
```

### Paso 3: Obtener Tipos de Cambio

Este comando consulta las APIs externas y guarda los tipos de cambio en la base de datos.

```bash
python manage.py obtener_tipos_cambio
```

**Salida esperada:**
```
Obteniendo tipos de cambio: USD -> CLP, PEN, COP

Intentando con fuente: ExchangeRate API (EXCHANGERATE_API)...
  ✓ Guardados 3 tipos de cambio

✓ Proceso completado exitosamente
```

**Nota:** Si ExchangeRate API falla (por falta de API key o límite alcanzado), el sistema intentará automáticamente con Banco Central de Chile (que no requiere API key pero solo tiene USD/CLP).

### Paso 4: Verificar en el Dashboard

1. Accede a `/microservicio/tipos-cambio/`
2. Deberías ver:
   - Tipos de cambio actuales para cada país
   - Gráfico histórico con datos
   - Estadísticas y métricas

---

## 🔧 Configuración Opcional: API Keys

### ¿Por qué configurar API keys?

- **ExchangeRate API:** Permite obtener tipos de cambio para múltiples monedas (CLP, PEN, COP, USD, EUR, etc.)
- **Fixer.io:** Alternativa a ExchangeRate API
- **Banco Central de Chile:** No requiere API key, pero solo tiene USD/CLP

### Cómo Configurar API Keys

#### Opción 1: Desde el Admin de Django

1. Accede a `/admin/microservicio/tipocambiofuente/`
2. Edita la fuente que quieras configurar (ej: "ExchangeRate API")
3. Ingresa tu API key en el campo "API Key"
4. Guarda los cambios

#### Opción 2: Obtener API Keys Gratuitas

**ExchangeRate API:**
1. Ve a https://www.exchangerate-api.com/
2. Crea una cuenta gratuita
3. Obtén tu API key del dashboard
4. Plan gratuito: 1,500 requests/mes

**Fixer.io:**
1. Ve a https://fixer.io/
2. Crea una cuenta gratuita
3. Obtén tu API key del dashboard
4. Plan gratuito: 100 requests/mes

**Banco Central de Chile:**
- No requiere API key
- Gratuito e ilimitado
- Solo USD/CLP

---

## 🧪 Verificación

### Verificar que las Fuentes Estén Creadas

```bash
# Desde el shell de Django
python manage.py shell

# En el shell:
from microservicio.models import TipoCambioFuente
print(f"Total fuentes: {TipoCambioFuente.objects.count()}")
for fuente in TipoCambioFuente.objects.all():
    print(f"- {fuente.codigo}: {fuente.nombre} (Activa: {fuente.activa})")
```

**Salida esperada:**
```
Total fuentes: 3
- EXCHANGERATE_API: ExchangeRate API (Activa: True)
- FIXER_IO: Fixer.io (Activa: True)
- BANCO_CENTRAL_CHILE: Banco Central de Chile (Activa: True)
```

### Verificar que Haya Tipos de Cambio

```bash
# Desde el shell de Django
python manage.py shell

# En el shell:
from microservicio.models import TipoCambio
from django.utils import timezone
from datetime import timedelta

hace_24_horas = timezone.now() - timedelta(hours=24)
tipos_recientes = TipoCambio.objects.filter(creado_en__gte=hace_24_horas)
print(f"Tipos de cambio en las últimas 24 horas: {tipos_recientes.count()}")

for tipo in tipos_recientes[:5]:
    print(f"- {tipo.moneda_origen}/{tipo.moneda_destino}: {tipo.tasa} ({tipo.fecha})")
```

**Salida esperada:**
```
Tipos de cambio en las últimas 24 horas: 3
- USD/CLP: 950.50 (2024-01-15)
- USD/PEN: 3.75 (2024-01-15)
- USD/COP: 4100.00 (2024-01-15)
```

---

## 🚨 Troubleshooting

### Error: "No hay fuentes activas configuradas"

**Causa:** No se han inicializado las fuentes en la base de datos.

**Solución:**
```bash
python manage.py inicializar_fuentes_tipos_cambio
```

### Error: "API key no configurada"

**Causa:** Intentaste usar ExchangeRate API o Fixer.io sin configurar la API key.

**Solución:**
1. Configura la API key en el admin (`/admin/microservicio/tipocambiofuente/`)
2. O usa Banco Central de Chile que no requiere API key:
   ```bash
   python manage.py obtener_tipos_cambio --fuente BANCO_CENTRAL_CHILE --monedas CLP
   ```

### Error: "Error al conectar con la API"

**Causa:** Problemas de conexión a internet o API caída.

**Solución:**
1. Verifica tu conexión a internet
2. Verifica que la API esté disponible (ej: https://www.exchangerate-api.com/)
3. Intenta con otra fuente:
   ```bash
   python manage.py obtener_tipos_cambio --fuente BANCO_CENTRAL_CHILE
   ```

### Los tipos de cambio no se actualizan

**Causa:** Ya existen tipos de cambio para hoy y el sistema no los actualiza automáticamente.

**Solución:**
```bash
# Forzar actualización aunque ya existan tipos de cambio para hoy
python manage.py obtener_tipos_cambio --forzar
```

### El dashboard sigue vacío después de ejecutar los comandos

**Causa:** Puede ser un problema de caché del navegador o los datos no se guardaron correctamente.

**Solución:**
1. Verifica que los datos estén en la BD (usar el shell de Django como se muestra arriba)
2. Limpia la caché del navegador (Ctrl+Shift+R o Cmd+Shift+R)
3. Verifica los logs de Django para ver si hay errores

---

## 📋 Checklist de Solución

Usa este checklist para asegurarte de que todo esté configurado:

- [ ] Django está corriendo (`runserver` o `runserver_plus`)
- [ ] Fuentes inicializadas (`inicializar_fuentes_tipos_cambio` ejecutado)
- [ ] Tipos de cambio obtenidos (`obtener_tipos_cambio` ejecutado)
- [ ] Verificación en BD (usar shell de Django)
- [ ] Dashboard accesible (`/microservicio/tipos-cambio/`)
- [ ] Datos visibles en el dashboard

---

## 🔄 Automatización (Opcional)

### Ejecutar Automáticamente al Iniciar Django

**⚠️ NO RECOMENDADO** porque puede ralentizar el inicio de Django.

Si aún así quieres habilitarlo, edita `proyecto_nuam/settings.py`:

```python
OBTENER_TIPOS_CAMBIO_AUTOMATICO = True  # Por defecto: False
```

**Recomendación:** Usa cron/tarea programada en su lugar.

### Ejecutar con Cron (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar diariamente a las 9:00 AM
0 9 * * * cd /ruta/a/tu/proyecto && /ruta/a/venv/bin/python manage.py obtener_tipos_cambio >> /var/log/nuam_tipos_cambio.log 2>&1
```

### Ejecutar con Task Scheduler (Windows)

1. Abre "Programador de tareas"
2. Crea una tarea básica
3. Configura para ejecutar diariamente
4. Programa: `C:\ruta\a\venv\Scripts\python.exe`
5. Argumentos: `manage.py obtener_tipos_cambio`
6. Directorio de inicio: `C:\ruta\a\tu\proyecto`

---

## 📚 Referencias

- **Guía de Inicio:** `Explicacion/GUIA_INICIO_PROYECTO.md`
- **Configuración Detallada:** `microservicio/docs/CONFIGURACION_TIPOS_CAMBIO.md`
- **README Principal:** `readme.md`

---

## 💡 Resumen Rápido

```bash
# 1. Inicializar fuentes (solo la primera vez)
python manage.py inicializar_fuentes_tipos_cambio

# 2. Obtener tipos de cambio
python manage.py obtener_tipos_cambio

# 3. Verificar en el dashboard
# Accede a: http://localhost:8000/microservicio/tipos-cambio/
```

¡Listo! El microservicio de tipos de cambio debería funcionar correctamente ahora.

