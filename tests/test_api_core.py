"""
Tests de integración para endpoints de Core (Catálogos Base)
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestPaisAPI:
    """Tests para endpoints de Países"""
    
    def test_list_paises_unauthenticated(self, api_client):
        """GET /api/paises/ debe funcionar sin autenticación"""
        response = api_client.get('/api/paises/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_create_pais_requires_auth(self, api_client, test_pais):
        """POST /api/paises/ requiere autenticación"""
        data = {
            'codigo': 'PER',
            'nombre': 'Perú'
        }
        response = api_client.post('/api/paises/', data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_pais_authenticated(self, authenticated_api_client, test_pais):
        """POST /api/paises/ funciona con autenticación"""
        data = {
            'codigo': 'PER',
            'nombre': 'Perú'
        }
        response = authenticated_api_client.post('/api/paises/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == 'PER'
        assert response.data['nombre'] == 'Perú'
    
    def test_retrieve_pais(self, api_client, test_pais):
        """GET /api/paises/{id}/ devuelve un país específico"""
        response = api_client.get(f'/api/paises/{test_pais.id_pais}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'CHL'
        assert response.data['nombre'] == 'Chile'


@pytest.mark.django_db
class TestMonedaAPI:
    """Tests para endpoints de Monedas"""
    
    def test_list_monedas(self, api_client):
        """GET /api/monedas/ devuelve lista de monedas"""
        response = api_client.get('/api/monedas/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_create_moneda_authenticated(self, authenticated_api_client):
        """POST /api/monedas/ crea una moneda con autenticación"""
        data = {
            'codigo': 'USD',
            'nombre': 'Dólar Estadounidense',
            'decimales': 2,
            'vigente': True
        }
        response = authenticated_api_client.post('/api/monedas/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['codigo'] == 'USD'


@pytest.mark.django_db
class TestMercadoAPI:
    """Tests para endpoints de Mercados"""
    
    def test_list_mercados(self, api_client):
        """GET /api/mercados/ devuelve lista de mercados"""
        response = api_client.get('/api/mercados/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_retrieve_mercado(self, api_client, test_mercado):
        """GET /api/mercados/{id}/ devuelve un mercado específico"""
        response = api_client.get(f'/api/mercados/{test_mercado.id_mercado}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'BCS'


@pytest.mark.django_db
class TestFuenteAPI:
    """Tests para endpoints de Fuentes"""
    
    def test_list_fuentes(self, api_client):
        """GET /api/fuentes/ devuelve lista de fuentes"""
        response = api_client.get('/api/fuentes/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_retrieve_fuente(self, api_client, test_fuente):
        """GET /api/fuentes/{id}/ devuelve una fuente específica"""
        response = api_client.get(f'/api/fuentes/{test_fuente.id_fuente}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['codigo'] == 'SVS'


