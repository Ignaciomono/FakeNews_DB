from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

# Importar routers
from app.routers import analysis, metrics, health
from app.services.ai_analyzer import ai_analyzer
from app.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Fake News Detector API",
    description="""
    API para detección de fake news usando inteligencia artificial.
    
    ## Características
    
    * **Análisis múltiple**: Acepta texto, URLs o archivos
    * **IA integrada**: Utiliza modelos de Hugging Face
    * **Extracción web**: Extrae contenido de noticias automáticamente
    * **Métricas completas**: Estadísticas y tendencias de análisis
    * **Seguridad**: Rate limiting y sanitización de contenido
    
    ## Endpoints principales
    
    * `/analyze` - Analizar contenido
    * `/metrics/summary` - Estadísticas generales
    * `/metrics/timeseries` - Datos temporales
    * `/health` - Estado del sistema
    """,
    version="1.0.0",
    contact={
        "name": "Fake News Detector API",
        "email": "support@fakenews-detector.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para React
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Evento de startup para inicialización
@app.on_event("startup")
async def startup_event():
    """Inicialización de la aplicación para Vercel"""
    try:
        logger.info("🚀 Inicializando Fake News Detector API...")
        
        # Inicializar modelo de IA
        await ai_analyzer.initialize()
        logger.info("✓ Modelo de IA inicializado")
        
        # La base de datos se inicializa automáticamente con las migraciones
        logger.info("✓ Aplicación lista para recibir requests")
        
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")
        # No fallar el startup, usar fallbacks

# Middleware personalizado para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"📨 {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Incluir routers
app.include_router(analysis.router)
app.include_router(metrics.router)
app.include_router(health.router)

# Endpoints adicionales
@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "Fake News Detector API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/info")
async def api_info():
    """Información detallada de la API"""
    model_info = ai_analyzer.get_model_info()
    
    return {
        "api": {
            "name": "Fake News Detector API",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        },
        "ai_model": {
            "name": model_info.get("model_name", "unknown"),
            "version": model_info.get("model_version", "unknown"),
            "loaded": model_info.get("is_loaded", False),
            "is_mock": model_info.get("is_mock", False)
        },
        "features": {
            "text_analysis": True,
            "url_extraction": True,
            "file_upload": True,
            "metrics": True,
            "timeseries": True
        },
        "limits": {
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "max_content_length": settings.MAX_CONTENT_LENGTH,
            "request_timeout": settings.REQUEST_TIMEOUT
        }
    }

# Handler global para errores no manejados
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"💥 Error no manejado en {request.url.path}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "path": str(request.url.path),
            "method": request.method
        }
    )

# Handler para errores HTTP
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"⚠️  HTTP {exc.status_code} en {request.url.path}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": str(request.url.path),
            "method": request.method,
            "status_code": exc.status_code
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🔥 Iniciando servidor de desarrollo...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )