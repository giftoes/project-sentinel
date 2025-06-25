# project_sentinel/analysis.py

"""
Módulo de Análisis de Sentimiento para Project Sentinel.

Este script contiene funciones para procesar datos de texto (como titulares
de noticias) y extraer insights, principalmente a través del análisis
de sentimiento.
"""

# Se necesita descargar el léxico de vader la primera vez.
# En un terminal, ejecuta:
# python -m nltk.downloader vader_lexicon
# Sin embargo, como vaderSentiment lo incluye, la importación directa suele funcionar.
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_headlines_sentiment(headlines: list[str]) -> dict:
    """
    Analiza una lista de titulares de noticias y calcula una puntuación de sentimiento promedio.

    Utiliza el SentimentIntensityAnalyzer de la librería VADER (Valence Aware Dictionary
    and sEntiment Reasoner), que está específicamente afinado para sentimientos
    expresados en redes sociales y textos cortos como titulares.

    Args:
        headlines (list[str]): Una lista de strings, donde cada string es un titular.

    Returns:
        dict: Un diccionario que contiene:
              - 'average_sentiment_compound' (float): La puntuación 'compound' promedio de todos los titulares.
                El rango es de -1 (muy negativo) a +1 (muy positivo).
              - 'details' (list[dict]): Una lista detallada con el análisis de cada titular,
                incluyendo su puntuación de sentimiento completa (neg, neu, pos, compound).
              Retorna un diccionario con valores por defecto si la lista de titulares está vacía.
    """
    if not headlines:
        print("[ANALYSIS]: La lista de titulares está vacía. No hay nada que analizar.")
        return {
            'average_sentiment_compound': 0.0,
            'details': []
        }

    analyzer = SentimentIntensityAnalyzer()
    detailed_results = []
    total_compound_score = 0.0

    print(f"[ANALYSIS]: Analizando {len(headlines)} titulares...")

    for headline in headlines:
        # 1. Calcular las puntuaciones de polaridad para el titular.
        # Esto devuelve un diccionario con puntuaciones para 'neg', 'neu', 'pos' y 'compound'.
        sentiment_scores = analyzer.polarity_scores(headline)
        
        # 2. Almacenar el resultado detallado.
        detailed_results.append({
            'headline': headline,
            'sentiment_scores': sentiment_scores
        })
        # print(f"[ANALYSIS]: Titular analizado: '{headline}' | Puntuación: {sentiment_scores}")
        
        # 3. Acumular la puntuación 'compound' para el promedio.
        # La puntuación 'compound' es la métrica normalizada más útil, de -1 a +1.
        total_compound_score += sentiment_scores['compound']

    # 4. Calcular el promedio de la puntuación 'compound'.
    average_compound = total_compound_score / len(headlines)
    
    print(f"[ANALYSIS]: Análisis completado. Sentimiento compuesto promedio: {average_compound:.4f}")

    # 5. Devolver el resultado agregado y el detallado.
    return {
        'average_sentiment_compound': average_compound,
        'details': detailed_results
    }