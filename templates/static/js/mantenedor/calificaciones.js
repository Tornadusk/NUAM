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

import { API_BASE_URL, fetchWithCSRF, getCookie, populateSelect, getEstadoBadgeClass, downloadBlob, buildCsvContent, CALIFICACION_EXPORT_HEADERS, buildReadableCalificacionRow } from './core.js';
import { setCalificacionesData } from './reportes.js';

// Estados del módulo
let calificacionesData = [];
let catalogoFactores = [];
let catalogoPaises = [];
let catalogoMonedas = [];
let catalogoInstrumentos = [];
let catalogoCorredoras = [];
let catalogoFuentes = [];
let catalogoMercados = [];
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
            const factData = await factRes.json();
            catalogoFactores = factData.results || factData; // Manejar paginación
        }
        
        // Cargar países
        const paisRes = await fetch(`${API_BASE_URL}/paises/`);
        if (paisRes.ok) {
            const paisData = await paisRes.json();
            catalogoPaises = paisData.results || paisData; // Manejar paginación
            console.log('Países cargados:', catalogoPaises); // DEBUG
            if (Array.isArray(catalogoPaises)) {
                populateSelect('formPais', catalogoPaises.map(p => ({ value: p.id_pais, text: p.nombre })));
            } else {
                console.error('catalogoPaises no es un array:', typeof catalogoPaises, catalogoPaises);
            }
        }
        
        // Cargar monedas
        const monRes = await fetch(`${API_BASE_URL}/monedas/`);
        if (monRes.ok) {
            const monData = await monRes.json();
            catalogoMonedas = monData.results || monData; // Manejar paginación
            console.log('Monedas cargadas:', catalogoMonedas); // DEBUG
            if (Array.isArray(catalogoMonedas)) {
                populateSelect('formMoneda', catalogoMonedas.map(m => ({ value: m.id_moneda, text: m.codigo })));
            } else {
                console.error('catalogoMonedas no es un array:', typeof catalogoMonedas, catalogoMonedas);
            }
        }
        
        // Cargar instrumentos
        const insRes = await fetch(`${API_BASE_URL}/instrumentos/`);
        if (insRes.ok) {
            const insData = await insRes.json();
            catalogoInstrumentos = insData.results || insData; // Manejar paginación
            console.log('Instrumentos cargados:', catalogoInstrumentos); // DEBUG
            if (Array.isArray(catalogoInstrumentos)) {
                populateSelect('formInstrumento', catalogoInstrumentos.map(i => ({ value: i.id_instrumento, text: i.codigo })));
            } else {
                console.error('catalogoInstrumentos no es un array:', typeof catalogoInstrumentos, catalogoInstrumentos);
            }
        }

        // Cargar corredoras
        const corrRes = await fetch(`${API_BASE_URL}/corredoras/`);
        if (corrRes.ok) {
            const corrData = await corrRes.json();
            catalogoCorredoras = corrData.results || corrData; // Manejar paginación
            console.log('Corredoras cargadas:', catalogoCorredoras); // DEBUG
            if (Array.isArray(catalogoCorredoras)) {
                populateSelect('formCorredora', catalogoCorredoras.map(c => ({ value: c.id_corredora, text: c.nombre })));
            } else {
                console.error('catalogoCorredoras no es un array:', typeof catalogoCorredoras, catalogoCorredoras);
            }
        }

        // Cargar fuentes
        const fuenteRes = await fetch(`${API_BASE_URL}/fuentes/`);
        if (fuenteRes.ok) {
            const fuenteData = await fuenteRes.json();
            catalogoFuentes = fuenteData.results || fuenteData; // Manejar paginación
            console.log('Fuentes cargadas:', catalogoFuentes); // DEBUG
            if (Array.isArray(catalogoFuentes)) {
                populateSelect('formFuente', catalogoFuentes.map(f => ({ value: f.id_fuente, text: f.nombre })));
                // Poblar filtro de Origen
                const filtroOrigen = document.getElementById('filtroOrigen');
                if (filtroOrigen) {
                    filtroOrigen.innerHTML = '<option value="">Todos</option>' + 
                        catalogoFuentes.map(f => `<option value="${f.id_fuente}">${f.nombre}</option>`).join('');
                }
            } else {
                console.error('catalogoFuentes no es un array:', typeof catalogoFuentes, catalogoFuentes);
            }
        }

        // Cargar mercados
        const mercadoRes = await fetch(`${API_BASE_URL}/mercados/`);
        if (mercadoRes.ok) {
            const mercadoData = await mercadoRes.json();
            catalogoMercados = mercadoData.results || mercadoData; // Manejar paginación
            console.log('Mercados cargados:', catalogoMercados); // DEBUG
            if (Array.isArray(catalogoMercados)) {
                // Poblar filtro de Mercado
                const filtroMercado = document.getElementById('filtroMercado');
                if (filtroMercado) {
                    filtroMercado.innerHTML = '<option value="">Todos</option>' + 
                        catalogoMercados.map(m => `<option value="${m.id_mercado}">${m.nombre}</option>`).join('');
                }
            } else {
                console.error('catalogoMercados no es un array:', typeof catalogoMercados, catalogoMercados);
            }
        }
        
        // Generar inputs de factores
        generarInputsFactores();
        
    } catch (error) {
        console.error('Error cargando catálogos:', error);
    }
}

/**
 * Cargar calificaciones desde la API
 * @param {Object} filtros - Objeto con filtros opcionales (mercado, origen, ejercicio, pendiente)
 */
export async function cargarCalificaciones(filtros = {}) {
    try {
        // Construir URL con parámetros de filtro
        const params = new URLSearchParams();
        if (filtros.mercado) params.append('mercado', filtros.mercado);
        if (filtros.origen) params.append('origen', filtros.origen);
        if (filtros.ejercicio) params.append('ejercicio', filtros.ejercicio);
        if (filtros.pendiente) params.append('pendiente', filtros.pendiente);
        
        const queryString = params.toString();
        const url = `${API_BASE_URL}/calificaciones${queryString ? '?' + queryString : ''}`;
        const res = await fetch(url);
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        calificacionesData = data.results || data; // Compatible con paginación
        setCalificacionesData(calificacionesData); // Compartir con reportes.js
        currentPage = 1; // Resetear a primera página al filtrar
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
            <td>${cal.id_corredora_pais_nombre || '-'}</td>
            <td>${cal.id_moneda_codigo || '-'}</td>
            <td>${cal.ejercicio || '-'}</td>
            <td>${cal.id_instrumento_nombre || cal.id_instrumento_codigo || '-'}</td>
            <td>${cal.fecha_pago || '-'}</td>
            <td>${cal.descripcion || '-'}</td>
            <td>
                <span class="badge ${getEstadoBadgeClass(cal.estado)}">${cal.estado || 'borrador'}</span>
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-primary" onclick="editCalificacion(${cal.id_calificacion})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-secondary" onclick="descargarCalificacionCSV(${cal.id_calificacion})" title="Descargar CSV">
                        <i class="fas fa-download"></i>
                    </button>
                    ${(cal.detalles_montos && cal.detalles_montos.length > 0) ? `
                    <button class="btn btn-info" onclick="calcularFactoresCalificacion(${cal.id_calificacion})" 
                            title="Calcular factores desde montos" 
                            data-bs-toggle="tooltip" 
                            data-bs-placement="top">
                        <i class="fas fa-calculator"></i>
                    </button>
                    ` : ''}
                    <button class="btn btn-danger" onclick="deleteCalificacion(${cal.id_calificacion})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Renderizar paginación
    renderPaginacion();
    
    // Inicializar tooltips en los botones de acciones
    const tooltipTriggerList = tbody.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
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
    const containerCrear = document.getElementById('factoresContainer');
    const containerEditar = document.getElementById('editarFactoresContainer');
    
    [containerCrear, containerEditar].forEach(container => {
        if (!container) return;
        
        if (!Array.isArray(catalogoFactores) || catalogoFactores.length === 0) {
            console.warn('catalogoFactores no es un array o está vacío:', catalogoFactores);
            container.innerHTML = '<p class="text-muted">No hay factores disponibles</p>';
            return;
        }
        
        // Generar inputs con la configuración de cada factor
        container.innerHTML = catalogoFactores.map(f => {
            const esRequerido = f.requerido || false;
            const tooltip = f.descripcion ? `title="${f.descripcion}"` : '';
            const asterisco = esRequerido ? ' <span class="text-danger">*</span>' : '';
            
            return `
                <div class="col-md-3 mb-2">
                    <label class="form-label" ${tooltip}>
                        ${f.codigo_factor}${asterisco}
                    </label>
                    <input type="number" 
                           class="form-control form-control-sm factor-input" 
                           data-factor="${f.id_factor}" 
                           data-aplica-suma="${f.aplica_en_suma || false}"
                           ${esRequerido ? 'required' : ''}
                           step="0.00001" 
                           min="0" 
                           max="1"
                           onchange="validarSumaFactores()">
                </div>
            `;
        }).join('');
    });
}

/**
 * Validar que la suma de factores no exceda 1
 * Solo suma los factores que tienen aplica_en_suma = true
 */
export function validarSumaFactores() {
    const inputs = document.querySelectorAll('.factor-input');
    
    // Filtrar solo los que aplican en suma
    const suma = Array.from(inputs).reduce((sum, input) => {
        const aplicaEnSuma = input.dataset.aplicaSuma === 'true';
        if (aplicaEnSuma) {
            return sum + parseFloat(input.value || 0);
        }
        return sum;
    }, 0);
    
    const alert = document.createElement('div');
    alert.className = suma > 1 ? 'alert alert-danger' : 'alert alert-success';
    alert.innerHTML = `<i class="fas fa-info-circle me-2"></i> Suma de factores: ${suma.toFixed(5)} ${suma > 1 ? '(excede el límite)' : '(válido)'}`;
    
    let existingAlert = document.querySelector('#factoresContainer + .alert');
    if (existingAlert) existingAlert.remove();
    
    const container = document.getElementById('factoresContainer');
    if (container) container.after(alert);
    
    return suma <= 1;
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
    console.log('Buscando calificaciones con filtros...');
    
    // Obtener valores de los filtros
    const filtroMercado = document.getElementById('filtroMercado');
    const filtroOrigen = document.getElementById('filtroOrigen');
    const filtroPeriodo = document.getElementById('filtroPeriodo');
    const filtroPendiente = document.getElementById('filtroPendiente');
    
    const filtros = {};
    
    if (filtroMercado && filtroMercado.value) {
        filtros.mercado = filtroMercado.value;
    }
    if (filtroOrigen && filtroOrigen.value) {
        filtros.origen = filtroOrigen.value;
    }
    if (filtroPeriodo && filtroPeriodo.value.trim()) {
        filtros.ejercicio = filtroPeriodo.value.trim();
    }
    if (filtroPendiente && filtroPendiente.checked) {
        filtros.pendiente = 'true';
    }
    
    console.log('Filtros aplicados:', filtros);
    cargarCalificaciones(filtros);
}

/**
 * Limpiar filtros de búsqueda
 */
export function limpiarFiltros() {
    const filtroMercado = document.getElementById('filtroMercado');
    const filtroOrigen = document.getElementById('filtroOrigen');
    const filtroPeriodo = document.getElementById('filtroPeriodo');
    const filtroPendiente = document.getElementById('filtroPendiente');
    
    if (filtroMercado) filtroMercado.value = '';
    if (filtroOrigen) filtroOrigen.value = '';
    if (filtroPeriodo) filtroPeriodo.value = '';
    if (filtroPendiente) filtroPendiente.checked = false;
    
    // Recargar sin filtros
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
    
    // Inicializar tooltips de Bootstrap en el modal
    const tooltipTriggerList = modalEl.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Limpiar tooltips cuando se cierre el modal
    modalEl.addEventListener('hidden.bs.modal', function() {
        tooltipList.forEach(tooltip => tooltip.dispose());
    });
}

/**
 * Abrir modal de modificar calificación
 */
export async function abrirModalModificar() {
    if (!selectedCalificacionId) return;
    const modalEl = document.getElementById('modalModificar');
    if (!modalEl) return;
    
    // Cargar datos de la calificación seleccionada
    try {
        const res = await fetch(`${API_BASE_URL}/calificaciones/${selectedCalificacionId}/`);
        if (res.ok) {
            const cal = await res.json();
            
            // Generar inputs de factores primero (esto también llena editarFactoresContainer)
            generarInputsFactores();
            
            // Precargar datos en los campos del modal de edición
            populateSelect('editarFormCorredora', catalogoCorredoras.map(c => ({ value: c.id_corredora, text: c.nombre })));
            populateSelect('editarFormInstrumento', catalogoInstrumentos.map(i => ({ value: i.id_instrumento, text: i.nombre || i.codigo })));
            populateSelect('editarFormFuente', catalogoFuentes.map(f => ({ value: f.id_fuente, text: f.nombre })));
            populateSelect('editarFormMoneda', catalogoMonedas.map(m => ({ value: m.id_moneda, text: m.codigo })));
            
            document.getElementById('editarFormCorredora').value = cal.id_corredora || '';
            document.getElementById('editarFormInstrumento').value = cal.id_instrumento || '';
            document.getElementById('editarFormFuente').value = cal.id_fuente || '';
            document.getElementById('editarFormMoneda').value = cal.id_moneda || '';
            document.getElementById('editarFormEjercicio').value = cal.ejercicio || '';
            document.getElementById('editarFormFechaPago').value = cal.fecha_pago || '';
            document.getElementById('editarFormSecuenciaEvento').value = cal.secuencia_evento || '';
            document.getElementById('editarFormDescripcion').value = cal.descripcion || '';
            
            // Precargar factores si existen (después de que se generen los inputs)
            if (cal.detalles_factores && cal.detalles_factores.length > 0) {
                setTimeout(() => {
                    cal.detalles_factores.forEach(det => {
                        const input = document.querySelector(`#editarFactoresContainer input[data-factor="${det.id_factor}"]`);
                        if (input) {
                            input.value = det.valor_factor || '';
                        }
                    });
                }, 100);
            }
            
            resetWizardEditar();
        } else {
            console.error('Error al cargar calificación para editar');
        }
    } catch (error) {
        console.error('Error:', error);
    }
    
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
 * Resetear wizard de edición a paso inicial
 */
export function resetWizardEditar() {
    const modalModificar = document.getElementById('modalModificar');
    if (!modalModificar) return;
    
    modalModificar.querySelectorAll('.wizard-step').forEach((step, idx) => {
        step.style.display = idx === 0 ? 'block' : 'none';
    });
    
    const wizardTabs = document.getElementById('wizardTabsEditar');
    if (wizardTabs) {
        wizardTabs.querySelectorAll('.nav-link .badge').forEach((badge, idx) => {
            badge.className = idx === 0 ? 'badge bg-primary me-2' : 'badge bg-secondary me-2';
        });
    }
}

/**
 * Avanzar al siguiente paso del wizard de edición
 */
export function nextWizardStepEditar() {
    const modalModificar = document.getElementById('modalModificar');
    if (!modalModificar) return;
    
    const currentStep = modalModificar.querySelector('.wizard-step:not([style*="display: none"])');
    if (!currentStep) return;
    
    const currentStepNum = parseInt(currentStep.dataset.step);
    const nextStep = modalModificar.querySelector(`.wizard-step[data-step="${currentStepNum + 1}"]`);
    
    if (nextStep) {
        currentStep.style.display = 'none';
        nextStep.style.display = 'block';
        
        // Actualizar badges
        const wizardTabs = document.getElementById('wizardTabsEditar');
        if (wizardTabs) {
            wizardTabs.querySelectorAll('.nav-link').forEach((link, idx) => {
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
 * Volver al paso anterior del wizard de edición
 */
export function prevWizardStepEditar() {
    const modalModificar = document.getElementById('modalModificar');
    if (!modalModificar) return;
    
    const currentStep = modalModificar.querySelector('.wizard-step:not([style*="display: none"])');
    if (!currentStep) return;
    
    const currentStepNum = parseInt(currentStep.dataset.step);
    const prevStep = modalModificar.querySelector(`.wizard-step[data-step="${currentStepNum - 1}"]`);
    
    if (prevStep) {
        currentStep.style.display = 'none';
        prevStep.style.display = 'block';
        
        // Actualizar badges
        const wizardTabs = document.getElementById('wizardTabsEditar');
        if (wizardTabs) {
            wizardTabs.querySelectorAll('.nav-link').forEach((link, idx) => {
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
 * Guardar nueva calificación
 */
export async function guardarCalificacion() {
    const formCorredora = document.getElementById('formCorredora');
    const formInstrumento = document.getElementById('formInstrumento');
    const formFuente = document.getElementById('formFuente');
    const formMoneda = document.getElementById('formMoneda');
    const formEjercicio = document.getElementById('formEjercicio');
    const formFechaPago = document.getElementById('formFechaPago');
    const formSecuenciaEvento = document.getElementById('formSecuenciaEvento');
    const formDescripcion = document.getElementById('formDescripcion');
    
    // Validación básica
    if (!formCorredora || !formCorredora.value) {
        alert('Por favor seleccione una Corredora');
        return;
    }
    if (!formInstrumento || !formInstrumento.value) {
        alert('Por favor seleccione un Instrumento');
        return;
    }
    if (!formFuente || !formFuente.value) {
        alert('Por favor seleccione una Fuente');
        return;
    }
    if (!formMoneda || !formMoneda.value) {
        alert('Por favor seleccione una Moneda');
        return;
    }
    if (!formEjercicio || !formEjercicio.value) {
        alert('Por favor ingrese el Año');
        return;
    }
    if (!formFechaPago || !formFechaPago.value) {
        alert('Por favor ingrese la Fecha de Pago');
        return;
    }
    if (!formSecuenciaEvento || !formSecuenciaEvento.value) {
        alert('Por favor ingrese la Secuencia Evento');
        return;
    }
    
    // Validar factores antes de guardar
    if (!validarSumaFactores()) {
        alert('La suma de factores excede 1. Por favor corrija los valores.');
        return;
    }
    
    const formData = {
        id_corredora: parseInt(formCorredora.value),
        id_instrumento: parseInt(formInstrumento.value),
        id_fuente: parseInt(formFuente.value),
        id_moneda: parseInt(formMoneda.value),
        ejercicio: parseInt(formEjercicio.value),
        fecha_pago: formFechaPago.value,
        secuencia_evento: formSecuenciaEvento.value,
        descripcion: formDescripcion ? formDescripcion.value : '',
        estado: 'borrador',
        ingreso_por_montos: false // Por ahora, siempre por factores
    };
    
    console.log('Guardando calificación con datos:', formData);
    
    try {
        const res = await fetchWithCSRF(`${API_BASE_URL}/calificaciones/`, {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        if (res.ok) {
            const data = await res.json();
            console.log('Calificación guardada:', data);
            
            // Guardar detalles de factores
            const factorInputs = document.querySelectorAll('.factor-input');
            for (const input of factorInputs) {
                const valor = parseFloat(input.value);
                if (!isNaN(valor) && valor > 0) {
                    const detalleData = {
                        id_calificacion: data.id_calificacion,
                        id_factor: parseInt(input.dataset.factor),
                        valor_factor: valor
                    };
                    
                    await fetchWithCSRF(`${API_BASE_URL}/calificacion-factor-detalle/`, {
                        method: 'POST',
                        body: JSON.stringify(detalleData)
                    });
                }
            }
            
            alert('✓ Calificación guardada exitosamente');
            const modalEl = document.getElementById('modalIngresar');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
            cargarCalificaciones();
        } else {
            const errorData = await res.json();
            console.error('Error al guardar calificación:', errorData);
            alert('Error al guardar calificación: ' + (errorData.detail || JSON.stringify(errorData)));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al guardar calificación');
    }
}

/**
 * Actualizar calificación existente
 */
export async function actualizarCalificacion() {
    if (!selectedCalificacionId) return;
    
    const formCorredora = document.getElementById('editarFormCorredora');
    const formInstrumento = document.getElementById('editarFormInstrumento');
    const formFuente = document.getElementById('editarFormFuente');
    const formMoneda = document.getElementById('editarFormMoneda');
    const formEjercicio = document.getElementById('editarFormEjercicio');
    const formFechaPago = document.getElementById('editarFormFechaPago');
    const formSecuenciaEvento = document.getElementById('editarFormSecuenciaEvento');
    const formDescripcion = document.getElementById('editarFormDescripcion');
    
    // Validación básica
    if (!formCorredora || !formCorredora.value) {
        alert('Por favor seleccione una Corredora');
        return;
    }
    if (!formInstrumento || !formInstrumento.value) {
        alert('Por favor seleccione un Instrumento');
        return;
    }
    if (!formFuente || !formFuente.value) {
        alert('Por favor seleccione una Fuente');
        return;
    }
    if (!formMoneda || !formMoneda.value) {
        alert('Por favor seleccione una Moneda');
        return;
    }
    if (!formEjercicio || !formEjercicio.value) {
        alert('Por favor ingrese el Año');
        return;
    }
    if (!formFechaPago || !formFechaPago.value) {
        alert('Por favor ingrese la Fecha de Pago');
        return;
    }
    if (!formSecuenciaEvento || !formSecuenciaEvento.value) {
        alert('Por favor ingrese la Secuencia Evento');
        return;
    }
    
    // Validar factores antes de guardar
    const modalModificar = document.getElementById('modalModificar');
    const factorInputs = modalModificar ? modalModificar.querySelectorAll('.factor-input') : [];
    
    const suma = Array.from(factorInputs).reduce((sum, input) => {
        const aplicaEnSuma = input.dataset.aplicaSuma === 'true';
        if (aplicaEnSuma) {
            return sum + parseFloat(input.value || 0);
        }
        return sum;
    }, 0);
    
    if (suma > 1) {
        alert('La suma de factores excede 1. Por favor corrija los valores.');
        return;
    }
    
    const formData = {
        id_corredora: parseInt(formCorredora.value),
        id_instrumento: parseInt(formInstrumento.value),
        id_fuente: parseInt(formFuente.value),
        id_moneda: parseInt(formMoneda.value),
        ejercicio: parseInt(formEjercicio.value),
        fecha_pago: formFechaPago.value,
        secuencia_evento: formSecuenciaEvento.value,
        descripcion: formDescripcion ? formDescripcion.value : '',
        ingreso_por_montos: false
    };
    
    console.log('Actualizando calificación con datos:', formData);
    
    try {
        // Actualizar calificación principal
        const res = await fetchWithCSRF(`${API_BASE_URL}/calificaciones/${selectedCalificacionId}/`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
        
        if (res.ok) {
            const data = await res.json();
            console.log('Calificación actualizada:', data);
            
            // Eliminar factores antiguos y crear nuevos
            // Primero, obtener factores actuales y eliminarlos
            const factoresRes = await fetch(`${API_BASE_URL}/calificacion-factor-detalle/?id_calificacion=${selectedCalificacionId}`);
            if (factoresRes.ok) {
                const factoresData = await factoresRes.json();
                const factoresActuales = factoresData.results || factoresData;
                
                // Eliminar factores actuales
                for (const factor of factoresActuales) {
                    await fetchWithCSRF(`${API_BASE_URL}/calificacion-factor-detalle/${factor.id}/`, {
                        method: 'DELETE'
                    });
                }
            }
            
            // Crear nuevos factores
            for (const input of factorInputs) {
                const valor = parseFloat(input.value);
                if (!isNaN(valor) && valor > 0) {
                    const detalleData = {
                        id_calificacion: selectedCalificacionId,
                        id_factor: parseInt(input.dataset.factor),
                        valor_factor: valor
                    };
                    
                    await fetchWithCSRF(`${API_BASE_URL}/calificacion-factor-detalle/`, {
                        method: 'POST',
                        body: JSON.stringify(detalleData)
                    });
                }
            }
            
            alert('✓ Calificación actualizada exitosamente');
            const modalEl = document.getElementById('modalModificar');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
            cargarCalificaciones();
        } else {
            const errorData = await res.json();
            console.error('Error al actualizar calificación:', errorData);
            alert('Error al actualizar calificación: ' + (errorData.detail || JSON.stringify(errorData)));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar calificación');
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

/**
 * Exportar calificaciones visibles a CSV
 */
export async function exportarCalificacionesCSV() {
    if (!calificacionesData || calificacionesData.length === 0) {
        alert('No hay calificaciones para exportar');
        return;
    }
    
    const rows = calificacionesData.map(cal => buildReadableCalificacionRow(cal));
    const csvContent = buildCsvContent(CALIFICACION_EXPORT_HEADERS, rows, { excelSepHint: true });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    downloadBlob(blob, `calificaciones_${new Date().toISOString().split('T')[0]}.csv`);
}

/**
 * Descargar una calificación individual como CSV
 */
export async function descargarCalificacionCSV(id) {
    let cal = calificacionesData.find(c => c.id_calificacion === id);
    
    // Si la calificación no está en los datos cargados, cargarla desde la API
    // Esto asegura que siempre tengamos los datos completos (incluyendo factores)
    if (!cal) {
        try {
            const res = await fetch(`${API_BASE_URL}/calificaciones/${id}/`);
            if (res.ok) {
                cal = await res.json();
            } else {
                alert('Error al cargar calificación');
                return;
            }
        } catch (error) {
            console.error('Error al cargar calificación:', error);
            alert('Error al cargar calificación');
            return;
        }
    }
    
    // Si la calificación existe pero no tiene detalles_factores cargados, cargarla desde la API
    if (cal && (!cal.detalles_factores || !Array.isArray(cal.detalles_factores))) {
        try {
            const res = await fetch(`${API_BASE_URL}/calificaciones/${id}/`);
            if (res.ok) {
                cal = await res.json();
                // Actualizar en calificacionesData si existe
                const index = calificacionesData.findIndex(c => c.id_calificacion === id);
                if (index !== -1) {
                    calificacionesData[index] = cal;
                }
            }
        } catch (error) {
            console.warn('No se pudieron cargar los factores, continuando con datos disponibles:', error);
        }
    }
    
    if (!cal) {
        alert('Calificación no encontrada');
        return;
    }
    
    const csvRow = [buildReadableCalificacionRow(cal)];
    const csvContent = buildCsvContent(CALIFICACION_EXPORT_HEADERS, csvRow, { excelSepHint: true });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    downloadBlob(blob, `calificacion_${cal.id_calificacion}.csv`);
}

// Variable global para almacenar el ID de calificación actual en preview
let calificacionIdPreview = null;

/**
 * Calcular factores desde montos de una calificación existente (mostrar preview)
 */
export async function calcularFactoresCalificacion(id) {
    if (!id) {
        alert('ID de calificación no válido');
        return;
    }
    
    try {
        // Llamar al endpoint de preview (GET)
        const res = await fetch(`${API_BASE_URL}/calificaciones/${id}/preview_factores_desde_montos/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await res.json();
        
        if (res.ok) {
            // Guardar ID de calificación para usar al grabar
            calificacionIdPreview = id;
            
            // Mostrar modal con preview
            mostrarPreviewFactoresCalculados(data);
        } else {
            alert('Error al calcular factores: ' + (data.error || JSON.stringify(data)));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al calcular factores. Ver consola (F12) para detalles.');
    }
}

/**
 * Mostrar preview de factores calculados en el modal
 */
function mostrarPreviewFactoresCalculados(data) {
    // Llenar resumen
    document.getElementById('previewCalificacionId').textContent = data.calificacion_id || '-';
    document.getElementById('previewSumaMontos').textContent = parseFloat(data.suma_montos || 0).toLocaleString('es-CL', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    document.getElementById('previewSumaFactores').textContent = parseFloat(data.suma_factores || 0).toLocaleString('es-CL', {
        minimumFractionDigits: 6,
        maximumFractionDigits: 6
    });
    
    // Llenar tabla de montos y factores
    const tbody = document.getElementById('previewFactoresTableBody');
    tbody.innerHTML = '';
    
    // Obtener códigos ordenados (F08-F37)
    const codigos = Array.from({ length: 30 }, (_, i) => `F${(i + 8).toString().padStart(2, '0')}`);
    
    let totalMontos = 0;
    let totalFactores = 0;
    let totalPorcentaje = 0;
    
    codigos.forEach(codigo => {
        const montoKey = codigo.replace('F', 'M');
        const monto = parseFloat(data.montos[montoKey] || 0);
        const factor = parseFloat(data.factores[codigo] || 0);
        
        if (monto > 0 || factor > 0) {
            totalMontos += monto;
            totalFactores += factor;
            
            const porcentaje = factor > 0 ? (factor * 100) : 0;
            totalPorcentaje += porcentaje;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${codigo} / ${montoKey}</strong></td>
                <td class="text-end">${monto.toLocaleString('es-CL', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}</td>
                <td class="text-end">${factor.toLocaleString('es-CL', {
                    minimumFractionDigits: 6,
                    maximumFractionDigits: 6
                })}</td>
                <td class="text-end">${porcentaje.toLocaleString('es-CL', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}%</td>
            `;
            tbody.appendChild(row);
        }
    });
    
    // Llenar totales
    document.getElementById('previewTotalMontos').textContent = totalMontos.toLocaleString('es-CL', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    document.getElementById('previewTotalFactores').textContent = totalFactores.toLocaleString('es-CL', {
        minimumFractionDigits: 6,
        maximumFractionDigits: 6
    });
    document.getElementById('previewTotalPorcentaje').textContent = totalPorcentaje.toLocaleString('es-CL', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + '%';
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalPreviewFactores'));
    modal.show();
}

/**
 * Limpiar preview de factores al cancelar
 */
export function limpiarPreviewFactores() {
    calificacionIdPreview = null;
}

/**
 * Grabar factores calculados después de confirmar en el modal
 */
export async function grabarFactoresCalculados() {
    if (!calificacionIdPreview) {
        alert('ID de calificación no válido');
        return;
    }
    
    if (!confirm('¿Está seguro de grabar los factores calculados?\n\nEsto sobrescribirá los factores actuales (si existen) con los factores calculados desde los montos.')) {
        return;
    }
    
    try {
        // Mostrar loading
        const btnGrabar = document.getElementById('btnGrabarFactores');
        if (btnGrabar) {
            btnGrabar.disabled = true;
            btnGrabar.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Grabando...';
        }
        
        // Llamar al endpoint de grabado (POST)
        const csrfToken = getCookie('csrftoken');
        const res = await fetchWithCSRF(`${API_BASE_URL}/calificaciones/${calificacionIdPreview}/calcular_factores_desde_montos/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await res.json();
        
        if (res.ok) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalPreviewFactores'));
            if (modal) {
                modal.hide();
            }
            
            // Mostrar mensaje de éxito
            alert(`✓ Factores calculados y grabados exitosamente\n\n` +
                  `Calificación ID: ${data.calificacion_id}\n` +
                  `Factores calculados: ${data.total_factores}\n` +
                  `Suma de factores: ${parseFloat(data.suma_factores).toFixed(6)}`);
            
            // Recargar calificaciones para mostrar los cambios
            cargarCalificaciones();
            
            // Limpiar variable
            calificacionIdPreview = null;
        } else {
            alert('Error al grabar factores: ' + (data.error || JSON.stringify(data)));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al grabar factores. Ver consola (F12) para detalles.');
    } finally {
        // Restaurar botón
        const btnGrabar = document.getElementById('btnGrabarFactores');
        if (btnGrabar) {
            btnGrabar.disabled = false;
            btnGrabar.innerHTML = '<i class="fas fa-save me-1"></i> Grabar Factores';
        }
    }
}

