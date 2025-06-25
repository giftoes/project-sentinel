# main.py
# Orquestador principal para el proyecto "Project Sentinel".
# Este script inicializa la configuración, llama a los módulos de
# conectores y análisis, y presenta un informe consolidado.

import configparser
from datetime import datetime
import pytz  # Para manejar zonas horarias de forma explícita

# --- Importaciones de Módulos del Proyecto ---
# Se importan las funciones específicas que necesitamos de nuestros módulos.
from connectors import get_btc_price, get_spy_name, get_market_news
from analysis import analyze_headlines_sentiment


def load_config(filename="config.ini"):
    """
    Carga de forma segura la configuración desde un archivo .ini.

    Args:
        filename (str): El nombre del archivo de configuración.

    Returns:
        configparser.ConfigParser: El objeto de configuración cargado.
        
    Raises:
        FileNotFoundError: Si el archivo de configuración no se encuentra.
    """
    config = configparser.ConfigParser()
    # config.read() devuelve una lista de los archivos que pudo leer.
    # Si la lista está vacía, el archivo no se encontró o no se pudo leer.
    if not config.read(filename):
        raise FileNotFoundError(f"Error: El archivo de configuración '{filename}' no fue encontrado.")
    return config

def get_sentiment_label(score):
    """
    Convierte una puntuación de sentimiento numérica en una etiqueta descriptiva.
    Esta lógica nos permite dar un contexto cualitativo al valor numérico.

    Args:
        score (float): La puntuación de sentimiento (compound), típicamente entre -1 y 1.

    Returns:
        str: Una etiqueta descriptiva del sentimiento.
    """
    if score > 0.3:
        return "POSITIVO"
    elif score > 0.05:
        return "NEUTRAL-POSITIVO"
    elif score < -0.3:
        return "NEGATIVO"
    elif score < -0.05:
        return "NEUTRAL-NEGATIVO"
    else:
        return "NEUTRAL"

def display_report(spy_name, sentiment_score, btc_price):
    """
    Formatea e imprime el informe final en la consola.

    Args:
        spy_name (str): El nombre completo del ETF SPY.
        sentiment_score (float): La puntuación de sentimiento promedio de las noticias.
        btc_price (float): El precio actual de Bitcoin.
    """
    # Generar la marca de tiempo actual en formato UTC para consistencia
    timestamp_utc = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    sentiment_label = get_sentiment_label(sentiment_score)
    
    # --- Creación del Informe ---
    # Usamos f-strings para un formato limpio y control preciso sobre la salida.
    # El separador se define una vez para reutilizarlo y mantener la consistencia.
    separator = "=" * 63
    
    print(separator)
    print("    PROJECT SENTINEL - CRYPTO & TRADFI SENTIMENT BRIDGE")
    print(f"            Fecha y Hora: {timestamp_utc}")
    print(separator)
    print() # Línea en blanco para espaciar

    print("[1] ANÁLISIS DEL MERCADO TRADICIONAL (S&P 500)")
    print("-" * 63)
    # :<30 alinea el texto a la izquierda en un espacio de 30 caracteres
    print(f"{'-> Activo de Referencia':<30}: {spy_name} (vía IBKR)")
    print(f"{'-> Sentimiento de Noticias':<30}: {sentiment_label} (vía NewsAPI & AI)")
    # :.3f formatea el float para que siempre tenga 3 decimales
    print(f"{'-> Puntuación de Sentimiento':<30}: {sentiment_score:.3f}")
    print()

    print("[2] DATOS DEL MERCADO CRYPTO")
    print("-" * 63)
    print(f"{'-> Activo':<30}: Bitcoin (XBT/USD) (vía Kraken)")
    # :>15 alinea el número a la derecha; :, agrega separador de miles; .2f fija 2 decimales
    print(f"{'-> Precio Actual':<30}: ${btc_price:,.2f}")
    print()

    print("[3] CONCLUSIÓN")
    print("-" * 63)
    print(f"El sentimiento del mercado tradicional es {sentiment_label}.")
    print("Monitorear si este sentimiento se traslada a los activos de riesgo como Bitcoin.")
    print()

    print(separator)
    print("                     FIN DEL INFORME")
    print(separator)


def main():
    """
    Función principal que orquesta la ejecución del script.
    """
    print("Iniciando Project Sentinel...")
    
    try:
        # 1. Cargar configuración desde el archivo .ini
        config = load_config()
        
        # Extraer parámetros de configuración
        ib_host = config.get('IBKR', 'HOST')
        ib_port = config.getint('IBKR', 'PORT')
        ib_client_id = config.getint('IBKR', 'CLIENT_ID')
        news_api_key = config.get('NEWS_API', 'API_KEY')
        
        print("Configuración cargada. Obteniendo datos...")

        # 2. Flujo de Ejecución: Obtener datos de TradFi
        spy_name = get_spy_name(ib_host, ib_port, ib_client_id)
        print(f"Nombre del ETF SPY obtenido: {spy_name}")
        headlines = get_market_news(news_api_key, spy_name)
        sentiment_analysis = analyze_headlines_sentiment(headlines)
        # Extraemos el valor específico que necesitamos del diccionario devuelto
        avg_sentiment_score = sentiment_analysis['average_sentiment_compound']

        # 3. Flujo de Ejecución: Obtener datos de Crypto
        btc_price = get_btc_price()

        print("Datos recopilados. Generando informe...")
        
        # 4. Generación del Informe Final
        display_report(spy_name, avg_sentiment_score, btc_price)

    except FileNotFoundError as e:
        print(f"\nERROR CRÍTICO: {e}")
        print("Por favor, asegúrate de que 'config.ini' existe en el mismo directorio.")
        print("Puedes crearlo a partir de 'config.ini.example'.")
    except configparser.NoSectionError as e:
        print(f"\nERROR DE CONFIGURACIÓN: Falta la sección {e.section} en 'config.ini'.")
    except configparser.NoOptionError as e:
        print(f"\nERROR DE CONFIGURACIÓN: Falta la opción '{e.option}' en la sección '{e.section}' de 'config.ini'.")
    except Exception as e:
        # Captura cualquier otra excepción inesperada durante la ejecución
        print(f"\nHA OCURRIDO UN ERROR INESPERADO:")
        print(f"Tipo de Error: {type(e).__name__}")
        print(f"Mensaje: {e}")
        print("La ejecución del programa se ha detenido.")


if __name__ == "__main__":
    # Este es el punto de entrada del script.
    # Llamar a main() asegura que todo el código de orquestación
    # se ejecute solo cuando el archivo es llamado directamente.
    main()