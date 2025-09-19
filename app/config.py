import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fakenews_db")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fake-news-secret-key-change-in-production")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # AI External API settings (Hugging Face Inference API - Free)
    HF_API_URL: str = "https://api-inference.huggingface.co/models/"
    HF_MODEL_NAME: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"  # Modelo gratuito para sentiment
    HF_FALLBACK_MODEL: str = "microsoft/DialoGPT-medium"  # Modelo de respaldo
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")  # Token opcional (rate limits más altos)
    
    # Content extraction settings
    REQUEST_TIMEOUT: int = 30
    MAX_CONTENT_LENGTH: int = 50000  # caracteres
    
    # API Rate limiting
    REQUESTS_PER_MINUTE: int = 60  # Para uso gratuito de HF
    
    class Config:
        case_sensitive = True

settings = Settings()