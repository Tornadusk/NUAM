"""
Configuración compartida para pytest
"""
import pytest
from django.contrib.auth import get_user_model
from core.models import Pais, Moneda, Mercado, Fuente
from usuarios.models import Persona, Rol, UsuarioRol

User = get_user_model()


@pytest.fixture
def api_client():
    """Cliente API sin autenticación"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """Cliente API autenticado"""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def test_user(db):
    """Usuario de prueba"""
    persona = Persona.objects.create(
        primer_nombre='Test',
        apellido_paterno='User',
        fecha_nacimiento='1990-01-01'
    )
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        id_persona=persona,
        estado='activo'
    )
    return user


@pytest.fixture
def admin_user(db):
    """Usuario administrador de prueba"""
    persona = Persona.objects.create(
        primer_nombre='Admin',
        apellido_paterno='User',
        fecha_nacimiento='1990-01-01'
    )
    user = User.objects.create_user(
        username='admin',
        password='admin123',
        id_persona=persona,
        estado='activo',
        is_staff=True
    )
    rol, _ = Rol.objects.get_or_create(nombre='Administrador')
    UsuarioRol.objects.create(id_usuario=user, id_rol=rol)
    return user


@pytest.fixture
def test_pais(db):
    """País de prueba"""
    return Pais.objects.create(
        codigo='CHL',
        nombre='Chile'
    )


@pytest.fixture
def test_moneda(db):
    """Moneda de prueba"""
    return Moneda.objects.create(
        codigo='CLP',
        nombre='Peso Chileno',
        decimales=0,
        vigente=True
    )


@pytest.fixture
def test_mercado(db):
    """Mercado de prueba"""
    return Mercado.objects.create(
        codigo='BCS',
        nombre='Bolsa de Comercio de Santiago'
    )


@pytest.fixture
def test_fuente(db):
    """Fuente de prueba"""
    return Fuente.objects.create(
        codigo='SVS',
        nombre='Superintendencia de Valores y Seguros'
    )


