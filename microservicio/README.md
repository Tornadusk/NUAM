# Microservicios NUAM

Este módulo contiene los microservicios del sistema NUAM.

## Estructura

### 1. Microservicio de Gráficos/Métricas
**Ubicación:** `microservicio/views.py`

Este microservicio expone datos agregados de la base de datos para visualización mediante gráficos.

#### Endpoints disponibles:
- `GET /microservicio/api/estadisticas-generales/` - Estadísticas generales del sistema
- `GET /microservicio/api/calificaciones-por-pais/` - Calificaciones agrupadas por país
- `GET /microservicio/api/calificaciones-por-moneda/` - Calificaciones agrupadas por moneda
- `GET /microservicio/api/actividad-reciente/` - Actividad de los últimos 30 días

#### Vista de gráficos:
- `GET /microservicio/graficos/` - Dashboard de gráficos interactivos

#### Características:
- Respeta Row-Level Security (RLS) según el rol del usuario
- Operadores solo ven datos de su corredora asignada
- Administradores ven todos los datos
- Usa Chart.js para visualización interactiva

### 2. Microservicio de Tipos de Cambio (En desarrollo)
**Ubicación:** `microservicio/models.py` (TipoCambioFuente, TipoCambio)

Este microservicio gestionará múltiples fuentes de tipos de cambio con sistema de respaldo.

#### Modelos:
- **TipoCambioFuente**: Tabla para gestionar múltiples fuentes de tipos de cambio
  - Soporta múltiples APIs (ExchangeRate, Banco Central, etc.)
  - Sistema de prioridades y fallback automático
  - Tracking de éxito/fallo de consultas
  
- **TipoCambio**: Almacena los tipos de cambio obtenidos
  - Relación con fuente
  - Soporte para múltiples pares de monedas
  - Historial temporal

#### Características planificadas:
- Consumo de APIs externas gratuitas (ExchangeRate API, Fixer.io, etc.)
- Sistema de respaldo automático si una fuente falla
- Caché de tipos de cambio
- Integración con Pulsar para notificaciones de cambios

### 3. Microservicio de Enriquecimiento de Cargas (Futuro)
Este microservicio consumirá mensajes de Pulsar cuando se complete una carga masiva y:
- Consultará el microservicio de tipos de cambio
- Aplicará reglas de negocio para convertir montos
- Publicará resultados de vuelta a Pulsar

## Instalación

1. Asegúrate de que el microservicio está registrado en `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'microservicio',
]
```

2. Ejecuta las migraciones:
```bash
python manage.py makemigrations microservicio
python manage.py migrate
```

3. Accede a los gráficos desde el menú principal o directamente en `/microservicio/graficos/`

## Próximos pasos

- [ ] Implementar consumidor de tipos de cambio desde APIs externas
- [ ] Integrar Apache Pulsar para eventos asíncronos
- [ ] Implementar microservicio de enriquecimiento de cargas
- [ ] Agregar más gráficos y métricas personalizadas
- [ ] Implementar caché para mejorar rendimiento


