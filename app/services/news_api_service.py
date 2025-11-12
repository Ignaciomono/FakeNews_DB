"""
Servicio NewsAPI - Verificación de Noticias Recientes (100% GRATIS)
100 requests por día en plan gratuito
"""
import aiohttp
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class NewsAPIService:
    """Verificador de noticias recientes usando NewsAPI.org (GRATIS)"""
    
    NEWS_API_URL = "https://newsapi.org/v2/everything"
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")  # Obtener de variables de entorno
    
    # API Key gratuita de desarrollo (100 requests/día)
    # Los usuarios deben registrarse en: https://newsapi.org/register
    
    @staticmethod
    async def search_news(query: str, language: str = "es", days_back: int = 30) -> Optional[Dict]:
        """
        Busca noticias recientes relacionadas con el query
        
        Args:
            query: Texto a buscar en noticias
            language: Código de idioma (default: es)
            days_back: Días hacia atrás para buscar (default: 30)
            
        Returns:
            Dict con resultados de noticias o None si hay error
        """
        
        # Verificar si hay API key configurada
        if not NewsAPIService.NEWS_API_KEY:
            logger.warning("⚠️ NEWS_API_KEY no configurada. Registra en https://newsapi.org/register")
            return {
                "status": "error",
                "message": "NEWS_API_KEY no configurada",
                "articles": []
            }
        
        try:
            # Calcular fecha de inicio (días atrás)
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            params = {
                "q": query,
                "language": language,
                "from": from_date,
                "sortBy": "relevancy",
                "pageSize": 5,  # Máximo 5 artículos
                "apiKey": NewsAPIService.NEWS_API_KEY
            }
            
            headers = {
                "User-Agent": "DeepFakeDetector/1.0 (Educational Project)"
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    NewsAPIService.NEWS_API_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"NewsAPI request failed: {response.status}")
                        data = await response.json()
                        return {
                            "status": "error",
                            "message": data.get("message", "API error"),
                            "articles": []
                        }
                    
                    data = await response.json()
                    
                    if data.get("status") != "ok":
                        logger.warning(f"NewsAPI error: {data.get('message')}")
                        return {
                            "status": "error",
                            "message": data.get("message", "Unknown error"),
                            "articles": []
                        }
                    
                    articles = data.get("articles", [])
                    
                    logger.info(f"✅ NewsAPI encontró {len(articles)} artículos para: {query}")
                    
                    # Procesar y simplificar artículos
                    simplified_articles = []
                    for article in articles[:5]:  # Máximo 5
                        simplified_articles.append({
                            "title": article.get("title", "N/A"),
                            "description": article.get("description", "N/A"),
                            "source": article.get("source", {}).get("name", "Unknown"),
                            "url": article.get("url", ""),
                            "publishedAt": article.get("publishedAt", ""),
                            "author": article.get("author", "Unknown")
                        })
                    
                    return {
                        "status": "ok",
                        "totalResults": data.get("totalResults", 0),
                        "articles": simplified_articles
                    }
                    
        except Exception as e:
            logger.error(f"Error searching NewsAPI: {e}")
            return {
                "status": "error",
                "message": str(e),
                "articles": []
            }
    
    @staticmethod
    async def verify_political_claim(claim_text: str, person_name: Optional[str] = None) -> Dict:
        """
        Verifica un claim político buscando noticias recientes
        
        Args:
            claim_text: Texto del claim
            person_name: Nombre de persona mencionada (opcional)
            
        Returns:
            Dict con resultado de verificación
        """
        # Construir query de búsqueda
        if person_name:
            query = f"{person_name} {claim_text[:50]}"
        else:
            query = claim_text[:100]
        
        # Buscar noticias
        news_result = await NewsAPIService.search_news(query, language="es", days_back=30)
        
        if not news_result or news_result.get("status") != "ok":
            return {
                "verified": False,
                "found_articles": False,
                "message": "No se pudieron buscar noticias",
                "confidence": 0.3
            }
        
        articles = news_result.get("articles", [])
        total_results = news_result.get("totalResults", 0)
        
        if total_results == 0:
            return {
                "verified": False,
                "found_articles": False,
                "message": f"No se encontraron noticias recientes sobre: {claim_text[:50]}",
                "confidence": 0.4,
                "articles": []
            }
        
        # Analizar artículos encontrados
        relevant_count = 0
        sources = []
        
        for article in articles:
            title = article.get("title", "").lower()
            description = article.get("description", "").lower()
            
            # Verificar si el claim aparece en el título o descripción
            claim_keywords = claim_text.lower().split()[:5]  # Primeras 5 palabras
            
            matches = sum(1 for keyword in claim_keywords if keyword in title or keyword in description)
            
            if matches >= 2:  # Al menos 2 keywords coinciden
                relevant_count += 1
                sources.append(article.get("source", "Unknown"))
        
        # Determinar confianza basado en cantidad de artículos relevantes
        if relevant_count >= 3:
            confidence = 0.80
            verdict = "likely_true"
            message = f"Se encontraron {relevant_count} artículos relevantes de fuentes confiables"
        elif relevant_count >= 1:
            confidence = 0.65
            verdict = "possibly_true"
            message = f"Se encontraron {relevant_count} artículos relacionados, requiere más verificación"
        else:
            confidence = 0.50
            verdict = "uncertain"
            message = f"Se encontraron noticias pero no directamente relacionadas"
        
        return {
            "verified": True,
            "found_articles": True,
            "total_results": total_results,
            "relevant_articles": relevant_count,
            "verdict": verdict,
            "confidence": confidence,
            "message": message,
            "sources": list(set(sources)),  # Fuentes únicas
            "articles": articles
        }


# Instancia global
news_api_service = NewsAPIService()
