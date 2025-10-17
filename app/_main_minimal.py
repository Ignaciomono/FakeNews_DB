"""
Versión mínima de la aplicación para debugging
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time

# Crear aplicación FastAPI mínima
app = FastAPI(
    title="Fake News Detector API",
    description="API para detección de fake news",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    """Endpoint raíz básico"""
    return {
        "message": "Fake News Detector API - Versión Mínima",
        "version": "1.0.0",
        "status": "running",
        "timestamp": time.time(),
        "endpoints": [
            "GET /",
            "GET /health",
            "GET /docs",
            "POST /analyze-test"
        ]
    }

@app.get("/health")
async def health():
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Fake News Detector API"
    }

@app.post("/analyze-test")
async def analyze_test(data: dict):
    """Endpoint de análisis de prueba"""
    text = data.get("text", "")
    return {
        "text": text,
        "result": "fake" if "fake" in text.lower() else "real",
        "confidence": 0.85,
        "timestamp": time.time()
    }

@app.get("/docs-custom", response_class=HTMLResponse)
async def custom_docs():
    """Swagger UI personalizado y simple"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fake News API - Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({{
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.presets.standalone]
            }})
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)