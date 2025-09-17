from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class NewsAnalysis(Base):
    """Tabla para almacenar los análisis de noticias"""
    __tablename__ = "news_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # Contenido analizado
    source_type = Column(String(20), nullable=False)  # 'text', 'url', 'file'
    source_url = Column(String(500), nullable=True)  # URL si aplica
    file_name = Column(String(255), nullable=True)  # Nombre del archivo si aplica
    
    # Resultados del análisis
    score = Column(Float, nullable=False)  # Score de 0.0 a 1.0
    label = Column(String(50), nullable=False)  # 'REAL', 'FAKE', 'UNCERTAIN'
    confidence = Column(Float, nullable=False)  # Confianza del modelo
    
    # Metadatos
    model_version = Column(String(100), nullable=False)
    analysis_time_ms = Column(Integer, nullable=True)  # Tiempo de procesamiento en ms
    content_length = Column(Integer, nullable=False)  # Longitud del contenido
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con métricas
    metrics = relationship("AnalysisMetric", back_populates="analysis")


class ModelRegistry(Base):
    """Registro de modelos de IA utilizados"""
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(200), nullable=False, unique=True)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'huggingface', 'custom'
    is_active = Column(Boolean, default=False)
    
    # Configuración del modelo
    model_config = Column(Text, nullable=True)  # JSON con configuración
    performance_metrics = Column(Text, nullable=True)  # JSON con métricas de rendimiento
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)


class AnalysisMetric(Base):
    """Métricas adicionales por análisis"""
    __tablename__ = "analysis_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("news_analyses.id"))
    
    # Métricas adicionales
    word_count = Column(Integer, nullable=True)
    sentence_count = Column(Integer, nullable=True)
    readability_score = Column(Float, nullable=True)
    
    # Metadatos de extracción (para URLs)
    extraction_success = Column(Boolean, default=True)
    extraction_method = Column(String(50), nullable=True)  # 'newspaper', 'beautifulsoup'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación
    analysis = relationship("NewsAnalysis", back_populates="metrics")


class DailyStats(Base):
    """Estadísticas diarias agregadas"""
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, unique=True)
    
    # Contadores
    total_analyses = Column(Integer, default=0)
    fake_count = Column(Integer, default=0)
    real_count = Column(Integer, default=0)
    uncertain_count = Column(Integer, default=0)
    
    # Métricas de fuente
    text_analyses = Column(Integer, default=0)
    url_analyses = Column(Integer, default=0)
    file_analyses = Column(Integer, default=0)
    
    # Métricas de rendimiento
    avg_score = Column(Float, nullable=True)
    avg_confidence = Column(Float, nullable=True)
    avg_processing_time_ms = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())