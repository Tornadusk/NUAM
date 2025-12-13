"""
Tests unitarios para modelos
"""
import pytest
from django.core.exceptions import ValidationError
from core.models import Pais, Moneda, MonedaPais
from usuarios.models import Persona, Usuario, Rol, UsuarioRol


@pytest.mark.django_db
class TestPaisModel:
    """Tests para modelo Pais"""
    
    def test_create_pais(self):
        """Crear un país básico"""
        pais = Pais.objects.create(
            codigo='CHL',
            nombre='Chile'
        )
        assert pais.codigo == 'CHL'
        assert pais.nombre == 'Chile'
        assert str(pais) == 'Chile'
    
    def test_pais_str_representation(self):
        """Verificar representación string de Pais"""
        pais = Pais.objects.create(codigo='PER', nombre='Perú')
        assert str(pais) == 'Perú'


@pytest.mark.django_db
class TestMonedaModel:
    """Tests para modelo Moneda"""
    
    def test_create_moneda(self):
        """Crear una moneda básica"""
        moneda = Moneda.objects.create(
            codigo='CLP',
            nombre='Peso Chileno',
            decimales=0,
            vigente=True
        )
        assert moneda.codigo == 'CLP'
        assert moneda.nombre == 'Peso Chileno'
        assert moneda.decimales == 0
        assert moneda.vigente is True
    
    def test_moneda_str_representation(self):
        """Verificar representación string de Moneda"""
        moneda = Moneda.objects.create(
            codigo='USD',
            nombre='Dólar',
            decimales=2,
            vigente=True
        )
        assert 'USD' in str(moneda) or 'Dólar' in str(moneda)


@pytest.mark.django_db
class TestMonedaPaisModel:
    """Tests para modelo MonedaPais (relación M:N)"""
    
    def test_create_moneda_pais(self):
        """Crear relación moneda-país"""
        pais = Pais.objects.create(codigo='CHL', nombre='Chile')
        moneda = Moneda.objects.create(
            codigo='CLP',
            nombre='Peso Chileno',
            decimales=0,
            vigente=True
        )
        relacion = MonedaPais.objects.create(
            id_pais=pais,
            id_moneda=moneda
        )
        assert relacion.id_pais == pais
        assert relacion.id_moneda == moneda


@pytest.mark.django_db
class TestPersonaModel:
    """Tests para modelo Persona"""
    
    def test_create_persona(self):
        """Crear una persona básica"""
        persona = Persona.objects.create(
            primer_nombre='Juan',
            apellido_paterno='Pérez',
            fecha_nacimiento='1990-01-15'
        )
        assert persona.primer_nombre == 'Juan'
        assert persona.apellido_paterno == 'Pérez'
    
    def test_persona_nombre_completo(self):
        """Verificar método nombre_completo"""
        persona = Persona.objects.create(
            primer_nombre='María',
            apellido_paterno='González',
            fecha_nacimiento='1985-05-20'
        )
        nombre_completo = persona.nombre_completo
        assert 'María' in nombre_completo
        assert 'González' in nombre_completo


@pytest.mark.django_db
class TestUsuarioModel:
    """Tests para modelo Usuario"""
    
    def test_create_usuario(self):
        """Crear un usuario básico"""
        persona = Persona.objects.create(
            primer_nombre='Test',
            apellido_paterno='User',
            fecha_nacimiento='1990-01-01'
        )
        usuario = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            id_persona=persona,
            estado='activo'
        )
        assert usuario.username == 'testuser'
        assert usuario.id_persona == persona
        assert usuario.estado == 'activo'
        assert usuario.check_password('testpass123')
    
    def test_usuario_str_representation(self):
        """Verificar representación string de Usuario"""
        persona = Persona.objects.create(
            primer_nombre='Admin',
            apellido_paterno='User',
            fecha_nacimiento='1990-01-01'
        )
        usuario = Usuario.objects.create_user(
            username='admin',
            password='admin123',
            id_persona=persona
        )
        assert str(usuario) == 'admin'


@pytest.mark.django_db
class TestRolModel:
    """Tests para modelo Rol"""
    
    def test_create_rol(self):
        """Crear un rol"""
        rol = Rol.objects.create(nombre='Administrador')
        assert rol.nombre == 'Administrador'
        assert str(rol) == 'Administrador'
    
    def test_create_usuario_rol_relationship(self):
        """Crear relación usuario-rol"""
        persona = Persona.objects.create(
            primer_nombre='Test',
            apellido_paterno='User',
            fecha_nacimiento='1990-01-01'
        )
        usuario = Usuario.objects.create_user(
            username='testuser',
            password='test123',
            id_persona=persona
        )
        rol = Rol.objects.create(nombre='Operador')
        usuario_rol = UsuarioRol.objects.create(
            id_usuario=usuario,
            id_rol=rol
        )
        assert usuario_rol.id_usuario == usuario
        assert usuario_rol.id_rol == rol


