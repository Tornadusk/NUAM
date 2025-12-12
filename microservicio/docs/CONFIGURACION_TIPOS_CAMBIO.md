# Configuración de Tipos de Cambio desde APIs Externas

Este documento explica cómo configurar y usar el sistema de obtención automática de tipos de cambio desde APIs externas.

## Descripción

El sistema permite obtener tipos de cambio automáticamente desde múltiples fuentes con sistema de fallback. Si una fuente falla, automáticamente intenta con la siguiente según el orden de prioridad.

## Fuentes Soportadas

### 1. ExchangeRate API
- **URL**: https://www.exchangerate-api.com/
- **Plan Gratuito**: 1,500 requests/mes
- **Monedas**: Todas las principales (CLP, PEN, COP, USD, EUR, etc.)
- **Base**: Cualquier moneda
- **Ventajas**: Muy confiable, buena documentación
- **Desventajas**: Límite de requests en plan gratuito

### 2. Fixer.io
- **URL**: https://fixer.io/
- **Plan Gratuito**: 100 requests/mes
- **Monedas**: Todas las principales
- **Base**: Solo EUR en plan gratuito (se convierte automáticamente a USD)
- **Ventajas**: Buena precisión
- **Desventajas**: Plan gratuito limitado, solo EUR como base

### 3. Banco Central de Chile
- **URL**: https://si3.bcentral.cl/SieteRestWS/
- **Plan**: Gratuito
- **Monedas**: Solo CLP (USD/CLP)
- **Base**: Solo USD
- **Ventajas**: Oficial, gratuito, sin límites
- **Desventajas**: Solo para Chile

## Acceso desde la Interfaz

El dashboard de Tipos de Cambio está disponible en el menú principal de NUAM:
- **URL directa**: `/microservicio/tipos-cambio/`
- **Menú**: Enlace "Tipos de Cambio" en la barra de navegación (junto a "Gráficos" y "Pulsar")

## Configuración

### Paso 1: Crear Fuentes en el Admin

1. Accede al admin de Django: `/admin/microservicio/tipocambiofuente/`
2. Crea una nueva fuente para cada API que quieras usar:

#### ExchangeRate API:
- **Nombre**: `ExchangeRate API`
- **Código**: `EXCHANGERATE_API`
- **URL API**: `https://v6.exchangerate-api.com/v6`
- **API Key**: Tu API key de ExchangeRate API
- **Activa**: ✓ (marcado)
- **Orden Prioridad**: `1` (menor número = mayor prioridad)

#### Fixer.io:
- **Nombre**: `Fixer.io`
- **Código**: `FIXER_IO`
- **URL API**: `http://data.fixer.io/api`
- **API Key**: Tu API key de Fixer.io
- **Activa**: ✓ (marcado)
- **Orden Prioridad**: `2`

#### Banco Central de Chile:
- **Nombre**: `Banco Central de Chile`
- **Código**: `BANCO_CENTRAL_CHILE`
- **URL API**: `https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx`
- **API Key**: (dejar vacío)
- **Activa**: ✓ (marcado)
- **Orden Prioridad**: `3`

### Paso 2: Obtener API Keys

#### ExchangeRate API:
1. Ve a https://www.exchangerate-api.com/
2. Crea una cuenta gratuita
3. Obtén tu API key del dashboard
4. Copia la API key en el campo correspondiente en el admin

#### Fixer.io:
1. Ve a https://fixer.io/
2. Crea una cuenta gratuita
3. Obtén tu API key del dashboard
4. Copia la API key en el campo correspondiente en el admin

### Paso 3: Ejecutar el Comando

#### Obtener tipos de cambio manualmente:

```bash
# Obtener desde todas las fuentes activas (en orden de prioridad)
python manage.py obtener_tipos_cambio

# Obtener desde una fuente específica
python manage.py obtener_tipos_cambio --fuente EXCHANGERATE_API

# Especificar monedas específicas
python manage.py obtener_tipos_cambio --monedas CLP,PEN,COP

# Cambiar moneda base (default: USD)
python manage.py obtener_tipos_cambio --moneda-base EUR

# Forzar actualización aunque ya existan tipos de cambio para hoy
python manage.py obtener_tipos_cambio --forzar
```

#### Automatizar con Cron (Linux/Mac):

Edita el crontab:
```bash
crontab -e
```

Agrega una línea para ejecutar cada día a las 9:00 AM:
```cron
0 9 * * * cd /ruta/a/tu/proyecto && /ruta/a/venv/bin/python manage.py obtener_tipos_cambio >> /var/log/nuam_tipos_cambio.log 2>&1
```

#### Automatizar con Task Scheduler (Windows):

1. Abre "Programador de tareas"
2. Crea una tarea básica
3. Configura para ejecutar diariamente
4. Programa: `C:\ruta\a\venv\Scripts\python.exe`
5. Argumentos: `manage.py obtener_tipos_cambio`
6. Directorio de inicio: `C:\ruta\a\tu\proyecto`

#### Ejecución Automática al Iniciar Django (Opcional - No Recomendado):

Puedes habilitar la obtención automática de tipos de cambio al iniciar Django editando `proyecto_nuam/settings.py`:

```python
# En settings.py
OBTENER_TIPOS_CAMBIO_AUTOMATICO = True  # Por defecto: False
```

**⚠️ Nota**: Esta opción NO es recomendada porque:
- Puede ralentizar el inicio de Django
- Si la API está caída, retrasará el inicio de la aplicación
- Es mejor usar cron/tarea programada para ejecutar en horarios específicos

**Recomendación**: Usa cron/tarea programada en su lugar para mayor control y mejor rendimiento.

## Funcionamiento del Sistema de Fallback

1. El sistema intenta obtener tipos de cambio desde la fuente con mayor prioridad (menor número en `orden_prioridad`)
2. Si la fuente falla o no está disponible:
   - Se incrementa el contador `intentos_fallidos`
   - Se registra la fecha en `ultima_consulta_fallida`
   - Se intenta con la siguiente fuente según prioridad
3. Si una fuente tiene éxito:
   - Se resetea `intentos_fallidos` a 0
   - Se registra la fecha en `ultima_consulta_exitosa`
   - Se guardan los tipos de cambio en la base de datos
   - Se detiene el proceso (no intenta con otras fuentes)

## Monitoreo

Puedes monitorear el estado de las fuentes desde el admin:
- `/admin/microservicio/tipocambiofuente/`

Campos importantes:
- **Última Consulta Exitosa**: Fecha y hora de la última consulta exitosa
- **Última Consulta Fallida**: Fecha y hora de la última consulta fallida
- **Intentos Fallidos**: Número de intentos fallidos consecutivos

## Integración con Pulsar

Cuando se guarda un nuevo tipo de cambio, automáticamente se publica un evento en Pulsar:
- **Topic**: `persistent://public/default/nuam-tipo-cambio`
- **Datos**: `id_fuente`, `moneda_origen`, `moneda_destino`, `tasa`, `fecha`

Esto permite que otros microservicios reaccionen automáticamente a cambios en los tipos de cambio.

## Troubleshooting

### Error: "No hay fuentes activas configuradas"
- Verifica que hayas creado al menos una fuente en el admin
- Verifica que la fuente esté marcada como "Activa"

### Error: "API key no configurada"
- Verifica que hayas ingresado la API key en el campo correspondiente
- Para ExchangeRate API y Fixer.io, la API key es obligatoria

### Error: "Error al conectar con la API"
- Verifica tu conexión a internet
- Verifica que la URL de la API sea correcta
- Verifica que la API key sea válida y no haya expirado
- Revisa los logs para más detalles

### Los tipos de cambio no se actualizan
- Verifica que el comando se esté ejecutando correctamente
- Verifica los logs del comando
- Verifica que las fuentes estén activas
- Usa `--forzar` para actualizar aunque ya existan tipos de cambio para hoy

## Ejemplos de Uso

### Ejemplo 1: Configuración Básica
```bash
# Configurar ExchangeRate API como fuente principal
# En el admin, crear fuente con código EXCHANGERATE_API y prioridad 1

# Ejecutar diariamente
python manage.py obtener_tipos_cambio
```

### Ejemplo 2: Configuración con Fallback
```bash
# Configurar múltiples fuentes:
# 1. ExchangeRate API (prioridad 1)
# 2. Banco Central de Chile (prioridad 2) - solo para CLP

# El sistema intentará ExchangeRate primero, y si falla, usará Banco Central
python manage.py obtener_tipos_cambio
```

### Ejemplo 3: Solo para Chile
```bash
# Obtener solo CLP desde Banco Central de Chile
python manage.py obtener_tipos_cambio --fuente BANCO_CENTRAL_CHILE --monedas CLP
```

## Próximos Pasos

- [ ] Implementar más proveedores (Banco Central de Perú, Colombia, etc.)
- [ ] Agregar soporte para tipos de cambio históricos
- [ ] Implementar alertas cuando una fuente falla múltiples veces
- [ ] Crear dashboard de monitoreo de fuentes

