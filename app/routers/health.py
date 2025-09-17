from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import time
import logging

from app.database import get_db
from app.schemas.news import HealthResponse
from app.services.ai_analyzer import ai_analyzer
from app.utils.content_extractor import content_extractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Variable global para trackear el tiempo de inicio
start_time = time.time()

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
        model_info = ai_analyzer.get_model_info()
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
        model_info = ai_analyzer.get_model_info()
        
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