# Importar la Base desde el módulo de base de datos
from app.database import Base

# Importar cada modelo individualmente
from .news import NewsAnalysis, ModelRegistry, AnalysisMetric, DailyStats
from .user import User
