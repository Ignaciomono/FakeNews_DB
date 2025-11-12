from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import time
import logging
import os
import aiohttp
import asyncio

from app.database import get_db
from app.schemas.news import HealthResponse
from app.services.ai_analyzer import ai_analyzer
from app.services.entity_verifier import entity_verifier
from app.services.news_api_service import news_api_service
from app.services.wikipedia_verifier import wikipedia_verifier
from app.utils.content_extractor import content_extractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Variable global para trackear el tiempo de inicio
start_time = time.time()

@router.get("/ping")
async def ping():
    """Health check simple sin dependencias - para serverless"""
    return {
        "status": "healthy",
        "message": "Service is running",
        "timestamp": datetime.now(),
        "uptime_seconds": int(time.time() - start_time)
    }

@router.get("/", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Verifica el estado de salud del sistema.
    
    Chequea:
    - Conexión a base de datos
    - Estado del modelo de IA
    - Funcionalidad del extractor web
    """
    
    status = "healthy"
    database_ok = False
    ai_model_ok = False
    web_extractor_ok = False
    
    # Verificar base de datos
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1"))
        database_ok = result.scalar() == 1
    except Exception as e:
        logger.error(f"Error verificando base de datos: {e}")
        database_ok = False
    
    # Verificar modelo de IA
    try:
        model_info = await ai_analyzer.get_model_info()
        ai_model_ok = model_info.get("is_loaded", False)
        
        # Test básico del modelo si está cargado
        if ai_model_ok:
            test_result = await ai_analyzer.analyze_text("This is a test message.")
            ai_model_ok = test_result is not None
            
    except Exception as e:
        logger.error(f"Error verificando modelo de IA: {e}")
        ai_model_ok = False
    
    # Verificar extractor web (test básico)
    try:
        # Solo verificar que el extractor esté disponible
        web_extractor_ok = hasattr(content_extractor, 'extract_from_url')
    except Exception as e:
        logger.error(f"Error verificando extractor web: {e}")
        web_extractor_ok = False
    
    # Determinar estado general
    if database_ok and ai_model_ok and web_extractor_ok:
        status = "healthy"
    elif database_ok and (ai_model_ok or web_extractor_ok):
        status = "degraded"
    else:
        status = "unhealthy"
    
    # Calcular uptime
    uptime_seconds = int(time.time() - start_time)
    
    return HealthResponse(
        status=status,
        database=database_ok,
        ai_model=ai_model_ok,
        web_extractor=web_extractor_ok,
        timestamp=datetime.now(),
        version="1.0.0",
        uptime_seconds=uptime_seconds
    )

@router.get("/database")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Verificación específica de la base de datos"""
    try:
        from sqlalchemy import text
        
        # Test de conexión básica
        await db.execute(text("SELECT 1"))
        
        # Test de tablas principales
        from app.models.news import NewsAnalysis
        from sqlalchemy import select
        
        result = await db.execute(
            select(NewsAnalysis).limit(1)
        )
        
        return {
            "status": "healthy",
            "connection": True,
            "tables_accessible": True,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error en verificación de base de datos: {e}")
        return {
            "status": "unhealthy",
            "connection": False,
            "tables_accessible": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/ai-model")
async def ai_model_health():
    """Verificación específica del modelo de IA"""
    try:
        model_info = await ai_analyzer.get_model_info()
        
        # Test del modelo
        test_start = time.time()
        score, label, confidence, processing_time = await ai_analyzer.analyze_text(
            "This is a simple test message for health check."
        )
        test_duration = time.time() - test_start
        
        return {
            "status": "healthy",
            "model_loaded": model_info.get("is_loaded", False),
            "model_name": model_info.get("model_name", "unknown"),
            "is_mock": model_info.get("is_mock", False),
            "test_successful": True,
            "test_duration_ms": int(test_duration * 1000),
            "test_processing_time_ms": processing_time,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error en verificación de modelo de IA: {e}")
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "test_successful": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/web-extractor")
async def web_extractor_health():
    """Verificación específica del extractor web"""
    try:
        # Test con una URL de ejemplo (sin hacer request real)
        test_url = "https://example.com"
        url_valid = content_extractor.validate_url(test_url)
        
        return {
            "status": "healthy",
            "extractor_available": True,
            "url_validation_working": url_valid,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error en verificación de extractor web: {e}")
        return {
            "status": "unhealthy",
            "extractor_available": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/ner-service")
async def ner_service_health():
    """Verificación del servicio de NER (Named Entity Recognition)"""
    try:
        # Verificar que spaCy esté cargado
        if not entity_verifier.nlp:
            return {
                "status": "unhealthy",
                "spacy_loaded": False,
                "error": "spaCy model not loaded",
                "timestamp": datetime.now()
            }
        
        # Test de extracción de entidades (extract_entities NO es async)
        test_text = "Lionel Messi jugó en Barcelona hasta 2021"
        test_start = time.time()
        entities = entity_verifier.extract_entities(test_text)
        test_duration = time.time() - test_start
        
        # Verificar que detectó entidades
        entities_found = len(entities.get("persons", [])) > 0
        
        return {
            "status": "healthy",
            "spacy_loaded": True,
            "model_name": entity_verifier.nlp.meta.get("name", "unknown"),
            "model_version": entity_verifier.nlp.meta.get("version", "unknown"),
            "language": entity_verifier.nlp.meta.get("lang", "unknown"),
            "test_successful": entities_found,
            "entities_detected": len(entities.get("persons", [])),
            "test_duration_ms": int(test_duration * 1000),
            "database_entries": len(entity_verifier.verified_events),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error en verificación de NER: {e}")
        return {
            "status": "unhealthy",
            "spacy_loaded": False,
            "test_successful": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/wikipedia-api")
async def wikipedia_api_health():
    """Verificación del servicio de Wikipedia/Wikidata"""
    try:
        # Test de conexión real a Wikipedia
        test_start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://es.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "format": "json",
                        "list": "search",
                        "srsearch": "test",
                        "srlimit": 1
                    },
                    headers={
                        "User-Agent": "DeepFakeDetector/1.0 (Educational Project)"
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    test_duration = time.time() - test_start
                    
                    api_working = response.status == 200
                    
                    if api_working:
                        return {
                            "status": "healthy",
                            "api_accessible": True,
                            "test_successful": True,
                            "test_duration_ms": int(test_duration * 1000),
                            "response_status": response.status,
                            "user_agent": "DeepFakeDetector/1.0",
                            "timestamp": datetime.now()
                        }
                    else:
                        return {
                            "status": "degraded",
                            "api_accessible": False,
                            "test_successful": False,
                            "test_duration_ms": int(test_duration * 1000),
                            "response_status": response.status,
                            "timestamp": datetime.now()
                        }
        except asyncio.TimeoutError:
            return {
                "status": "degraded",
                "api_accessible": False,
                "test_successful": False,
                "error": "Connection timeout",
                "timestamp": datetime.now()
            }
        
    except Exception as e:
        logger.error(f"Error en verificación de Wikipedia API: {e}")
        return {
            "status": "degraded",
            "api_accessible": False,
            "test_successful": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/news-api")
async def news_api_health():
    """Verificación del servicio de NewsAPI"""
    try:
        # Verificar que la API key esté configurada
        api_key = os.getenv("NEWS_API_KEY")
        api_key_configured = api_key is not None and len(api_key) > 0
        
        if not api_key_configured:
            return {
                "status": "degraded",
                "api_key_configured": False,
                "api_accessible": False,
                "message": "NewsAPI key not configured - service will be skipped",
                "timestamp": datetime.now()
            }
        
        # Test de conexión real a NewsAPI
        test_start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": "test",
                        "apiKey": api_key,
                        "pageSize": 1
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    test_duration = time.time() - test_start
                    
                    api_working = response.status == 200
                    
                    if api_working:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "api_key_configured": True,
                            "api_accessible": True,
                            "test_successful": True,
                            "test_duration_ms": int(test_duration * 1000),
                            "response_status": response.status,
                            "timestamp": datetime.now()
                        }
                    else:
                        return {
                            "status": "degraded",
                            "api_key_configured": True,
                            "api_accessible": False,
                            "test_successful": False,
                            "test_duration_ms": int(test_duration * 1000),
                            "response_status": response.status,
                            "timestamp": datetime.now()
                        }
        except asyncio.TimeoutError:
            return {
                "status": "degraded",
                "api_key_configured": True,
                "api_accessible": False,
                "test_successful": False,
                "error": "Connection timeout",
                "timestamp": datetime.now()
            }
        
    except Exception as e:
        logger.error(f"Error en verificación de NewsAPI: {e}")
        return {
            "status": "degraded",
            "api_key_configured": api_key_configured if 'api_key_configured' in locals() else False,
            "api_accessible": False,
            "test_successful": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/political-detector")
async def political_detector_health():
    """Verificación del detector de claims políticos"""
    try:
        # Test de detección de claims políticos
        test_cases = [
            ("Milei implementó la pena de muerte", True),  # Debería detectar
            ("Messi ganó el mundial", False)  # No debería detectar
        ]
        
        results = []
        for text, should_detect in test_cases:
            is_detected = entity_verifier._check_controversial_political_claims(text)
            results.append({
                "text": text,
                "expected": should_detect,
                "detected": is_detected,
                "correct": is_detected == should_detect
            })
        
        all_correct = all(r["correct"] for r in results)
        
        return {
            "status": "healthy" if all_correct else "degraded",
            "detector_available": True,
            "test_successful": all_correct,
            "test_results": results,
            "political_keywords": len(entity_verifier.political_keywords),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error en verificación de detector político: {e}")
        return {
            "status": "unhealthy",
            "detector_available": False,
            "test_successful": False,
            "error": str(e),
            "timestamp": datetime.now()
        }

@router.get("/verification-layers")
async def verification_layers_health():
    """Verificación completa del sistema de verificación de 8 capas"""
    try:
        # Verificar todos los componentes
        components = {
            "ner_service": entity_verifier.nlp is not None,
            "wikipedia_api": True,  # Siempre disponible (no requiere API key)
            "news_api": news_api_service.api_key is not None,
            "political_detector": True,  # Siempre disponible
            "ai_analyzer": ai_analyzer is not None,
            "web_extractor": content_extractor is not None,
        }
        
        # Contar componentes activos
        active_count = sum(1 for v in components.values() if v)
        total_count = len(components)
        
        # Determinar estado general
        if active_count == total_count:
            status = "healthy"
        elif active_count >= total_count * 0.7:  # 70% o más
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "active_components": active_count,
            "total_components": total_count,
            "availability_percentage": int((active_count / total_count) * 100),
            "components": components,
            "verification_layers": {
                "layer_1": "NER + Entity Database",
                "layer_2": "Wikipedia/Wikidata",
                "layer_3": "Political Claims Detector",
                "layer_4": "NewsAPI",
                "layer_5": "Google Fact Check",
                "layer_6": "AI Sentiment Analysis",
                "layer_7": "Web Content Extraction",
                "layer_8": "Absurd Claims Detection"
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error en verificación de capas: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }