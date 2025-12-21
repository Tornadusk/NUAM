# Arquitectura de Exportación de Bolsa

## ✅ Confirmación: Es un Microservicio Externo (No Monolito)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                          DJANGO (Monolito)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Vista: api_exportar_grafico()                           │  │
│  │  (microservicio/views/graficos.py)                       │  │
│  │                                                           │  │
│  │  1. Recibe petición: /exportar/bolsa/pdf/               │  │
│  │  2. Llama a: exportar_mercados()                        │  │
│  │     (microservicio/services/market_info_client.py)      │  │
│  │  3. Hace HTTP POST → http://localhost:5200/exportar/pdf │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST (JSON)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              MARKET-INFO-SERVICE (Microservicio FastAPI)        │
│                    🐳 Docker: nuam-market-info-service         │
│                     Puerto: 5200                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Endpoint: POST /exportar/{formato}                      │  │
│  │  (services/market-info-service/main.py)                  │  │
│  │                                                           │  │
│  │  1. Recibe datos en JSON                                 │  │
│  │  2. Genera PDF/Excel/HTML                                │  │
│  │     (services/market-info-service/exportador.py)        │  │
│  │  3. Devuelve archivo binario                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Características del Microservicio

### ✅ Es Externo (Separado de Django)
- **Código independiente**: `services/market-info-service/`
- **Framework diferente**: FastAPI (no Django)
- **Base de código separada**: No comparte código con Django

### ✅ Corre en Docker
- **Contenedor**: `nuam-market-info-service`
- **Puerto**: `5200`
- **Imagen**: Construida desde `./services/market-info-service/Dockerfile`

### ✅ Comunicación por HTTP
- Django llama al microservicio vía HTTP POST
- Usa `requests` library en `market_info_client.py`
- URL: `http://localhost:5200/exportar/{formato}`

---

## Código que Demuestra que es Externo

### 1. Cliente Django (llama al microservicio)

**Archivo:** `microservicio/services/market_info_client.py`

```python
def exportar_mercados(datos_mercado: List[Dict], formato: str, titulo: str = "Información de Bolsas") -> requests.Response:
    """
    Llama al endpoint de exportación del microservicio market-info-service.
    """
    base_url = _get_base_url()  # http://localhost:5200
    url = f"{base_url}/exportar/{formato}"  # POST http://localhost:5200/exportar/pdf
    
    payload = {
        "datos_mercado": datos_mercado,
        "titulo": titulo,
    }
    
    resp = requests.post(url, json=payload, timeout=30)  # ← HTTP POST externo
    resp.raise_for_status()
    return resp
```

### 2. Vista Django (usa el cliente)

**Archivo:** `microservicio/views/graficos.py`

```python
elif tipo_grafico == 'bolsa' or tipo_grafico == 'mercados':
    # Exportar datos de bolsa usando el microservicio market-info-service
    from microservicio.services.market_info_client import exportar_mercados, obtener_resumen_mercados
    
    # ... obtener datos ...
    
    # Llamar al microservicio para generar el archivo
    response = exportar_mercados(datos_exportar, formato, "Información de Bolsas")
    # ↑ Esto hace HTTP POST al microservicio externo
```

### 3. Microservicio FastAPI (separado)

**Archivo:** `services/market-info-service/main.py`

```python
@app.post("/exportar/pdf", tags=["exportacion"])
def exportar_pdf(payload: ExportarRequest) -> Response:
    """
    Exporta datos de mercados en formato PDF.
    
    Recibe una lista de datos de mercados y devuelve un archivo PDF listo para descargar.
    """
    try:
        pdf_content = generar_pdf(payload.datos_mercado, payload.titulo)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            # ...
        )
```

---

## Docker Compose

**Archivo:** `docker-compose.yml`

```yaml
  # Microservicio de Información de Mercados (Bolsa Chile/Perú/Colombia)
  market-info-service:
    build: ./services/market-info-service
    container_name: nuam-market-info-service
    ports:
      - "5200:5200"
    environment:
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY:-O0OACAT3N86XNKEY}
    restart: unless-stopped
    networks:
      - nuam-network
```

---

## Comparación: Monolito vs Microservicio

| Aspecto | Si fuera Monolito | Como está (Microservicio) |
|---------|-------------------|---------------------------|
| **Código** | Todo en Django | Separado en `services/market-info-service/` |
| **Framework** | Solo Django | Django + FastAPI |
| **Comunicación** | Funciones internas | HTTP POST |
| **Docker** | Un solo contenedor | Contenedor separado |
| **Puerto** | Mismo puerto (8443) | Puerto diferente (5200) |
| **Independencia** | No se puede apagar solo | Se puede apagar/reiniciar independientemente |

---

## Respuesta Directa

**Pregunta:** ¿La exportación del gráfico de bolsa es por Docker igual cierto? ¿Es externa igual no como microservicio? ¿No monolito?

**Respuesta:** ✅ **SÍ, es exactamente así:**

1. ✅ **Es por Docker**: Corre en el contenedor `nuam-market-info-service`
2. ✅ **Es externa**: Es un microservicio FastAPI completamente separado de Django
3. ✅ **No es monolito**: Django llama al microservicio por HTTP, no es código interno

**Flujo:**
```
Usuario → Django → HTTP POST → market-info-service (Docker) → Archivo PDF/Excel/HTML
```

---

## Verificación

Para verificar que el microservicio está corriendo:

```bash
# Ver contenedor
docker-compose ps market-info-service

# Ver logs
docker-compose logs market-info-service

# Probar endpoint directamente
curl -X POST http://localhost:5200/exportar/pdf \
  -H "Content-Type: application/json" \
  -d '{"datos_mercado": [...], "titulo": "Test"}'
```

---

## Ventajas de esta Arquitectura

✅ **Independencia**: Se puede desarrollar, desplegar y escalar independientemente  
✅ **Tecnología adecuada**: FastAPI es ideal para APIs REST  
✅ **Separación de responsabilidades**: Django maneja web, microservicio maneja exportación  
✅ **Reutilizable**: Otros sistemas pueden usar el mismo microservicio  
✅ **Fácil de probar**: Se puede probar el microservicio sin Django  


