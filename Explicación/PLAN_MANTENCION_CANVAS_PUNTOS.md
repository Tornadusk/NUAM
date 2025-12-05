# Plan de Mantención NUAM - Puntos para Canvas

## 🔧 ACTUALIZACIONES
- Mensual: Parches seguridad (GitHub Actions CI/CD)
- Trimestral: Features y mejoras
- Automatizado: dependabot para dependencias

## 🚀 OPTIMIZACIONES
- Caché Redis para catálogos
- Índices BD revisión trimestral
- CDN para archivos estáticos
- Revisión mensual métricas performance

## 🐛 RESOLUCIÓN DE ERRORES
- Niveles: Crítico (<1h), Alto (<4h), Medio (<24h)
- Herramientas: Sentry + Prometheus + Grafana
- Testing: 80% cobertura, CI/CD automático
- Post-mortem para errores críticos

## 📊 RECURSOS Y ROLES
- DevOps: Infraestructura, CI/CD (1 persona)
- Backend: Django, API (1-2 personas)
- DBA: Oracle, backups (0.5 persona)
- QA: Testing (0.5 persona)

## 🛠️ HERRAMIENTAS
- CI/CD: GitHub Actions
- Monitoreo: Prometheus + Grafana + Sentry
- Contenedores: Docker → Kubernetes
- BD: Backups diarios, tuning trimestral

## 🔄 MICROSERVICIOS
- Fase 1: Containerización + API Gateway
- Fase 2: Separación por dominio (Calificaciones, Auditoría, Cargas)
- Fase 3: Kubernetes + Service Mesh (Istio)

## 📈 FRECUENCIAS
- Diaria: Monitoreo 24/7, revisión logs
- Semanal: Métricas, análisis performance
- Mensual: Actualizaciones, optimizaciones
- Trimestral: Auditoría código, roadmap

## ✅ MÉTRICAS
- Disponibilidad: ≥ 99.5%
- Performance: P95 ≤ 800ms
- Errores: < 1%
- MTTR: < 30 min

## 💰 COSTOS MENSUALES
- **MVP**: USD 2,000-4,000/mes
- **Producción Básica**: USD 6,000-9,000/mes
- **Producción Completa**: USD 19,000-28,000/mes
- **Desglose**: Infraestructura (USD 135-800) + Herramientas (USD 50-400) + Recursos Humanos (USD 2,000-26,800)

