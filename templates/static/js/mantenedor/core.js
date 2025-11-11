/**
 * core.js - Utilidades compartidas y helpers UI
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Este módulo contiene:
 * - Configuración global (API_BASE_URL)
 * - Funciones de cookies y CSRF
 * - Helpers de UI (populateSelect, getEstadoBadgeClass, etc.)
 */

// Configuración global
export const API_BASE_URL = '/api';

/**
 * Obtener valor de una cookie por nombre
 */
export function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Obtener token CSRF de las cookies
 */
export function getCsrfToken() {
    return getCookie('csrftoken');
}

/**
 * Hacer petición fetch con CSRF token automático
 */
export async function fetchWithCSRF(url, options = {}) {
    const csrfToken = getCsrfToken();
    const method = options.method ? options.method.toUpperCase() : 'GET';
    
    // Preparar headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // Si es POST, PUT, PATCH o DELETE, agregar token CSRF
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        } else {
            console.warn('CSRF token no encontrado. Asegúrate de estar autenticado.');
        }
    }
    
    // Configurar opciones de fetch
    const fetchOptions = {
        ...options,
        method: method,
        credentials: 'include', // Incluir cookies (necesario para CSRF)
        headers: headers
    };
    
    return fetch(url, fetchOptions);
}

/**
 * Poblar un select con opciones
 */
export function populateSelect(selectId, options) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = '<option value="">Seleccione...</option>' + 
        options.map(opt => `<option value="${opt.value}">${opt.text}</option>`).join('');
}

/**
 * Obtener clase CSS para badge de estado
 */
export function getEstadoBadgeClass(estado) {
    const classes = {
        'borrador': 'bg-secondary',
        'validada': 'bg-info',
        'publicada': 'bg-success',
        'pendiente': 'bg-warning',
        'activo': 'bg-success',
        'bloqueado': 'bg-danger',
        'inactivo': 'bg-secondary',
        'activa': 'bg-success',
        'inactiva': 'bg-secondary'
    };
    return classes[estado] || 'bg-secondary';
}

/**
 * Formatear fecha para mostrar en UI
 */
export function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-CL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * Formatear número con separadores de miles
 */
export function formatNumber(num) {
    if (!num) return '0';
    return num.toLocaleString('es-CL');
}

/**
 * Validar email
 */
export function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Descargar blob como archivo
 */
export function downloadBlob(blob, filename) {
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Construir contenido CSV con delimitador configurable (default ;)
 * Se agrega BOM para que Excel reconozca UTF-8 y se escapan comillas dobles.
 */
export function buildCsvContent(headers = [], rows = [], options = {}) {
    const { delimiter = ';', includeBom = true, alwaysQuote = false, excelSepHint = false } = options || {};

    const escapeCell = (cell) => {
        if (cell === null || cell === undefined) return '';
        let value = String(cell);
        const needsQuote = alwaysQuote || value.includes(delimiter) || value.includes('"') || /\r|\n/.test(value);
        if (needsQuote) {
            value = `"${value.replace(/"/g, '""')}"`;
        }
        return value;
    };

    const lines = [];
    if (excelSepHint && delimiter === ';') {
        lines.push('sep=;');
    }
    if (headers && headers.length) {
        lines.push(headers.map(escapeCell).join(delimiter));
    }
    rows.forEach(row => {
        lines.push(row.map(escapeCell).join(delimiter));
    });

    const content = lines.join('\r\n');
    return includeBom ? '\ufeff' + content : content;
}

export const CALIFICACION_EXPORT_HEADERS = [
    'País',
    'Moneda',
    'Ejercicio',
    'Instrumento',
    'Fecha Pago',
    'Descripción',
    'Estado',
    'Corredora',
    'Origen',
    'Acogido SFUT',
    'Factor Actualización'
];

export function buildReadableCalificacionRow(cal) {
    if (!cal) return Array(CALIFICACION_EXPORT_HEADERS.length).fill('');

    const boolLabel = (value) => {
        if (value === null || value === undefined || value === '') return '';
        const normalized = String(value).toLowerCase();
        if (['true', '1', 'sí', 'si', 'yes'].includes(normalized)) return 'Sí';
        if (['false', '0', 'no'].includes(normalized)) return 'No';
        return value;
    };

    return [
        cal.id_corredora_pais_nombre ?? '',
        cal.id_moneda_codigo ?? '',
        cal.ejercicio ?? '',
        cal.id_instrumento_nombre ?? cal.id_instrumento_codigo ?? '',
        cal.fecha_pago ?? '',
        cal.descripcion ?? '',
        cal.estado ?? '',
        cal.id_corredora_nombre ?? '',
        cal.id_fuente_nombre ?? '',
        boolLabel(cal.acogido_sfut),
        cal.factor_actualizacion ?? ''
    ];
}

export const CALIFICACION_REPORT_HEADERS = [
    'Corredora',
    'Fuente',
    'País',
    'Moneda',
    'Instrumento',
    'Ejercicio',
    'Fecha Pago',
    'Descripción',
    'Estado',
    'Secuencia Evento',
    'Acogido SFUT',
    'Ingreso por Montos',
    'Factor Actualización',
    'Creado En',
    'Actualizado En'
];

export function buildReportCalificacionRow(cal) {
    if (!cal) return Array(CALIFICACION_REPORT_HEADERS.length).fill('');

    const boolLabel = (value) => {
        if (value === null || value === undefined || value === '') return '';
        const normalized = String(value).toLowerCase();
        if (['true', '1', 'sí', 'si', 'yes'].includes(normalized)) return 'Sí';
        if (['false', '0', 'no'].includes(normalized)) return 'No';
        return value;
    };

    return [
        cal.id_corredora_nombre ?? '',
        cal.id_fuente_nombre ?? '',
        cal.id_corredora_pais_nombre ?? '',
        cal.id_moneda_codigo ?? '',
        cal.id_instrumento_nombre ?? cal.id_instrumento_codigo ?? '',
        cal.ejercicio ?? '',
        cal.fecha_pago ?? '',
        cal.descripcion ?? '',
        cal.estado ?? '',
        cal.secuencia_evento ?? '',
        boolLabel(cal.acogido_sfut),
        boolLabel(cal.ingreso_por_montos),
        cal.factor_actualizacion ?? '',
        cal.creado_en ?? '',
        cal.actualizado_en ?? ''
    ];
}

/**
 * Mostrar notificación toast (Bootstrap 5)
 */
export function showToast(message, type = 'info') {
    const bgColor = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';
    
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white ${bgColor} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

/**
 * Crear contenedor de toasts si no existe
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '11';
    document.body.appendChild(container);
    return container;
}

