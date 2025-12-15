"""
Servicios auxiliares del microservicio Django.

Este paquete puede contener:
 - Clientes HTTP para microservicios externos (ej. exchange-rate-service)
 - Adaptadores para integrar lógica externa con los modelos Django
"""

from . import exchange_rate_client  # noqa: F401

