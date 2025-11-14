# 📄 Explicación de la Lógica de CSVs en Proyecto NUAM

## 🎯 Resumen

Este documento explica cómo funciona la generación y lectura de archivos CSV en el proyecto NUAM, incluyendo las características técnicas que garantizan compatibilidad con Excel y la flexibilidad para trabajar con datos legibles (nombres) en lugar de IDs técnicos.

---

## 1️⃣ GENERACIÓN DE CSVs (EXPORTACIÓN)

### Características Técnicas

#### **UTF-8 con BOM (`\ufeff`)**
```python
# Se agrega al inicio del archivo para que Excel reconozca UTF-8
content = '\ufeff' + content  # Si include_bom=True
```
**¿Por qué?** Sin BOM, Excel interpreta el archivo como ANSI (Windows-1252), causando caracteres especiales mal codificados (ej: `CalificaciÃ³n` en lugar de `Calificación`).

#### **Delimitador Punto y Coma (`;`)**
```python
delimiter = ';'  # Default
```
**¿Por qué?** En regiones donde la coma (`,`) se usa como separador decimal (ej: `1,50`), el punto y coma (`;`) se usa como delimitador de columnas. Esto evita conflictos con valores numéricos.

#### **Línea `sep=;`**
```python
if excel_sep_hint and delimiter == ';':
    lines.append('sep=;')  # Primera línea del archivo
```
**¿Por qué?** Excel lee esta línea y automáticamente usa `;` como delimitador, incluso si la configuración regional espera comas.

#### **Escapado de Comillas Dobles**
```python
# Si una celda contiene comillas, se duplican
'"Hola "Mundo"!"' → '"Hola ""Mundo""!"'
```
**¿Por qué?** Según el estándar CSV RFC 4180, las comillas dentro de celdas deben escaparse duplicándolas.

#### **Salto de Línea Windows (`\r\n`)**
```python
content = '\r\n'.join(lines)  # En lugar de '\n'
```
**¿Por qué?** Windows usa `\r\n`, mientras que Unix/Mac usan `\n`. Usar `\r\n` garantiza compatibilidad total.

---

### Tipos de Exportación

#### **A) Exportación Individual (Mantenedor)**
- **Ubicación**: Tab "Mantenedor" → Botón "Descargar CSV" en fila
- **Headers**: País, Moneda, Ejercicio, Instrumento, Fecha Pago, Descripción, Estado, Corredora, Origen, Acogido SFUT, Factor Actualización, Secuencia Evento, Valor Histórico, **F08-F37** (30 factores)
- **Uso**: Exportar una calificación específica para editar y reimportar

#### **B) Exportación Masiva (Reportes)**
- **Ubicación**: Tab "Reportes" → Botón "Exportar CSV"
- **Headers**: Similar a Mantenedor pero incluye: Fuente (adicional), Ingreso por Montos, **Creado En, Actualizado En** (timestamps)
- **Uso**: Exportar todas las calificaciones filtradas para análisis masivo

#### **C) Plantilla Excel (Carga x Factor / Carga x Monto)**
- **Ubicación**: Tab "Cargas Masivas" → Botones "Descargar Formato"
- **Formato**: `.xlsx` (Excel nativo, generado con `openpyxl`)
- **Uso**: Descargar plantilla vacía para carga masiva

---

## 2️⃣ LECTURA DE CSVs (IMPORTACIÓN)

### Proceso de Parseo

#### **Paso 1: Detectar y Saltar `sep=;`**
```python
if lines[0].strip().startswith('sep='):
    delimiter = lines[0].split('=')[1].strip()
    start_idx = 1  # Saltar esta línea
```

#### **Paso 2: Detectar Delimitador Automáticamente**
```python
# Si no hay `sep=`, contar cuál delimitador aparece más
if ';' in line and line.count(';') > line.count(','):
    delimiter = ';'
elif ',' in line:
    delimiter = ','
```

#### **Paso 3: Normalizar Headers**
```python
def normalize_header(header):
    return header.strip().lower().replace('_', ' ')
# "Corredora" → "corredora"
# "ID Corredora" → "id corredora"
# "Fecha Pago" → "fecha pago"
```

#### **Paso 4: Mapear Headers Legibles a IDs Técnicos**
```python
mapping = {
    'corredora': 'id_corredora',
    'instrumento': 'id_instrumento',
    'fuente': 'id_fuente',
    'ejercicio': 'ejercicio',
    'fecha pago': 'fecha_pago',
    # ... más alias
}
```

**Ejemplo**:
```python
# CSV tiene: "Corredora" → Buscar en BD: Corredora.objects.get(nombre="Banco de Chile")
# Obtener: corredora.id_corredora → Usar este ID en calificacion.id_corredora
```

#### **Paso 5: Buscar Valores con Múltiples Alias**
```python
def get_cell(row, headers, *aliases, default=''):
    # Buscar 'ejercicio', 'año', 'year' → retornar el primero encontrado
    for alias in aliases:
        if alias in headers:
            return row[headers.index(alias)]
    return default
```

---

## 3️⃣ TIPOS DE IMPORTACIÓN

### **A) Carga x Factor**

**Archivo esperado**:
- **Headers requeridos**: Corredora, Instrumento, Ejercicio, Secuencia Evento, Fecha Pago
- **30 factores**: F08, F09, ..., F37
- **Validación**: Suma de factores F08-F16 debe ser ≤ 1.0

**Ejemplo CSV**:
```csv
sep=;
Corredora;Instrumento;Ejercicio;Secuencia Evento;Fecha Pago;F08;F09;...;F37
Banco de Chile;ACCION COMUN;2024;1;2024-12-31;0.10;0.05;...;0.02
```

**Proceso**:
1. Parsear CSV
2. Mapear nombres legibles → IDs técnicos
3. Validar suma de factores F08-F16
4. Buscar/crear `Calificacion` (clave única: corredora, instrumento, ejercicio, secuencia_evento)
5. Guardar factores en `calificacion_factor_detalle`
6. Registrar en `Carga` y `CargaDetalle`

---

### **B) Carga x Monto**

**Archivo esperado**:
- **Headers requeridos**: Corredora, Instrumento, Ejercicio, Secuencia Evento, Fecha Pago
- **30 montos**: M08, M09, ..., M37
- **Cálculo automático**: Factores F08-F37 = Monto / Suma Total de Montos

**Ejemplo CSV**:
```csv
sep=;
Corredora;Instrumento;Ejercicio;Secuencia Evento;Fecha Pago;M08;M09;...;M37
Banco de Chile;ACCION COMUN;2024;1;2024-12-31;100000;50000;...;20000
```

**Proceso**:
1. Parsear CSV
2. Mapear nombres legibles → IDs técnicos
3. Extraer montos M08-M37
4. Calcular suma total de montos
5. Calcular factores: `Factor = Monto / Suma Total`
6. Validar suma de factores F08-F16 ≤ 1.0
7. Buscar/crear `Calificacion`
8. Guardar montos en `calificacion_monto_detalle`
9. Guardar factores calculados en `calificacion_factor_detalle`
10. Registrar en `Carga` y `CargaDetalle`

---

## 4️⃣ FLUJO COMPLETO: EXPORTAR → EDITAR → REIMPORTAR

### **Caso de Uso Real**

1. **Usuario exporta** una calificación desde Mantenedor (CSV con headers legibles)
2. **Usuario abre** el CSV en Excel
   - Excel reconoce UTF-8 gracias al BOM
   - Excel usa `;` como delimitador gracias a `sep=;`
   - Usuario ve nombres legibles (ej: "Banco de Chile") en lugar de IDs
3. **Usuario edita** valores (factores, fechas, descripciones)
4. **Usuario guarda** el CSV editado
5. **Usuario reimporta** usando "Carga x Factor"
   - Sistema parsea el CSV
   - Sistema mapea "Banco de Chile" → busca ID en BD → usa ID técnico
   - Sistema valida y guarda los cambios

**Ventajas**:
- ✅ Usuario trabaja con datos legibles (no IDs)
- ✅ Excel abre el archivo correctamente (UTF-8, delimitador correcto)
- ✅ Sistema maneja la conversión automáticamente (legible → técnico)

---

## 5️⃣ ARCHIVOS DEL PROYECTO

### **Frontend (Generación de CSV)**
- **`templates/static/js/mantenedor/core.js`**:
  - `buildCsvContent()`: Función principal para generar CSV
  - `CALIFICACION_EXPORT_HEADERS`: Headers para exportación individual
  - `CALIFICACION_REPORT_HEADERS`: Headers para exportación masiva
  - `buildReadableCalificacionRow()`: Construir fila con valores legibles
  - `buildReportCalificacionRow()`: Construir fila para reportes

### **Backend (Lectura de CSV)**
- **`api/views.py`**:
  - `upload_factores()`: Importar CSV con factores (F08-F37)
  - `upload_montos()`: Importar CSV con montos (M08-M37) y calcular factores
  - `normalizeHeader()`: Normalizar nombres de headers
  - `get_cell()`: Obtener valor de celda por múltiples alias
  - `_calcular_factores_desde_montos_helper()`: Calcular factores desde montos

---

## 6️⃣ EJEMPLO PRÁCTICO COMPLETO

### **Generar CSV**:
```javascript
// Frontend (core.js)
const headers = ['Corredora', 'Instrumento', 'Ejercicio', 'F08', 'F09', ...];
const rows = [
    ['Banco de Chile', 'ACCION COMUN', '2024', '0.10', '0.05', ...]
];
const csv = buildCsvContent(headers, rows, {
    delimiter: ';',
    include_bom: true,      // UTF-8 BOM
    excel_sep_hint: true    // Línea sep=;
});
// Descargar: downloadBlob(new Blob([csv], {type: 'text/csv;charset=utf-8;'}), 'calificaciones.csv')
```

### **Leer CSV**:
```python
# Backend (api/views.py)
def upload_factores(self, request):
    file = request.FILES['archivo']
    content = file.read().decode('utf-8-sig')  # Decodificar con BOM
    
    # Parsear CSV
    lines = content.strip().split('\n')
    if lines[0].startswith('sep='):
        delimiter = lines[0].split('=')[1].strip()
        headers_line = lines[1]
    else:
        delimiter = detect_delimiter(lines[0])
        headers_line = lines[0]
    
    headers = [normalize_header(h) for h in headers_line.split(delimiter)]
    
    # Procesar filas
    for line in lines[2:]:
        row = parse_csv_row(line, delimiter)
        
        # Mapear valores legibles → IDs técnicos
        corredora_nombre = get_cell(row, headers, 'corredora', 'corredora nombre')
        corredora = Corredora.objects.get(nombre=corredora_nombre)
        
        # Guardar en BD...
```

---

## 7️⃣ NOTAS IMPORTANTES

### **✅ Buenas Prácticas**
- Siempre usar UTF-8 con BOM para exportación
- Siempre incluir `sep=;` para Excel
- Usar headers legibles (no IDs) para mejor UX
- Validar headers requeridos antes de procesar
- Manejar errores de codificación y delimitador

### **⚠️ Consideraciones**
- El delimitador puede variar (`,` o `;`) → detectar automáticamente
- Los headers pueden tener variaciones ("Corredora", "ID Corredora", "corredora nombre") → usar alias múltiples
- Los valores pueden venir en diferentes formatos (booleano: "Sí", "Si", "true", "1") → normalizar

---

## 📝 RESUMEN

**Exportación (Frontend)**:
1. Generar CSV con UTF-8 BOM, `sep=;`, delimitador `;`
2. Usar headers legibles (nombres, no IDs)
3. Escapar comillas y caracteres especiales

**Importación (Backend)**:
1. Detectar y saltar línea `sep=;`
2. Detectar delimitador automáticamente
3. Normalizar headers (minúsculas, sin espacios extra)
4. Mapear valores legibles → IDs técnicos
5. Validar y guardar en BD

**Resultado**: Sistema flexible que permite trabajar con datos legibles mientras mantiene la integridad técnica en la base de datos.

---

**Archivos relacionados**:
- `templates/static/js/mantenedor/core.js` (generación)
- `api/views.py` (lectura y procesamiento)
- `ejemplo_csv_logic.py` (script de ejemplo ejecutable)

