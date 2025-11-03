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
 * Exportar calificaciones a CSV (Tab Reportes)
 * Formato más completo que el del header de tabla
 */
export function exportarCSV() {
    if (calificacionesData.length === 0) {
        alert('No hay calificaciones para exportar');
        return;
    }
    
    // Preparar headers (más completos que el CSV de tabla)
    const headers = [
        'ID', 'Corredora', 'País', 'Instrumento', 'Moneda', 'Ejercicio', 
        'Fecha Pago', 'Descripción', 'Estado', 'Secuencia Evento', 
        'Factor Actualización', 'Acogido SFUT', 'Creado En', 'Actualizado En'
    ];
    
    // Preparar filas
    const rows = calificacionesData.map(cal => [
        cal.id_calificacion || '',
        cal.id_corredora_nombre || '',
        cal.id_corredora_pais_nombre || '',
        cal.id_instrumento_nombre || '',
        cal.id_moneda_codigo || '',
        cal.ejercicio || '',
        cal.fecha_pago || '',
        (cal.descripcion || '').replace(/"/g, '""'), // Escapar comillas
        cal.estado || '',
        cal.secuencia_evento || '',
        cal.factor_actualizacion || '',
        cal.acogido_sfut ? 'Sí' : 'No',
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
            console.error('Error del servidor:', errorData);
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        // Descargar el archivo
        const blob = await response.blob();
        const filename = `calificaciones_${new Date().toISOString().split('T')[0]}.xlsx`;
        downloadBlob(blob, filename);
        
    } catch (error) {
        console.error('Error al exportar Excel:', error);
        const usarCSV = confirm(
            '⚠️ Error al generar Excel desde backend.\n\n' +
            '¿Deseas descargar el reporte como CSV?\n' +
            '(Excel puede abrir archivos CSV automáticamente)'
        );
        if (usarCSV) {
            exportarCSV();
        }
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
            console.error('Error del servidor:', errorData);
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        // Descargar el archivo
        const blob = await response.blob();
        const filename = `calificaciones_${new Date().toISOString().split('T')[0]}.pdf`;
        downloadBlob(blob, filename);
        
    } catch (error) {
        console.error('Error al exportar PDF:', error);
        const usarCSV = confirm(
            '⚠️ Error al generar PDF desde backend.\n\n' +
            '¿Deseas descargar el reporte como CSV?\n' +
            '(Puedes convertir CSV a PDF en Excel o Google Sheets)'
        );
        if (usarCSV) {
            exportarCSV();
        }
    }
}

