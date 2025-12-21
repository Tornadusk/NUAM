# Exportación de PDF/Excel para Tipos de Cambio y Bolsa

## Situación Actual

### Exportación de Gráficos:
- ✅ **Gráficos**: Exporta directamente desde Django usando `microservicio/utils/exportador.py`
- ❌ **NO usa** el microservicio `docs-generator`

### Exportación de Reportes (Mantenedor):
- ✅ **Reportes del mantenedor**: Usa `docs-generator` (microservicio)
- ✅ Soporta: PDF, Excel, CSV

### Tipos de Cambio y Bolsa:
- ✅ **Tipos de Cambio**: Tiene exportación implementada (CSV, Excel, PDF, HTML)
  - Incluye datos simulados y datos reales
  - Endpoint: `/microservicio/api/exportar/tipos_cambio/<formato>/`
  - Botones de exportación en el dashboard
- ❌ **Bolsa**: NO tiene exportación actualmente
- Solo se pueden ver en el dashboard web

---

## Opciones para Agregar Exportación

### ✅ Opción A: Extender `docs-generator` (RECOMENDADO)

**Ventajas:**
- Ya existe el microservicio
- Ya tiene la lógica de PDF/Excel/CSV
- Centraliza todas las exportaciones
- Menos mantenimiento

**Cómo hacerlo:**

1. Agregar nuevos endpoints en `docs-generator`:
   ```python
   # services/docs-generator/src/main.py
   
   @app.post("/exportar/tipos-cambio")
   async def exportar_tipos_cambio(datos: DatosTiposCambio):
       # Lógica para exportar tipos de cambio
       pass
   
   @app.post("/exportar/bolsa")
   async def exportar_bolsa(datos: DatosBolsa):
       # Lógica para exportar datos de bolsa
       pass
   ```

2. Desde Django, llamar a estos endpoints cuando el usuario presione "Exportar"

3. El microservicio genera el archivo y Django lo devuelve

**Ejemplo de uso:**
```python
# En microservicio/views/tipos_cambio.py
def api_exportar_tipos_cambio(request, formato):
    # Obtener datos desde la BD
    tipos_cambio = TipoCambio.objects.filter(...)
    
    # Preparar datos para docs-generator
    payload = {
        "titulo": "Tipos de Cambio",
        "items": [serializar_tipo_cambio(tc) for tc in tipos_cambio],
        "formato": formato  # pdf, excel, csv
    }
    
    # Llamar a docs-generator
    response = requests.post("http://localhost:5001/exportar/tipos-cambio", json=payload)
    return HttpResponse(response.content, content_type="application/pdf")
```

---

### Opción B: Agregar exportación en los microservicios actuales

**Ventajas:**
- Cada microservicio maneja su propia exportación
- Más desacoplado
- Los microservicios pueden exportar sus propios datos sin depender de otros servicios

**Desventajas:**
- Duplica lógica de PDF/Excel/HTML (pero se puede reutilizar código)
- Más código que mantener

**Formatos a soportar:**
- ✅ PDF
- ✅ Excel (.xlsx)
- ✅ HTML (para vista previa o descarga)
- ✅ CSV (opcional, pero útil)

**Cómo hacerlo:**

1. **Agregar endpoints en `exchange-rate-service`**:
   ```python
   # services/exchange-rate-service/main.py
   
   from fastapi.responses import Response
   from reportlab.lib.pagesizes import letter
   from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
   from openpyxl import Workbook
   from jinja2 import Template
   
   @app.post("/exportar/pdf")
   async def exportar_pdf_tipos_cambio(datos: List[TipoCambioItem]):
       """Exporta tipos de cambio a PDF"""
       buffer = io.BytesIO()
       doc = SimpleDocTemplate(buffer, pagesize=letter)
       # ... lógica de generación PDF
       buffer.seek(0)
       return Response(content=buffer.read(), media_type="application/pdf")
   
   @app.post("/exportar/excel")
   async def exportar_excel_tipos_cambio(datos: List[TipoCambioItem]):
       """Exporta tipos de cambio a Excel"""
       wb = Workbook()
       ws = wb.active
       # ... lógica de generación Excel
       buffer = io.BytesIO()
       wb.save(buffer)
       buffer.seek(0)
       return Response(
           content=buffer.read(),
           media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
           headers={"Content-Disposition": "attachment; filename=tipos_cambio.xlsx"}
       )
   
   @app.post("/exportar/html")
   async def exportar_html_tipos_cambio(datos: List[TipoCambioItem]):
       """Exporta tipos de cambio a HTML"""
       html_template = """
       <!DOCTYPE html>
       <html>
       <head><title>Tipos de Cambio</title></head>
       <body>
           <h1>Tipos de Cambio</h1>
           <table>
               {% for item in datos %}
               <tr>
                   <td>{{ item.moneda_origen }}/{{ item.moneda_destino }}</td>
                   <td>{{ item.tasa }}</td>
                   <td>{{ item.fecha }}</td>
               </tr>
               {% endfor %}
           </table>
       </body>
       </html>
       """
       template = Template(html_template)
       html_content = template.render(datos=datos)
       return Response(content=html_content, media_type="text/html")
   ```

2. **Agregar endpoints en `market-info-service`**:
   ```python
   # services/market-info-service/main.py
   
   @app.post("/exportar/pdf")
   async def exportar_pdf_bolsa(datos: MarketSummaryResponse):
       """Exporta datos de bolsa a PDF"""
       # Similar implementación
       pass
   
   @app.post("/exportar/excel")
   async def exportar_excel_bolsa(datos: MarketSummaryResponse):
       """Exporta datos de bolsa a Excel"""
       # Similar implementación
       pass
   
   @app.post("/exportar/html")
   async def exportar_html_bolsa(datos: MarketSummaryResponse):
       """Exporta datos de bolsa a HTML"""
       # Similar implementación
       pass
   ```

3. **Agregar dependencias en `requirements.txt` de cada microservicio**:
   ```txt
   # Para PDF
   reportlab>=3.6.0
   
   # Para Excel
   openpyxl>=3.1.0
   
   # Para HTML (si usas templates)
   jinja2>=3.1.0
   ```

4. **Desde Django, llamar a estos endpoints**:
   ```python
   # En microservicio/views/tipos_cambio.py
   def api_exportar_tipos_cambio(request, formato):
       # Obtener datos desde la BD
       tipos_cambio = TipoCambio.objects.filter(...)
       
       # Serializar datos
       datos = [serializar_tipo_cambio(tc) for tc in tipos_cambio]
       
       # Llamar al microservicio
       url = f"http://localhost:5100/exportar/{formato}"  # pdf, excel, html
       response = requests.post(url, json=datos)
       
       content_type = {
           'pdf': 'application/pdf',
           'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
           'html': 'text/html'
       }[formato]
       
       return HttpResponse(response.content, content_type=content_type)
   ```

---

### ❌ Opción C: Crear microservicios separados

**NO RECOMENDADO:**
- Añade complejidad innecesaria
- Duplica infraestructura
- Más contenedores Docker que mantener

---

## Comparación: Opción A vs Opción B

### Opción A: Extender `docs-generator` (Centralizado)

**Ventajas:**
1. ✅ **Ya existe**: `docs-generator` ya funciona para reportes
2. ✅ **Reutiliza código**: No duplicar lógica de PDF/Excel/HTML
3. ✅ **Centralizado**: Todas las exportaciones en un solo lugar
4. ✅ **Fácil de mantener**: Un solo microservicio para exportaciones
5. ✅ **Consistente**: Todos los PDFs/Excel tendrán el mismo formato

**Desventajas:**
- Dependencia: Si `docs-generator` cae, no se puede exportar nada
- Acoplamiento: Todos los módulos dependen de un servicio

### Opción B: Exportación en cada microservicio (Desacoplado)

**Ventajas:**
1. ✅ **Desacoplado**: Cada microservicio es independiente
2. ✅ **Sin dependencias**: Si un microservicio cae, los otros siguen funcionando
3. ✅ **Especializado**: Cada servicio exporta solo sus datos
4. ✅ **Escalable**: Puedes escalar exportaciones independientemente

**Desventajas:**
- Duplica lógica de PDF/Excel/HTML (pero se puede crear librería compartida)
- Más código que mantener

### Recomendación según caso:

- **Opción A**: Si quieres mantener todo centralizado y consistente
- **Opción B**: Si prefieres microservicios más independientes y desacoplados (más alineado con arquitectura de microservicios pura)

### Implementación sugerida:

```
Django (Tipos de Cambio/Bolsa)
    ↓ HTTP POST
docs-generator
    ↓
Genera PDF/Excel/CSV
    ↓
Django devuelve archivo al usuario
```

### Endpoints propuestos para docs-generator:

```
POST /exportar/tipos-cambio
  - Recibe: datos de tipos de cambio
  - Genera: PDF, Excel o CSV
  - Devuelve: Archivo listo para descargar

POST /exportar/bolsa
  - Recibe: datos de mercados
  - Genera: PDF, Excel o CSV
  - Devuelve: Archivo listo para descargar
```

---

## ✅ Exportación de Tipos de Cambio - IMPLEMENTADA (Usa Microservicio)

### Estado Actual:
- ✅ **Usa microservicio**: `exchange-rate-service` con endpoints `/exportar/pdf`, `/exportar/excel`, `/exportar/html`
- ✅ **Funciona correctamente**: PDF, Excel (.xlsx), HTML (CSV sigue usando Django)
- ✅ **Incluye datos simulados**: La exportación incluye todos los tipos de cambio, tanto de APIs reales como simulados
- ✅ **Botones en dashboard**: Botones de exportación en el header del gráfico histórico
- ✅ **Arquitectura**: Sigue el patrón de microservicios (Opción B implementada)

### ✅ IMPLEMENTADO:
La exportación ahora **usa microservicios** (`exchange-rate-service`). Django obtiene los datos de la BD y los envía al microservicio, que genera los archivos.

### Cómo usar:
1. **Desde el Dashboard**:
   - Ve a `/microservicio/tipos-cambio/`
   - En el header del gráfico "Evolución Histórica", hay botones: CSV, Excel, PDF, HTML
   - Haz clic en el formato deseado para descargar

2. **Directamente por URL**:
   ```
   /microservicio/api/exportar/tipos_cambio/csv/
   /microservicio/api/exportar/tipos_cambio/excel/
   /microservicio/api/exportar/tipos_cambio/pdf/
   /microservicio/api/exportar/tipos_cambio/html/
   ```

### Datos incluidos en la exportación:
- Par de Monedas (ej: USD/CLP)
- Tasa de cambio
- Fecha
- Fuente (nombre de la fuente)
- Código Fuente (ej: EXCHANGERATE_API, SIMULADO)
- Es Simulado (Sí/No)
- Vigente Desde (timestamp)

### Generar Datos Simulados:
- ✅ **Botón implementado**: "Cargar Datos Simulados" en el dashboard
- Genera datos para los últimos 12 meses con valores realistas
- Útil para pruebas y desarrollo cuando las APIs no están disponibles

---

## Pasos para Implementar Exportación de Bolsa (Opción B - Recomendada para microservicios independientes)

### Para `exchange-rate-service`:

1. **Agregar dependencias en `requirements.txt`**:
   ```txt
   reportlab>=3.6.0  # PDF
   openpyxl>=3.1.0   # Excel
   jinja2>=3.1.0     # HTML templates
   ```

2. **Agregar endpoints en `services/exchange-rate-service/main.py`**:
   - `POST /exportar/pdf` - Genera PDF
   - `POST /exportar/excel` - Genera Excel
   - `POST /exportar/html` - Genera HTML
   - Todos reciben `List[TipoCambioItem]` como entrada

3. **Crear módulo de exportación** (opcional, para reutilizar código):
   ```python
   # services/exchange-rate-service/exportador.py
   def generar_pdf_tipos_cambio(tipos_cambio: List[TipoCambioItem]) -> bytes:
       # Lógica de generación PDF
       pass
   
   def generar_excel_tipos_cambio(tipos_cambio: List[TipoCambioItem]) -> bytes:
       # Lógica de generación Excel
       pass
   
   def generar_html_tipos_cambio(tipos_cambio: List[TipoCambioItem]) -> str:
       # Lógica de generación HTML
       pass
   ```

### Para `market-info-service`:

1. **Agregar dependencias** (igual que arriba)

2. **Agregar endpoints en `services/market-info-service/main.py`**:
   - `POST /exportar/pdf` - Genera PDF
   - `POST /exportar/excel` - Genera Excel
   - `POST /exportar/html` - Genera HTML
   - Todos reciben `MarketSummaryResponse` como entrada

### Desde Django:

1. **Agregar botones en templates**:
   - `templates/microservicio/tipos_cambio/dashboard.html`: Botones "Exportar PDF", "Exportar Excel", "Exportar HTML"
   - `templates/microservicio/mercados/dashboard.html`: Botones "Exportar PDF", "Exportar Excel", "Exportar HTML"

2. **Crear vistas en Django**:
   ```python
   # microservicio/views/tipos_cambio.py
   @api_view(['POST'])
   def api_exportar_tipos_cambio(request, formato):
       # Obtener datos de la BD
       tipos_cambio = TipoCambio.objects.filter(...)
       datos = [serializar_tipo_cambio(tc) for tc in tipos_cambio]
       
       # Llamar al microservicio
       url = f"http://localhost:5100/exportar/{formato}"
       response = requests.post(url, json=datos)
       
       content_type = {
           'pdf': 'application/pdf',
           'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
           'html': 'text/html'
       }[formato]
       
       return HttpResponse(response.content, content_type=content_type)
   ```

3. **Agregar URLs**:
   ```python
   # microservicio/urls.py
   path('api/exportar-tipos-cambio/<str:formato>/', api_exportar_tipos_cambio, name='api_exportar_tipos_cambio'),
   ```

---

## Nota sobre API Keys

Para que las APIs externas funcionen y obtengas datos reales:

### APIs - Estado Actual:

1. **ExchangeRate API** ✅ YA TIENES LA KEY:
   - API Key: `effbc5f153954a92a297e710`
   - Web: https://www.exchangerate-api.com/
   - Plan: Free (1500 requests/mes disponibles)
   - Ejemplo funcionando: https://v6.exchangerate-api.com/v6/effbc5f153954a92a297e710/latest/USD
   - ✅ **Configurar en docker-compose.yml o .env**

2. **Fixer.io** (opcional):
   - Web: https://fixer.io/
   - Gratis: Plan limitado
   - Requiere registro si quieres usarlo

3. **Alpha Vantage** ✅ YA CONFIGURADA:
   - API Key: `O0OACAT3N86XNKEY`
   - Plan: Free (25 requests/día)
   - ✅ Ya configurada en `docker-compose.yml`

### Configurar API Keys:

**✅ RECOMENDADO: Actualizar `docker-compose.yml`** con tu key de ExchangeRate:
```yaml
exchange-rate-service:
  environment:
    - EXCHANGERATE_API_KEY=effbc5f153954a92a297e710  # ← Tu key aquí
    - FIXER_API_KEY=${FIXER_API_KEY:-}  # Opcional
```

**O en archivo `.env`** (si prefieres):
```env
EXCHANGERATE_API_KEY=effbc5f153954a92a297e710
FIXER_API_KEY=tu_key_aqui_si_la_tienes
ALPHA_VANTAGE_API_KEY=O0OACAT3N86XNKEY
```

**Después de configurar, reiniciar el contenedor:**
```bash
docker-compose restart exchange-rate-service
```

---

## ✅ Conclusión - ESTADO ACTUAL (IMPLEMENTADO)

### Exportación Implementada:
- ✅ **Usa microservicios** (Opción B implementada)
- ✅ **exchange-rate-service** → `/exportar/pdf`, `/exportar/excel`, `/exportar/html`
- ✅ **market-info-service** → `/exportar/pdf`, `/exportar/excel`, `/exportar/html`
- ✅ **Funciona correctamente** (PDF, Excel, HTML)
- ✅ **Sigue arquitectura de microservicios**

**Ver**: `Explicacion/EXPORTACION_ESTADO_ACTUAL.md` para detalles completos

- **Formatos a soportar**: PDF, Excel (.xlsx), HTML (y opcionalmente CSV)

- **Para API keys**: 
  - ✅ **ExchangeRate API**: Ya tienes la key `effbc5f153954a92a297e710` (1500 requests/mes gratis)
  - ✅ **Alpha Vantage**: Ya configurada `O0OACAT3N86XNKEY` (25 requests/día)
  - ✅ **Configurada en `docker-compose.yml`**

