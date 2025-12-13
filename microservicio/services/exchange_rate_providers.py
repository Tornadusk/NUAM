"""
Proveedores de APIs de tipos de cambio
Implementa diferentes proveedores con interfaz común para facilitar el fallback
"""
import requests
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.utils import timezone

logger = logging.getLogger(__name__)


class ExchangeRateProvider:
    """Clase base para proveedores de tipos de cambio"""
    
    def __init__(self, nombre: str, codigo: str, url_api: str = None, api_key: str = None):
        self.nombre = nombre
        self.codigo = codigo
        self.url_api = url_api
        self.api_key = api_key
        self.timeout = 10  # segundos
    
    def obtener_tipos_cambio(self, moneda_base: str = 'USD', monedas_destino: List[str] = None) -> Dict:
        """
        Obtiene tipos de cambio desde la API
        
        Args:
            moneda_base: Moneda base (default: USD)
            monedas_destino: Lista de monedas destino (ej: ['CLP', 'PEN', 'COP'])
        
        Returns:
            Dict con estructura:
            {
                'exito': bool,
                'fecha': date,
                'tipos_cambio': [
                    {
                        'moneda_origen': 'USD',
                        'moneda_destino': 'CLP',
                        'tasa': Decimal,
                        'fecha': date
                    },
                    ...
                ],
                'error': str (si hay error)
            }
        """
        raise NotImplementedError("Subclases deben implementar este método")
    
    def _hacer_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[requests.Response]:
        """Método auxiliar para hacer requests HTTP"""
        try:
            if headers is None:
                headers = {}
            
            if params is None:
                params = {}
            
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.error(f"{self.nombre}: Timeout al consultar API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.nombre}: Error al consultar API: {e}")
            return None
        except Exception as e:
            logger.error(f"{self.nombre}: Error inesperado: {e}")
            return None


class ExchangeRateAPIProvider(ExchangeRateProvider):
    """
    Proveedor usando ExchangeRate API (https://www.exchangerate-api.com/)
    Plan gratuito: 1,500 requests/mes
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            nombre="ExchangeRate API",
            codigo="EXCHANGERATE_API",
            url_api="https://v6.exchangerate-api.com/v6",
            api_key=api_key
        )
    
    def obtener_tipos_cambio(self, moneda_base: str = 'USD', monedas_destino: List[str] = None) -> Dict:
        """
        Obtiene tipos de cambio desde ExchangeRate API
        """
        if not self.api_key:
            return {
                'exito': False,
                'error': 'API key no configurada'
            }
        
        if monedas_destino is None:
            monedas_destino = ['CLP', 'PEN', 'COP']
        
        url = f"{self.url_api}/{self.api_key}/latest/{moneda_base}"
        
        response = self._hacer_request(url)
        if not response:
            return {
                'exito': False,
                'error': 'Error al conectar con la API'
            }
        
        try:
            data = response.json()
            
            if data.get('result') != 'success':
                return {
                    'exito': False,
                    'error': data.get('error-type', 'Error desconocido')
                }
            
            fecha_str = data.get('time_last_update_utc', '')
            # Parsear fecha ISO 8601
            fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00')).date() if fecha_str else date.today()
            
            tipos_cambio = []
            rates = data.get('conversion_rates', {})
            
            for moneda_destino in monedas_destino:
                if moneda_destino in rates:
                    tipos_cambio.append({
                        'moneda_origen': moneda_base,
                        'moneda_destino': moneda_destino,
                        'tasa': Decimal(str(rates[moneda_destino])),
                        'fecha': fecha
                    })
            
            return {
                'exito': True,
                'fecha': fecha,
                'tipos_cambio': tipos_cambio
            }
        except Exception as e:
            logger.error(f"Error al procesar respuesta de ExchangeRate API: {e}")
            return {
                'exito': False,
                'error': str(e)
            }


class FixerIOProvider(ExchangeRateProvider):
    """
    Proveedor usando Fixer.io (https://fixer.io/)
    Plan gratuito: 100 requests/mes
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            nombre="Fixer.io",
            codigo="FIXER_IO",
            url_api="http://data.fixer.io/api",
            api_key=api_key
        )
    
    def obtener_tipos_cambio(self, moneda_base: str = 'USD', monedas_destino: List[str] = None) -> Dict:
        """
        Obtiene tipos de cambio desde Fixer.io
        """
        if not self.api_key:
            return {
                'exito': False,
                'error': 'API key no configurada'
            }
        
        if monedas_destino is None:
            monedas_destino = ['CLP', 'PEN', 'COP']
        
        # Fixer.io usa EUR como base en plan gratuito, necesitamos convertir
        url = f"{self.url_api}/latest"
        params = {
            'access_key': self.api_key,
            'base': 'EUR',  # Plan gratuito solo permite EUR como base
            'symbols': ','.join([moneda_base] + monedas_destino)
        }
        
        response = self._hacer_request(url, params=params)
        if not response:
            return {
                'exito': False,
                'error': 'Error al conectar con la API'
            }
        
        try:
            data = response.json()
            
            if not data.get('success', False):
                return {
                    'exito': False,
                    'error': data.get('error', {}).get('info', 'Error desconocido')
                }
            
            fecha_str = data.get('date', '')
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
            
            rates = data.get('rates', {})
            
            # Convertir desde EUR a USD si es necesario
            if moneda_base == 'USD':
                eur_to_usd = Decimal(str(rates.get('USD', 1)))
            else:
                eur_to_usd = Decimal('1')
            
            tipos_cambio = []
            for moneda_destino in monedas_destino:
                if moneda_destino in rates:
                    # Convertir desde EUR a la moneda destino, luego a USD si es necesario
                    tasa_desde_eur = Decimal(str(rates[moneda_destino]))
                    tasa_final = tasa_desde_eur / eur_to_usd if moneda_base == 'USD' else tasa_desde_eur
                    
                    tipos_cambio.append({
                        'moneda_origen': moneda_base,
                        'moneda_destino': moneda_destino,
                        'tasa': tasa_final,
                        'fecha': fecha
                    })
            
            return {
                'exito': True,
                'fecha': fecha,
                'tipos_cambio': tipos_cambio
            }
        except Exception as e:
            logger.error(f"Error al procesar respuesta de Fixer.io: {e}")
            return {
                'exito': False,
                'error': str(e)
            }


class BancoCentralChileProvider(ExchangeRateProvider):
    """
    Proveedor usando API del Banco Central de Chile
    Solo proporciona USD/CLP
    """
    
    def __init__(self):
        super().__init__(
            nombre="Banco Central de Chile",
            codigo="BANCO_CENTRAL_CHILE",
            url_api="https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
        )
    
    def obtener_tipos_cambio(self, moneda_base: str = 'USD', monedas_destino: List[str] = None) -> Dict:
        """
        Obtiene tipo de cambio USD/CLP desde Banco Central de Chile
        """
        if moneda_base != 'USD':
            return {
                'exito': False,
                'error': 'Banco Central de Chile solo soporta USD como base'
            }
        
        if monedas_destino is None:
            monedas_destino = ['CLP']
        
        if 'CLP' not in monedas_destino:
            return {
                'exito': False,
                'error': 'Banco Central de Chile solo proporciona CLP'
            }
        
        # API del Banco Central de Chile
        # Serie F073.TCO.PRE.Z.D: Tipo de cambio peso chileno/dólar observado
        url = f"{self.url_api}"
        params = {
            'user': '176555555',
            'pass': '123456',
            'firstdate': date.today().strftime('%Y-%m-%d'),
            'lastdate': date.today().strftime('%Y-%m-%d'),
            'timeseries': 'F073.TCO.PRE.Z.D'
        }
        
        response = self._hacer_request(url, params=params)
        if not response:
            return {
                'exito': False,
                'error': 'Error al conectar con la API'
            }
        
        try:
            data = response.json()
            
            if 'Series' not in data or len(data['Series']) == 0:
                return {
                    'exito': False,
                    'error': 'No se encontraron datos'
                }
            
            serie = data['Series'][0]
            obs = serie.get('Obs', [])
            
            if not obs:
                return {
                    'exito': False,
                    'error': 'No hay observaciones disponibles'
                }
            
            # Obtener la última observación
            ultima_obs = obs[-1]
            tasa_str = ultima_obs.get('value', '0')
            fecha_str = ultima_obs.get('indexDateString', date.today().strftime('%Y-%m-%d'))
            
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            tasa = Decimal(str(tasa_str))
            
            tipos_cambio = [{
                'moneda_origen': 'USD',
                'moneda_destino': 'CLP',
                'tasa': tasa,
                'fecha': fecha
            }]
            
            return {
                'exito': True,
                'fecha': fecha,
                'tipos_cambio': tipos_cambio
            }
        except Exception as e:
            logger.error(f"Error al procesar respuesta del Banco Central de Chile: {e}")
            return {
                'exito': False,
                'error': str(e)
            }


def crear_proveedor_desde_fuente(fuente) -> Optional[ExchangeRateProvider]:
    """
    Crea un proveedor basado en una instancia de TipoCambioFuente
    
    Args:
        fuente: Instancia de TipoCambioFuente
    
    Returns:
        Instancia de ExchangeRateProvider o None
    """
    codigo = fuente.codigo.upper()
    
    if codigo == 'EXCHANGERATE_API':
        return ExchangeRateAPIProvider(api_key=fuente.api_key)
    elif codigo == 'FIXER_IO':
        return FixerIOProvider(api_key=fuente.api_key)
    elif codigo == 'BANCO_CENTRAL_CHILE':
        return BancoCentralChileProvider()
    else:
        logger.warning(f"Código de fuente desconocido: {codigo}")
        return None


