# Comparación: Carga x Factor vs Carga x Monto

## 📊 Diferencias Principales

### 1. **Columnas de Datos**

| Aspecto | Carga x Factor | Carga x Monto |
|---------|----------------|---------------|
| **Columnas** | F08, F09, F10, ..., F37 | M08, M09, M10, ..., M37 |
| **Tipo de Valores** | Factores (decimales pequeños) | Montos (valores monetarios) |
| **Ejemplo de Valores** | 0.00001, 0.00002, 0.00003 | 1000.00, 2000.00, 1500.00 |
| **Rango Típico** | 0.00001 - 1.0 (proporciones) | 100.00 - 1000000.00 (montos) |
| **Origen** | Ya calculados por el usuario | Proporcionados por el usuario |

### 2. **Columnas Adicionales**

| Columna | Carga x Factor | Carga x Monto |
|---------|----------------|---------------|
| **Ingreso por Montos** | ✅ Sí (puede ser "No") | ❌ No (siempre implícito "Sí") |

### 3. **Columnas Compartidas (Iguales en Ambos)**

```
✅ Linea
✅ ID (opcional)
✅ Corredora
✅ Instrumento
✅ Instrumento Código
✅ Fuente
✅ Moneda
✅ Ejercicio
✅ Fecha Pago
✅ Descripción
✅ Estado
✅ Acogido SFUT
✅ Secuencia Evento
✅ Valor Histórico
```

### 4. **Procesamiento en el Backend**

| Aspecto | Carga x Factor | Carga x Monto |
|---------|----------------|---------------|
| **Validación** | Valida que factores sumen ≤ 1 | Valida montos y calcula factores |
| **Cálculo** | ❌ No calcula (usa factores directos) | ✅ Calcula factores desde montos |
| **Fórmula** | N/A | `Factor = Monto / Suma Total de Montos` |
| **Almacenamiento** | `calificacion_factor_detalle` | `calificacion_monto_detalle` + `calificacion_factor_detalle` |
| **Campo `ingreso_por_montos`** | Depende del CSV (puede ser "No") | Siempre `True` |

### 5. **Flujo de Trabajo**

#### **Carga x Factor:**
1. Usuario descarga formato CSV/Excel
2. Usuario llena factores F08-F37 (ya calculados)
3. Usuario sube archivo
4. Sistema valida y graba directamente

#### **Carga x Monto:**
1. Usuario descarga formato CSV/Excel
2. Usuario llena montos M08-M37
3. Usuario sube archivo y hace clic en "Calcular Factores"
4. Sistema calcula factores y muestra preview
5. Usuario revisa preview
6. Usuario hace clic en "Grabar"
7. Sistema graba montos y factores calculados

### 6. **Ejemplo de Archivos**

#### **Carga x Factor (formato_carga_factor.csv):**
```csv
sep=;
Linea;ID;Corredora;...;Ingreso por Montos;Secuencia Evento;Valor Histórico;F08;F09;F10;...
1;;Banco de Chile;...;No;00002;0.00001000;0.00001;0.00001;0.00002;...
```

#### **Carga x Monto (formato_carga_monto.csv):**
```csv
sep=;
Linea;ID;Corredora;...;Secuencia Evento;Valor Histórico;M08;M09;M10;...
1;;Banco de Chile;...;00002;1000.00;1000.00;2000.00;1500.00;...
```

## 🎯 Cuándo Usar Cada Uno

### **Usar Carga x Factor cuando:**
- ✅ Ya tienes los factores calculados externamente
- ✅ Los factores vienen de otro sistema o cálculo previo
- ✅ Quieres ingresar factores manualmente
- ✅ Necesitas control total sobre los factores

### **Usar Carga x Monto cuando:**
- ✅ Tienes los montos (dividendos, etc.) pero no los factores
- ✅ Quieres que el sistema calcule los factores automáticamente
- ✅ Los montos vienen de fuentes externas (archivos bancarios, etc.)
- ✅ Necesitas verificar los factores antes de grabar (preview)

## ⚠️ Notas Importantes

1. **No se pueden mezclar**: Un archivo debe ser solo de factores O solo de montos, no ambos
2. **Validación**: En Carga x Factor, la suma de factores debe ser ≤ 1
3. **Cálculo en Carga x Monto**: Los factores se calculan proporcionalmente: `Factor = Monto / Suma Total`
4. **Preview**: Solo Carga x Monto tiene preview antes de grabar
5. **Campo `ingreso_por_montos`**: 
   - Carga x Factor: Puede ser "No" si se ingresan factores directos
   - Carga x Monto: Siempre es `True` (implícito)

