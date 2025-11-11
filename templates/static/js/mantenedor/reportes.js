/**
 * reportes.js - Módulo de Reportes y Exportación
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - Exportar calificaciones a CSV
 * - Exportar a Excel (placeholder)
 * - Exportar a PDF (placeholder)
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
 * Exportar calificaciones a CSV (Tab Reportes)
 * Formato más completo que el del header de tabla
 */
export function exportarCSV() {
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
 * Exportar a Excel (backend genera .xlsx)
 */
export async function exportarExcel() {
    try {
        // Llamar al backend que genera el Excel
        const response = await fetch(`${API_BASE_URL}/calificaciones/export_excel/`, {
            method: 'GET',
            credentials: 'include' // Incluir cookies para autenticación
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            console.warn('Excel no disponible, usando CSV. Detalle:', errorData);
            exportarCSV();
            return;
        }
        
        // Descargar el archivo
        const blob = await response.blob();
        const filename = `calificaciones_${new Date().toISOString().split('T')[0]}.xlsx`;
        downloadBlob(blob, filename);
        
    } catch (error) {
        console.warn('Excel no disponible (excepción), usando CSV:', error);
        exportarCSV();
    }
}

/**
 * Exportar a PDF (backend genera .pdf)
 */
export async function exportarPDF() {
    try {
        // Llamar al backend que genera el PDF
        const response = await fetch(`${API_BASE_URL}/calificaciones/export_pdf/`, {
            method: 'GET',
            credentials: 'include' // Incluir cookies para autenticación
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            console.warn('PDF no disponible, usando CSV. Detalle:', errorData);
            exportarCSV();
            return;
        }
        
        // Descargar el archivo
        const blob = await response.blob();
        const filename = `calificaciones_${new Date().toISOString().split('T')[0]}.pdf`;
        downloadBlob(blob, filename);
        
    } catch (error) {
        console.warn('PDF no disponible (excepción), usando CSV:', error);
        exportarCSV();
    }
}

