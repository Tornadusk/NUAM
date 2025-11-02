/**
 * NUAM - Sistema de Calificaciones Tributarias
 * JavaScript Principal
 */

// Wait for document to be ready
$(document).ready(function() {
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers
    if (typeof bootstrap !== 'undefined') {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
    
    // Confirm delete actions
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('¿Está seguro de que desea eliminar este registro?')) {
            e.preventDefault();
            return false;
        }
    });
    
    // Form validation
    $('form').on('submit', function(e) {
        if (this.checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
    
    // Loading states for buttons
    $('.btn-loading').on('click', function() {
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.html('<span class="loading-spinner"></span> Cargando...');
    });
    
    // AJAX form submission
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        var $form = $(this);
        var $submitBtn = $form.find('button[type="submit"]');
        
        $.ajax({
            url: $form.attr('action'),
            method: $form.attr('method') || 'POST',
            data: $form.serialize(),
            beforeSend: function() {
                $submitBtn.prop('disabled', true);
                $submitBtn.html('<span class="loading-spinner"></span> Enviando...');
            },
            success: function(response) {
                if (response.success) {
                    showAlert('success', response.message || 'Operación realizada exitosamente');
                    if (response.redirect) {
                        setTimeout(function() {
                            window.location.href = response.redirect;
                        }, 1500);
                    } else if (response.reload) {
                        setTimeout(function() {
                            location.reload();
                        }, 1500);
                    }
                } else {
                    showAlert('danger', response.message || 'Error en la operación');
                }
            },
            error: function(xhr, status, error) {
                showAlert('danger', 'Error de conexión. Por favor, intente nuevamente.');
                console.error('Error:', error);
            },
            complete: function() {
                $submitBtn.prop('disabled', false);
                $submitBtn.html($submitBtn.data('original-text') || 'Enviar');
            }
        });
    });
    
    // Table row highlight
    $('.table tbody tr').on('click', function() {
        $('.table tbody tr').removeClass('table-active');
        $(this).addClass('table-active');
    });
    
    // Search functionality
    $('#searchInput').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('.searchable').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
    
    // Print functionality
    $('.btn-print').on('click', function() {
        window.print();
    });
    
    // Scroll to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });
    
    $('.scroll-to-top').on('click', function() {
        $('html, body').animate({scrollTop: 0}, 600);
    });
    
    // Fade in elements
    $('.fade-in').fadeIn('slow');
    
});

/**
 * Show alert message
 */
function showAlert(type, message) {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    var $alert = $(alertHtml);
    $('.container:first').prepend($alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(function() {
        $alert.fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

/**
 * Get icon for alert type
 */
function getAlertIcon(type) {
    switch(type) {
        case 'success':
            return 'check-circle';
        case 'danger':
        case 'error':
            return 'exclamation-circle';
        case 'warning':
            return 'exclamation-triangle';
        case 'info':
            return 'info-circle';
        default:
            return 'info-circle';
    }
}

/**
 * Format currency
 */
function formatCurrency(value, currency = 'CLP') {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * Format date
 */
function formatDate(date) {
    if (!date) return '-';
    var d = new Date(date);
    return d.toLocaleDateString('es-CL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format datetime
 */
function formatDateTime(date) {
    if (!date) return '-';
    var d = new Date(date);
    return d.toLocaleString('es-CL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Debounce function
 */
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    var inThrottle;
    return function() {
        var args = arguments;
        var context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(function() {
                inThrottle = false;
            }, limit);
        }
    };
}

// Export functions for use in other scripts
window.NUAM = {
    showAlert: showAlert,
    formatCurrency: formatCurrency,
    formatDate: formatDate,
    formatDateTime: formatDateTime,
    debounce: debounce,
    throttle: throttle
};

