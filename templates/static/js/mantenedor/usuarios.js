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
 * Cargar usuarios desde la API
 */
export async function cargarUsuarios() {
    try {
        const res = await fetch(`${API_BASE_URL}/usuarios/`);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        const usuarios = data.results || data;
        renderUsuarios(usuarios);
    } catch (error) {
        console.error('Error cargando usuarios:', error);
        const tbody = document.getElementById('tBodyUsuarios');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-circle me-2"></i> Error al cargar usuarios
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
        const roles = usuario.roles ? usuario.roles.join(', ') : 'Sin rol';
        const estadoBadge = usuario.estado === 'activo' 
            ? '<span class="badge bg-success">Activo</span>'
            : '<span class="badge bg-danger">Bloqueado</span>';
        
        const nombreCompleto = usuario.id_persona_detalle 
            ? `${usuario.id_persona_detalle.primer_nombre} ${usuario.id_persona_detalle.apellido_paterno}`
            : 'N/A';
        
        const email = usuario.colaborador ? usuario.colaborador : 'N/A';
        
        return `
            <tr>
                <td>${usuario.id_usuario}</td>
                <td><strong>${usuario.username}</strong></td>
                <td>${nombreCompleto}</td>
                <td>${email}</td>
                <td>${roles}</td>
                <td>${estadoBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editarUsuario(${usuario.id_usuario})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarUsuario(${usuario.id_usuario})">
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
    
    // Si no hay roles cargados aún, cargarlos
    if (catalogoRoles.length === 0) {
        await cargarRoles();
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
    
    // Validar contraseñas coincidan
    const password = document.getElementById('crearPassword').value;
    const passwordConfirm = document.getElementById('crearPasswordConfirm').value;
    
    if (password !== passwordConfirm) {
        const errorDiv = document.getElementById('passwordMatchError');
        errorDiv.style.display = 'block';
        document.getElementById('crearPasswordConfirm').classList.add('is-invalid');
        return;
    } else {
        document.getElementById('passwordMatchError').style.display = 'none';
        document.getElementById('crearPasswordConfirm').classList.remove('is-invalid');
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
            nacionalidad: null
        };

        const personaRes = await fetchWithCSRF(`${API_BASE_URL}/personas/`, {
            method: 'POST',
            body: JSON.stringify(personaData)
        });

        if (!personaRes.ok) {
            const errorData = await personaRes.json();
            if (errorData.detail) {
                throw new Error(`Error al crear persona: ${errorData.detail}`);
            } else {
                throw new Error(`Error al crear persona: ${JSON.stringify(errorData)}`);
            }
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
            const errorData = await usuarioRes.json();
            if (errorData.detail) {
                throw new Error(`Error al crear usuario: ${errorData.detail}`);
            } else {
                throw new Error(`Error al crear usuario: ${JSON.stringify(errorData)}`);
            }
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
                    const errorData = await colaboradorRes.json();
                    if (errorData.detail) {
                        throw new Error(`Error al crear colaborador: ${errorData.detail}`);
                    } else {
                        throw new Error(`Error al crear colaborador: ${JSON.stringify(errorData)}`);
                    }
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
        alert('❌ Error al crear usuario: ' + error.message);
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
            nacionalidad: null
        };

        const personaRes = await fetchWithCSRF(`${API_BASE_URL}/personas/${personaId}/`, {
            method: 'PUT',
            body: JSON.stringify(personaData)
        });

        if (!personaRes.ok) {
            const errorData = await personaRes.json();
            if (errorData.detail) {
                throw new Error(`Error al actualizar persona: ${errorData.detail}`);
            } else {
                throw new Error(`Error al actualizar persona: ${JSON.stringify(errorData)}`);
            }
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
            const errorData = await usuarioRes.json();
            if (errorData.detail) {
                throw new Error(`Error al actualizar usuario: ${errorData.detail}`);
            } else {
                throw new Error(`Error al actualizar usuario: ${JSON.stringify(errorData)}`);
            }
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
                    const errorData = await colaboradorRes.json();
                    if (errorData.detail) {
                        throw new Error(`Error al actualizar colaborador: ${errorData.detail}`);
                    } else {
                        throw new Error(`Error al actualizar colaborador: ${JSON.stringify(errorData)}`);
                    }
                }
            } else {
                // Crear nuevo colaborador
                const colaboradorRes = await fetchWithCSRF(`${API_BASE_URL}/colaboradores/`, {
                    method: 'POST',
                    body: JSON.stringify(colaboradorData)
                });
                
                if (!colaboradorRes.ok) {
                    const errorData = await colaboradorRes.json();
                    if (errorData.detail) {
                        throw new Error(`Error al crear colaborador: ${errorData.detail}`);
                    } else {
                        throw new Error(`Error al crear colaborador: ${JSON.stringify(errorData)}`);
                    }
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
        alert('❌ Error al actualizar usuario: ' + error.message);
    }
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
 * Configurar toggles de visibilidad de contraseñas
 */
export function setupPasswordToggles() {
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

