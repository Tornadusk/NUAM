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
    // Cambiar al tab Cargas Masivas
    const cargasTab = document.getElementById('cargas-tab');
    if (cargasTab) {
        const tab = new bootstrap.Tab(cargasTab);
        tab.show();
    }
}

export function abrirModalCargaMonto() {
    // Cambiar al tab Cargas Masivas
    const cargasTab = document.getElementById('cargas-tab');
    if (cargasTab) {
        const tab = new bootstrap.Tab(cargasTab);
        tab.show();
    }
}

/**
 * Descargar formato CSV para carga masiva
 */
export function descargarFormatoCSV() {
    window.location.href = '/static/files/formato_carga_factor.csv';
}

/**
 * Mostrar preview de factores calculados
 */
function mostrarPreviewFactores(data) {
    // Crear o actualizar contenedor de preview
    let previewContainer = document.getElementById('previewFactores');
    if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.id = 'previewFactores';
        previewContainer.className = 'mt-3';
        const form = document.getElementById('formCargaMonto');
        if (form) {
            form.appendChild(previewContainer);
        }
    }
    
    if (!data.preview || data.preview.length === 0) {
        previewContainer.innerHTML = '<div class="alert alert-warning">No hay datos para mostrar en el preview</div>';
        return;
    }
    
    // Mostrar tabla de preview (máximo 5 filas)
    const previewRows = data.preview.slice(0, 5);
    let html = '<div class="card"><div class="card-header"><h6 class="mb-0">Preview de Factores Calculados</h6></div><div class="card-body"><div class="table-responsive" style="max-height: 300px;"><table class="table table-sm table-bordered"><thead><tr><th>Línea</th><th>Suma Montos</th><th>Suma Factores</th><th>Factores (F08-F37)</th></tr></thead><tbody>';
    
    previewRows.forEach(row => {
        const factoresList = Object.keys(row.factores).map(k => `${k}: ${parseFloat(row.factores[k]).toFixed(6)}`).join(', ');
        html += `<tr>
            <td>${row.linea}</td>
            <td>${parseFloat(row.suma_montos).toFixed(2)}</td>
            <td>${parseFloat(row.suma_factores).toFixed(6)}</td>
            <td><small>${factoresList || 'N/A'}</small></td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    if (data.preview.length > 5) {
        html += `<p class="text-muted mt-2"><small>Mostrando 5 de ${data.preview.length} filas</small></p>`;
    }
    html += '</div></div>';
    
    previewContainer.innerHTML = html;
}

/**
 * Descargar formato Excel para carga masiva
 */
export async function descargarFormatoExcel() {
    try {
        const csrfToken = getCookie('csrftoken');
        const res = await fetch(`${API_BASE_URL}/cargas/download_template/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            },
            credentials: 'include' // Incluir cookies para autenticación
        });
        
        if (!res.ok) {
            const errorData = await res.text();
            console.error('Error al descargar formato Excel:', errorData);
            alert('Error al descargar formato Excel. Ver consola (F12) para detalles.');
            return;
        }
        
        // Obtener blob
        const blob = await res.blob();
        
        // Crear URL temporal y descargar
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'formato_carga_factor.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error al descargar formato Excel:', error);
        alert('Error al descargar formato Excel. Ver consola (F12) para detalles.');
    }
}

/**
 * Procesar carga de archivo con factores
 */
/**
 * Descargar formato Excel para carga masiva
 */
export async function descargarFormatoExcelMontos() {
    try {
        const csrfToken = getCookie('csrftoken');
        const res = await fetch(`${API_BASE_URL}/cargas/download_template_montos/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            },
            credentials: 'include'
        });
        
        if (!res.ok) {
            const errorData = await res.text();
            console.error('Error al descargar formato Excel:', errorData);
            alert('Error al descargar formato Excel. Ver consola (F12) para detalles.');
            return;
        }
        
        // Obtener blob
        const blob = await res.blob();
        
        // Crear URL temporal y descargar
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'formato_carga_monto.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error al descargar formato Excel:', error);
        alert('Error al descargar formato Excel. Ver consola (F12) para detalles.');
    }
}

/**
 * Procesar carga de archivo con factores
 */
export async function cargarFactor(event) {
    if (event) event.preventDefault();
    
    const form = event.target;
    const fileInput = form.querySelector('input[type="file"]');
    
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Por favor seleccione un archivo CSV o Excel');
        return;
    }
    
    const file = fileInput.files[0];
    const isCsv = file.name.endsWith('.csv');
    const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
    
    if (!isCsv && !isExcel) {
        alert('El archivo debe ser CSV o Excel (.xlsx, .xls)');
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
            
            // Limpiar formulario
            form.reset();
            
            // Recargar calificaciones automáticamente después de carga masiva
            recargarCalificacionesDespuesDeCarga();
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
 * Procesar carga de archivo con montos (grabar después de calcular factores)
 */
export async function cargarMonto(event) {
    if (event) event.preventDefault();
    
    const form = event.target;
    const fileInput = form.querySelector('input[type="file"]');
    
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Por favor seleccione un archivo CSV o Excel');
        return;
    }
    
    const file = fileInput.files[0];
    const isCsv = file.name.endsWith('.csv');
    const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
    
    if (!isCsv && !isExcel) {
        alert('El archivo debe ser CSV o Excel (.xlsx, .xls)');
        return;
    }
    
    // Verificar que se hayan calculado factores primero
    if (!previewFactores || !previewFactores.preview || previewFactores.preview.length === 0) {
        alert('Por favor calcule los factores primero haciendo clic en "Calcular Factores"');
        return;
    }
    
    // Mostrar indicador de carga
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Grabando...';
    
    try {
        // Enviar archivo al backend para grabar
        const formData = new FormData();
        formData.append('file', file);
        
        const csrfToken = getCookie('csrftoken');
        const res = await fetch(`${API_BASE_URL}/cargas/upload_montos/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });
        
        const text = await res.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error('Respuesta no JSON:', text);
            alert('Error del servidor. Ver consola (F12) para detalles.');
            return;
        }
        
        if (res.ok) {
            let mensaje = `Carga completada:\n\n` +
                         `Filas totales: ${data.filas_total}\n` +
                         `Insertadas: ${data.insertados}\n` +
                         `Rechazadas: ${data.rechazados}`;
            
            if (data.errores && data.errores.length > 0) {
                const erroresTexto = data.errores.map(e => `Línea ${e.linea}: ${e.error}`).join('\n');
                mensaje += '\n\nErrores:\n' + erroresTexto;
            }
            
            alert(mensaje);
            
            // Limpiar formulario y preview
            form.reset();
            previewFactores = null;
            const previewContainer = document.getElementById('previewFactores');
            if (previewContainer) {
                previewContainer.innerHTML = '';
            }
            
            // Ocultar barra de progreso
            const progress = document.getElementById('progressCalculo');
            if (progress) {
                progress.style.display = 'none';
                const bar = progress.querySelector('.progress-bar');
                if (bar) {
                    bar.style.width = '0%';
                    bar.classList.remove('bg-success');
                }
            }
            
            // Deshabilitar botón "Grabar"
            btn.disabled = true;
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
            
            // Recargar calificaciones automáticamente después de carga masiva
            recargarCalificacionesDespuesDeCarga();
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
 * Variable global para almacenar preview de factores
 */
let previewFactores = null;

/**
 * Calcular factores desde montos (mostrar preview antes de grabar)
 */
export async function calcularFactores() {
    const form = document.getElementById('formCargaMonto');
    if (!form) {
        alert('Formulario de carga de montos no encontrado');
        return;
    }
    
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Por favor seleccione un archivo CSV o Excel');
        return;
    }
    
    const file = fileInput.files[0];
    const isCsv = file.name.endsWith('.csv');
    const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
    
    if (!isCsv && !isExcel) {
        alert('El archivo debe ser CSV o Excel (.xlsx, .xls)');
        return;
    }
    
    // Mostrar barra de progreso
    const progress = document.getElementById('progressCalculo');
    if (progress) {
        progress.style.display = 'block';
        const bar = progress.querySelector('.progress-bar');
        if (bar) {
            bar.style.width = '0%';
            bar.textContent = 'Calculando...';
        }
    }
    
    try {
        // Enviar archivo al backend para calcular factores
        const formData = new FormData();
        formData.append('file', file);
        
        const csrfToken = getCookie('csrftoken');
        const res = await fetch(`${API_BASE_URL}/cargas/calculate_factores/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });
        
        const text = await res.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error('Respuesta no JSON:', text);
            alert('Error del servidor. Ver consola (F12) para detalles.');
            return;
        }
        
        if (res.ok) {
            // Guardar preview para usar en cargarMonto
            previewFactores = data;
            
            // Mostrar preview en UI
            mostrarPreviewFactores(data);
            
            // Habilitar botón "Grabar"
            const btnGrabar = form.querySelector('button[type="submit"]');
            if (btnGrabar) {
                btnGrabar.disabled = false;
                btnGrabar.classList.remove('btn-secondary');
                btnGrabar.classList.add('btn-primary');
            }
            
            // Mostrar resumen
            let mensaje = `Cálculo completado:\n\n` +
                         `Filas totales: ${data.total_filas}\n` +
                         `Válidas: ${data.validas}\n` +
                         `Rechazadas: ${data.rechazadas}`;
            
            if (data.errores && data.errores.length > 0) {
                const erroresTexto = data.errores.map(e => `Línea ${e.linea}: ${e.error}`).join('\n');
                mensaje += '\n\nErrores:\n' + erroresTexto;
            }
            
            alert(mensaje);
            
            // Actualizar barra de progreso
            if (progress) {
                const bar = progress.querySelector('.progress-bar');
                if (bar) {
                    bar.style.width = '100%';
                    bar.classList.add('bg-success');
                    bar.textContent = 'Cálculo completado';
                }
            }
        } else {
            alert('Error al calcular factores: ' + (data.error || JSON.stringify(data)));
            
            // Ocultar barra de progreso en caso de error
            if (progress) {
                progress.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al calcular factores. Ver consola (F12) para detalles.');
        
        // Ocultar barra de progreso en caso de error
        if (progress) {
            progress.style.display = 'none';
        }
    }
}

/**
 * Función helper para recargar calificaciones después de carga masiva
 */
function recargarCalificacionesDespuesDeCarga() {
    if (!window.cargarCalificaciones) {
        console.warn('cargarCalificaciones no está disponible');
        return;
    }
    
    // Verificar si el tab Mantenedor está visible
    const mantenedorPane = document.getElementById('mantenedor');
    const isMantenedorVisible = mantenedorPane && 
        (mantenedorPane.classList.contains('show') || mantenedorPane.classList.contains('active'));
    
    if (isMantenedorVisible) {
        // Si ya está visible, recargar directamente
        console.log('Tab Mantenedor visible, recargando calificaciones...');
        setTimeout(() => {
            window.cargarCalificaciones();
        }, 300);
    } else {
        // Si no está visible, cambiar al tab y luego recargar
        console.log('Cambiando al tab Mantenedor y recargando calificaciones...');
        const mantenedorTab = document.getElementById('mantenedor-tab');
        if (mantenedorTab) {
            const tab = new bootstrap.Tab(mantenedorTab);
            tab.show();
            
            // Esperar a que se active el tab antes de cargar
            mantenedorTab.addEventListener('shown.bs.tab', function() {
                setTimeout(() => {
                    window.cargarCalificaciones();
                }, 300);
            }, { once: true });
        } else {
            // Si no existe el tab, intentar recargar de todas formas
            setTimeout(() => {
                window.cargarCalificaciones();
            }, 500);
        }
    }
}
