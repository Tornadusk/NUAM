/**
 * calificaciones.js - Módulo de Gestión de Calificaciones
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - CRUD completo de calificaciones tributarias
 * - Wizard de 3 pasos (Datos Básicos → Factores → Confirmar)
 * - Carga de catálogos (factores, países, monedas, instrumentos)
 * - Filtros y búsqueda
 * - Paginación
 */

import { API_BASE_URL, fetchWithCSRF, populateSelect, getEstadoBadgeClass } from './core.js';
import { setCalificacionesData } from './reportes.js';

// Estados del módulo
let calificacionesData = [];
let catalogoFactores = [];
let catalogoPaises = [];
let catalogoMonedas = [];
let catalogoInstrumentos = [];
let selectedCalificacionId = null;
let currentPage = 1;
const pageSize = 10;

/**
 * Cargar catálogos desde la API
 */
export async function cargarCatalogos() {
    try {
        // Cargar factores
        const factRes = await fetch(`${API_BASE_URL}/factores/`);
        if (factRes.ok) {
            catalogoFactores = await factRes.json();
        }
        
        // Cargar países
        const paisRes = await fetch(`${API_BASE_URL}/paises/`);
        if (paisRes.ok) {
            catalogoPaises = await paisRes.json();
            populateSelect('filtroPais', catalogoPaises.map(p => ({ value: p.id_pais, text: p.nombre })));
            populateSelect('formPais', catalogoPaises.map(p => ({ value: p.id_pais, text: p.nombre })));
        }
        
        // Cargar monedas
        const monRes = await fetch(`${API_BASE_URL}/monedas/`);
        if (monRes.ok) {
            catalogoMonedas = await monRes.json();
            populateSelect('filtroMoneda', catalogoMonedas.map(m => ({ value: m.id_moneda, text: m.codigo })));
            populateSelect('formMoneda', catalogoMonedas.map(m => ({ value: m.id_moneda, text: m.codigo })));
        }
        
        // Cargar instrumentos
        const insRes = await fetch(`${API_BASE_URL}/instrumentos/`);
        if (insRes.ok) {
            catalogoInstrumentos = await insRes.json();
            populateSelect('filtroInstrumento', catalogoInstrumentos.map(i => ({ value: i.id_instrumento, text: i.codigo })));
            populateSelect('formInstrumento', catalogoInstrumentos.map(i => ({ value: i.id_instrumento, text: i.codigo })));
        }
        
        // Generar inputs de factores
        generarInputsFactores();
        
    } catch (error) {
        console.error('Error cargando catálogos:', error);
    }
}

/**
 * Cargar calificaciones desde la API
 */
export async function cargarCalificaciones() {
    try {
        const res = await fetch(`${API_BASE_URL}/calificaciones/`);
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        calificacionesData = data.results || data; // Compatible con paginación
        setCalificacionesData(calificacionesData); // Compartir con reportes.js
        renderCalificaciones();
    } catch (error) {
        console.error('Error cargando calificaciones:', error);
        const tbody = document.getElementById('tBodyCalificaciones');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-circle me-2"></i> Error al cargar calificaciones: ${error.message}
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * Renderizar calificaciones en la tabla
 */
function renderCalificaciones() {
    const tbody = document.getElementById('tBodyCalificaciones');
    const contador = document.getElementById('contadorCalificaciones');
    
    if (!tbody) return;
    
    if (calificacionesData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    No hay calificaciones registradas
                </td>
            </tr>
        `;
        if (contador) contador.textContent = '0';
        return;
    }
    
    if (contador) contador.textContent = calificacionesData.length;
    
    // Obtener página actual
    const startIdx = (currentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, calificacionesData.length);
    const pageData = calificacionesData.slice(startIdx, endIdx);
    
    tbody.innerHTML = pageData.map(cal => `
        <tr>
            <td>
                <input type="radio" name="calSelected" value="${cal.id_calificacion}" onclick="selectCalificacion(${cal.id_calificacion})">
            </td>
            <td>${cal.id_corredora || '-'}</td>
            <td>${cal.id_instrumento || '-'}</td>
            <td>${cal.ejercicio || '-'}</td>
            <td>${cal.id_instrumento || '-'}</td>
            <td>${cal.fecha_pago || '-'}</td>
            <td>${cal.descripcion || '-'}</td>
            <td>
                <span class="badge ${getEstadoBadgeClass(cal.estado)}">${cal.estado || 'borrador'}</span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editCalificacion(${cal.id_calificacion})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteCalificacion(${cal.id_calificacion})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
    
    // Renderizar paginación
    renderPaginacion();
}

/**
 * Renderizar paginación
 */
function renderPaginacion() {
    const paginacion = document.getElementById('paginacion');
    if (!paginacion) return;
    
    const totalPages = Math.ceil(calificacionesData.length / pageSize);
    
    if (totalPages <= 1) {
        paginacion.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    paginacion.innerHTML = html;
}

/**
 * Ir a una página específica
 */
export function goToPage(page) {
    currentPage = page;
    renderCalificaciones();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Generar inputs de factores dinámicamente
 */
function generarInputsFactores() {
    const container = document.getElementById('factoresContainer');
    if (!container) return;
    
    container.innerHTML = catalogoFactores.map(f => `
        <div class="col-md-3">
            <label class="form-label">${f.codigo_factor}</label>
            <input type="number" class="form-control form-control-sm factor-input" 
                   data-factor="${f.id_factor}" 
                   step="0.00001" 
                   min="0" 
                   max="1"
                   onchange="validarSumaFactores()">
        </div>
    `).join('');
}

/**
 * Validar que la suma de factores no exceda 1
 */
export function validarSumaFactores() {
    const inputs = document.querySelectorAll('.factor-input');
    const suma = Array.from(inputs).reduce((sum, input) => sum + parseFloat(input.value || 0), 0);
    
    const alert = document.createElement('div');
    alert.className = suma > 1 ? 'alert alert-danger' : 'alert alert-success';
    alert.innerHTML = `<i class="fas fa-info-circle me-2"></i> Suma de factores: ${suma.toFixed(5)}`;
    
    let existingAlert = document.querySelector('#factoresContainer + .alert');
    if (existingAlert) existingAlert.remove();
    
    const container = document.getElementById('factoresContainer');
    if (container) container.after(alert);
}

/**
 * Seleccionar calificación y habilitar botones de acción
 */
export function selectCalificacion(id) {
    selectedCalificacionId = id;
    const btnModificar = document.getElementById('btnModificar');
    const btnEliminar = document.getElementById('btnEliminar');
    const btnCopiar = document.getElementById('btnCopiar');
    
    if (btnModificar) btnModificar.disabled = false;
    if (btnEliminar) btnEliminar.disabled = false;
    if (btnCopiar) btnCopiar.disabled = false;
}

/**
 * Buscar calificaciones con filtros
 */
export function buscarCalificaciones() {
    console.log('Buscando calificaciones...');
    // TODO: Implementar filtrado real con API
    cargarCalificaciones();
}

/**
 * Limpiar filtros de búsqueda
 */
export function limpiarFiltros() {
    const filtroPais = document.getElementById('filtroPais');
    const filtroMoneda = document.getElementById('filtroMoneda');
    const filtroInstrumento = document.getElementById('filtroInstrumento');
    
    if (filtroPais) filtroPais.value = '';
    if (filtroMoneda) filtroMoneda.value = '';
    if (filtroInstrumento) filtroInstrumento.value = '';
    
    cargarCalificaciones();
}

/**
 * Abrir modal de ingresar calificación
 */
export function abrirModalIngresar() {
    const modalEl = document.getElementById('modalIngresar');
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
    resetWizard();
}

/**
 * Abrir modal de modificar calificación
 */
export function abrirModalModificar() {
    if (!selectedCalificacionId) return;
    const modalEl = document.getElementById('modalModificar');
    if (!modalEl) return;
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

/**
 * Avanzar al siguiente paso del wizard
 */
export function nextWizardStep() {
    const currentStep = document.querySelector('.wizard-step:not([style*="display: none"])');
    if (!currentStep) return;
    
    const currentStepNum = parseInt(currentStep.dataset.step);
    const nextStep = document.querySelector(`.wizard-step[data-step="${currentStepNum + 1}"]`);
    
    if (nextStep) {
        currentStep.style.display = 'none';
        nextStep.style.display = 'block';
        
        // Actualizar badges
        const modalBody = currentStep.closest('.modal-body');
        if (modalBody) {
            modalBody.querySelectorAll('.nav-link').forEach((link, idx) => {
                if (idx < currentStepNum + 1) {
                    link.querySelector('.badge').className = 'badge bg-primary me-2';
                } else {
                    link.querySelector('.badge').className = 'badge bg-secondary me-2';
                }
            });
        }
    }
}

/**
 * Volver al paso anterior del wizard
 */
export function prevWizardStep() {
    const currentStep = document.querySelector('.wizard-step:not([style*="display: none"])');
    if (!currentStep) return;
    
    const currentStepNum = parseInt(currentStep.dataset.step);
    const prevStep = document.querySelector(`.wizard-step[data-step="${currentStepNum - 1}"]`);
    
    if (prevStep) {
        currentStep.style.display = 'none';
        prevStep.style.display = 'block';
        
        // Actualizar badges
        const modalBody = currentStep.closest('.modal-body');
        if (modalBody) {
            modalBody.querySelectorAll('.nav-link').forEach((link, idx) => {
                if (idx < currentStepNum - 1) {
                    link.querySelector('.badge').className = 'badge bg-primary me-2';
                } else {
                    link.querySelector('.badge').className = 'badge bg-secondary me-2';
                }
            });
        }
    }
}

/**
 * Resetear wizard a paso inicial
 */
export function resetWizard() {
    document.querySelectorAll('.wizard-step').forEach((step, idx) => {
        step.style.display = idx === 0 ? 'block' : 'none';
    });
    
    const wizardTabs = document.getElementById('wizardTabs');
    if (wizardTabs) {
        wizardTabs.querySelectorAll('.nav-link .badge').forEach((badge, idx) => {
            badge.className = idx === 0 ? 'badge bg-primary me-2' : 'badge bg-secondary me-2';
        });
    }
}

/**
 * Guardar nueva calificación
 */
export async function guardarCalificacion() {
    const formInstrumento = document.getElementById('formInstrumento');
    const formEjercicio = document.getElementById('formEjercicio');
    const formFechaPago = document.getElementById('formFechaPago');
    const formDescripcion = document.getElementById('formDescripcion');
    
    const formData = {
        id_corredora: 1, // TODO: obtener del usuario logueado
        id_instrumento: formInstrumento ? formInstrumento.value : null,
        ejercicio: formEjercicio ? formEjercicio.value : null,
        fecha_pago: formFechaPago ? formFechaPago.value : null,
        descripcion: formDescripcion ? formDescripcion.value : null,
        estado: 'borrador'
    };
    
    try {
        const res = await fetchWithCSRF(`${API_BASE_URL}/calificaciones/`, {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        if (res.ok) {
            alert('✓ Calificación guardada exitosamente');
            const modalEl = document.getElementById('modalIngresar');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
            cargarCalificaciones();
        } else {
            alert('Error al guardar calificación');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al guardar calificación');
    }
}

/**
 * Eliminar calificación
 */
export function eliminarCalificacion() {
    if (!selectedCalificacionId) return;
    
    if (!confirm('¿Está seguro de eliminar esta calificación?')) return;
    
    fetchWithCSRF(`${API_BASE_URL}/calificaciones/${selectedCalificacionId}/`, {
        method: 'DELETE'
    })
    .then(res => {
        if (res.ok) {
            alert('✓ Calificación eliminada exitosamente');
            cargarCalificaciones();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al eliminar calificación');
    });
}

/**
 * Copiar calificación
 */
export function copiarCalificacion() {
    if (!selectedCalificacionId) return;
    alert('Funcionalidad de copiar en desarrollo');
}

/**
 * Toggle seleccionar todos
 */
export function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    if (!selectAll) return;
    
    const checked = selectAll.checked;
    document.querySelectorAll('input[name="calSelected"]').forEach(radio => {
        radio.checked = checked;
        if (checked) selectCalificacion(radio.value);
    });
}

/**
 * Editar calificación (helper para onclick)
 */
export function editCalificacion(id) {
    selectedCalificacionId = id;
    abrirModalModificar();
}

/**
 * Eliminar calificación (helper para onclick)
 */
export function deleteCalificacion(id) {
    selectedCalificacionId = id;
    eliminarCalificacion();
}

