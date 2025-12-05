# Plan de Mantención NUAM - Canvas (Versión Breve)

## 🔧 ACTUALIZACIONES
- **Frecuencia**: Mensual (seguridad) / Trimestral (features)
- **Herramientas**: GitHub Actions CI/CD, dependabot
- **Responsable**: DevOps + Desarrolladores

## 🚀 OPTIMIZACIONES
- **Performance**: Caché Redis, índices BD trimestrales, CDN estáticos
- **Escalabilidad**: Arquitectura modular → microservicios (Docker/K8s)
- **Frecuencia**: Revisión mensual métricas

## 🐛 RESOLUCIÓN DE ERRORES
- **Niveles**: Crítico (<1h), Alto (<4h), Medio (<24h)
- **Herramientas**: Sentry, logs estructurados, Prometheus
- **Testing**: 80% cobertura, CI/CD automático

## 📊 RECURSOS Y ROLES
- **DevOps**: Infraestructura, CI/CD (1 persona)
- **Backend**: Django, API (1-2 personas)
- **DBA**: Oracle, backups (0.5 persona)
- **QA**: Testing (0.5 persona)

## 🛠️ HERRAMIENTAS
- **CI/CD**: GitHub Actions
- **Monitoreo**: Prometheus + Grafana + Sentry
- **Contenedores**: Docker → Kubernetes (microservicios)
- **BD**: Backups diarios, tuning trimestral

## 🔄 MICROSERVICIOS (Roadmap)
- **Fase 1**: Containerización + API Gateway
- **Fase 2**: Separación por dominio (Calificaciones, Auditoría, Cargas)
- **Fase 3**: Kubernetes + Service Mesh

## 📈 FRECUENCIAS
- **Diaria**: Monitoreo, logs
- **Semanal**: Métricas, performance
- **Mensual**: Actualizaciones, optimizaciones
- **Trimestral**: Auditoría código, roadmap

## ✅ MÉTRICAS DE ÉXITO
- Disponibilidad: ≥ 99.5%
- Performance: P95 ≤ 800ms
- Errores: < 1%
- MTTR: < 30 min

