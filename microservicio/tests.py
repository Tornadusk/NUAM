"""
Tests para Microservicios NUAM
"""
from django.test import TestCase
from django.contrib.auth.models import User
from microservicio.models import TipoCambioFuente, TipoCambio


class TipoCambioFuenteModelTest(TestCase):
    """Tests para el modelo TipoCambioFuente"""
    
    def test_crear_fuente(self):
        """Test: Crear una fuente de tipo de cambio"""
        fuente = TipoCambioFuente.objects.create(
            codigo='EXCHANGERATE',
            nombre='ExchangeRate API',
            url_api='https://api.exchangerate-api.com/v4/latest',
            activa=True,
            orden_prioridad=1
        )
        self.assertEqual(str(fuente), 'EXCHANGERATE - ExchangeRate API')
        self.assertTrue(fuente.activa)
        self.assertEqual(fuente.orden_prioridad, 1)




