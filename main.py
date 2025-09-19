"""
Punto de entrada principal para la aplicación Fake News Detector - Vercel
"""

# Usar versión mejorada que funciona en Vercel
from app.main_enhanced import app

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )