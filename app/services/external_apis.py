"""
Servicios para integración con APIs externas de fact-checking
"""
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from app.config_apis import api_config

logger = logging.getLogger(__name__)


class GoogleFactCheckService:
    """Servicio para Google Fact Check Tools API"""
    
    @staticmethod
    async def check_claim(query: str, language_code: str = "en") -> Dict[str, Any]:
        """
        Verificar un claim usando Google Fact Check Tools API
        
        Args:
            query: Texto del claim a verificar
            language_code: Código de idioma (default: en)
            
        Returns:
            Dict con resultados del fact-check
        """
        if not api_config.is_google_configured():
            return {
                "error": "Google Fact Check API no configurada",
                "configured": False,
                "message": "Por favor configure GOOGLE_FACT_CHECK_API_KEY"
            }
        
        try:
            params = {
                "query": query,
                "languageCode": language_code,
                "key": api_config.GOOGLE_FACT_CHECK_API_KEY
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    api_config.GOOGLE_FACT_CHECK_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=api_config.REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "api": "google_fact_check",
                            "claims": data.get("claims", []),
                            "total_results": len(data.get("claims", []))
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Google Fact Check API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
                        
        except Exception as e:
            logger.error(f"Error calling Google Fact Check API: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class ClaimBusterService:
    """Servicio para ClaimBuster API"""
    
    @staticmethod
    async def score_text(text: str) -> Dict[str, Any]:
        """
        Obtener score de verificabilidad de ClaimBuster
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict con score de verificabilidad
        """
        if not api_config.is_claimbuster_configured():
            return {
                "error": "ClaimBuster API no configurada",
                "configured": False,
                "message": "Por favor configure CLAIMBUSTER_API_KEY"
            }
        
        try:
            headers = {
                "x-api-key": api_config.CLAIMBUSTER_API_KEY
            }
            
            payload = {
                "input_text": text
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_config.CLAIMBUSTER_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=api_config.REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "api": "claimbuster",
                            "score": data.get("score", 0),
                            "text": text,
                            "interpretation": "check-worthy" if data.get("score", 0) > 0.5 else "not check-worthy"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"ClaimBuster API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
                        
        except Exception as e:
            logger.error(f"Error calling ClaimBuster API: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class WordLiftService:
    """Servicio para WordLift Fact-Checking API"""
    
    @staticmethod
    async def fact_check(text: str) -> Dict[str, Any]:
        """
        Verificar hechos usando WordLift API
        
        Args:
            text: Texto a verificar
            
        Returns:
            Dict con resultados de fact-checking
        """
        if not api_config.is_wordlift_configured():
            return {
                "error": "WordLift API no configurada",
                "configured": False,
                "message": "Por favor configure WORDLIFT_API_KEY"
            }
        
        try:
            headers = {
                "Authorization": f"Key {api_config.WORDLIFT_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_config.WORDLIFT_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=api_config.REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "api": "wordlift",
                            "results": data
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"WordLift API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
                        
        except Exception as e:
            logger.error(f"Error calling WordLift API: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class MBFCService:
    """Servicio para Media Bias / Fact Check API"""
    
    @staticmethod
    async def check_source(url: str) -> Dict[str, Any]:
        """
        Verificar sesgo y credibilidad de una fuente
        
        Args:
            url: URL de la fuente a verificar
            
        Returns:
            Dict con información de sesgo y credibilidad
        """
        if not api_config.is_mbfc_configured():
            return {
                "error": "MBFC API no configurada",
                "configured": False,
                "message": "Por favor configure MBFC_API_KEY"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {api_config.MBFC_API_KEY}"
            }
            
            params = {
                "url": url
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{api_config.MBFC_URL}/source",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=api_config.REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "api": "mbfc",
                            "bias": data.get("bias"),
                            "credibility": data.get("credibility"),
                            "factual_reporting": data.get("factual_reporting"),
                            "source_info": data
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"MBFC API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
                        
        except Exception as e:
            logger.error(f"Error calling MBFC API: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class RapidAPIFakeNewsService:
    """Servicio para Fake News Detection en RapidAPI"""
    
    @staticmethod
    async def detect_fake_news(text: str, title: str = "") -> Dict[str, Any]:
        """
        Detectar fake news usando RapidAPI
        
        Args:
            text: Contenido del artículo
            title: Título del artículo (opcional)
            
        Returns:
            Dict con resultado de detección
        """
        if not api_config.is_rapidapi_configured():
            return {
                "error": "RapidAPI no configurada",
                "configured": False,
                "message": "Por favor configure RAPIDAPI_KEY"
            }
        
        try:
            headers = {
                "X-RapidAPI-Key": api_config.RAPIDAPI_KEY,
                "X-RapidAPI-Host": api_config.RAPIDAPI_HOST,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "title": title
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_config.RAPIDAPI_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=api_config.REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "api": "rapidapi_fake_news",
                            "is_fake": data.get("is_fake", False),
                            "confidence": data.get("confidence", 0),
                            "details": data
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"RapidAPI error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "details": error_text
                        }
                        
        except Exception as e:
            logger.error(f"Error calling RapidAPI: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Instancias de servicios
google_fact_check_service = GoogleFactCheckService()
claimbuster_service = ClaimBusterService()
wordlift_service = WordLiftService()
mbfc_service = MBFCService()
rapidapi_service = RapidAPIFakeNewsService()