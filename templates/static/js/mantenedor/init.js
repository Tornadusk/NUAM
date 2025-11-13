/**
 * init.js - Punto de Entrada del Mantenedor
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Este archivo orquesta la inicialización de todos los módulos,
 * configura listeners globales y expone funciones necesarias
 * para los eventos onclick del HTML.
 */

// Importar módulos
import * as Core from './core.js';
import * as Calificaciones from './calificaciones.js';
import * as Cargas from './cargas.js';
import * as Usuarios from './usuarios.js';
import * as Auditoria from './auditoria.js';
import * as Reportes from './reportes.js';
import * as KPIs from './kpis.js';

// Inicialización al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando Mantenedor NUAM (versión modular)');
    
    // Obtener username del DOM (podría pasarse desde Django)
    const usernameElement = document.querySelector('.navbar-nav .dropdown-toggle');
    const username = usernameElement ? usernameElement.textContent.trim() : 'guest';
    
    // Restaurar el último tab activo desde localStorage (por usuario)
    const lastTabKey = `lastMantenedorTab_${username}`;
    const lastTab = localStorage.getItem(lastTabKey) || 'mantenedor';
    const tabElement = document.getElementById(`${lastTab}-tab`);
    if (tabElement) {
        // Verificar que el tab pane correspondiente existe antes de activarlo
        const tabPaneId = tabElement.getAttribute('data-bs-target');
        const tabPane = document.querySelector(tabPaneId);
        if (tabPane && !tabPane.classList.contains('d-none')) {
            const tab = new bootstrap.Tab(tabElement);
            tab.show();
        }
    }
    
    // Guardar el tab activo cuando cambie y cargar contenido específico
    // Usar delegación de eventos para capturar todos los tabs
    const mainTabsContainer = document.getElementById('mainTabs');
    if (mainTabsContainer) {
        mainTabsContainer.addEventListener('shown.bs.tab', function(event) {
            // event.target es el botón del tab que fue clickeado
            const buttonId = event.target.getAttribute('id') || '';
            const activeTab = buttonId.replace('-tab', '');
            
            console.log('Tab activado:', activeTab, 'Button ID:', buttonId);
            
            if (activeTab) {
                localStorage.setItem(lastTabKey, activeTab);
                
                // Cargar contenido específico según el tab activo
                switch(activeTab) {
                    case 'usuarios':
                        console.log('✅ Activando tab Usuarios, cargando usuarios...');
                        // Usar setTimeout para asegurar que el tab pane está visible
                        setTimeout(() => {
                            Usuarios.cargarUsuarios();
                        }, 100);
                        break;
                    case 'auditoria':
                        console.log('✅ Activando tab Auditoría, cargando auditoría completa...');
                        setTimeout(() => {
                            Auditoria.cargarAuditoriaCompleta();
                        }, 100);
                        break;
                    case 'reportes':
                        console.log('✅ Activando tab Reportes, inicializando tooltips...');
                        setTimeout(() => {
                            inicializarTooltips('#reportes');
                        }, 100);
                        break;
                    case 'cargas':
                        console.log('✅ Activando tab Cargas, inicializando tooltips...');
                        setTimeout(() => {
                            inicializarTooltips('#cargas');
                        }, 100);
                        break;
                    default:
                        // No hacer nada para otros tabs
                        break;
                }
            }
        });
    }
    
    // Si el tab de usuarios ya está activo al cargar, cargar usuarios inmediatamente
    const usuariosTabPane = document.getElementById('usuarios');
    if (usuariosTabPane && usuariosTabPane.classList.contains('active')) {
        console.log('Tab Usuarios ya está activo al cargar, cargando usuarios...');
        setTimeout(() => {
            Usuarios.cargarUsuarios();
        }, 500); // Dar tiempo a que el DOM esté completamente listo
    }
    
    // Si el tab de auditoría ya está activo al cargar, cargar auditoría inmediatamente
    const auditoriaTabPane = document.getElementById('auditoria');
    if (auditoriaTabPane && auditoriaTabPane.classList.contains('active')) {
        console.log('Tab Auditoría ya está activo al cargar, cargando auditoría completa...');
        setTimeout(() => {
            Auditoria.cargarAuditoriaCompleta();
        }, 500); // Dar tiempo a que el DOM esté completamente listo
    }
    
    // Si el tab de reportes ya está activo al cargar, inicializar tooltips
    const reportesTabPane = document.getElementById('reportes');
    if (reportesTabPane && reportesTabPane.classList.contains('active')) {
        console.log('Tab Reportes ya está activo al cargar, inicializando tooltips...');
        setTimeout(() => {
            inicializarTooltips('#reportes');
        }, 500);
    }
    
    // Si el tab de cargas ya está activo al cargar, inicializar tooltips
    const cargasTabPane = document.getElementById('cargas');
    if (cargasTabPane && cargasTabPane.classList.contains('active')) {
        console.log('Tab Cargas ya está activo al cargar, inicializando tooltips...');
        setTimeout(() => {
            inicializarTooltips('#cargas');
        }, 500);
    }
    
    // Inicializar módulos principales
    Calificaciones.cargarCatalogos();
    Calificaciones.cargarCalificaciones();
    Auditoria.cargarAuditoriaReciente();
    Usuarios.cargarRoles();
    KPIs.cargarKPIs();
    
    // Mostrar/ocultar campo de email según checkbox colaborador
    const checkboxColaborador = document.getElementById('crearEsColaborador');
    if (checkboxColaborador) {
        checkboxColaborador.addEventListener('change', function() {
            const emailContainer = document.getElementById('colaboradorEmailContainer');
            if (emailContainer) {
                emailContainer.style.display = this.checked ? 'block' : 'none';
            }
        });
    }
    
    // Configurar toggles de contraseñas
    Usuarios.setupPasswordToggles();
    
    // Validación en tiempo real de coincidencia de contraseñas
    const passwordConfirmInput = document.getElementById('crearPasswordConfirm');
    if (passwordConfirmInput) {
        passwordConfirmInput.addEventListener('input', Usuarios.validarPasswordCoincidencia);
    }
    const passwordInput = document.getElementById('crearPassword');
    if (passwordInput) {
        passwordInput.addEventListener('input', Usuarios.validarPasswordCoincidencia);
    }
    
    console.log('✅ Mantenedor NUAM inicializado correctamente');
});

/**
 * Función helper para inicializar tooltips de Bootstrap en un contenedor específico
 * @param {string} selector - Selector CSS del contenedor (ej: '#reportes')
 */
function inicializarTooltips(selector) {
    if (typeof bootstrap === 'undefined') {
        console.warn('Bootstrap no está disponible, no se pueden inicializar tooltips');
        return;
    }
    
    const container = document.querySelector(selector);
    if (!container) {
        console.warn(`No se encontró el contenedor: ${selector}`);
        return;
    }
    
    // Destruir tooltips existentes para evitar duplicados
    const existingTooltips = container.querySelectorAll('[data-bs-toggle="tooltip"]');
    existingTooltips.forEach(el => {
        const existingTooltip = bootstrap.Tooltip.getInstance(el);
        if (existingTooltip) {
            existingTooltip.dispose();
        }
    });
    
    // Inicializar todos los tooltips dentro del contenedor
    const tooltipTriggerList = [].slice.call(container.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log(`✅ Tooltips inicializados en ${selector} (${tooltipTriggerList.length} tooltips)`);
}

// ============================================================
// EXPORTAR FUNCIONES GLOBALES PARA ONCLICK EN HTML
// ============================================================

// Exportar todas las funciones necesarias para onclick en HTML
window.abrirModalIngresar = Calificaciones.abrirModalIngresar;
window.abrirModalModificar = Calificaciones.abrirModalModificar;
window.abrirModalCrearUsuario = Usuarios.abrirModalCrearUsuario;
window.abrirModalCargaFactor = Cargas.abrirModalCargaFactor;
window.abrirModalCargaMonto = Cargas.abrirModalCargaMonto;

window.guardarCalificacion = Calificaciones.guardarCalificacion;
window.guardarUsuario = Usuarios.guardarUsuario;
window.actualizarUsuario = Usuarios.actualizarUsuario;
window.editarUsuario = Usuarios.editarUsuario;
window.eliminarUsuario = Usuarios.eliminarUsuario;

window.eliminarCalificacion = Calificaciones.eliminarCalificacion;
window.copiarCalificacion = Calificaciones.copiarCalificacion;
window.buscarCalificaciones = Calificaciones.buscarCalificaciones;
window.cargarCalificaciones = Calificaciones.cargarCalificaciones;
window.limpiarFiltros = Calificaciones.limpiarFiltros;
window.exportarCalificacionesCSV = Calificaciones.exportarCalificacionesCSV;
window.descargarCalificacionCSV = Calificaciones.descargarCalificacionCSV;

window.exportarCSV = Reportes.exportarCSV;
window.exportarExcel = Reportes.exportarExcel;
window.exportarPDF = Reportes.exportarPDF;

window.calcularFactores = Cargas.calcularFactores;
window.cargarFactor = Cargas.cargarFactor;
window.cargarMonto = Cargas.cargarMonto;
window.descargarFormatoExcel = Cargas.descargarFormatoExcel;
window.descargarFormatoExcelMontos = Cargas.descargarFormatoExcelMontos;
window.calcularFactoresCalificacion = Calificaciones.calcularFactoresCalificacion;
window.grabarFactoresCalculados = Calificaciones.grabarFactoresCalculados;
window.limpiarPreviewFactores = Calificaciones.limpiarPreviewFactores;

window.nextWizardStep = Calificaciones.nextWizardStep;
window.prevWizardStep = Calificaciones.prevWizardStep;
window.nextWizardStepEditar = Calificaciones.nextWizardStepEditar;
window.prevWizardStepEditar = Calificaciones.prevWizardStepEditar;

window.toggleSelectAll = Calificaciones.toggleSelectAll;
window.editCalificacion = Calificaciones.editCalificacion;
window.deleteCalificacion = Calificaciones.deleteCalificacion;

window.goToPage = Calificaciones.goToPage;
window.validarSumaFactores = Calificaciones.validarSumaFactores;
window.selectCalificacion = Calificaciones.selectCalificacion;
window.actualizarCalificacion = Calificaciones.actualizarCalificacion;

// Log de funciones exportadas
console.log('📦 Funciones globales exportadas para eventos onclick');

