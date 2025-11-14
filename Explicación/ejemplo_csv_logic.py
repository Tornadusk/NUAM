"""
SCRIPT DE EJEMPLO TEMPORAL - Lógica de CSVs en Proyecto NUAM
=============================================================

Este script explica y demuestra la lógica completa de generación y lectura de CSVs
en el proyecto NUAM, incluyendo:

1. Generación de CSVs (Exportación):
   - UTF-8 con BOM para compatibilidad con Excel
   - Delimitador punto y coma (;)
   - Línea `sep=;` para indicar el separador
   - Headers legibles (ej: "Corredora", "Instrumento") en lugar de IDs técnicos
   - Escapado de caracteres especiales (comillas dobles)

2. Lectura de CSVs (Importación):
   - Detección automática de delimitador (`,` o `;`)
   - Salto de línea `sep=;` si está presente
   - Mapeo de headers legibles a IDs técnicos
   - Validación de encabezados requeridos
   - Conversión de tipos de datos

3. Tipos de CSVs:
   - Mantenedor: Exportación individual de calificaciones
   - Reportes: Exportación masiva con todos los campos
   - Carga x Factor: Importación masiva con factores F08-F37
   - Carga x Monto: Importación masiva con montos M08-M37

Autor: Sistema NUAM
Fecha: 2025
"""

# ============================================================================
# PARTE 1: GENERACIÓN DE CSVs (EXPORTACIÓN)
# ============================================================================

def build_csv_content(headers=[], rows=[], delimiter=';', include_bom=True, excel_sep_hint=False):
    """
    Construir contenido CSV con formato compatible con Excel.
    
    Características:
    - UTF-8 con BOM (\ufeff) para que Excel reconozca correctamente los caracteres especiales
    - Delimitador punto y coma (;) por defecto (estándar en regiones que usan coma como decimal)
    - Línea `sep=;` opcional para indicar explícitamente el separador
    - Escapado de comillas dobles ("" dentro de celdas)
    - Saltos de línea Windows (\r\n) para compatibilidad
    
    Args:
        headers: Lista de nombres de columnas
        rows: Lista de listas, cada lista es una fila de datos
        delimiter: Caracter delimitador (default: ';')
        include_bom: Si True, agrega BOM UTF-8 al inicio
        excel_sep_hint: Si True, agrega línea `sep=;` al inicio
    
    Returns:
        str: Contenido del CSV como string
    """
    
    def escape_cell(cell):
        """Escapar una celda según reglas CSV RFC 4180"""
        if cell is None or cell == '':
            return ''
        
        cell_str = str(cell)
        # Si contiene delimitador, comillas o saltos de línea, encerrar en comillas
        needs_quote = (
            delimiter in cell_str or 
            '"' in cell_str or 
            '\n' in cell_str or 
            '\r' in cell_str
        )
        
        if needs_quote:
            # Escapar comillas dobles duplicándolas
            cell_str = cell_str.replace('"', '""')
            return f'"{cell_str}"'
        
        return cell_str
    
    lines = []
    
    # 1. Agregar línea sep=; si se solicita (para Excel)
    if excel_sep_hint and delimiter == ';':
        lines.append('sep=;')
    
    # 2. Agregar headers
    if headers:
        lines.append(delimiter.join(escape_cell(h) for h in headers))
    
    # 3. Agregar filas de datos
    for row in rows:
        lines.append(delimiter.join(escape_cell(cell) for cell in row))
    
    # 4. Unir todas las líneas con saltos de línea Windows
    content = '\r\n'.join(lines)
    
    # 5. Agregar BOM UTF-8 al inicio si se solicita
    if include_bom:
        content = '\ufeff' + content
    
    return content


# Ejemplo 1: Generar CSV de Mantenedor (exportación individual)
def ejemplo_exportacion_mantenedor():
    """
    Ejemplo de exportación individual desde el Mantenedor.
    
    Incluye: País, Moneda, Ejercicio, Instrumento, Fecha Pago, Descripción,
    Estado, Corredora, Origen, Acogido SFUT, Factor Actualización,
    Secuencia Evento, Valor Histórico, F08-F37 (30 factores)
    """
    
    # Headers legibles (no IDs técnicos)
    headers = [
        'País', 'Moneda', 'Ejercicio', 'Instrumento', 'Fecha Pago',
        'Descripción', 'Estado', 'Corredora', 'Origen', 'Acogido SFUT',
        'Factor Actualización', 'Secuencia Evento', 'Valor Histórico'
    ]
    
    # Agregar factores F08-F37
    factor_codigos = [f'F{i:02d}' for i in range(8, 38)]  # F08, F09, ..., F37
    headers.extend(factor_codigos)
    
    # Ejemplo de fila de datos
    row = [
        'Chile',           # País (nombre legible, no ID)
        'CLP',             # Moneda (código ISO, no ID)
        '2024',            # Ejercicio
        'ACCION COMUN',    # Instrumento (nombre legible)
        '2024-12-31',      # Fecha Pago
        'Dividendo anual', # Descripción
        'validada',        # Estado
        'Banco de Chile',  # Corredora (nombre legible)
        'SII',             # Origen/Fuente (nombre legible)
        'Sí',              # Acogido SFUT (booleano legible)
        '1.50000000',      # Factor Actualización
        '1',               # Secuencia Evento
        '1000000.00'       # Valor Histórico
    ]
    
    # Agregar valores de factores F08-F37 (30 valores)
    # En el sistema real, estos se obtienen de calificacion_factor_detalle
    factores = [f'0.{i:02d}' for i in range(8, 38)]  # Ejemplo: 0.08, 0.09, ..., 0.37
    row.extend(factores)
    
    rows = [row]  # Puede haber múltiples filas
    
    # Generar contenido CSV
    csv_content = build_csv_content(
        headers=headers,
        rows=rows,
        delimiter=';',
        include_bom=True,      # CRÍTICO: Para que Excel reconozca UTF-8
        excel_sep_hint=True    # CRÍTICO: Para que Excel use ; como delimitador
    )
    
    return csv_content


# Ejemplo 2: Generar CSV de Reportes (exportación masiva)
def ejemplo_exportacion_reportes():
    """
    Ejemplo de exportación masiva desde el tab de Reportes.
    
    Similar a Mantenedor pero incluye campos adicionales:
    - Fuente (además de Corredora)
    - Ingreso por Montos (booleano)
    - Creado En, Actualizado En (timestamps)
    """
    
    headers = [
        'Corredora', 'Fuente', 'País', 'Moneda', 'Instrumento',
        'Ejercicio', 'Fecha Pago', 'Descripción', 'Estado',
        'Secuencia Evento', 'Acogido SFUT', 'Ingreso por Montos',
        'Factor Actualización', 'Valor Histórico'
    ]
    
    # Agregar factores F08-F37
    factor_codigos = [f'F{i:02d}' for i in range(8, 38)]
    headers.extend(factor_codigos)
    
    # Agregar timestamps
    headers.extend(['Creado En', 'Actualizado En'])
    
    # Ejemplo de fila
    row = [
        'Banco de Chile', 'SII', 'Chile', 'CLP', 'ACCION COMUN',
        '2024', '2024-12-31', 'Dividendo anual', 'validada',
        '1', 'Sí', 'No', '1.50000000', '1000000.00'
    ]
    
    # Factores F08-F37
    factores = [f'0.{i:02d}' for i in range(8, 38)]
    row.extend(factores)
    
    # Timestamps
    row.extend(['2024-01-15 10:30:00', '2024-01-20 14:45:00'])
    
    csv_content = build_csv_content(
        headers=headers,
        rows=[row],
        delimiter=';',
        include_bom=True,
        excel_sep_hint=True
    )
    
    return csv_content


# ============================================================================
# PARTE 2: LECTURA DE CSVs (IMPORTACIÓN)
# ============================================================================

def normalize_header(header):
    """
    Normalizar nombre de header para hacerlo insensible a mayúsculas/minúsculas
    y espacios extra.
    
    Ejemplos:
    - "Corredora" -> "corredora"
    - "ID Corredora" -> "id corredora"
    - "Fecha Pago" -> "fecha pago"
    """
    if not header:
        return ''
    return header.strip().lower().replace('_', ' ')


def detect_delimiter(first_line):
    """
    Detectar delimitador del CSV (coma o punto y coma).
    
    Lógica:
    - Si la línea contiene más `;` que `,`, usar `;`
    - Si la línea contiene más `,` que `;`, usar `,`
    - Por defecto, usar `;`
    """
    if ';' in first_line and first_line.count(';') > first_line.count(','):
        return ';'
    elif ',' in first_line:
        return ','
    return ';'  # Default


def parse_csv_import(file_content):
    """
    Parsear CSV para importación, manejando:
    - Salto de línea `sep=;`
    - Detección automática de delimitador
    - Normalización de headers
    
    Returns:
        tuple: (headers, rows, delimiter)
    """
    lines = file_content.strip().split('\n')
    
    # 1. Detectar y saltar línea `sep=;`
    delimiter = ';'  # Default
    start_idx = 0
    
    if lines and lines[0].strip().startswith('sep='):
        delimiter = lines[0].strip().split('=')[1].strip()
        start_idx = 1
    
    # 2. Detectar delimitador si no se encontró `sep=`
    if start_idx < len(lines):
        detected = detect_delimiter(lines[start_idx])
        if detected:
            delimiter = detected
    
    # 3. Obtener headers (primera línea después de `sep=`)
    if start_idx >= len(lines):
        raise ValueError("Archivo CSV vacío o sin headers")
    
    headers_line = lines[start_idx].strip().rstrip('\r')
    headers = [h.strip().strip('"') for h in headers_line.split(delimiter)]
    headers = [normalize_header(h) for h in headers]  # Normalizar
    
    # 4. Obtener filas de datos
    rows = []
    for line in lines[start_idx + 1:]:
        line = line.strip().rstrip('\r')
        if not line:
            continue
        
        # Parsear celda (manejar comillas escapadas)
        cells = []
        current_cell = ''
        inside_quotes = False
        
        for char in line:
            if char == '"':
                if inside_quotes:
                    # Verificar si es comilla escapada ("")
                    if len(current_cell) > 0 and current_cell[-1] == '"':
                        current_cell = current_cell[:-1] + '"'
                    else:
                        inside_quotes = False
                else:
                    inside_quotes = True
            elif char == delimiter and not inside_quotes:
                cells.append(current_cell.strip().strip('"'))
                current_cell = ''
            else:
                current_cell += char
        
        # Agregar última celda
        if current_cell:
            cells.append(current_cell.strip().strip('"'))
        
        rows.append(cells)
    
    return headers, rows, delimiter


# ============================================================================
# PARTE 3: MAPEO DE HEADERS LEGIBLES A IDs TÉCNICOS
# ============================================================================

def get_header_mapping():
    """
    Mapeo de headers legibles a campos técnicos del modelo.
    
    En el sistema real, este mapeo permite que los usuarios suban CSVs
    con nombres amigables (ej: "Corredora") en lugar de IDs técnicos.
    """
    
    # Múltiples alias para el mismo campo (flexibilidad)
    mapping = {
        # Identificadores principales
        'corredora': 'id_corredora',
        'id corredora': 'id_corredora',
        'corredora nombre': 'id_corredora',
        
        'instrumento': 'id_instrumento',
        'id instrumento': 'id_instrumento',
        'instrumento codigo': 'id_instrumento',
        'instrumento nombre': 'id_instrumento',
        
        'fuente': 'id_fuente',
        'origen': 'id_fuente',
        'id fuente': 'id_fuente',
        'fuente nombre': 'id_fuente',
        
        # Campos básicos
        'ejercicio': 'ejercicio',
        'año': 'ejercicio',
        'year': 'ejercicio',
        
        'fecha pago': 'fecha_pago',
        'fecha de pago': 'fecha_pago',
        'payment date': 'fecha_pago',
        
        'descripcion': 'descripcion',
        'descripción': 'descripcion',
        'description': 'descripcion',
        
        'estado': 'estado',
        'status': 'estado',
        
        'secuencia evento': 'secuencia_evento',
        'secuencia': 'secuencia_evento',
        'evento secuencia': 'secuencia_evento',
        
        'valor historico': 'valor_historico',
        'valor histórico': 'valor_historico',
        'valor': 'valor_historico',
        
        'acogido sfut': 'acogido_sfut',
        'acogido': 'acogido_sfut',
        
        'factor actualizacion': 'factor_actualizacion',
        'factor actualización': 'factor_actualizacion',
    }
    
    # Agregar mapeo para factores F08-F37
    for i in range(8, 38):
        codigo = f'F{i:02d}'
        mapping[codigo.lower()] = f'factor_{codigo}'
        mapping[f'factor {codigo.lower()}'] = f'factor_{codigo}'
    
    # Agregar mapeo para montos M08-M37
    for i in range(8, 38):
        codigo = f'M{i:02d}'
        mapping[codigo.lower()] = f'monto_{codigo}'
        mapping[f'monto {codigo.lower()}'] = f'monto_{codigo}'
    
    return mapping


def get_cell(row, headers, *aliases, default=''):
    """
    Obtener valor de una celda buscando por múltiples alias de header.
    
    Ejemplo:
        row = ['Banco de Chile', '2024', '1000.00']
        headers = ['corredora', 'ejercicio', 'valor']
        valor = get_cell(row, headers, 'ejercicio', 'año', 'year', default='0')
        # Retorna: '2024'
    """
    for alias in aliases:
        normalized_alias = normalize_header(alias)
        try:
            idx = headers.index(normalized_alias)
            value = row[idx].strip() if idx < len(row) else ''
            if value:
                return value
        except ValueError:
            continue
    return default


# ============================================================================
# PARTE 4: EJEMPLOS DE IMPORTACIÓN
# ============================================================================

def ejemplo_importacion_carga_factor():
    """
    Ejemplo de importación "Carga x Factor".
    
    El CSV debe incluir:
    - Campos de identificación: Corredora, Instrumento, Ejercicio, Secuencia Evento, Fecha Pago
    - 30 factores: F08, F09, ..., F37
    - Validación: La suma de factores F08-F16 debe ser <= 1
    """
    
    # CSV de ejemplo (simulado)
    csv_content = """sep=;
Corredora;Instrumento;Ejercicio;Secuencia Evento;Fecha Pago;Descripción;F08;F09;F10;...;F37
Banco de Chile;ACCION COMUN;2024;1;2024-12-31;Dividendo anual;0.10;0.05;0.08;...;0.02
Banco Santander;ACCION PREFERENTE;2024;1;2024-12-31;Dividendo preferente;0.12;0.06;0.09;...;0.03"""
    
    # Parsear CSV
    headers, rows, delimiter = parse_csv_import(csv_content)
    
    print(f"Delimitador detectado: {delimiter}")
    print(f"Headers: {headers[:5]}...")
    print(f"Número de filas: {len(rows)}")
    
    # Mapear headers a campos técnicos
    header_mapping = get_header_mapping()
    
    # Procesar cada fila
    for idx, row in enumerate(rows, start=2):  # Empezar en 2 (después de headers y sep=)
        # Obtener valores usando alias
        corredora_nombre = get_cell(row, headers, 'corredora', 'corredora nombre')
        instrumento_nombre = get_cell(row, headers, 'instrumento', 'instrumento nombre')
        ejercicio = get_cell(row, headers, 'ejercicio', 'año', 'year')
        secuencia_evento = get_cell(row, headers, 'secuencia evento', 'secuencia')
        fecha_pago = get_cell(row, headers, 'fecha pago', 'fecha de pago')
        
        # Obtener factores F08-F37
        factores = {}
        for i in range(8, 38):
            codigo = f'F{i:02d}'
            factor_key = codigo.lower()
            valor = get_cell(row, headers, factor_key, f'factor {factor_key}', default='0')
            factores[codigo] = float(valor) if valor else 0.0
        
        # Validar suma de factores F08-F16 (debe ser <= 1)
        suma_factores = sum(factores[f'F{i:02d}'] for i in range(8, 17))
        if suma_factores > 1.0:
            print(f"ERROR fila {idx}: Suma de factores F08-F16 ({suma_factores}) excede 1.0")
            continue
        
        print(f"Fila {idx}: {corredora_nombre} - {instrumento_nombre} - Ejercicio {ejercicio}")
        print(f"  Factores cargados: {len(factores)}")
        print(f"  Suma F08-F16: {suma_factores}")


def ejemplo_importacion_carga_monto():
    """
    Ejemplo de importación "Carga x Monto".
    
    El CSV debe incluir:
    - Campos de identificación: Corredora, Instrumento, Ejercicio, Secuencia Evento, Fecha Pago
    - 30 montos: M08, M09, ..., M37
    - Los factores (F08-F37) se calculan automáticamente desde los montos:
      Factor = Monto / Suma Total de Montos
    """
    
    csv_content = """sep=;
Corredora;Instrumento;Ejercicio;Secuencia Evento;Fecha Pago;Descripción;M08;M09;M10;...;M37
Banco de Chile;ACCION COMUN;2024;1;2024-12-31;Dividendo anual;100000;50000;80000;...;20000
Banco Santander;ACCION PREFERENTE;2024;1;2024-12-31;Dividendo preferente;120000;60000;90000;...;30000"""
    
    headers, rows, delimiter = parse_csv_import(csv_content)
    
    # Procesar cada fila
    for idx, row in enumerate(rows, start=2):
        # Obtener montos M08-M37
        montos = {}
        for i in range(8, 38):
            codigo = f'M{i:02d}'
            monto_key = codigo.lower()
            valor = get_cell(row, headers, monto_key, f'monto {monto_key}', default='0')
            montos[codigo] = float(valor) if valor else 0.0
        
        # Calcular suma total de montos
        suma_montos = sum(montos.values())
        
        # Calcular factores desde montos
        factores = {}
        if suma_montos > 0:
            for codigo, monto in montos.items():
                factor = monto / suma_montos
                factores[codigo.replace('M', 'F')] = factor  # Convertir M08 -> F08
        
        print(f"Fila {idx}: Suma Montos = {suma_montos}")
        print(f"  Factores calculados: {len(factores)}")
        print(f"  Suma Factores: {sum(factores.values())}")


# ============================================================================
# PARTE 5: FLUJO COMPLETO (EXPORTAR Y REIMPORTAR)
# ============================================================================

def flujo_completo_exportar_importar():
    """
    Demostrar flujo completo: Exportar CSV y luego reimportarlo.
    
    Este es el caso de uso real: El usuario exporta datos desde el Mantenedor,
    los edita en Excel, y luego los reimporta usando "Carga x Factor".
    """
    
    print("=" * 70)
    print("FLUJO COMPLETO: EXPORTAR -> EDITAR EN EXCEL -> REIMPORTAR")
    print("=" * 70)
    
    # 1. EXPORTAR: Generar CSV desde el sistema
    print("\n1. EXPORTAR: Generando CSV de exportación...")
    csv_exportado = ejemplo_exportacion_mantenedor()
    
    # Guardar a archivo (simulado)
    print(f"   CSV generado: {len(csv_exportado)} caracteres")
    print(f"   Incluye BOM UTF-8: {csv_exportado.startswith('\ufeff')}")
    print(f"   Incluye sep=;: {csv_exportado.startswith('sep=') or csv_exportado.split('\n')[0].startswith('sep=')}")
    
    # 2. SIMULAR: Usuario edita en Excel y guarda
    print("\n2. SIMULAR: Usuario edita en Excel...")
    print("   - Excel reconoce UTF-8 gracias al BOM")
    print("   - Excel usa ';' como delimitador gracias a 'sep=;'")
    print("   - Usuario modifica algunos valores y guarda")
    
    # 3. REIMPORTAR: Leer CSV editado
    print("\n3. REIMPORTAR: Procesando CSV editado...")
    
    # CSV editado (simulado)
    csv_editado = """sep=;
País;Moneda;Ejercicio;Instrumento;Fecha Pago;Descripción;Estado;Corredora;Origen;Acogido SFUT;Factor Actualización;Secuencia Evento;Valor Histórico;F08;F09;F10
Chile;CLP;2024;ACCION COMUN;2024-12-31;Dividendo anual EDITADO;validada;Banco de Chile;SII;Sí;1.50000000;1;1000000.00;0.15;0.06;0.09"""
    
    headers, rows, delimiter = parse_csv_import(csv_editado)
    
    print(f"   Delimitador detectado: {delimiter}")
    print(f"   Headers encontrados: {len(headers)}")
    print(f"   Filas de datos: {len(rows)}")
    
    # 4. VALIDAR: Verificar headers requeridos
    print("\n4. VALIDAR: Verificando headers requeridos...")
    headers_requeridos = ['corredora', 'instrumento', 'ejercicio', 'secuencia evento', 'fecha pago']
    headers_encontrados = [normalize_header(h) for h in headers]
    
    for header_req in headers_requeridos:
        encontrado = header_req in headers_encontrados
        status = "[OK]" if encontrado else "[X]"
        print(f"   {status} {header_req}: {'ENCONTRADO' if encontrado else 'FALTANTE'}")
    
    # 5. MAPEAR: Convertir valores legibles a IDs técnicos
    print("\n5. MAPEAR: Convirtiendo valores legibles a IDs técnicos...")
    print("   - 'Banco de Chile' (nombre) -> buscar ID en tabla 'corredora'")
    print("   - 'ACCION COMUN' (nombre) -> buscar ID en tabla 'instrumento'")
    print("   - 'SII' (nombre) -> buscar ID en tabla 'fuente'")
    
    # 6. GUARDAR: Insertar/actualizar en base de datos
    print("\n6. GUARDAR: Insertando/actualizando en base de datos...")
    print("   - Buscar calificación existente por (corredora, instrumento, ejercicio, secuencia_evento)")
    print("   - Si existe: UPDATE")
    print("   - Si no existe: INSERT")
    print("   - Guardar factores F08-F37 en tabla 'calificacion_factor_detalle'")
    
    print("\n" + "=" * 70)
    print("FLUJO COMPLETO FINALIZADO")
    print("=" * 70)


# ============================================================================
# MAIN: Ejecutar ejemplos
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("EJEMPLOS DE LÓGICA DE CSVs - PROYECTO NUAM")
    print("=" * 70)
    
    # Ejemplo 1: Generar CSV de exportación
    print("\n" + "-" * 70)
    print("EJEMPLO 1: Generación de CSV de Mantenedor")
    print("-" * 70)
    csv_export = ejemplo_exportacion_mantenedor()
    print(f"CSV generado ({len(csv_export)} caracteres)")
    # Mostrar sin BOM para evitar error de codificación
    csv_display = csv_export[1:] if csv_export.startswith('\ufeff') else csv_export
    print(f"Primeras líneas (sin BOM):")
    print(csv_display.split('\n')[:3])
    
    # Ejemplo 2: Parsear CSV de importación
    print("\n" + "-" * 70)
    print("EJEMPLO 2: Importación 'Carga x Factor'")
    print("-" * 70)
    ejemplo_importacion_carga_factor()
    
    # Ejemplo 3: Importación con montos
    print("\n" + "-" * 70)
    print("EJEMPLO 3: Importación 'Carga x Monto'")
    print("-" * 70)
    ejemplo_importacion_carga_monto()
    
    # Ejemplo 4: Flujo completo
    print("\n" + "-" * 70)
    flujo_completo_exportar_importar()
    
    print("\n[OK] Todos los ejemplos completados.")
    print("\nNOTA: Este es un script de ejemplo temporal.")
    print("      En el proyecto real, esta lógica está distribuida en:")
    print("      - Frontend: templates/static/js/mantenedor/core.js (buildCsvContent)")
    print("      - Backend: api/views.py (upload_factores, upload_montos)")
    print("\n")

