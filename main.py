"""
Punto de entrada principal para la aplicación Fake News Detector - Vercel
"""

# Usar versión mínima para debugging
from app.main_minimal import app

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )