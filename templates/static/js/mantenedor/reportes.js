/**
 * reportes.js - Módulo de Reportes y Exportación
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - Exportar calificaciones a CSV (con fallback a sistema antiguo)
 * - Exportar a Excel (intenta microservicio, fallback a sistema antiguo CSV)
 * - Exportar a PDF (intenta microservicio, fallback a sistema antiguo CSV)
 * 
 * Estrategia: Intentar usar microservicio primero, si falla usar sistema antiguo JavaScript
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
 * Esta es la función de fallback que funciona sin microservicio
 */
function exportarCSV_SistemaAntiguo() {
    if (calificacionesData.length === 0) {
        alert('No hay calificaciones para exportar');
        return;
    }
    
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
 * Intenta usar microservicio, si falla usa sistema antiguo (CSV)
 */
export async function exportarExcel() {
    try {
        // Intentar usar el microservicio primero (o fallback de Django)
        const response = await fetch('/calificaciones/exportar/excel/', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            // Verificar si la respuesta es un Excel válido o un HTML de error
            const contentType = response.headers.get('content-type') || '';
            
            if (contentType.includes('text/html')) {
                // Es un mensaje de error HTML, usar sistema antiguo
                console.warn('Microservicio no disponible para Excel (HTML de error recibido), usando sistema antiguo (CSV)');
                alert('Excel no disponible sin microservicio. Se exportará como CSV usando datos de la tabla.');
                exportarCSV_SistemaAntiguo();
                return;
            }
            
            // Es un Excel válido, descargar archivo
            const blob = await response.blob();
            const filename = `Reporte_Calificaciones_NUAM_${new Date().toISOString().split('T')[0]}.xlsx`;
            downloadBlob(blob, filename);
            return;
        }
        
        // Si el microservicio falla (código de error), usar sistema antiguo
        console.warn(`Microservicio no disponible para Excel (status ${response.status}), usando sistema antiguo (CSV)`);
        alert('Excel no disponible sin microservicio. Se exportará como CSV usando datos de la tabla.');
        exportarCSV_SistemaAntiguo();
        
    } catch (error) {
        // Error de conexión, usar sistema antiguo
        console.warn('Error al conectar con microservicio, usando sistema antiguo (CSV):', error);
        alert('Excel no disponible sin microservicio. Se exportará como CSV usando datos de la tabla.');
        exportarCSV_SistemaAntiguo();
    }
}

/**
 * Exportar a PDF
 * Intenta usar microservicio, si falla usa sistema antiguo (CSV)
 */
export async function exportarPDF() {
    try {
        // Intentar usar el microservicio primero (o fallback de Django)
        const response = await fetch('/calificaciones/exportar/pdf/', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            // Verificar si la respuesta es un PDF válido o un HTML de error
            const contentType = response.headers.get('content-type') || '';
            
            if (contentType.includes('text/html')) {
                // Es un mensaje de error HTML, usar sistema antiguo
                console.warn('Microservicio no disponible para PDF (HTML de error recibido), usando sistema antiguo (CSV)');
                alert('PDF no disponible sin microservicio. Se exportará como CSV usando datos de la tabla.');
                exportarCSV_SistemaAntiguo();
                return;
            }
            
            // Es un PDF válido, descargar archivo
            const blob = await response.blob();
            const filename = `Reporte_Calificaciones_NUAM_${new Date().toISOString().split('T')[0]}.pdf`;
            downloadBlob(blob, filename);
            return;
        }
        
        // Si el microservicio falla (código de error), usar sistema antiguo
        console.warn(`Microservicio no disponible para PDF (status ${response.status}), usando sistema antiguo (CSV)`);
        alert('PDF no disponible sin microservicio. Se exportará como CSV usando datos de la tabla.');
        exportarCSV_SistemaAntiguo();
        
    } catch (error) {
        // Error de conexión, usar sistema antiguo
        console.warn('Error al conectar con microservicio, usando sistema antiguo (CSV):', error);
        alert('PDF no disponible sin microservicio. Se exportará como CSV usando datos de la tabla.');
        exportarCSV_SistemaAntiguo();
    }
}

