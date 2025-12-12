# 🧪 Tests - NUAM

Este directorio contiene tests unitarios y de integración para el proyecto NUAM.

## 📁 Estructura

```
tests/
├── __init__.py
├── conftest.py              # Configuración compartida de pytest (fixtures)
├── test_api_core.py         # Tests para endpoints de Core (catálogos)
├── test_api_usuarios.py     # Tests para endpoints de Usuarios
├── test_models.py           # Tests unitarios para modelos
└── README.md                # Este archivo
```

## 🚀 Ejecutar Tests

### Ejecutar todos los tests

```bash
# Usando pytest (recomendado)
pytest

# Usando Django test runner
python manage.py test
```

### Ejecutar tests específicos

```bash
# Solo tests de API
pytest tests/test_api_*.py

# Solo tests de modelos
pytest tests/test_models.py

# Solo tests de Core
pytest tests/test_api_core.py

# Un test específico
pytest tests/test_api_core.py::TestPaisAPI::test_list_paises_unauthenticated
```

### Ejecutar con cobertura

```bash
# Con cobertura de código
pytest --cov=. --cov-report=html

# Ver reporte en navegador
# Abre htmlcov/index.html
```

### Opciones útiles

```bash
# Verbose (mostrar más información)
pytest -v

# Mostrar prints (útil para debugging)
pytest -s

# Detener en primer error
pytest -x

# Mostrar código local en errores
pytest -l

# Combinación útil para desarrollo
pytest -v -s -l
```

## 📊 Cobertura de Código

**Objetivo:** 70-80% de cobertura mínimo

**Verificar cobertura:**
```bash
pytest --cov=. --cov-report=term-missing
```

Esto mostrará:
- Porcentaje de cobertura por módulo
- Líneas que no están cubiertas

## 🧩 Fixtures Disponibles

Los fixtures están definidos en `conftest.py`:

- `api_client` - Cliente API sin autenticación
- `authenticated_api_client` - Cliente API autenticado
- `test_user` - Usuario de prueba
- `admin_user` - Usuario administrador de prueba
- `test_pais` - País de prueba (Chile)
- `test_moneda` - Moneda de prueba (CLP)
- `test_mercado` - Mercado de prueba (BCS)
- `test_fuente` - Fuente de prueba (SVS)

**Uso:**
```python
def test_algo(authenticated_api_client, test_user):
    response = authenticated_api_client.get('/api/usuarios/')
    assert response.status_code == 200
```

## 📝 Escribir Nuevos Tests

### Estructura de un test

```python
import pytest
from rest_framework import status

@pytest.mark.django_db
class TestMiEndpoint:
    """Tests para mi endpoint"""
    
    def test_list_unauthorized(self, api_client):
        """GET sin autenticación debe retornar 401"""
        response = api_client.get('/api/endpoint/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_authenticated(self, authenticated_api_client):
        """GET con autenticación debe retornar 200"""
        response = authenticated_api_client.get('/api/endpoint/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
```

### Convenciones

1. **Nombres descriptivos:** `test_<accion>_<condicion>`
2. **Una aserción principal por test** (si es posible)
3. **Usar fixtures** para datos de prueba
4. **Marcar con `@pytest.mark.django_db`** si accede a la BD
5. **Documentar con docstrings** qué prueba cada test

## 🔧 Configuración

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = proyecto_nuam.settings
python_files = test_*.py *_test.py tests.py
python_classes = Test*
python_functions = test_*
```

### Variables de entorno para tests

Los tests usan la configuración de `settings.py`. Si necesitas una configuración específica para tests, crea `pytest.ini` o `conftest.py` con:

```python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'proyecto_nuam.settings'
```

## 📈 Integración Continua (CI)

Para integrar tests en CI/CD:

```yaml
# Ejemplo GitHub Actions
- name: Run tests
  run: |
    pytest --cov=. --cov-report=xml
    coverage report --fail-under=70
```

## ✅ Estado Actual

**Tests Implementados:**
- ✅ Tests de modelos básicos (Core, Usuarios)
- ✅ Tests de API (Core, Usuarios)
- ✅ Fixtures compartidos (conftest.py)
- ✅ Configuración pytest

**Pendientes:**
- Tests para Calificaciones
- Tests para Corredoras
- Tests para Instrumentos
- Tests para Cargas
- Tests para Auditoría
- Tests para Pulsar
- Tests para Microservicios

## 📚 Recursos

- **Documentación pytest:** https://docs.pytest.org/
- **pytest-django:** https://pytest-django.readthedocs.io/
- **factory-boy:** https://factoryboy.readthedocs.io/
- **coverage.py:** https://coverage.readthedocs.io/

