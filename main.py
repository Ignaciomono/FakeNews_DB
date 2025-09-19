"""
Punto de entrada principal para la aplicación Fake News Detector - Vercel
"""

try:
    # Importar la aplicación FastAPI para Vercel
    from app.main import app
    print("✅ App importada correctamente")
except Exception as e:
    print(f"❌ Error importando app: {e}")
    # Crear una app mínima como fallback
    from fastapi import FastAPI
    app = FastAPI(
        title="Fake News Detector API",
        description="API para detección de fake news",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {"message": "Fake News Detector API", "status": "running", "docs": "/docs"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "API funcionando"}

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )