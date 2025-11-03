/**
 * reportes.js - Módulo de Reportes y Exportación
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - Exportar calificaciones a CSV
 * - Exportar a Excel (placeholder)
 * - Exportar a PDF (placeholder)
 */

import { API_BASE_URL } from './core.js';
import { downloadBlob } from './core.js';

// Variable global que será compartida con calificaciones.js
export let calificacionesData = [];

/**
 * Establecer datos de calificaciones (llamado desde calificaciones.js)
 */
export function setCalificacionesData(data) {
    calificacionesData = data;
}

/**
 * Exportar calificaciones a CSV
 */
export function exportarCSV() {
    if (calificacionesData.length === 0) {
        alert('No hay calificaciones para exportar');
        return;
    }
    
    // Preparar headers
    const headers = [
        'ID', 'Corredora', 'Instrumento', 'Ejercicio', 'Fecha Pago', 
        'Descripción', 'Estado', 'Creado En', 'Actualizado En'
    ];
    
    // Preparar filas
    const rows = calificacionesData.map(cal => [
        cal.id_calificacion || '',
        cal.id_corredora || '',
        cal.id_instrumento || '',
        cal.ejercicio || '',
        cal.fecha_pago || '',
        (cal.descripcion || '').replace(/"/g, '""'), // Escapar comillas
        cal.estado || '',
        cal.creado_en || '',
        cal.actualizado_en || ''
    ]);
    
    // Crear contenido CSV
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    // Crear blob y descargar
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const filename = `calificaciones_nuam_${new Date().toISOString().split('T')[0]}.csv`;
    downloadBlob(blob, filename);
}

/**
 * Exportar a Excel (requiere librería externa)
 */
export function exportarExcel() {
    alert('⚠️ Exportación Excel requiere librería externa (ej: xlsx.js)');
    alert('Por ahora, usa la exportación CSV que es compatible con Excel');
}

/**
 * Exportar a PDF (requiere librería externa)
 */
export function exportarPDF() {
    alert('⚠️ Exportación PDF requiere librería externa (ej: jsPDF)');
    alert('Por ahora, usa la exportación CSV para generar reportes');
}

