import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fakenews_db")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fake-news-secret-key-change-in-production")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # AI Model settings
    AI_MODEL_NAME: str = "martin-ha/toxic-comment-model"  # Modelo para empezar
    AI_MODEL_BACKUP: str = "unitary/toxic-bert"  # Modelo de respaldo
    
    # Content extraction settings
    REQUEST_TIMEOUT: int = 30
    MAX_CONTENT_LENGTH: int = 50000  # caracteres
    
    class Config:
        case_sensitive = True

settings = Settings()