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
    const tbody = document.getElementById('tBodyAuditoria');
    if (!tbody) {
        console.warn('tBodyAuditoria no encontrado, el tab de auditoría puede no estar visible');
        return;
    }
    
    // Mostrar estado de carga
    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="text-center text-muted py-4">
                <i class="fas fa-spinner fa-spin me-2"></i> Cargando auditoría...
            </td>
        </tr>
    `;
    
    try {
        console.log('Cargando auditoría desde:', `${API_BASE_URL}/auditoria/`);
        const res = await fetch(`${API_BASE_URL}/auditoria/`);
        
        if (!res.ok) {
            const errorText = await res.text();
            console.error('Error HTTP:', res.status, errorText);
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        console.log('Auditoría recibida:', data);
        const auditoriaList = data.results || data;
        
        console.log(`Total de eventos de auditoría: ${auditoriaList.length}`);
        renderAuditoria(auditoriaList);
    } catch (error) {
        console.error('Error cargando auditoría:', error);
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-circle me-2"></i> Error al cargar auditoría: ${error.message}
                        <br><small>Ver consola (F12) para más detalles</small>
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
    if (!tbody) {
        console.warn('tBodyAuditoria no encontrado');
        return;
    }
    
    if (!auditoriaList || auditoriaList.length === 0) {
        console.log('No hay registros de auditoría para mostrar');
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4">
                    <i class="fas fa-info-circle me-2"></i> No hay registros de auditoría
                    <br><small>Los eventos de auditoría aparecerán aquí cuando se realicen acciones en el sistema</small>
                </td>
            </tr>
        `;
        return;
    }
    
    console.log(`Renderizando ${auditoriaList.length} eventos de auditoría`);
    
    tbody.innerHTML = auditoriaList.map((event, index) => {
        console.log(`Evento ${index + 1}:`, event);
        
        // Formatear fecha
        let fechaStr = '-';
        if (event.fecha) {
            try {
                const fecha = new Date(event.fecha);
                fechaStr = fecha.toLocaleString('es-CL', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                fechaStr = event.fecha;
            }
        }
        
        // Usuario: intentar mostrar username, sino ID
        let usuarioStr = '-';
        if (event.actor_username) {
            usuarioStr = event.actor_username;
        } else if (event.actor_id) {
            usuarioStr = `ID: ${event.actor_id}`;
        }
        
        // Badge de acción con color según tipo
        let accionBadge = event.accion || '-';
        let badgeClass = 'bg-info';
        if (event.accion) {
            const accionUpper = event.accion.toUpperCase();
            if (accionUpper.includes('INSERT') || accionUpper.includes('CREATE')) {
                badgeClass = 'bg-success';
            } else if (accionUpper.includes('UPDATE') || accionUpper.includes('MODIFY')) {
                badgeClass = 'bg-warning';
            } else if (accionUpper.includes('DELETE') || accionUpper.includes('REMOVE')) {
                badgeClass = 'bg-danger';
            }
        }
        
        return `
            <tr>
                <td><small>${fechaStr}</small></td>
                <td>${usuarioStr}</td>
                <td><span class="badge ${badgeClass}">${accionBadge}</span></td>
                <td>${event.entidad || '-'}</td>
                <td><small class="text-muted">${event.entidad_id || '-'}</small></td>
            </tr>
        `;
    }).join('');
}

