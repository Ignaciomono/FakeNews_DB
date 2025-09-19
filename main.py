"""
Punto de entrada principal para la aplicación Fake News Detector
"""

# Importar la aplicación FastAPI para Vercel
from app.main import app

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )