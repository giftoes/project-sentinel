# project_sentinel/connectors.py

"""
Módulo de Conectores Externos para Project Sentinel.

Este script contiene todas las funciones necesarias para conectarse a APIs
de terceros y obtener datos de mercado, como precios de criptomonedas,
información de activos financieros tradicionales y noticias de mercado.
"""

import krakenex
import requests
from ib_insync import IB, Stock, util

# --- Funciones de Conexión y Obtención de Datos ---

def get_btc_price() -> float:
    """
    Obtiene el último precio de cierre de Bitcoin (XBT/USD) desde la API pública de Kraken.

    Utiliza la librería krakenex para realizar una llamada al endpoint público 'Ticker'.
    No requiere clave de API.

    Returns:
        float: El precio de cierre más reciente de XBT/USD.
               Retorna 0.0 si ocurre un error o no se puede obtener el precio.
    
    Raises:
        Exception: Captura y reporta errores de conexión o de formato de respuesta de la API.
    """
    try:
        # 1. Inicializar la API de Kraken. No se necesitan claves para endpoints públicos.
        k = krakenex.API()

        # 2. Realizar la consulta al endpoint 'Ticker' para el par XBT/USD.
        # Kraken usa 'XBT' como designación oficial para Bitcoin en su API.
        # El par completo es 'XXBTZUSD'.
        response = k.query_public('Ticker', {'pair': 'XXBTZUSD'})

        # 3. Manejar errores devueltos por la API de Kraken.
        if response.get('error'):
            print(f"[Error KRAKEN API]: {response['error']}")
            return 0.0

        # 4. Extraer y devolver el precio de cierre ('c').
        # El resultado es un diccionario donde la clave es el par consultado.
        # El valor 'c' es una lista [precio, volumen_del_lote_en_las_24h], nos quedamos con el precio.
        last_trade_price = float(response['result']['XXBTZUSD']['c'][0])
        print(f"[KRAKEN]: Precio de BTC/USD obtenido: {last_trade_price}")
        return last_trade_price

    except Exception as e:
        print(f"[Error Crítico en get_btc_price]: No se pudo conectar o procesar la respuesta de Kraken. {e}")
        return 0.0

def get_spy_name(host: str, port: int, client_id: int) -> str:
    """
    Obtiene el nombre largo del ETF SPY (SPDR S&P 500 ETF Trust) desde Interactive Brokers.

    Utiliza la librería ib_insync para conectarse a la TWS o Gateway, solicitar
    los detalles completos del contrato y extraer su 'longName'.

    Args:
        host (str): La dirección IP del host donde se ejecuta TWS/Gateway.
        port (int): El puerto de conexión de la API de TWS/Gateway.
        client_id (int): Un ID de cliente único para la conexión.

    Returns:
        str: El nombre completo (longName) del contrato.
             Retorna "Desconocido" si la conexión o la obtención de detalles falla.
    """
    ib = IB()
    try:
        # 1. Conectar a la instancia de TWS/Gateway.
        print(f"[IBKR]: Conectando a {host}:{port} con ClientID {client_id}...")
        ib.connect(host, port, clientId=client_id, timeout=10)

        # 2. Definir el contrato para el ETF SPY.
        contract = Stock('SPY', 'SMART', 'USD')

        # 3. Solicitar los detalles completos del contrato (NO cualificar).
        # Esta llamada devuelve una lista de objetos ContractDetails que son más ricos.
        details_list = ib.reqContractDetails(contract)
        # print(f"[IBKR]: Detalles del contrato SPY obtenidos: {details_list} resultados.")
        
        # 4. Validar que hemos obtenido detalles y extraer el nombre.
        if not details_list:
            print(f"[Error IBKR]: No se encontraron detalles para el contrato {contract.symbol}.")
            return "Desconocido"

        # 5. Extraer el 'longName' del primer resultado de la lista.
        # El objeto ContractDetails sí tiene el atributo 'longName'.
        long_name = details_list[0].longName
        print(f"[IBKR]: Nombre del contrato obtenido: {long_name}")
        return long_name

    except ConnectionRefusedError:
        print(f"[Error Crítico en get_spy_name]: Conexión rechazada. ¿Está TWS/Gateway en ejecución y la API habilitada en {host}:{port}?")
        return "Desconocido"
    except Exception as e:
        print(f"[Error Crítico en get_spy_name]: Ocurrió un error con Interactive Brokers. {e}")
        return "Desconocido"
    finally:
        # 6. Asegurar la desconexión en cualquier caso (éxito o error).
        if ib.isConnected():
            print("[IBKR]: Desconectando sesión.")
            ib.disconnect()

def get_market_news(api_key: str, query: str) -> list[str]:
    """
    Obtiene una lista de titulares de noticias de mercado desde NewsAPI.

    Args:
        api_key (str): Tu clave de API para NewsAPI.
        query (str): El término de búsqueda para las noticias (ej. "S&P 500").

    Returns:
        list[str]: Una lista de strings, donde cada string es un titular de noticia.
                   Retorna una lista vacía si ocurre un error.
    """
    base_url = "https://newsapi.org/v2/everything"
    params = {
        'q': query,
        'language': 'en',
        'sortBy': 'publishedAt', # Obtener las noticias más recientes
        'apiKey': api_key
    }
    
    try:
        # 1. Realizar la petición GET a la API.
        response = requests.get(base_url, params=params)
        
        # 2. Lanzará una excepción para respuestas de error (4xx o 5xx).
        response.raise_for_status()

        # 3. Procesar la respuesta JSON.
        data = response.json()
        
        # 4. Extraer solo los titulares de los artículos.
        # Usamos .get('articles', []) para evitar un KeyError si 'articles' no está presente.
        headlines = [article['title'] for article in data.get('articles', [])]
        print(f"[NEWSAPI]: Obtenidos {len(headlines)} titulares para la consulta '{query}'.")
        return headlines
        
    except requests.exceptions.RequestException as e:
        print(f"[Error Crítico en get_market_news]: Fallo en la solicitud a NewsAPI. {e}")
        return []
    except KeyError:
        print("[Error Crítico en get_market_news]: Formato de respuesta inesperado de NewsAPI.")
        return []
    except Exception as e:
        print(f"[Error Crítico en get_market_news]: Ocurrió un error inesperado. {e}")
        return []