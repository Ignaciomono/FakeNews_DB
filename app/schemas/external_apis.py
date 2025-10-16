"""
Schemas para las APIs externas de fact-checking
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GoogleFactCheckRequest(BaseModel):
    """Request para Google Fact Check API"""
    query: str = Field(..., description="Texto del claim a verificar")
    language_code: str = Field(default="en", description="Código de idioma (ej: en, es)")


class ClaimBusterRequest(BaseModel):
    """Request para ClaimBuster API"""
    text: str = Field(..., description="Texto a analizar para verificabilidad")


class WordLiftRequest(BaseModel):
    """Request para WordLift API"""
    text: str = Field(..., description="Texto a verificar hechos")


class MBFCRequest(BaseModel):
    """Request para MBFC API"""
    url: str = Field(..., description="URL de la fuente a verificar")


class RapidAPIRequest(BaseModel):
    """Request para RapidAPI Fake News Detection"""
    text: str = Field(..., description="Contenido del artículo")
    title: str = Field(default="", description="Título del artículo (opcional)")


class MultiAPIRequest(BaseModel):
    """Request para análisis con múltiples APIs"""
    text: str = Field(..., description="Texto a analizar")
    url: Optional[str] = Field(None, description="URL de la fuente (opcional)")
    title: Optional[str] = Field(None, description="Título (opcional)")
    apis: List[str] = Field(
        default=["all"],
        description="APIs a usar: google, claimbuster, wordlift, mbfc, rapidapi, o 'all'"
    )


class APIStatus(BaseModel):
    """Estado de configuración de las APIs"""
    google_fact_check: bool
    claimbuster: bool
    wordlift: bool
    mbfc: bool
    rapidapi: bool
    configured_apis: List[str]


class FactCheckResult(BaseModel):
    """Resultado genérico de fact-checking"""
    success: bool
    api: str
    data: Dict[str, Any]
    error: Optional[str] = None


class MultiAPIResult(BaseModel):
    """Resultado de análisis con múltiples APIs"""
    text: str
    results: Dict[str, Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: float