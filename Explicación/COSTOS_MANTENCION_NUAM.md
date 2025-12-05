# Costos de Mantención NUAM

## 💰 RESUMEN EJECUTIVO

### **Costo Mensual Estimado (Producción Básica)**
- **Infraestructura**: USD 135-240/mes
- **Herramientas/Servicios**: USD 50-250/mes
- **Recursos Humanos**: USD 8,000-12,000/mes
- **TOTAL MENSUAL**: USD 8,185-12,490/mes
- **TOTAL ANUAL**: USD 98,220-149,880/año

---

## 🖥️ COSTOS DE INFRAESTRUCTURA

### **Servidores**
| Componente | MVP (Bajo Costo) | Producción Básica | Costo Mensual |
|------------|------------------|-------------------|---------------|
| **Servidor App/Web** | 1 VM única (App+DB) | 2 VMs separadas (4 vCPU, 8-16 GB RAM, 100-200 GB SSD) | USD 120-200 |
| **Servidor BD** | Incluido en VM única | VM dedicada (8 vCPU, 16-32 GB RAM, 500 GB SSD) | USD 200-400 |
| **Oracle License** | Oracle XE (Free) | Oracle Standard/Enterprise | Según licencia |
| **Almacenamiento Backups** | NAS interno | Storage DC (retención ≥30 días) | USD 15-40 |
| **Dominio + SSL** | Let's Encrypt (Free) | Dominio público + SSL gestionado | USD 1-9/mes |

**Subtotal Infraestructura**: USD 135-240/mes (sin licencia Oracle)

---

## 🛠️ COSTOS DE HERRAMIENTAS Y SERVICIOS

### **Desarrollo y CI/CD**
| Herramienta | MVP | Producción | Costo Mensual |
|-------------|-----|------------|---------------|
| **CI/CD** | GitHub/GitLab Free | Pipeline completo con artefactos | USD 0-50 |
| **Testing Tools** | pytest (OSS) | pytest + coverage.py | USD 0 |
| **Linting** | flake8, black (OSS) | flake8, black, bandit | USD 0 |
| **Documentación** | Markdown | Swagger/OpenAPI SaaS | USD 0-20 |

### **Monitoreo y Observabilidad**
| Herramienta | MVP | Producción | Costo Mensual |
|-------------|-----|------------|---------------|
| **Monitoreo** | Logs básicos | Prometheus + Grafana (self-hosted) | USD 0 |
| **Error Tracking** | Logs locales | Sentry (SaaS) | USD 0-26 (Free tier) |
| **Logs Centralizados** | Rotación básica | ELK Stack / Graylog SaaS | USD 0-50 |
| **Alertas** | Email básico | PagerDuty / Opsgenie | USD 0-29 |

### **Seguridad**
| Herramienta | MVP | Producción | Costo Mensual |
|-------------|-----|-----------|---------------|
| **SAST/DAST** | Bandit + OWASP ZAP (OSS) | ZAP completo + WAF | USD 0-200 |
| **Firewall App** | Nginx básico | WAF dedicado | USD 50-200 |
| **SSL/TLS** | Let's Encrypt | Certificado gestionado | USD 0-7/mes |

### **Caché y Performance**
| Herramienta | MVP | Producción | Costo Mensual |
|-------------|-----|-----------|---------------|
| **Redis** | Local | Redis Cloud / AWS ElastiCache | USD 0-30 |
| **CDN** | Sin CDN | CloudFlare / AWS CloudFront | USD 0-20 |

**Subtotal Herramientas**: USD 50-250/mes

---

## 👥 COSTOS DE RECURSOS HUMANOS

### **Equipo de Mantención (Tiempo Completo)**
| Rol | Horas/Mes | Tarifa USD/hora | Costo Mensual |
|-----|-----------|-----------------|---------------|
| **DevOps Engineer** | 160 horas (1 FTE) | USD 40-60 | USD 6,400-9,600 |
| **Backend Developer** | 160 horas (1 FTE) | USD 35-50 | USD 5,600-8,000 |
| **DBA Oracle** | 80 horas (0.5 FTE) | USD 50-70 | USD 4,000-5,600 |
| **QA Engineer** | 80 horas (0.5 FTE) | USD 30-45 | USD 2,400-3,600 |

**Subtotal Recursos Humanos**: USD 18,400-26,800/mes

### **Equipo de Mantención (Tiempo Parcial - Escenario Realista)**
| Rol | Horas/Mes | Tarifa USD/hora | Costo Mensual |
|-----|-----------|-----------------|---------------|
| **DevOps** | 40 horas (0.25 FTE) | USD 40-60 | USD 1,600-2,400 |
| **Backend Developer** | 80 horas (0.5 FTE) | USD 35-50 | USD 2,800-4,000 |
| **DBA Oracle** | 20 horas (0.125 FTE) | USD 50-70 | USD 1,000-1,400 |
| **QA Engineer** | 20 horas (0.125 FTE) | USD 30-45 | USD 600-900 |

**Subtotal Recursos Humanos (Parcial)**: USD 6,000-8,700/mes

---

## 📊 DESGLOSE POR CATEGORÍA

### **Costos Fijos Mensuales**
- Infraestructura: USD 135-240
- Herramientas básicas: USD 50-100
- **Subtotal Fijos**: USD 185-340/mes

### **Costos Variables**
- Herramientas avanzadas: USD 0-150
- Escalamiento infraestructura: Según uso
- Incidentes/emergencias: USD 0-500 (esporádico)

### **Costos de Recursos Humanos**
- Escenario completo: USD 18,400-26,800/mes
- Escenario parcial: USD 6,000-8,700/mes

---

## 💵 ESCENARIOS DE COSTO

### **Escenario 1: MVP / Desarrollo (Bajo Costo)**
- Infraestructura: USD 0-50/mes (Oracle XE local)
- Herramientas: USD 0/mes (OSS)
- Recursos Humanos: USD 2,000-4,000/mes (tiempo parcial)
- **TOTAL**: USD 2,000-4,050/mes

### **Escenario 2: Producción Básica (Recomendado)**
- Infraestructura: USD 135-240/mes
- Herramientas: USD 50-150/mes
- Recursos Humanos: USD 6,000-8,700/mes (tiempo parcial)
- **TOTAL**: USD 6,185-9,090/mes
- **ANUAL**: USD 74,220-109,080/año

### **Escenario 3: Producción Completa (Alta Disponibilidad)**
- Infraestructura: USD 400-800/mes (con redundancia)
- Herramientas: USD 200-400/mes
- Recursos Humanos: USD 18,400-26,800/mes (tiempo completo)
- **TOTAL**: USD 19,000-28,000/mes
- **ANUAL**: USD 228,000-336,000/año

---

## 📈 COSTOS ADICIONALES (Ocasionales)

### **Migración a Microservicios**
- Arquitectura y diseño: USD 5,000-10,000 (una vez)
- Desarrollo: USD 15,000-30,000 (3-6 meses)
- Infraestructura Kubernetes: USD 200-500/mes adicionales
- **TOTAL Inicial**: USD 20,000-40,000

### **Auditorías y Compliance**
- Auditoría seguridad anual: USD 3,000-8,000
- Penetration testing: USD 2,000-5,000
- Compliance ISO 27001: USD 5,000-15,000 (certificación inicial)

### **Capacitación**
- Capacitación equipo: USD 1,000-3,000/año
- Certificaciones: USD 500-2,000/persona/año

---

## 🎯 OPTIMIZACIÓN DE COSTOS

### **Recomendaciones**
1. **Empezar con MVP**: Usar herramientas OSS y Oracle XE
2. **Escalar gradualmente**: Aumentar recursos según necesidad real
3. **Automatización**: Reducir tiempo manual con CI/CD
4. **Monitoreo proactivo**: Detectar problemas antes que escalen
5. **Contratos anuales**: Descuentos en infraestructura (10-20%)

### **Ahorros Potenciales**
- Infraestructura anual: -10% a -20%
- Herramientas SaaS: -15% a -25% (planes anuales)
- Recursos humanos: Optimización con automatización (-20% tiempo)

---

## 📋 RESUMEN PARA CANVAS

### **Costo Mensual Estimado**
- **MVP**: USD 2,000-4,000/mes
- **Producción Básica**: USD 6,000-9,000/mes
- **Producción Completa**: USD 19,000-28,000/mes

### **Desglose Rápido**
- Infraestructura: USD 135-800/mes
- Herramientas: USD 50-400/mes
- Recursos Humanos: USD 2,000-26,800/mes

### **Costo Anual Estimado**
- **Producción Básica**: USD 74,000-109,000/año
- **Producción Completa**: USD 228,000-336,000/año

---

**Nota**: Los costos son estimativos y pueden variar según:
- Región geográfica
- Proveedor de servicios cloud
- Modelo de licenciamiento Oracle
- Nivel de experiencia del equipo
- Volumen de datos y tráfico

