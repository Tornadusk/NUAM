"""
Tests de integración para endpoints de Usuarios
"""
import pytest
from rest_framework import status
from usuarios.models import Persona, Usuario, Rol, UsuarioRol


@pytest.mark.django_db
class TestUsuarioAPI:
    """Tests para endpoints de Usuarios"""
    
    def test_list_usuarios_requires_auth(self, api_client):
        """GET /api/usuarios/ requiere autenticación"""
        response = api_client.get('/api/usuarios/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_usuarios_authenticated(self, authenticated_api_client, test_user):
        """GET /api/usuarios/ funciona con autenticación"""
        response = authenticated_api_client.get('/api/usuarios/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_retrieve_usuario(self, authenticated_api_client, test_user):
        """GET /api/usuarios/{id}/ devuelve un usuario específico"""
        response = authenticated_api_client.get(f'/api/usuarios/{test_user.id_usuario}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
    
    def test_create_usuario_authenticated(self, authenticated_api_client):
        """POST /api/usuarios/ crea un usuario"""
        # Primero crear persona
        persona_data = {
            'primer_nombre': 'Nuevo',
            'apellido_paterno': 'Usuario',
            'fecha_nacimiento': '1995-05-15'
        }
        persona_response = authenticated_api_client.post('/api/personas/', persona_data, format='json')
        assert persona_response.status_code == status.HTTP_201_CREATED
        persona_id = persona_response.data['id_persona']
        
        # Crear usuario
        usuario_data = {
            'id_persona': persona_id,
            'username': 'nuevousuario',
            'password': 'nuevopass123',
            'estado': 'activo'
        }
        response = authenticated_api_client.post('/api/usuarios/', usuario_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'nuevousuario'


@pytest.mark.django_db
class TestRolAPI:
    """Tests para endpoints de Roles"""
    
    def test_list_roles_authenticated(self, authenticated_api_client):
        """GET /api/roles/ devuelve lista de roles"""
        response = authenticated_api_client.get('/api/roles/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_rol(self, authenticated_api_client):
        """POST /api/roles/ crea un rol"""
        data = {
            'nombre': 'TestRol'
        }
        response = authenticated_api_client.post('/api/roles/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nombre'] == 'TestRol'


@pytest.mark.django_db
class TestPersonaAPI:
    """Tests para endpoints de Personas"""
    
    def test_list_personas_requires_auth(self, api_client):
        """GET /api/personas/ requiere autenticación"""
        response = api_client.get('/api/personas/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_persona(self, authenticated_api_client):
        """POST /api/personas/ crea una persona"""
        data = {
            'primer_nombre': 'Juan',
            'apellido_paterno': 'Pérez',
            'fecha_nacimiento': '1985-03-20'
        }
        response = authenticated_api_client.post('/api/personas/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['primer_nombre'] == 'Juan'

