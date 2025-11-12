"""
Fake News Detector API - Main Application
Optimizado para producción en Vercel con Neon PostgreSQL
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

# Importar routers
from app.routers import analysis, metrics, health, auth, fact_check_apis, models
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
    ## 🔍 API para Detección de Fake News con IA
    
    ### Características
    
    * **Análisis de Contenido**: Texto, URLs o archivos
    * **IA Integrada**: Modelos de Hugging Face
    * **5 APIs de Fact-Checking**: Google, ClaimBuster, WordLift, MBFC, RapidAPI
    * **Autenticación**: Sistema JWT con registro y login
    * **Base de Datos**: PostgreSQL en Neon
    * **Métricas**: Estadísticas y tendencias de análisis
    
    ### Endpoints Principales
    
    * `POST /analyze` - Analizar contenido para detectar fake news
    * `GET /fact-check/status` - Estado de APIs de fact-checking
    * `POST /fact-check/multi-check` - Verificación con múltiples APIs
    * `POST /auth/register` - Registrar nuevo usuario
    * `POST /auth/login` - Autenticación de usuario
    * `GET /metrics/summary` - Estadísticas generales
    * `GET /health` - Estado del sistema
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Inicialización de la aplicación"""
    try:
        logger.info("🚀 Iniciando Fake News Detector API v2.0.0")
        await ai_analyzer.initialize()
        logger.info("✅ IA inicializada correctamente")
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.3f}s"
    )
    
    return response

# Incluir todos los routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(fact_check_apis.router)
app.include_router(metrics.router)
app.include_router(models.router)

# Endpoint raíz
@app.get("/", tags=["Root"])
async def root():
    """Información básica de la API"""
    return {
        "name": "Fake News Detector API",
        "version": "2.0.0",
        "status": "running",
        "documentation": "/docs",
        "current_model": settings.HF_MODEL_NAME,  # Mostrar modelo actual
        "features": {
            "ai_analysis": True,
            "fake_news_models": 6,
            "fact_checking_apis": 5,
            "authentication": True,
            "database": "Neon PostgreSQL",
            "metrics": True
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "analyze": "/analyze",
            "models": "/models (list all AI models)",
            "auth": "/auth/register & /auth/login",
            "fact_check": "/fact-check/status",
            "metrics": "/metrics/summary"
        }
    }

# Manejadores de errores
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": str(request.url.path),
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "path": str(request.url.path)
        }
    )

# Punto de entrada para desarrollo local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
