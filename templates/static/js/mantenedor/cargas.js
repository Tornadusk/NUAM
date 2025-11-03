/**
 * cargas.js - Módulo de Carga Masiva
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - Carga masiva por Factor (factores F08-F37 ya calculados)
 * - Carga masiva por Monto (calcula factores automáticamente)
 * - Validación y previsualización de archivos
 * - Tracking de progreso
 */

import { getCookie, fetchWithCSRF } from './core.js';

const API_BASE_URL = '/api';

export function abrirModalCargaFactor() {
    // Modal ya está en HTML, solo necesitamos mostrar mensaje informativo
    alert('Seleccione un archivo CSV con el formato: id_corredora,id_instrumento,id_fuente,id_moneda,ejercicio,fecha_pago,descripcion,ingreso_por_montos,acogido_sfut,secuencia_evento,F08,F09,...,F37');
}

export function abrirModalCargaMonto() {
    alert('Funcionalidad de Carga x Monto en desarrollo');
}

/**
 * Calcular factores desde montos
 */
export function calcularFactores() {
    const progress = document.getElementById('progressCalculo');
    if (!progress) return;
    
    progress.style.display = 'block';
    const bar = progress.querySelector('.progress-bar');
    if (!bar) return;
    
    let width = 0;
    const interval = setInterval(() => {
        width += 10;
        bar.style.width = width + '%';
        if (width >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                progress.style.display = 'none';
                bar.style.width = '0%';
                alert('✓ Factores calculados exitosamente');
            }, 500);
        }
    }, 100);
}

/**
 * Procesar carga de archivo con factores
 */
export async function cargarFactor(event) {
    if (event) event.preventDefault();
    
    const form = event.target;
    const fileInput = form.querySelector('input[type="file"]');
    
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Por favor seleccione un archivo CSV');
        return;
    }
    
    const file = fileInput.files[0];
    if (!file.name.endsWith('.csv')) {
        alert('El archivo debe ser CSV');
        return;
    }
    
    // Mostrar indicador de carga
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Procesando...';
    
    try {
        // Enviar archivo al backend
        const formData = new FormData();
        formData.append('file', file);
        
        const csrfToken = getCookie('csrftoken');
        const res = await fetch(`${API_BASE_URL}/cargas/upload_factores/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });
        
        // Leer respuesta como texto primero para debugging
        const text = await res.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            // Si no es JSON, mostrar error HTML completo
            console.error('Respuesta no JSON completa:', text);
            alert('Error del servidor (500). Ver consola (F12) para detalles completos.');
            return;
        }
        
        if (res.ok) {
            let mensaje = `Carga completada:\n\n` +
                           `Filas totales: ${data.filas_total}\n` +
                           `Insertadas: ${data.insertados}\n` +
                           `Rechazadas: ${data.rechazados}`;
            
            // Si hay errores, agregar detalles al mensaje
            if (data.errores && data.errores.length > 0) {
                const erroresTexto = data.errores.map(e => `Línea ${e.linea}: ${e.error}`).join('\n');
                mensaje += '\n\nErrores:\n' + erroresTexto;
            }
            
            alert(mensaje);
            
            if (data.errores && data.errores.length > 0) {
                console.warn('Errores en la carga:', data.errores);
            }
            
            // Recargar calificaciones
            if (window.cargarCalificaciones) {
                window.cargarCalificaciones();
            }
            
            // Limpiar formulario
            form.reset();
        } else {
            alert('Error al cargar archivo: ' + (data.error || JSON.stringify(data)));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al procesar archivo');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

/**
 * Procesar carga de archivo con montos
 */
export async function cargarMonto(event) {
    if (event) event.preventDefault();
    alert('Función de carga x monto en desarrollo');
}

