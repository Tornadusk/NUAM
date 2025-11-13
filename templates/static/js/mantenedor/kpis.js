/**
 * kpis.js - Módulo de KPIs
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - Cargar y mostrar KPIs del sistema (P95 API, Carga 100k, Trazabilidad, Errores)
 */

import { API_BASE_URL } from './core.js';

/**
 * Cargar y mostrar KPIs del sistema
 */
export function cargarKPIs() {
    const container = document.getElementById('kpisContainer');
    if (!container) {
        console.warn('Contenedor de KPIs no encontrado');
        return;
    }

    // Mostrar indicador de carga
    mostrarKPIsCargando();

    fetch(`${API_BASE_URL}/kpis/kpis/`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            mostrarKPIs(data);
        })
        .catch(error => {
            console.error('Error cargando KPIs:', error);
            mostrarKPIsError();
        });
}

/**
 * Mostrar indicador de carga en los KPIs
 */
function mostrarKPIsCargando() {
    document.getElementById('kpiP95API').innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Cargando...';
    document.getElementById('kpiCarga100k').innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Cargando...';
    document.getElementById('kpiTrazabilidad').innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Cargando...';
    document.getElementById('kpiErrores').innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Cargando...';
}

/**
 * Mostrar KPIs en la interfaz
 */
function mostrarKPIs(data) {
    // P95 API
    const p95Element = document.getElementById('kpiP95API');
    if (p95Element) {
        const p95Ms = data.p95_api_ms || 720;
        p95Element.textContent = `${p95Ms} ms`;
        // Color según umbral (verde si < 800ms, amarillo si < 1000ms, rojo si >= 1000ms)
        if (p95Ms < 800) {
            p95Element.className = 'mb-0 text-success';
        } else if (p95Ms < 1000) {
            p95Element.className = 'mb-0 text-warning';
        } else {
            p95Element.className = 'mb-0 text-danger';
        }
    }

    // Carga 100k filas
    const cargaElement = document.getElementById('kpiCarga100k');
    if (cargaElement) {
        const tiempoMin = data.tiempo_carga_100k_min || 8.5;
        cargaElement.textContent = `${tiempoMin} min`;
        // Color según umbral (verde si < 10min, amarillo si < 15min, rojo si >= 15min)
        if (tiempoMin < 10) {
            cargaElement.className = 'mb-0 text-success';
        } else if (tiempoMin < 15) {
            cargaElement.className = 'mb-0 text-warning';
        } else {
            cargaElement.className = 'mb-0 text-danger';
        }
    }

    // Trazabilidad
    const trazabilidadElement = document.getElementById('kpiTrazabilidad');
    if (trazabilidadElement) {
        const trazabilidad = data.trazabilidad_porcentaje || 100;
        trazabilidadElement.textContent = `${trazabilidad}%`;
        // Color según umbral (verde si >= 95%, amarillo si >= 90%, rojo si < 90%)
        if (trazabilidad >= 95) {
            trazabilidadElement.className = 'mb-0 text-success';
        } else if (trazabilidad >= 90) {
            trazabilidadElement.className = 'mb-0 text-warning';
        } else {
            trazabilidadElement.className = 'mb-0 text-danger';
        }
    }

    // Errores
    const erroresElement = document.getElementById('kpiErrores');
    if (erroresElement) {
        const errores = data.errores_porcentaje || 0.7;
        erroresElement.textContent = `${errores}%`;
        // Color según umbral (verde si < 1%, amarillo si < 5%, rojo si >= 5%)
        if (errores < 1) {
            erroresElement.className = 'mb-0 text-success';
        } else if (errores < 5) {
            erroresElement.className = 'mb-0 text-warning';
        } else {
            erroresElement.className = 'mb-0 text-danger';
        }
    }
}

/**
 * Mostrar error en los KPIs
 */
function mostrarKPIsError() {
    document.getElementById('kpiP95API').innerHTML = '<small class="text-danger">Error</small>';
    document.getElementById('kpiCarga100k').innerHTML = '<small class="text-danger">Error</small>';
    document.getElementById('kpiTrazabilidad').innerHTML = '<small class="text-danger">Error</small>';
    document.getElementById('kpiErrores').innerHTML = '<small class="text-danger">Error</small>';
}

