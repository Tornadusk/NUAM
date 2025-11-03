/**
 * auditoria.js - Módulo de Auditoría
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - Cargar y mostrar eventos de auditoría recientes (sidebar)
 * - Cargar y mostrar auditoría completa (tab)
 */

import { API_BASE_URL } from './core.js';

/**
 * Cargar y mostrar últimos 5 eventos de auditoría
 */
export function cargarAuditoriaReciente() {
    fetch(`${API_BASE_URL}/auditoria/?limit=5`)
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById('auditoriaReciente');
        if (!container) return;
        
        const auditoriaList = data.results || data;
        
        if (auditoriaList.length === 0) {
            container.innerHTML = '<small class="text-muted">No hay eventos recientes</small>';
            return;
        }
        container.innerHTML = auditoriaList.map(event => `
            <div class="d-flex justify-content-between align-items-start mb-2 pb-2 border-bottom">
                <div>
                    <div class="fw-semibold">${event.accion} - ${event.entidad}</div>
                    <small class="text-muted">${event.fecha}</small>
                </div>
                <small class="badge bg-secondary">ID ${event.entidad_id}</small>
            </div>
        `).join('');
    })
    .catch(error => {
        console.error('Error:', error);
        const container = document.getElementById('auditoriaReciente');
        if (container) {
            container.innerHTML = '<small class="text-danger">Error al cargar auditoría</small>';
        }
    });
}

/**
 * Cargar auditoría completa para el tab
 */
export async function cargarAuditoriaCompleta() {
    try {
        const res = await fetch(`${API_BASE_URL}/auditoria/`);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        const auditoriaList = data.results || data;
        renderAuditoria(auditoriaList);
    } catch (error) {
        console.error('Error cargando auditoría:', error);
        const tbody = document.getElementById('tBodyAuditoria');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-circle me-2"></i> Error al cargar auditoría
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * Renderizar auditoría en tabla
 */
function renderAuditoria(auditoriaList) {
    const tbody = document.getElementById('tBodyAuditoria');
    if (!tbody) return;
    
    if (!auditoriaList || auditoriaList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4">
                    No hay registros de auditoría
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = auditoriaList.map(event => `
        <tr>
            <td>${event.fecha || '-'}</td>
            <td>${event.actor_id ? 'Usuario ID:' + event.actor_id : '-'}</td>
            <td><span class="badge bg-info">${event.accion || '-'}</span></td>
            <td>${event.entidad || '-'}</td>
            <td><small class="text-muted">${event.entidad_id || '-'}</small></td>
        </tr>
    `).join('');
}

