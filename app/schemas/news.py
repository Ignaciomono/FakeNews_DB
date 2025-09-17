from pydantic import BaseModel, Field, validator
from typing import Optional, Union, Literal
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    TEXT = "text"
    URL = "url" 
    FILE = "file"

class AnalysisLabel(str, Enum):
    REAL = "REAL"
    FAKE = "FAKE"
    UNCERTAIN = "UNCERTAIN"

# Schemas de entrada (request)
class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000, description="Texto a analizar")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('El texto no puede estar vacío')
        return v.strip()

class AnalyzeUrlRequest(BaseModel):
    url: str = Field(..., description="URL de la noticia a analizar")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('La URL debe comenzar con http:// o https://')
        return v

# Schema unificado para análisis
class AnalyzeRequest(BaseModel):
    source_type: SourceType
    content: Optional[str] = None  # Para texto directo
    url: Optional[str] = None      # Para URLs
    # file será manejado por FastAPI directamente

    @validator('content')
    def validate_content(cls, v, values):
        if values.get('source_type') == SourceType.TEXT and not v:
            raise ValueError('El contenido es requerido para análisis de texto')
        return v
    
    @validator('url')
    def validate_url_field(cls, v, values):
        if values.get('source_type') == SourceType.URL and not v:
            raise ValueError('La URL es requerida para análisis de URL')
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('La URL debe comenzar con http:// o https://')
        return v

# Schemas de salida (response)
class AnalysisResult(BaseModel):
    id: int
    score: float = Field(..., ge=0.0, le=1.0, description="Score de 0.0 (fake) a 1.0 (real)")
    label: AnalysisLabel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza del modelo")
    model_version: str
    analysis_time_ms: Optional[int]
    content_length: int
    source_type: SourceType
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisMetricsResponse(BaseModel):
    word_count: Optional[int]
    sentence_count: Optional[int]
    readability_score: Optional[float]
    extraction_success: bool
    extraction_method: Optional[str]
    
    class Config:
        from_attributes = True

class DetailedAnalysisResult(AnalysisResult):
    content: str
    source_url: Optional[str]
    file_name: Optional[str]
    metrics: Optional[AnalysisMetricsResponse]

# Schemas para métricas y estadísticas
class SummaryMetrics(BaseModel):
    total_analyses: int
    fake_count: int
    real_count: int
    uncertain_count: int
    fake_percentage: float
    real_percentage: float
    uncertain_percentage: float
    avg_score: Optional[float]
    avg_confidence: Optional[float]
    
    # Métricas por fuente
    text_analyses: int
    url_analyses: int
    file_analyses: int

class TimeseriesDataPoint(BaseModel):
    date: str  # YYYY-MM-DD
    total_analyses: int
    fake_count: int
    real_count: int
    uncertain_count: int
    avg_score: Optional[float]
    avg_confidence: Optional[float]

class TimeseriesResponse(BaseModel):
    data: list[TimeseriesDataPoint]
    period_days: int
    total_points: int

# Schema para estado del sistema
class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    database: bool
    ai_model: bool
    web_extractor: bool
    timestamp: datetime
    version: str = "1.0.0"
    uptime_seconds: Optional[int]

# Schema para registro de modelos
class ModelRegistryResponse(BaseModel):
    id: int
    model_name: str
    model_version: str
    model_type: str
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]
    
    class Config:
        from_attributes = True