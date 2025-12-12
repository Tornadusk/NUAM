/**
 * reportes.js - Módulo de Reportes y Exportación
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - Exportar calificaciones a CSV (con fallback a sistema antiguo JavaScript)
 * - Exportar a Excel (Microservicio → Fallback Django openpyxl → Error)
 * - Exportar a PDF (Microservicio → Fallback Django reportlab → Error)
 * 
 * Estrategia de Exportación:
 * - CSV: 1) Microservicio → 2) Fallback Django → 3) Sistema antiguo JavaScript
 * - Excel: 1) Microservicio → 2) Fallback Django (openpyxl) → 3) Mostrar error HTML
 * - PDF: 1) Microservicio → 2) Fallback Django (reportlab) → 3) Mostrar error HTML
 * 
 * IMPORTANTE: Los datos SIEMPRE vienen de la API REST de Django (/api/calificaciones/)
 * que es cargada por calificaciones.js. El microservicio es solo opcional para la 
 * generación del archivo. El fallback de Django también genera PDF/Excel usando reportlab/openpyxl.
 */

import { API_BASE_URL, downloadBlob, buildCsvContent, CALIFICACION_REPORT_HEADERS, buildReportCalificacionRow } from './core.js';

// Variable global que será compartida con calificaciones.js
export let calificacionesData = [];

/**
 * Establecer datos de calificaciones (llamado desde calificaciones.js)
 */
export function setCalificacionesData(data) {
    calificacionesData = data;
}

/**
 * Exportar calificaciones a CSV usando sistema antiguo (JavaScript - Cliente)
 * Esta es la función de fallback que funciona sin microservicio.
 * 
 * NOTA: Los datos vienen de la API REST de Django (/api/calificaciones/)
 * que son cargados por calificaciones.js y almacenados en calificacionesData.
 * Esta función genera el CSV directamente en el navegador usando esos datos.
 */
function exportarCSV_SistemaAntiguo() {
    if (calificacionesData.length === 0) {
        alert('No hay calificaciones para exportar');
        return;
    }
    
    // calificacionesData viene de la API REST de Django (cargada por calificaciones.js)
    const rows = calificacionesData.map(cal => buildReportCalificacionRow(cal));
    const csvContent = buildCsvContent(CALIFICACION_REPORT_HEADERS, rows, { excelSepHint: true });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const filename = `calificaciones_completo_${new Date().toISOString().split('T')[0]}.csv`;
    downloadBlob(blob, filename);
}

/**
 * Exportar calificaciones a CSV (Tab Reportes)
 * Intenta usar microservicio, si falla usa sistema antiguo
 */
export async function exportarCSV() {
    try {
        // Intentar usar el microservicio primero (o fallback de Django)
        const response = await fetch('/calificaciones/exportar/csv/', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            // Verificar si la respuesta es un CSV válido o un HTML de error
            const contentType = response.headers.get('content-type') || '';
            
            if (contentType.includes('text/html')) {
                // Es un mensaje de error HTML, usar sistema antiguo
                console.warn('Microservicio no disponible (HTML de error recibido), usando sistema antiguo (CSV JavaScript)');
                exportarCSV_SistemaAntiguo();
                return;
            }
            
            // Es un CSV válido, descargar archivo
            const blob = await response.blob();
            const filename = `Reporte_Calificaciones_NUAM_${new Date().toISOString().split('T')[0]}.csv`;
            downloadBlob(blob, filename);
            return;
        }
        
        // Si el microservicio falla (código de error), usar sistema antiguo
        console.warn(`Microservicio no disponible (status ${response.status}), usando sistema antiguo (CSV JavaScript)`);
        exportarCSV_SistemaAntiguo();
        
    } catch (error) {
        // Error de conexión, usar sistema antiguo
        console.warn('Error al conectar con microservicio, usando sistema antiguo (CSV JavaScript):', error);
        exportarCSV_SistemaAntiguo();
    }
}

/**
 * Exportar a Excel
 * Flujo: 1) Microservicio → 2) Fallback Django (openpyxl) → 3) Error HTML
 */
export async function exportarExcel() {
    try {
        // Intentar usar el microservicio primero, o fallback de Django (openpyxl)
        const response = await fetch('/calificaciones/exportar/excel/', {
            method: 'GET',
            credentials: 'include'
        });
        
        // Verificar el tipo de contenido
        const contentType = response.headers.get('content-type') || '';
        
        if (response.ok && !contentType.includes('text/html')) {
            // Es un Excel válido (del microservicio o del fallback de Django)
            const blob = await response.blob();
            const filename = `Reporte_Calificaciones_NUAM_${new Date().toISOString().split('T')[0]}.xlsx`;
            downloadBlob(blob, filename);
            return;
        }
        
        // Si es HTML, mostrar el mensaje de error de Django
        if (contentType.includes('text/html')) {
            const htmlContent = await response.text();
            // Mostrar el HTML de error en una ventana nueva
            const errorWindow = window.open('', '_blank');
            errorWindow.document.write(htmlContent);
            console.warn('Excel no disponible: Django devolvió mensaje HTML de error');
            return;
        }
        
        // Si llegamos aquí, hay un error HTTP
        console.error(`Error al exportar Excel: HTTP ${response.status}`);
        alert(`Error al exportar Excel. Estado HTTP: ${response.status}`);
        
    } catch (error) {
        // Error de conexión
        console.error('Error de conexión al exportar Excel:', error);
        alert('Error de conexión al exportar Excel. Verifica que el servidor esté disponible.');
    }
}

/**
 * Exportar a PDF
 * Flujo: 1) Microservicio → 2) Fallback Django (reportlab) → 3) Error HTML
 */
export async function exportarPDF() {
    try {
        // Intentar usar el microservicio primero, o fallback de Django (reportlab)
        const response = await fetch('/calificaciones/exportar/pdf/', {
            method: 'GET',
            credentials: 'include'
        });
        
        // Verificar el tipo de contenido
        const contentType = response.headers.get('content-type') || '';
        
        if (response.ok && !contentType.includes('text/html')) {
            // Es un PDF válido (del microservicio o del fallback de Django)
            const blob = await response.blob();
            const filename = `Reporte_Calificaciones_NUAM_${new Date().toISOString().split('T')[0]}.pdf`;
            downloadBlob(blob, filename);
            return;
        }
        
        // Si es HTML, mostrar el mensaje de error de Django
        if (contentType.includes('text/html')) {
            const htmlContent = await response.text();
            // Mostrar el HTML de error en una ventana nueva
            const errorWindow = window.open('', '_blank');
            errorWindow.document.write(htmlContent);
            console.warn('PDF no disponible: Django devolvió mensaje HTML de error');
            return;
        }
        
        // Si llegamos aquí, hay un error HTTP
        console.error(`Error al exportar PDF: HTTP ${response.status}`);
        alert(`Error al exportar PDF. Estado HTTP: ${response.status}`);
        
    } catch (error) {
        // Error de conexión
        console.error('Error de conexión al exportar PDF:', error);
        alert('Error de conexión al exportar PDF. Verifica que el servidor esté disponible.');
    }
}


