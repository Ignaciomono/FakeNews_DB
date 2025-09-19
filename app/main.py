from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
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

# Crear aplicación FastAPI con configuración especial para Vercel
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
    # Deshabilitar docs automático para usar versión personalizada
    docs_url=None,
    redoc_url="/redoc",
    # Configuración específica para Vercel
    openapi_url="/openapi.json",  # Habilitamos el endpoint automático
    swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
        "operationsSorter": "method",
        "docExpansion": "none"
    }
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

# Incluir routers con prefijos para mejor organización
app.include_router(analysis.router, prefix="/api")
app.include_router(metrics.router, prefix="/api") 
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

# Endpoints de prueba y documentación
@app.get("/test-routing")
async def test_routing():
    """Endpoint simple para probar que el routing funciona en Vercel"""
    return {
        "message": "✅ Routing funcionando correctamente",
        "timestamp": time.time(),
        "vercel_test": "OK"
    }

@app.get("/api-docs", response_class=HTMLResponse)
async def api_documentation():
    """Documentación básica de la API como fallback"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fake News Detector API - Documentación</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            .header { background: #007acc; color: white; padding: 20px; border-radius: 8px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .get { background: #61affe; }
            .post { background: #49cc90; }
            code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Fake News Detector API</h1>
            <p>API para detección de fake news usando inteligencia artificial</p>
        </div>
        
        <h2>📋 Endpoints Principales</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/</strong>
            <p>Información básica de la API</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/analyze</strong>
            <p>Analizar contenido para detectar fake news</p>
            <code>{"text": "texto a analizar"}</code>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/health</strong>
            <p>Estado de salud del sistema</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/metrics/summary</strong>
            <p>Estadísticas generales del sistema</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/redoc</strong>
            <p>Documentación detallada (ReDoc)</p>
        </div>
        
        <h2>🔗 Enlaces útiles</h2>
        <ul>
            <li><a href="/redoc">📖 Documentación ReDoc</a></li>
            <li><a href="/openapi.json">⚙️ Schema OpenAPI</a></li>
            <li><a href="/health">💚 Health Check</a></li>
            <li><a href="/test-routing">🧪 Test Routing</a></li>
        </ul>
        
        <h2>🚀 Uso de la API</h2>
        <p>Base URL: <code>https://fakenewsignacionomonos-projects.vercel.app</code></p>
        
        <h3>Ejemplo de análisis:</h3>
        <pre>
POST /api/analyze
Content-Type: application/json

{
  "text": "Este es un texto de ejemplo para analizar"
}
        </pre>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Solución directa para Swagger UI en Vercel
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi

@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
async def swagger_ui_docs():
    """Swagger UI completamente manual para Vercel - con CDN mejorado"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{app.title} - API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css" />
        <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/favicon-32x32.png" sizes="32x32" />
        <style>
            html {{
                box-sizing: border-box;
                overflow: -moz-scrollbars-vertical;
                overflow-y: scroll;
            }}
            *, *:before, *:after {{
                box-sizing: inherit;
            }}
            body {{
                margin: 0;
                background: #fafafa;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            .loading {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-size: 18px;
                color: #666;
            }}
            .error {{
                margin: 50px;
                padding: 20px;
                background: #fee;
                border: 1px solid #fcc;
                border-radius: 5px;
                color: #c33;
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui">
            <div class="loading">
                🔄 Cargando documentación de la API...
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
        <script>
            window.addEventListener('load', function() {{
                try {{
                    console.log('Inicializando Swagger UI...');
                    
                    const ui = SwaggerUIBundle({{
                        url: window.location.origin + '/openapi.json',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout",
                        tryItOutEnabled: true,
                        supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                        onComplete: function() {{
                            console.log('✅ Swagger UI cargado correctamente');
                        }},
                        onFailure: function(data) {{
                            console.error('❌ Error en Swagger UI:', data);
                            showError('Error al cargar la documentación: ' + JSON.stringify(data));
                        }}
                    }});
                    
                    // Timeout de seguridad
                    setTimeout(function() {{
                        const content = document.getElementById('swagger-ui').innerHTML;
                        if (content.includes('Cargando documentación')) {{
                            showError('Timeout: La documentación está tardando mucho en cargar.');
                        }}
                    }}, 10000);
                    
                }} catch(e) {{
                    console.error('❌ Error fatal:', e);
                    showError('Error fatal al inicializar Swagger UI: ' + e.message);
                }}
            }});
            
            function showError(message) {{
                document.getElementById('swagger-ui').innerHTML = `
                    <div class="error">
                        <h2>⚠️ Error al cargar documentación</h2>
                        <p>${{message}}</p>
                        <p><strong>Alternativas:</strong></p>
                        <ul>
                            <li><a href="/api-docs">📋 Documentación básica</a></li>
                            <li><a href="/redoc">📖 ReDoc (alternativa)</a></li>
                            <li><a href="/openapi.json">⚙️ Schema OpenAPI directo</a></li>
                        </ul>
                    </div>
                `;
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    """OpenAPI schema que incluye todos los endpoints"""
    return app.openapi()

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