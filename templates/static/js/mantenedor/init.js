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
    
    // Guardar el tab activo cuando cambie
    const allTabs = document.querySelectorAll('#mainTabs button[data-bs-toggle="tab"]');
    allTabs.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            const activeTab = event.target.getAttribute('id').replace('-tab', '');
            localStorage.setItem(lastTabKey, activeTab);
        });
    });
    
    // Inicializar módulos principales
    Calificaciones.cargarCatalogos();
    Calificaciones.cargarCalificaciones();
    Auditoria.cargarAuditoriaReciente();
    Usuarios.cargarRoles();
    
    // Cargar usuarios cuando se active el tab
    const usuariosTab = document.getElementById('usuarios-tab');
    if (usuariosTab) {
        usuariosTab.addEventListener('shown.bs.tab', function() {
            Usuarios.cargarUsuarios();
        });
    }
    
    // Cargar auditoría completa cuando se active el tab
    const auditoriaTab = document.getElementById('auditoria-tab');
    if (auditoriaTab) {
        auditoriaTab.addEventListener('shown.bs.tab', function() {
            Auditoria.cargarAuditoriaCompleta();
        });
    }
    
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

window.exportarCSV = Reportes.exportarCSV;
window.exportarExcel = Reportes.exportarExcel;
window.exportarPDF = Reportes.exportarPDF;

window.calcularFactores = Cargas.calcularFactores;
window.cargarFactor = Cargas.cargarFactor;
window.cargarMonto = Cargas.cargarMonto;

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

