"""
Proveedores de tipos de cambio para el microservicio independiente.

Este módulo está inspirado en `microservicio/services/exchange_rate_providers.py`,
pero se mantiene completamente desacoplado de Django. Solo se encarga de:

- Consultar las APIs externas (ExchangeRate API, Fixer.io, Banco Central de Chile).
- Devolver los datos en memoria con una estructura uniforme.

La persistencia en base de datos queda a cargo del proyecto NUAM.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional

import requests


class ExchangeRateProvider:
    """Clase base para proveedores de tipos de cambio."""

    def __init__(self, nombre: str, codigo: str, url_api: str | None = None, api_key: str | None = None) -> None:
        self.nombre = nombre
        self.codigo = codigo
        self.url_api = url_api
        self.api_key = api_key
        self.timeout = 10  # segundos

    def obtener_tipos_cambio(self, moneda_base: str = "USD", monedas_destino: Optional[List[str]] = None) -> Dict:
        raise NotImplementedError

    def _hacer_request(self, url: str, params: Dict | None = None, headers: Dict | None = None) -> Optional[requests.Response]:
        """Método auxiliar para hacer requests HTTP con manejo básico de errores."""
        try:
            response = requests.get(url, params=params or {}, headers=headers or {}, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException:
            return None


class ExchangeRateAPIProvider(ExchangeRateProvider):
    """Proveedor usando ExchangeRate API."""

    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(
            nombre="ExchangeRate API",
            codigo="EXCHANGERATE_API",
            url_api="https://v6.exchangerate-api.com/v6",
            api_key=api_key,
        )

    def obtener_tipos_cambio(self, moneda_base: str = "USD", monedas_destino: Optional[List[str]] = None) -> Dict:
        if not self.api_key:
            return {"exito": False, "error": "API key no configurada"}

        if monedas_destino is None:
            monedas_destino = ["CLP", "PEN", "COP"]

        url = f"{self.url_api}/{self.api_key}/latest/{moneda_base}"
        response = self._hacer_request(url)
        if not response:
            return {"exito": False, "error": "Error al conectar con la API"}

        try:
            data = response.json()
            if data.get("result") != "success":
                return {"exito": False, "error": data.get("error-type", "Error desconocido")}

            # Usar fecha de hoy como default (la API puede devolver formatos de fecha complejos)
            fecha = date.today()
            fecha_str = data.get("time_last_update_utc", "")
            if fecha_str:
                try:
                    # Intentar parsear formato RFC 2822 (ej: "Sun, 21 Dec 2025 00:00:01 +0000")
                    if "," in fecha_str:
                        date_part = fecha_str.split(",", 1)[1].strip()
                        fecha = datetime.strptime(date_part, "%d %b %Y %H:%M:%S %z").date()
                    # Intentar formato ISO con Z
                    elif "Z" in fecha_str:
                        fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00")).date()
                    # Intentar formato ISO estándar
                    elif "+" in fecha_str or (len(fecha_str) > 10 and fecha_str[10] in ["T", " "]):
                        fecha = datetime.fromisoformat(fecha_str).date()
                except (ValueError, AttributeError, TypeError):
                    # Si falla cualquier parsing, usar fecha de hoy (no es crítico)
                    fecha = date.today()

            tipos_cambio: List[Dict] = []
            rates = data.get("conversion_rates", {})
            for moneda_destino in monedas_destino:
                if moneda_destino in rates:
                    tipos_cambio.append(
                        {
                            "moneda_origen": moneda_base,
                            "moneda_destino": moneda_destino,
                            "tasa": Decimal(str(rates[moneda_destino])),
                            "fecha": fecha,
                        }
                    )

            return {"exito": True, "fecha": fecha, "tipos_cambio": tipos_cambio}
        except Exception as exc:  # pragma: no cover - fallo inesperado
            return {"exito": False, "error": str(exc)}


class FixerIOProvider(ExchangeRateProvider):
    """Proveedor usando Fixer.io."""

    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(
            nombre="Fixer.io",
            codigo="FIXER_IO",
            url_api="http://data.fixer.io/api",
            api_key=api_key,
        )

    def obtener_tipos_cambio(self, moneda_base: str = "USD", monedas_destino: Optional[List[str]] = None) -> Dict:
        if not self.api_key:
            return {"exito": False, "error": "API key no configurada"}

        if monedas_destino is None:
            monedas_destino = ["CLP", "PEN", "COP"]

        url = f"{self.url_api}/latest"
        params = {
            "access_key": self.api_key,
            "base": "EUR",
            "symbols": ",".join([moneda_base] + monedas_destino),
        }

        response = self._hacer_request(url, params=params)
        if not response:
            return {"exito": False, "error": "Error al conectar con la API"}

        try:
            data = response.json()
            if not data.get("success", False):
                return {"exito": False, "error": data.get("error", {}).get("info", "Error desconocido")}

            fecha_str = data.get("date", "")
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else date.today()

            rates = data.get("rates", {})
            eur_to_usd = Decimal(str(rates.get("USD", 1))) if moneda_base == "USD" else Decimal("1")

            tipos_cambio: List[Dict] = []
            for moneda_destino in monedas_destino:
                if moneda_destino in rates:
                    tasa_desde_eur = Decimal(str(rates[moneda_destino]))
                    tasa_final = tasa_desde_eur / eur_to_usd if moneda_base == "USD" else tasa_desde_eur
                    tipos_cambio.append(
                        {
                            "moneda_origen": moneda_base,
                            "moneda_destino": moneda_destino,
                            "tasa": tasa_final,
                            "fecha": fecha,
                        }
                    )

            return {"exito": True, "fecha": fecha, "tipos_cambio": tipos_cambio}
        except Exception as exc:  # pragma: no cover
            return {"exito": False, "error": str(exc)}


class BancoCentralChileProvider(ExchangeRateProvider):
    """Proveedor usando la API del Banco Central de Chile (USD/CLP)."""

    def __init__(self) -> None:
        super().__init__(
            nombre="Banco Central de Chile",
            codigo="BANCO_CENTRAL_CHILE",
            url_api="https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx",
        )

    def obtener_tipos_cambio(self, moneda_base: str = "USD", monedas_destino: Optional[List[str]] = None) -> Dict:
        if moneda_base != "USD":
            return {"exito": False, "error": "Banco Central de Chile solo soporta USD como base"}

        if monedas_destino is None:
            monedas_destino = ["CLP"]

        if "CLP" not in monedas_destino:
            return {"exito": False, "error": "Banco Central de Chile solo proporciona CLP"}

        url = self.url_api
        params = {
            "user": "176555555",
            "pass": "123456",
            "firstdate": date.today().strftime("%Y-%m-%d"),
            "lastdate": date.today().strftime("%Y-%m-%d"),
            "timeseries": "F073.TCO.PRE.Z.D",
        }

        response = self._hacer_request(url, params=params)
        if not response:
            return {"exito": False, "error": "Error al conectar con la API del Banco Central de Chile"}

        try:
            data = response.json()
        except ValueError:
            return {
                "exito": False,
                "error": f"La API no devolvió JSON válido. Código HTTP: {response.status_code}",
            }

        if "Series" not in data:
            mensaje_error = data.get("message", data.get("error", "No se encontraron datos"))
            return {"exito": False, "error": f"No se encontraron datos: {mensaje_error}"}
        
        series_list = data.get("Series", [])
        if not series_list or len(series_list) == 0:
            mensaje_error = data.get("message", data.get("error", "No se encontraron series de datos"))
            return {"exito": False, "error": f"No se encontraron datos: {mensaje_error}"}

        try:
            serie = series_list[0]
            if not serie:
                return {"exito": False, "error": "La serie de datos está vacía"}
        except (IndexError, KeyError, TypeError) as e:
            return {"exito": False, "error": f"Error al procesar los datos de la API: {str(e)}"}
        
        obs = serie.get("Obs", [])
        if not obs:
            return {"exito": False, "error": "No hay observaciones disponibles para la fecha solicitada"}

        ultima_obs = obs[-1]
        tasa_str = ultima_obs.get("value", "0")
        fecha_str = ultima_obs.get("indexDateString", date.today().strftime("%Y-%m-%d"))

        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        tasa = Decimal(str(tasa_str))

        tipos_cambio = [
            {
                "moneda_origen": "USD",
                "moneda_destino": "CLP",
                "tasa": tasa,
                "fecha": fecha,
            }
        ]

        return {"exito": True, "fecha": fecha, "tipos_cambio": tipos_cambio}


def crear_proveedores(
    api_key_exchangerate: str | None = None,
    api_key_fixer: str | None = None,
    incluir: Optional[List[str]] = None,
) -> List[ExchangeRateProvider]:
    """
    Crea una lista de proveedores activos según las API keys disponibles.

    Args:
        api_key_exchangerate: API key para ExchangeRate API (opcional).
        api_key_fixer: API key para Fixer.io (opcional).
        incluir: lista opcional de códigos de proveedores a incluir.
    """
    incluir_codigos = {c.upper() for c in incluir} if incluir else None

    proveedores: List[ExchangeRateProvider] = []

    if api_key_exchangerate and (incluir_codigos is None or "EXCHANGERATE_API" in incluir_codigos):
        proveedores.append(ExchangeRateAPIProvider(api_key=api_key_exchangerate))

    if api_key_fixer and (incluir_codigos is None or "FIXER_IO" in incluir_codigos):
        proveedores.append(FixerIOProvider(api_key=api_key_fixer))

    if incluir_codigos is None or "BANCO_CENTRAL_CHILE" in incluir_codigos:
        proveedores.append(BancoCentralChileProvider())

    return proveedores


