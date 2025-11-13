# Flujo de Descarga de Archivos Excel

## Resumen
Los archivos Excel **NO se guardan en el servidor**. Se generan en memoria y se envían directamente al navegador del usuario.

## Flujo Completo

### 1. Usuario hace clic en "Descargar Excel"
   - Frontend: `descargarFormatoExcel()` o `exportarExcel()`
   - Ubicación: `templates/static/js/mantenedor/cargas.js` o `reportes.js`

### 2. Frontend hace petición al backend
   ```javascript
   fetch('/api/cargas/download_template/')  // Para formato de carga
   fetch('/api/calificaciones/export_excel/')  // Para exportar calificaciones
   ```

### 3. Backend genera Excel en memoria
   ```python
   # api/views.py
   buffer = io.BytesIO()  # Buffer en memoria RAM (NO en disco)
   wb = Workbook()        # Crear workbook
   wb.save(buffer)        # Guardar en buffer
   buffer.seek(0)         # Volver al inicio
   
   # Enviar como respuesta HTTP
   response = HttpResponse(
       buffer.read(),
       content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
   )
   response['Content-Disposition'] = 'attachment; filename="archivo.xlsx"'
   return response
   ```

### 4. Frontend recibe el archivo
   ```javascript
   const blob = await response.blob();  // Convertir a Blob
   const url = window.URL.createObjectURL(blob);  // Crear URL temporal
   
   // Crear link de descarga
   const link = document.createElement('a');
   link.href = url;
   link.download = 'archivo.xlsx';
   link.click();  // Descargar
   
   // Limpiar
   window.URL.revokeObjectURL(url);
   ```

### 5. Navegador descarga el archivo
   - El archivo se guarda en la carpeta de **Descargas** del usuario
   - Ubicación típica:
     - Windows: `C:\Users\[Usuario]\Downloads\`
     - Mac: `~/Downloads/`
     - Linux: `~/Downloads/`

## Ventajas de este enfoque

1. **No ocupa espacio en el servidor**: Los archivos no se guardan en disco
2. **Siempre actualizado**: Cada descarga genera un archivo nuevo con datos actuales
3. **Seguro**: No hay archivos residuales en el servidor
4. **Eficiente**: Se genera solo cuando el usuario lo solicita

## Archivos relacionados

### Backend
- `api/views.py`:
  - `CargaViewSet.download_template()`: Genera formato Excel para carga
  - `CalificacionViewSet.export_excel()`: Exporta calificaciones a Excel

### Frontend
- `templates/static/js/mantenedor/cargas.js`:
  - `descargarFormatoExcel()`: Descarga formato Excel
- `templates/static/js/mantenedor/reportes.js`:
  - `exportarExcel()`: Exporta calificaciones a Excel
- `templates/static/js/mantenedor/core.js`:
  - `downloadBlob()`: Función helper para descargar archivos

## Notas importantes

1. **No se guarda en el servidor**: El Excel se genera en memoria y se envía directamente
2. **Buffer en memoria**: Usa `io.BytesIO()` para generar en RAM
3. **Descarga automática**: El navegador descarga automáticamente gracias al header `Content-Disposition: attachment`
4. **Carpeta de descargas**: El archivo se guarda en la carpeta de descargas configurada en el navegador del usuario

