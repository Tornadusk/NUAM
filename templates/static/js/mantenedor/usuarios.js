/**
 * usuarios.js - Módulo de Gestión de Usuarios
 * NUAM - Mantenedor de Calificaciones Tributarias
 * 
 * Funcionalidades:
 * - CRUD completo de usuarios (Persona + Usuario + Colaborador)
 * - Asignación de roles
 * - Validaciones de formulario
 * - Manejo de password toggles
 */

import { API_BASE_URL, fetchWithCSRF, populateSelect } from './core.js';

let catalogoRoles = [];
let catalogoPaises = [];

/**
 * Cargar roles desde la API
 */
export async function cargarRoles() {
    try {
        const rolesRes = await fetch(`${API_BASE_URL}/roles/`);
        if (rolesRes.ok) {
            const data = await rolesRes.json();
            catalogoRoles = data.results || data; // Manejar paginación
            populateSelect('crearRoles', catalogoRoles.map(r => ({ value: r.id_rol, text: r.nombre })));
            populateSelect('editarRoles', catalogoRoles.map(r => ({ value: r.id_rol, text: r.nombre })));
        }
    } catch (error) {
        console.error('Error cargando roles:', error);
    }
}

/**
 * Cargar países desde la API para nacionalidad (valor = codigo ISO-3)
 */
export async function cargarPaises() {
    try {
        const res = await fetch(`${API_BASE_URL}/paises/`);
        if (res.ok) {
            const data = await res.json();
            catalogoPaises = data.results || data;
            const opciones = catalogoPaises.map(p => ({ value: p.codigo, text: `${p.nombre} (${p.codigo})` }));
            populateSelect('crearNacionalidad', [{ value: '', text: 'Seleccione...' }, ...opciones]);
            populateSelect('editarNacionalidad', [{ value: '', text: 'Seleccione...' }, ...opciones]);
        }
    } catch (error) {
        console.error('Error cargando países:', error);
    }
}

/**
 * Cargar usuarios desde la API
 */
export async function cargarUsuarios() {
    const tbody = document.getElementById('tBodyUsuarios');
    if (!tbody) {
        console.warn('tBodyUsuarios no encontrado, el tab de usuarios puede no estar visible');
        return;
    }
    
    // Mostrar estado de carga
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center text-muted py-4">
                <i class="fas fa-spinner fa-spin me-2"></i> Cargando usuarios...
            </td>
        </tr>
    `;
    
    try {
        console.log('Cargando usuarios desde:', `${API_BASE_URL}/usuarios/`);
        const res = await fetch(`${API_BASE_URL}/usuarios/`);
        
        if (!res.ok) {
            const errorText = await res.text();
            console.error('Error HTTP:', res.status, errorText);
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        console.log('Usuarios recibidos:', data);
        const usuarios = data.results || data;
        renderUsuarios(usuarios);
    } catch (error) {
        console.error('Error cargando usuarios:', error);
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-circle me-2"></i> Error al cargar usuarios: ${error.message}
                        <br><small>Ver consola (F12) para más detalles</small>
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * Renderizar usuarios en tabla
 */
function renderUsuarios(usuarios) {
    const tbody = document.getElementById('tBodyUsuarios');
    if (!tbody) return;

    if (!usuarios || usuarios.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    No hay usuarios registrados
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = usuarios.map(usuario => {
        // Roles: puede ser array o string
        const roles = usuario.roles 
            ? (Array.isArray(usuario.roles) ? usuario.roles.join(', ') : usuario.roles)
            : 'Sin rol';
        
        // Estado: badge con color
        const estadoBadge = usuario.estado === 'activo' 
            ? '<span class="badge bg-success">Activo</span>'
            : '<span class="badge bg-danger">Bloqueado</span>';
        
        // Nombre completo: desde id_persona_detalle (objeto PersonaSerializer)
        let nombreCompleto = 'N/A';
        if (usuario.id_persona_detalle) {
            const persona = usuario.id_persona_detalle;
            const primerNombre = persona.primer_nombre || '';
            const apellidoPaterno = persona.apellido_paterno || '';
            nombreCompleto = `${primerNombre} ${apellidoPaterno}`.trim() || 'N/A';
        }
        
        // Email: desde colaborador (string o null)
        const email = usuario.colaborador || 'N/A';
        
        return `
            <tr>
                <td>${usuario.id_usuario || '-'}</td>
                <td><strong>${usuario.username || '-'}</strong></td>
                <td>${nombreCompleto}</td>
                <td>${email}</td>
                <td>${roles}</td>
                <td>${estadoBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editarUsuario(${usuario.id_usuario})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarUsuario(${usuario.id_usuario})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Abrir modal de crear usuario
 */
export async function abrirModalCrearUsuario() {
    // Limpiar formulario
    document.getElementById('formCrearUsuario').reset();
    document.getElementById('colaboradorEmailContainer').style.display = 'none';
    document.getElementById('crearEsColaborador').checked = false;
    document.getElementById('passwordMatchError').style.display = 'none';
    document.getElementById('crearPasswordConfirm').classList.remove('is-invalid');
    document.getElementById('emailErrorCreate').style.display = 'none';
    document.getElementById('crearEmail').classList.remove('is-invalid');
    
    // Establecer fecha máxima (hoy) para fecha de nacimiento
    const fechaNacimientoInput = document.getElementById('crearFechaNacimiento');
    if (fechaNacimientoInput) {
        const hoy = new Date();
        const fechaMax = new Date(hoy.getFullYear() - 18, hoy.getMonth(), hoy.getDate()); // 18 años atrás
        fechaNacimientoInput.max = fechaMax.toISOString().split('T')[0];
        fechaNacimientoInput.setAttribute('max', fechaMax.toISOString().split('T')[0]);
    }
    
    // Si no hay roles cargados aún, cargarlos
    if (catalogoRoles.length === 0) {
        await cargarRoles();
    }
    // Cargar países si fuese necesario
    if (catalogoPaises.length === 0) {
        await cargarPaises();
    }
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalCrearUsuario'));
    modal.show();
}

/**
 * Guardar nuevo usuario
 */
export async function guardarUsuario() {
    const form = document.getElementById('formCrearUsuario');
    
    // Validar username PRIMERO
    const username = document.getElementById('crearUsername').value.trim();
    if (!username || username.length < 3) {
        const usernameInput = document.getElementById('crearUsername');
        usernameInput.classList.add('is-invalid');
        let errorDiv = document.getElementById('crearUsernameError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'crearUsernameError';
            errorDiv.className = 'invalid-feedback';
            usernameInput.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = 'El username debe tener al menos 3 caracteres.';
        errorDiv.style.display = 'block';
        alert('❌ Error: El username debe tener al menos 3 caracteres.');
        usernameInput.focus();
        return;
    }
    if (username.length > 60) {
        const usernameInput = document.getElementById('crearUsername');
        usernameInput.classList.add('is-invalid');
        let errorDiv = document.getElementById('crearUsernameError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'crearUsernameError';
            errorDiv.className = 'invalid-feedback';
            usernameInput.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = 'El username no puede tener más de 60 caracteres.';
        errorDiv.style.display = 'block';
        alert('❌ Error: El username no puede tener más de 60 caracteres.');
        usernameInput.focus();
        return;
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        const usernameInput = document.getElementById('crearUsername');
        usernameInput.classList.add('is-invalid');
        let errorDiv = document.getElementById('crearUsernameError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'crearUsernameError';
            errorDiv.className = 'invalid-feedback';
            usernameInput.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = 'El username solo puede contener letras, números, guiones (-) y guiones bajos (_).';
        errorDiv.style.display = 'block';
        alert('❌ Error: El username solo puede contener letras, números, guiones (-) y guiones bajos (_).');
        usernameInput.focus();
        return;
    }
    // Limpiar errores de username si es válido
    document.getElementById('crearUsername').classList.remove('is-invalid');
    const usernameErrorDiv = document.getElementById('crearUsernameError');
    if (usernameErrorDiv) {
        usernameErrorDiv.style.display = 'none';
    }
    
    // Validar contraseña SEGUNDO (ANTES de validar coincidencia)
    const password = document.getElementById('crearPassword').value;
    if (!password || password.length < 6) {
        const passwordInput = document.getElementById('crearPassword');
        passwordInput.classList.add('is-invalid');
        let errorDiv = document.getElementById('crearPasswordError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'crearPasswordError';
            errorDiv.className = 'invalid-feedback';
            passwordInput.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = 'La contraseña debe tener al menos 6 caracteres.';
        errorDiv.style.display = 'block';
        alert('❌ Error: La contraseña debe tener al menos 6 caracteres.');
        passwordInput.focus();
        return;
    }
    if (password.length > 128) {
        const passwordInput = document.getElementById('crearPassword');
        passwordInput.classList.add('is-invalid');
        let errorDiv = document.getElementById('crearPasswordError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'crearPasswordError';
            errorDiv.className = 'invalid-feedback';
            passwordInput.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = 'La contraseña no puede tener más de 128 caracteres.';
        errorDiv.style.display = 'block';
        alert('❌ Error: La contraseña no puede tener más de 128 caracteres.');
        passwordInput.focus();
        return;
    }
    // Limpiar errores de contraseña si es válida
    document.getElementById('crearPassword').classList.remove('is-invalid');
    const passwordErrorDiv = document.getElementById('crearPasswordError');
    if (passwordErrorDiv) {
        passwordErrorDiv.style.display = 'none';
    }
    
    // Validar contraseñas coincidan TERCERO
    const passwordConfirm = document.getElementById('crearPasswordConfirm').value;
    
    if (password !== passwordConfirm) {
        const errorDiv = document.getElementById('passwordMatchError');
        errorDiv.style.display = 'block';
        document.getElementById('crearPasswordConfirm').classList.add('is-invalid');
        alert('❌ Error: Las contraseñas no coinciden.');
        document.getElementById('crearPasswordConfirm').focus();
        return;
    } else {
        document.getElementById('passwordMatchError').style.display = 'none';
        document.getElementById('crearPasswordConfirm').classList.remove('is-invalid');
    }
    
    // Validar fecha de nacimiento
    const fechaNacimiento = document.getElementById('crearFechaNacimiento').value;
    if (fechaNacimiento) {
        const fechaNac = new Date(fechaNacimiento);
        const hoy = new Date();
        if (fechaNac > hoy) {
            alert('❌ Error: La fecha de nacimiento no puede ser superior a la fecha actual.');
            document.getElementById('crearFechaNacimiento').focus();
            return;
        }
        // Validar edad mínima (18 años)
        const fechaMinima = new Date(hoy.getFullYear() - 18, hoy.getMonth(), hoy.getDate());
        if (fechaNac > fechaMinima) {
            alert('❌ Error: La fecha de nacimiento debe ser de al menos 18 años atrás.');
            document.getElementById('crearFechaNacimiento').focus();
            return;
        }
    }
    
    // Validar email Gmail si es colaborador
    const esColaborador = document.getElementById('crearEsColaborador').checked;
    if (esColaborador) {
        const email = document.getElementById('crearEmail').value.trim().toLowerCase();
        if (!email) {
            const errorDiv = document.getElementById('emailErrorCreate');
            errorDiv.style.display = 'block';
            errorDiv.textContent = 'El email es obligatorio si el usuario es colaborador.';
            document.getElementById('crearEmail').classList.add('is-invalid');
            alert('❌ Error: El email es obligatorio si el usuario es colaborador.');
            document.getElementById('crearEmail').focus();
            return;
        }
        if (!email.endsWith('@gmail.com')) {
            const errorDiv = document.getElementById('emailErrorCreate');
            errorDiv.style.display = 'block';
            errorDiv.textContent = 'El email debe ser una cuenta de Gmail válida (ej: usuario@gmail.com).';
            document.getElementById('crearEmail').classList.add('is-invalid');
            alert('❌ Error: El email debe ser una cuenta de Gmail válida (ej: usuario@gmail.com)');
            document.getElementById('crearEmail').focus();
            return;
        }
        // Extraer parte local
        const parteLocal = email.replace('@gmail.com', '');
        // Validar longitud mínima (1 carácter en parte local)
        if (parteLocal.length < 1) {
            const errorDiv = document.getElementById('emailErrorCreate');
            errorDiv.style.display = 'block';
            errorDiv.textContent = 'El email debe tener al menos 1 carácter antes de @gmail.com.';
            document.getElementById('crearEmail').classList.add('is-invalid');
            alert('❌ Error: El email debe tener al menos 1 carácter antes de @gmail.com.');
            document.getElementById('crearEmail').focus();
            return;
        }
        // Validar longitud máxima de parte local (64 caracteres)
        if (parteLocal.length > 64) {
            const errorDiv = document.getElementById('emailErrorCreate');
            errorDiv.style.display = 'block';
            errorDiv.textContent = 'La parte del email antes de @gmail.com no puede tener más de 64 caracteres.';
            document.getElementById('crearEmail').classList.add('is-invalid');
            alert('❌ Error: La parte del email antes de @gmail.com no puede tener más de 64 caracteres.');
            document.getElementById('crearEmail').focus();
            return;
        }
        // Validar longitud máxima total (254 caracteres)
        if (email.length > 254) {
            const errorDiv = document.getElementById('emailErrorCreate');
            errorDiv.style.display = 'block';
            errorDiv.textContent = 'El email no puede tener más de 254 caracteres en total.';
            document.getElementById('crearEmail').classList.add('is-invalid');
            alert('❌ Error: El email no puede tener más de 254 caracteres en total.');
            document.getElementById('crearEmail').focus();
            return;
        }
        // Limpiar errores si es válido
        document.getElementById('emailErrorCreate').style.display = 'none';
        document.getElementById('crearEmail').classList.remove('is-invalid');
    }
    
    // Validar formulario
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    try {
        // 1. Crear Persona
        const personaData = {
            primer_nombre: document.getElementById('crearPrimerNombre').value,
            segundo_nombre: document.getElementById('crearSegundoNombre').value || null,
            apellido_paterno: document.getElementById('crearApellidoPaterno').value,
            apellido_materno: document.getElementById('crearApellidoMaterno').value || null,
            genero: document.getElementById('crearGenero').value || null,
            fecha_nacimiento: document.getElementById('crearFechaNacimiento').value,
            nacionalidad: document.getElementById('crearNacionalidad').value || null
        };

        const personaRes = await fetchWithCSRF(`${API_BASE_URL}/personas/`, {
            method: 'POST',
            body: JSON.stringify(personaData)
        });

        if (!personaRes.ok) {
            let errorData;
            try {
                errorData = await personaRes.json();
            } catch (e) {
                errorData = { detail: 'Error desconocido al crear persona' };
            }
            
            // Mostrar errores en los campos del formulario
            const errores = mostrarErroresValidacion(errorData, 'create');
            mostrarAlertaErrores(errores, 'Error al crear persona');
            
            // No continuar si hay errores
            return;
        }

        const persona = await personaRes.json();

        // 2. Crear Usuario
        const usuarioData = {
            id_persona: persona.id_persona,
            username: document.getElementById('crearUsername').value,
            estado: document.getElementById('crearEstado').value,
            password: document.getElementById('crearPassword').value
        };

        const usuarioRes = await fetchWithCSRF(`${API_BASE_URL}/usuarios/`, {
            method: 'POST',
            body: JSON.stringify(usuarioData)
        });

        if (!usuarioRes.ok) {
            let errorData;
            try {
                errorData = await usuarioRes.json();
            } catch (e) {
                errorData = { detail: 'Error desconocido al crear usuario' };
            }
            
            // Mostrar errores en los campos del formulario
            const errores = mostrarErroresValidacion(errorData, 'create');
            mostrarAlertaErrores(errores, 'Error al crear usuario');
            
            // No continuar si hay errores
            return;
        }

        const usuario = await usuarioRes.json();

        // 3. Asignar Roles
        const rolesSeleccionados = Array.from(document.getElementById('crearRoles').selectedOptions);
        for (const option of rolesSeleccionados) {
            const rolData = {
                id_usuario: usuario.id_usuario,
                id_rol: parseInt(option.value)
            };

            await fetchWithCSRF(`${API_BASE_URL}/usuario-rol/`, {
                method: 'POST',
                body: JSON.stringify(rolData)
            });
        }

        // 4. Crear Colaborador si es necesario
        const esColaborador = document.getElementById('crearEsColaborador').checked;
        if (esColaborador) {
            const email = document.getElementById('crearEmail').value;
            if (email) {
                const colaboradorData = {
                    id_usuario: usuario.id_usuario,
                    gmail: email
                };

                const colaboradorRes = await fetchWithCSRF(`${API_BASE_URL}/colaboradores/`, {
                    method: 'POST',
                    body: JSON.stringify(colaboradorData)
                });
                
                if (!colaboradorRes.ok) {
                    let errorData;
                    try {
                        errorData = await colaboradorRes.json();
                    } catch (e) {
                        errorData = { detail: 'Error desconocido al crear colaborador' };
                    }
                    
                    // Mostrar errores en los campos del formulario
                    const errores = mostrarErroresValidacion(errorData, 'create');
                    mostrarAlertaErrores(errores, 'Error al crear colaborador');
                    
                    // No continuar si hay errores
                    return;
                }
            }
        }

        // Cerrar modal y recargar usuarios
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalCrearUsuario'));
        modal.hide();
        
        alert('✅ Usuario creado exitosamente');
        cargarUsuarios();

    } catch (error) {
        console.error('Error al guardar usuario:', error);
        // Si es un error de red u otro error no manejado
        if (!error.message.includes('Error al crear')) {
            alert('❌ Error inesperado: ' + error.message + '\n\nPor favor, verifica tu conexión e inténtalo nuevamente.');
        }
    }
}

/**
 * Editar usuario (cargar datos y mostrar modal)
 */
export async function editarUsuario(id) {
    try {
        // Cargar datos del usuario desde la API
        const res = await fetch(`${API_BASE_URL}/usuarios/${id}/`);
        if (!res.ok) {
            throw new Error('Error al cargar datos del usuario');
        }
        
        const usuario = await res.json();
        
        // Llenar formulario de edición con datos existentes
        document.getElementById('editarUsuarioId').value = usuario.id_usuario;
        document.getElementById('editarPersonaId').value = usuario.id_persona;
        
        // Datos de Persona
        const persona = usuario.id_persona_detalle;
        document.getElementById('editarPrimerNombre').value = persona.primer_nombre || '';
        document.getElementById('editarSegundoNombre').value = persona.segundo_nombre || '';
        document.getElementById('editarApellidoPaterno').value = persona.apellido_paterno || '';
        document.getElementById('editarApellidoMaterno').value = persona.apellido_materno || '';
        document.getElementById('editarFechaNacimiento').value = persona.fecha_nacimiento || '';
        document.getElementById('editarGenero').value = persona.genero || '';
        
        // Establecer fecha máxima (hoy) para fecha de nacimiento en edición
        const fechaNacimientoInput = document.getElementById('editarFechaNacimiento');
        if (fechaNacimientoInput) {
            const hoy = new Date();
            const fechaMax = new Date(hoy.getFullYear() - 18, hoy.getMonth(), hoy.getDate()); // 18 años atrás
            fechaNacimientoInput.max = fechaMax.toISOString().split('T')[0];
            fechaNacimientoInput.setAttribute('max', fechaMax.toISOString().split('T')[0]);
        }
        
        // Asegurar países cargados y setear nacionalidad
        if (catalogoPaises.length === 0) {
            await cargarPaises();
        }
        document.getElementById('editarNacionalidad').value = persona.nacionalidad || '';
        
        // Datos de Usuario
        document.getElementById('editarUsername').value = usuario.username;
        document.getElementById('editarEstado').value = usuario.estado;
        
        // Cargar roles (si no se han cargado)
        if (catalogoRoles.length === 0) {
            await cargarRoles();
        }
        
        // Seleccionar roles actuales
        const rolesSelect = document.getElementById('editarRoles');
        if (rolesSelect) {
            // Primero llenar las opciones
            populateSelect('editarRoles', catalogoRoles.map(r => ({ value: r.id_rol, text: r.nombre })));
            
            // Luego seleccionar los roles actuales
            if (usuario.roles && usuario.roles.length > 0) {
                // Buscar IDs de roles por nombre
                usuario.roles.forEach(rolNombre => {
                    const rol = catalogoRoles.find(r => r.nombre === rolNombre);
                    if (rol) {
                        const option = rolesSelect.querySelector(`option[value="${rol.id_rol}"]`);
                        if (option) option.selected = true;
                    }
                });
            }
        }
        
        // Datos de Colaborador
        if (usuario.colaborador) {
            document.getElementById('editarEmail').value = usuario.colaborador;
        } else {
            document.getElementById('editarEmail').value = '';
        }
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('modalEditarUsuario'));
        modal.show();
        
    } catch (error) {
        console.error('Error al cargar usuario para editar:', error);
        alert('❌ Error al cargar datos del usuario: ' + error.message);
    }
}

/**
 * Actualizar usuario existente
 */
export async function actualizarUsuario() {
    const form = document.getElementById('formEditarUsuario');
    
    // Validar fecha de nacimiento
    const fechaNacimiento = document.getElementById('editarFechaNacimiento').value;
    if (fechaNacimiento) {
        const fechaNac = new Date(fechaNacimiento);
        const hoy = new Date();
        if (fechaNac > hoy) {
            alert('❌ Error: La fecha de nacimiento no puede ser superior a la fecha actual.');
            document.getElementById('editarFechaNacimiento').focus();
            return;
        }
        // Validar edad mínima (18 años)
        const fechaMinima = new Date(hoy.getFullYear() - 18, hoy.getMonth(), hoy.getDate());
        if (fechaNac > fechaMinima) {
            alert('❌ Error: La fecha de nacimiento debe ser de al menos 18 años atrás.');
            document.getElementById('editarFechaNacimiento').focus();
            return;
        }
    }
    
    // Validar email Gmail si se proporciona
    const email = document.getElementById('editarEmail').value;
    if (email && email.trim() !== '') {
        if (!email.match(/^[a-zA-Z0-9._%+-]+@gmail\.com$/i)) {
            const errorDiv = document.getElementById('emailErrorEdit');
            errorDiv.style.display = 'block';
            document.getElementById('editarEmail').classList.add('is-invalid');
            alert('❌ Error: El email debe ser una cuenta de Gmail válida (ej: usuario@gmail.com)');
            document.getElementById('editarEmail').focus();
            return;
        } else {
            document.getElementById('emailErrorEdit').style.display = 'none';
            document.getElementById('editarEmail').classList.remove('is-invalid');
        }
    }
    
    // Validar formulario
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    try {
        const userId = document.getElementById('editarUsuarioId').value;
        const personaId = document.getElementById('editarPersonaId').value;
        
        // 1. Actualizar Persona
        const personaData = {
            primer_nombre: document.getElementById('editarPrimerNombre').value,
            segundo_nombre: document.getElementById('editarSegundoNombre').value || null,
            apellido_paterno: document.getElementById('editarApellidoPaterno').value,
            apellido_materno: document.getElementById('editarApellidoMaterno').value || null,
            genero: document.getElementById('editarGenero').value || null,
            fecha_nacimiento: document.getElementById('editarFechaNacimiento').value,
            nacionalidad: document.getElementById('editarNacionalidad').value || null
        };

        const personaRes = await fetchWithCSRF(`${API_BASE_URL}/personas/${personaId}/`, {
            method: 'PUT',
            body: JSON.stringify(personaData)
        });

        if (!personaRes.ok) {
            let errorData;
            try {
                errorData = await personaRes.json();
            } catch (e) {
                errorData = { detail: 'Error desconocido al actualizar persona' };
            }
            
            // Mostrar errores en los campos del formulario
            const errores = mostrarErroresValidacion(errorData, 'edit');
            mostrarAlertaErrores(errores, 'Error al actualizar persona');
            
            // No continuar si hay errores
            return;
        }

        // 2. Actualizar Usuario
        const usuarioData = {
            id_persona: parseInt(personaId),
            username: document.getElementById('editarUsername').value,
            estado: document.getElementById('editarEstado').value,
            password: null
        };

        const usuarioRes = await fetchWithCSRF(`${API_BASE_URL}/usuarios/${userId}/`, {
            method: 'PUT',
            body: JSON.stringify(usuarioData)
        });

        if (!usuarioRes.ok) {
            let errorData;
            try {
                errorData = await usuarioRes.json();
            } catch (e) {
                errorData = { detail: 'Error desconocido al actualizar usuario' };
            }
            
            // Mostrar errores en los campos del formulario
            const errores = mostrarErroresValidacion(errorData, 'edit');
            mostrarAlertaErrores(errores, 'Error al actualizar usuario');
            
            // No continuar si hay errores
            return;
        }

        // 3. Actualizar Roles (eliminar todos y agregar nuevos)
        const usuarioActual = await fetch(`${API_BASE_URL}/usuarios/${userId}/`).then(r => r.json());
        
        // Eliminar roles actuales usando roles_ids
        if (usuarioActual.roles_ids && usuarioActual.roles_ids.length > 0) {
            for (const usuarioRol of usuarioActual.roles_ids) {
                await fetchWithCSRF(`${API_BASE_URL}/usuario-rol/${usuarioRol.id}/`, {
                    method: 'DELETE'
                });
            }
        }
        
        // Agregar nuevos roles
        const rolesSeleccionados = Array.from(document.getElementById('editarRoles').selectedOptions);
        for (const option of rolesSeleccionados) {
            const rolData = {
                id_usuario: parseInt(userId),
                id_rol: parseInt(option.value)
            };
            
            await fetchWithCSRF(`${API_BASE_URL}/usuario-rol/`, {
                method: 'POST',
                body: JSON.stringify(rolData)
            });
        }

        // 4. Actualizar/Crear/Eliminar Colaborador
        const email = document.getElementById('editarEmail').value;
        
        // Verificar si el usuario ya tiene colaborador
        const colaboradorExistente = await fetch(`${API_BASE_URL}/colaboradores/?id_usuario=${userId}`).then(r => r.json());
        
        if (email && email.trim() !== '') {
            // Hay email: crear o actualizar
            const colaboradorData = {
                id_usuario: parseInt(userId),
                gmail: email.trim()
            };
            
            if (colaboradorExistente.results && colaboradorExistente.results.length > 0) {
                // Actualizar colaborador existente
                const colaboradorId = colaboradorExistente.results[0].id_colaborador;
                const colaboradorRes = await fetchWithCSRF(`${API_BASE_URL}/colaboradores/${colaboradorId}/`, {
                    method: 'PUT',
                    body: JSON.stringify(colaboradorData)
                });
                
                if (!colaboradorRes.ok) {
                    let errorData;
                    try {
                        errorData = await colaboradorRes.json();
                    } catch (e) {
                        errorData = { detail: 'Error desconocido al actualizar colaborador' };
                    }
                    
                    // Mostrar errores en los campos del formulario
                    const errores = mostrarErroresValidacion(errorData, 'edit');
                    mostrarAlertaErrores(errores, 'Error al actualizar colaborador');
                    
                    // No continuar si hay errores
                    return;
                }
            } else {
                // Crear nuevo colaborador
                const colaboradorRes = await fetchWithCSRF(`${API_BASE_URL}/colaboradores/`, {
                    method: 'POST',
                    body: JSON.stringify(colaboradorData)
                });
                
                if (!colaboradorRes.ok) {
                    let errorData;
                    try {
                        errorData = await colaboradorRes.json();
                    } catch (e) {
                        errorData = { detail: 'Error desconocido al crear colaborador' };
                    }
                    
                    // Mostrar errores en los campos del formulario
                    const errores = mostrarErroresValidacion(errorData, 'edit');
                    mostrarAlertaErrores(errores, 'Error al crear colaborador');
                    
                    // No continuar si hay errores
                    return;
                }
            }
        } else if (colaboradorExistente.results && colaboradorExistente.results.length > 0) {
            // Email vacío pero el usuario es colaborador: eliminar
            const colaboradorId = colaboradorExistente.results[0].id_colaborador;
            await fetchWithCSRF(`${API_BASE_URL}/colaboradores/${colaboradorId}/`, {
                method: 'DELETE'
            });
        }

        // Cerrar modal y recargar usuarios
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarUsuario'));
        modal.hide();
        
        alert('✅ Usuario actualizado exitosamente');
        cargarUsuarios();

    } catch (error) {
        console.error('Error al actualizar usuario:', error);
        // Si es un error de red u otro error no manejado
        if (!error.message.includes('Error al actualizar') && !error.message.includes('Error al crear')) {
            alert('❌ Error inesperado: ' + error.message + '\n\nPor favor, verifica tu conexión e inténtalo nuevamente.');
        }
    }
}

/**
 * Mapeo de campos del formulario a campos del backend
 */
const campoMap = {
    'primer_nombre': { create: 'crearPrimerNombre', edit: 'editarPrimerNombre', label: 'Primer Nombre' },
    'segundo_nombre': { create: 'crearSegundoNombre', edit: 'editarSegundoNombre', label: 'Segundo Nombre' },
    'apellido_paterno': { create: 'crearApellidoPaterno', edit: 'editarApellidoPaterno', label: 'Apellido Paterno' },
    'apellido_materno': { create: 'crearApellidoMaterno', edit: 'editarApellidoMaterno', label: 'Apellido Materno' },
    'fecha_nacimiento': { create: 'crearFechaNacimiento', edit: 'editarFechaNacimiento', label: 'Fecha de Nacimiento' },
    'genero': { create: 'crearGenero', edit: 'editarGenero', label: 'Género' },
    'nacionalidad': { create: 'crearNacionalidad', edit: 'editarNacionalidad', label: 'Nacionalidad' },
    'username': { create: 'crearUsername', edit: 'editarUsername', label: 'Username' },
    'estado': { create: 'crearEstado', edit: 'editarEstado', label: 'Estado' },
    'email': { create: 'crearEmail', edit: 'editarEmail', label: 'Email' },
    'gmail': { create: 'crearEmail', edit: 'editarEmail', label: 'Email Gmail' },
    'password': { create: 'crearPassword', edit: null, label: 'Contraseña' }
};

/**
 * Mostrar errores de validación en los campos del formulario
 * @param {Object} errorData - Datos de error del backend
 * @param {string} mode - 'create' o 'edit'
 * @returns {Array} Lista de mensajes de error formateados
 */
function mostrarErroresValidacion(errorData, mode = 'create') {
    const errores = [];
    const erroresPorCampo = {};
    
    // Limpiar errores previos
    document.querySelectorAll('.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
    document.querySelectorAll('.invalid-feedback').forEach(el => {
        if (el.id && (el.id.includes('Error') || el.id.includes('error'))) {
            el.style.display = 'none';
        }
    });
    
    // Procesar errores del backend
    if (errorData && typeof errorData === 'object') {
        // Si es un objeto con campos específicos (error de validación de Django)
        for (const [campo, mensajes] of Object.entries(errorData)) {
            if (Array.isArray(mensajes) && mensajes.length > 0) {
                erroresPorCampo[campo] = mensajes;
                
                // Buscar el campo correspondiente en el formulario
                const campoInfo = campoMap[campo];
                if (campoInfo) {
                    const campoId = campoInfo[mode];
                    if (campoId) {
                        const input = document.getElementById(campoId);
                        if (input) {
                            // Resaltar el campo con error
                            input.classList.add('is-invalid');
                            
                            // Crear o actualizar mensaje de error
                            let errorDiv = document.getElementById(`${campoId}Error`);
                            if (!errorDiv) {
                                errorDiv = document.createElement('div');
                                errorDiv.id = `${campoId}Error`;
                                errorDiv.className = 'invalid-feedback';
                                input.parentNode.appendChild(errorDiv);
                            }
                            
                            // Mostrar el primer mensaje de error
                            errorDiv.textContent = mensajes[0];
                            errorDiv.style.display = 'block';
                            
                            // Agregar al resumen de errores
                            errores.push(`• ${campoInfo.label}: ${mensajes[0]}`);
                            
                            // Hacer scroll al primer campo con error
                            if (errores.length === 1) {
                                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                input.focus();
                            }
                        }
                    }
                } else {
                    // Campo no mapeado, agregar al resumen general
                    errores.push(`• ${campo}: ${mensajes[0]}`);
                }
            }
        }
        
        // Si hay un error general (detail)
        if (errorData.detail && typeof errorData.detail === 'string') {
            errores.push(`• Error general: ${errorData.detail}`);
        }
        
        // Si hay un error no estructurado
        if (errores.length === 0 && errorData.detail) {
            errores.push(`• ${errorData.detail}`);
        }
    }
    
    return errores;
}

/**
 * Mostrar mensaje de error amigable en una alerta
 * @param {Array} errores - Lista de mensajes de error
 * @param {string} titulo - Título del error (opcional)
 */
function mostrarAlertaErrores(errores, titulo = 'Error de validación') {
    if (errores.length === 0) {
        alert('❌ Ha ocurrido un error. Por favor, verifica los datos ingresados.');
        return;
    }
    
    let mensaje = `❌ ${titulo}:\n\n`;
    
    if (errores.length === 1) {
        mensaje = `❌ ${errores[0]}`;
    } else {
        mensaje += errores.join('\n');
        mensaje += '\n\nPor favor, corrige los errores indicados y vuelve a intentar.';
    }
    
    alert(mensaje);
}

/**
 * Eliminar usuario
 */
export async function eliminarUsuario(id) {
    if (!confirm('¿Estás seguro de eliminar este usuario?')) {
        return;
    }

    try {
        // Cargar datos del usuario para mostrar información
        const res = await fetch(`${API_BASE_URL}/usuarios/${id}/`);
        if (!res.ok) {
            throw new Error('Error al cargar datos del usuario');
        }
        
        const usuario = await res.json();
        const nombre = usuario.id_persona_detalle 
            ? `${usuario.id_persona_detalle.primer_nombre} ${usuario.id_persona_detalle.apellido_paterno}`
            : usuario.username;

        // Confirmación adicional
        const confirmacion = confirm(
            `⚠️ ADVERTENCIA: Se eliminará el usuario "${nombre}" (${usuario.username})\n\n` +
            `Esto eliminará:\n` +
            `- Todos los roles asignados\n` +
            `- Los datos de colaborador (si existe)\n` +
            `- Las relaciones con corredoras\n` +
            `- El registro de usuario\n\n` +
            `Los datos de auditoría se conservarán (con ID nulo).\n\n` +
            `¿Deseas continuar?`
        );

        if (!confirmacion) {
            return;
        }

        // Eliminar usuario
        const deleteRes = await fetchWithCSRF(`${API_BASE_URL}/usuarios/${id}/`, {
            method: 'DELETE'
        });

        if (!deleteRes.ok) {
            const errorData = await deleteRes.json();
            if (errorData.detail) {
                throw new Error(`Error al eliminar usuario: ${errorData.detail}`);
            } else {
                throw new Error(`Error al eliminar usuario: ${JSON.stringify(errorData)}`);
            }
        }

        alert(`✅ Usuario "${nombre}" eliminado exitosamente`);
        cargarUsuarios();

    } catch (error) {
        console.error('Error al eliminar usuario:', error);
        
        // Verificar si el error es por RESTRICT
        if (error.message.includes('RESTRICT') || error.message.includes('Cannot delete')) {
            alert('❌ No se puede eliminar este usuario porque tiene registros asociados que impiden su eliminación.\n\nPor favor, contacta al administrador del sistema para más información.');
        } else {
            alert('❌ Error al eliminar usuario: ' + error.message);
        }
    }
}

/**
 * Configurar toggles de visibilidad de contraseñas y checkbox de colaborador
 */
export function setupPasswordToggles() {
    // Toggle checkbox de colaborador
    const crearEsColaborador = document.getElementById('crearEsColaborador');
    const colaboradorEmailContainer = document.getElementById('colaboradorEmailContainer');
    const crearEmail = document.getElementById('crearEmail');
    
    if (crearEsColaborador && colaboradorEmailContainer) {
        crearEsColaborador.addEventListener('change', function() {
            if (this.checked) {
                colaboradorEmailContainer.style.display = 'block';
                if (crearEmail) {
                    crearEmail.required = true;
                }
            } else {
                colaboradorEmailContainer.style.display = 'none';
                if (crearEmail) {
                    crearEmail.required = false;
                    crearEmail.value = '';
                    crearEmail.classList.remove('is-invalid');
                    document.getElementById('emailErrorCreate').style.display = 'none';
                }
            }
        });
    }
    // Toggle contraseña
    const togglePasswordCreate = document.getElementById('togglePasswordCreate');
    if (togglePasswordCreate) {
        togglePasswordCreate.addEventListener('click', function() {
            const passwordInput = document.getElementById('crearPassword');
            const icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
    
    // Toggle confirmar contraseña
    const togglePasswordConfirmCreate = document.getElementById('togglePasswordConfirmCreate');
    if (togglePasswordConfirmCreate) {
        togglePasswordConfirmCreate.addEventListener('click', function() {
            const passwordInput = document.getElementById('crearPasswordConfirm');
            const icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
}

/**
 * Validar coincidencia de contraseñas en tiempo real
 */
export function validarPasswordCoincidencia() {
    const password = document.getElementById('crearPassword').value;
    const passwordConfirm = document.getElementById('crearPasswordConfirm').value;
    const errorDiv = document.getElementById('passwordMatchError');
    const passwordConfirmInput = document.getElementById('crearPasswordConfirm');
    
    if (passwordConfirm && password !== passwordConfirm) {
        errorDiv.style.display = 'block';
        passwordConfirmInput.classList.add('is-invalid');
    } else if (passwordConfirm) {
        errorDiv.style.display = 'none';
        passwordConfirmInput.classList.remove('is-invalid');
    }
}

