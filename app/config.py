import os

# No usar dotenv en producción para evitar problemas
if os.getenv("VERCEL") != "1":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fakenews_db")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fake-news-secret-key-change-in-production")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    # Configuración de CORS más permisiva para producción
    _cors_origins = os.getenv("CORS_ORIGINS", "*")
    CORS_ORIGINS: list = _cors_origins.split(",") if _cors_origins != "*" else ["*"]
    
    # AI External API settings (Hugging Face Inference API - Free)
    HF_API_URL: str = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/")
    HF_MODEL_NAME: str = os.getenv("HF_MODEL_NAME", "hamzab/roberta-fake-news-classification")
    HF_FALLBACK_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"  # Modelo de respaldo
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")  # Token opcional (rate limits más altos)
    
    # Content extraction settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "50000"))
    
    # API Rate limiting
    REQUESTS_PER_MINUTE: int = int(os.getenv("REQUESTS_PER_MINUTE", "60"))
    
    class Config:
        case_sensitive = True

settings = Settings()