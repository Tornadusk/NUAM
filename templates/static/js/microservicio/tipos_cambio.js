/**
 * tipos_cambio.js - Dashboard de Tipos de Cambio
 * NUAM - Microservicio de Tipos de Cambio
 * 
 * CONEXIONES DEL PROYECTO:
 * ------------------------
 * Este archivo JS se carga en:
 * - templates/microservicio/tipos_cambio/dashboard.html (dashboard de tipos de cambio)
 * 
 * PETICIONES DE TIPOS DE CAMBIO (TC):
 * -----------------------------------
 * Este archivo hace las siguientes peticiones TC:
 * - GET /microservicio/api/tipos-cambio-por-pais/<codigo_pais>/ (obtener tipos de cambio por país)
 * - GET /microservicio/api/tipos-cambio-actuales/ (obtener tipos de cambio actuales)
 * - POST /microservicio/api/obtener-tipos-cambio/ (ejecutar comando obtener_tipos_cambio)
 * 
 * FUNCIONALIDADES:
 * ----------------
 * - Cargar tipos de cambio por país (CHL, PER, COL, USA)
 * - Mostrar tipos de cambio actuales en tarjetas
 * - Mostrar estadísticas (promedio, máximo, mínimo)
 * - Mostrar tabla de tipos de cambio recientes
 * - Mostrar gráfico histórico con Chart.js
 * - Actualizar tipos de cambio desde APIs externas
 */

// Variable global para el gráfico histórico
let graficoHistorico = null;

/**
 * Cargar tipos de cambio por país
 * Petición TC: GET /microservicio/api/tipos-cambio-por-pais/<codigo_pais>/
 */
function cargarTiposCambio(codigoPais, clickedButton = null) {
    // Actualizar botones activos
    document.querySelectorAll('.country-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    // Activar el botón clickeado si se proporciona
    if (clickedButton) {
        clickedButton.classList.add('active');
    }

    const url = codigoPais 
        ? `/microservicio/api/tipos-cambio-por-pais/${codigoPais}/`
        : '/microservicio/api/tipos-cambio-por-pais/';

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data); // Debug
            if (data.error) {
                console.error('Error en respuesta:', data.error);
                mostrarError(data.error);
                return;
            }
            
            // Verificar que existan los datos esperados
            if (!data.tipos_cambio_recientes) {
                console.warn('No se encontró tipos_cambio_recientes en la respuesta:', data);
                mostrarError('La respuesta de la API no tiene el formato esperado');
                return;
            }
            
            mostrarTiposActuales(data);
            mostrarEstadisticas(data);
            mostrarTablaTiposCambio(data);
            mostrarGraficoHistorico(data);
        })
        .catch(error => {
            console.error('Error al cargar tipos de cambio:', error);
            mostrarError('Error al cargar los tipos de cambio: ' + error.message);
        });
}

/**
 * Mostrar tipos de cambio actuales en tarjetas
 */
function mostrarTiposActuales(data) {
    const container = document.getElementById('tipos-actuales-content');
    
    if (!data.tipos_cambio_recientes || data.tipos_cambio_recientes.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay tipos de cambio disponibles</p>';
        return;
    }

    let html = '<div class="row">';
    data.tipos_cambio_recientes.forEach(tipo => {
        html += `
            <div class="col-md-3 mb-3">
                <div class="stat-card-exchange">
                    <h3>${tipo.par}</h3>
                    <div class="tasa">${tipo.tasa_actual.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</div>
                    <div class="fecha">
                        <i class="fas fa-calendar me-1"></i>
                        ${tipo.fecha_actual || 'N/A'}
                    </div>
                    ${tipo.fuente ? `<small><i class="fas fa-database me-1"></i>${tipo.fuente}</small>` : ''}
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

/**
 * Mostrar estadísticas de tipos de cambio
 */
function mostrarEstadisticas(data) {
    const container = document.getElementById('estadisticas-content');
    
    if (!data.tipos_cambio_recientes || data.tipos_cambio_recientes.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay estadísticas disponibles</p>';
        return;
    }

    let html = '';
    data.tipos_cambio_recientes.forEach(tipo => {
        const stats = tipo.estadisticas;
        html += `
            <div class="mb-3 p-3 border rounded">
                <h6 class="par-moneda">${tipo.par}</h6>
                <div class="small">
                    <div class="mb-2">
                        <strong>Registros:</strong> ${stats.total_registros}
                    </div>
                    <div class="mb-2">
                        <strong>Promedio:</strong> ${stats.tasa_promedio.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}
                    </div>
                    <div class="mb-2">
                        <strong>Máximo:</strong> ${stats.tasa_maxima.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}
                    </div>
                    <div>
                        <strong>Mínimo:</strong> ${stats.tasa_minima.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html || '<p class="text-muted text-center">No hay estadísticas disponibles</p>';
}

/**
 * Mostrar tabla de tipos de cambio recientes
 */
function mostrarTablaTiposCambio(data) {
    const tbody = document.getElementById('tabla-tipos-cambio');
    
    if (!data.tipos_cambio_recientes || data.tipos_cambio_recientes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No hay datos disponibles</td></tr>';
        return;
    }

    let html = '';
    data.tipos_cambio_recientes.forEach(tipo => {
        const stats = tipo.estadisticas;
        html += `
            <tr>
                <td><span class="par-moneda">${tipo.par}</span></td>
                <td><strong>${tipo.tasa_actual.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</strong></td>
                <td>${stats.tasa_promedio.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</td>
                <td>${stats.tasa_maxima.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</td>
                <td>${stats.tasa_minima.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</td>
                <td>${tipo.fecha_actual || 'N/A'}</td>
                <td><small>${tipo.fuente || 'N/A'}</small></td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

/**
 * Mostrar gráfico histórico con Chart.js
 */
function mostrarGraficoHistorico(data) {
    // Esperar a que el DOM esté completamente cargado
    const buscarCanvas = () => {
        const ctx = document.getElementById('grafico-historico');
        if (!ctx) {
            // Si no existe, intentar de nuevo después de un pequeño delay
            setTimeout(buscarCanvas, 100);
            return;
        }
        crearGrafico(ctx, data);
    };
    
    buscarCanvas();
}

/**
 * Crea el gráfico histórico en el canvas proporcionado
 */
function crearGrafico(ctx, data) {
    // Verificar que el elemento existe y es un canvas válido
    if (!ctx || !ctx.getContext) {
        console.warn('Elemento grafico-historico no encontrado o no es un canvas válido');
        return;
    }
    
    if (!data.historico_mensual || data.historico_mensual.length === 0) {
        // Destruir gráfico anterior si existe
        if (typeof graficoHistorico !== 'undefined' && graficoHistorico) {
            try {
                graficoHistorico.destroy();
            } catch (e) {
                console.warn('Error al destruir gráfico anterior:', e);
            }
            graficoHistorico = null;
        }
        
        // Mostrar mensaje de que no hay datos
        const chartContainer = ctx.closest('.chart-container') || ctx.parentElement;
        if (chartContainer) {
            chartContainer.innerHTML = '<p class="text-muted text-center py-5">No hay datos históricos disponibles para mostrar</p>';
        }
        return;
    }

    // Agrupar por par de monedas
    const pares = {};
    data.historico_mensual.forEach(item => {
        const par = `${item.moneda_origen}/${item.moneda_destino}`;
        if (!pares[par]) {
            pares[par] = [];
        }
        pares[par].push({
            fecha: `${item.año}-${String(item.mes).padStart(2, '0')}`,
            tasa: parseFloat(item.tasa_promedio)
        });
    });

    // Ordenar por fecha
    Object.keys(pares).forEach(par => {
        pares[par].sort((a, b) => a.fecha.localeCompare(b.fecha));
    });

    // Preparar datos para Chart.js
    const datasets = Object.keys(pares).map((par, index) => {
        const colors = [
            'rgb(102, 126, 234)',
            'rgb(255, 51, 51)',
            'rgb(25, 135, 84)',
            'rgb(255, 193, 7)',
            'rgb(220, 53, 69)'
        ];
        return {
            label: par,
            data: pares[par].map(item => item.tasa),
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length].replace('rgb', 'rgba').replace(')', ', 0.1)'),
            tension: 0.4,
            fill: false
        };
    });

    // Obtener todas las fechas únicas
    const todasFechas = [...new Set(data.historico_mensual.map(item => 
        `${item.año}-${String(item.mes).padStart(2, '0')}`
    ))].sort();

    // Verificar nuevamente que ctx existe y es un elemento válido antes de crear el gráfico
    if (!ctx || !ctx.getContext) {
        console.error('No se puede crear el gráfico: elemento grafico-historico no encontrado o no es un canvas válido');
        // Intentar encontrar el contenedor para mostrar un mensaje de error
        try {
            const chartContainer = document.querySelector('.chart-container');
            if (chartContainer) {
                chartContainer.innerHTML = '<p class="text-danger text-center">Error: No se pudo crear el gráfico</p>';
            }
        } catch (e) {
            console.warn('No se pudo mostrar mensaje de error:', e);
        }
        return;
    }

    // Limpiar gráfico anterior si existe
    if (graficoHistorico) {
        try {
            graficoHistorico.destroy();
        } catch (e) {
            console.warn('Error al destruir gráfico anterior:', e);
        }
        graficoHistorico = null;
    }

    // Intentar crear el gráfico con manejo de errores
    try {
        graficoHistorico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: todasFechas,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('es-CL', {minimumFractionDigits: 2, maximumFractionDigits: 4});
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
    } catch (error) {
        console.error('Error al crear el gráfico de Chart.js:', error);
        // Mostrar mensaje de error en el contenedor
        if (ctx) {
            const container = ctx.closest('.chart-container, .card-body');
            if (container) {
                container.innerHTML = '<p class="text-danger text-center">Error al crear el gráfico. Ver consola para más detalles.</p>';
            }
        }
        graficoHistorico = null;
    }
}

/**
 * Actualizar tipos de cambio desde APIs externas
 * Petición TC: POST /microservicio/api/obtener-tipos-cambio/
 */
function actualizarTiposCambio() {
    // Esperar a que el DOM esté completamente cargado si es necesario
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', actualizarTiposCambio);
        return;
    }
    
    const btn = document.getElementById('btn-actualizar-tipos');
    
    // Validar que el botón exista
    if (!btn) {
        console.error('Botón btn-actualizar-tipos no encontrado');
        alert('Error: No se pudo encontrar el botón de actualización');
        return;
    }
    
    // Buscar el elemento de mensaje
    let mensajeDiv = document.getElementById('mensaje-actualizacion');
    
    // Si no existe, crearlo dinámicamente (el elemento debería existir en el HTML, pero por si acaso)
    if (!mensajeDiv) {
        const container = document.querySelector('.container-fluid');
        if (container) {
            mensajeDiv = document.createElement('div');
            mensajeDiv.id = 'mensaje-actualizacion';
            mensajeDiv.className = 'alert alert-info d-none';
            mensajeDiv.setAttribute('role', 'alert');
            mensajeDiv.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i><span id="mensaje-texto">Actualizando tipos de cambio...</span>';
            // Insertar después del header (después del primer row)
            const firstRow = container.querySelector('.row:first-of-type');
            if (firstRow) {
                firstRow.insertAdjacentElement('afterend', mensajeDiv);
            } else {
                container.insertBefore(mensajeDiv, container.firstChild);
            }
        }
    }
    
    // Obtener el elemento de texto del mensaje
    let mensajeTexto = null;
    if (mensajeDiv) {
        mensajeTexto = mensajeDiv.querySelector('#mensaje-texto');
        if (!mensajeTexto) {
            // Si no existe el span, crearlo
            mensajeTexto = document.createElement('span');
            mensajeTexto.id = 'mensaje-texto';
            mensajeDiv.appendChild(mensajeTexto);
        }
    }
    
    // Deshabilitar botón y mostrar loading
    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Actualizando...';
        
        if (mensajeDiv && mensajeTexto) {
            mensajeDiv.classList.remove('d-none', 'alert-success', 'alert-danger');
            mensajeDiv.classList.add('alert-info');
            mensajeTexto.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Actualizando tipos de cambio desde APIs externas...';
        }
    } catch (e) {
        console.error('Error al inicializar elementos:', e);
        alert('Error al inicializar la actualización. Por favor, recarga la página.');
        return;
    }
    
    // Obtener país actual seleccionado
    const paisActual = document.querySelector('.country-btn.active');
    let codigoPais = null;
    if (paisActual) {
        const onclickAttr = paisActual.getAttribute('onclick');
        if (onclickAttr) {
            const match = onclickAttr.match(/cargarTiposCambio\('?([^',)]+)'?/);
            codigoPais = match ? (match[1] === 'null' ? null : match[1]) : null;
        }
    }
    
    fetch('/microservicio/api/obtener-tipos-cambio/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            monedas: 'CLP,PEN,COP',
            forzar: false
        })
    })
    .then(response => response.json())
    .then(data => {
        // Re-buscar elementos por si acaso
        if (!mensajeDiv) {
            mensajeDiv = document.getElementById('mensaje-actualizacion');
        }
        if (!mensajeTexto && mensajeDiv) {
            mensajeTexto = mensajeDiv.querySelector('#mensaje-texto');
        }
        
        if (!mensajeDiv || !mensajeTexto) {
            // Si aún no existen, mostrar alert en lugar de error silencioso
            if (data.success) {
                alert('Tipos de cambio actualizados correctamente. Recarga la página para ver los cambios.');
            } else {
                alert('Error al actualizar tipos de cambio: ' + (data.error || 'Error desconocido'));
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Actualizar desde APIs';
            return;
        }
        
        if (data.success) {
            // Mostrar éxito
            mensajeDiv.classList.remove('alert-info', 'alert-danger');
            mensajeDiv.classList.add('alert-success');
            mensajeTexto.innerHTML = `<i class="fas fa-check-circle me-2"></i>${data.message} (${data.tipos_obtenidos} tipos obtenidos)`;
            
            // Recargar los datos después de 1 segundo
            setTimeout(() => {
                cargarTiposCambio(codigoPais);
                if (mensajeDiv) {
                    mensajeDiv.classList.add('d-none');
                }
            }, 2000);
        } else {
            // Mostrar error
            mensajeDiv.classList.remove('alert-info', 'alert-success');
            mensajeDiv.classList.add('alert-danger');
            mensajeTexto.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Error: ${data.error || data.message || 'Error desconocido'}`;
        }
    })
    .catch(error => {
        console.error('Error al actualizar tipos de cambio:', error);
        if (mensajeDiv && mensajeTexto) {
            mensajeDiv.classList.remove('alert-info', 'alert-success');
            mensajeDiv.classList.add('alert-danger');
            mensajeTexto.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Error al actualizar tipos de cambio: ${error.message}`;
        }
    })
    .finally(() => {
        // Rehabilitar botón
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Actualizar desde APIs';
        }
    });
}

/**
 * Función auxiliar para obtener CSRF token desde cookies
 */
function getCookie(name) {
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
 * Mostrar mensaje de error
 */
function mostrarError(mensaje) {
    const container = document.getElementById('tipos-actuales-content');
    container.innerHTML = `<div class="alert alert-danger">${mensaje}</div>`;
}

/**
 * Generar datos simulados de tipos de cambio
 * Petición TC: POST /microservicio/api/generar-datos-simulados/
 */
function generarDatosSimulados() {
    const btn = document.getElementById('btn-generar-simulados');
    if (!btn) {
        console.error('Botón btn-generar-simulados no encontrado');
        return;
    }
    
    // Deshabilitar botón y mostrar loading
    btn.disabled = true;
    const textoOriginal = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generando...';
    
    // Obtener mensaje de actualización
    let mensajeDiv = document.getElementById('mensaje-actualizacion');
    let mensajeTexto = mensajeDiv ? mensajeDiv.querySelector('#mensaje-texto') : null;
    
    if (mensajeDiv && mensajeTexto) {
        mensajeDiv.classList.remove('d-none', 'alert-success', 'alert-danger');
        mensajeDiv.classList.add('alert-info');
        mensajeTexto.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generando datos simulados para los últimos 12 meses...';
    }
    
    fetch('/microservicio/api/generar-datos-simulados/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (mensajeDiv && mensajeTexto) {
            if (data.success) {
                mensajeDiv.classList.remove('alert-info', 'alert-danger');
                mensajeDiv.classList.add('alert-success');
                mensajeTexto.innerHTML = `<i class="fas fa-check-circle me-2"></i>${data.message}`;
                
                // Recargar los datos después de 1 segundo
                setTimeout(() => {
                    const paisActual = document.querySelector('.country-btn.active');
                    let codigoPais = null;
                    if (paisActual) {
                        const onclickAttr = paisActual.getAttribute('onclick');
                        if (onclickAttr) {
                            const match = onclickAttr.match(/cargarTiposCambio\('?([^',)]+)'?/);
                            codigoPais = match ? (match[1] === 'null' ? null : match[1]) : null;
                        }
                    }
                    cargarTiposCambio(codigoPais);
                    mensajeDiv.classList.add('d-none');
                }, 2000);
            } else {
                mensajeDiv.classList.remove('alert-info', 'alert-success');
                mensajeDiv.classList.add('alert-danger');
                mensajeTexto.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Error: ${data.error || 'Error desconocido'}`;
            }
        }
    })
    .catch(error => {
        console.error('Error al generar datos simulados:', error);
        if (mensajeDiv && mensajeTexto) {
            mensajeDiv.classList.remove('alert-info', 'alert-success');
            mensajeDiv.classList.add('alert-danger');
            mensajeTexto.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Error al generar datos simulados: ${error.message}`;
        }
    })
    .finally(() => {
        // Rehabilitar botón
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    });
}

// Exportar funciones para uso global INMEDIATAMENTE (onclick en HTML)
// Esto asegura que las funciones estén disponibles tan pronto como se carga el script
window.cargarTiposCambio = cargarTiposCambio;
window.actualizarTiposCambio = actualizarTiposCambio;
window.generarDatosSimulados = generarDatosSimulados;

// Inicialización al cargar el DOM
// Usar DOMContentLoaded o verificar si el DOM ya está listo
(function() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            // Cargar todos los países por defecto
            cargarTiposCambio(null);
        });
    } else {
        // DOM ya está listo, ejecutar inmediatamente
        cargarTiposCambio(null);
    }
})();

