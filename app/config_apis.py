"""
Configuración de APIs externas de fact-checking
"""
import os
from typing import Optional

class APIConfig:
    """Configuración centralizada para todas las APIs de fact-checking"""
    
    # Google Fact Check Tools API
    GOOGLE_FACT_CHECK_API_KEY: Optional[str] = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
    GOOGLE_FACT_CHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    # ClaimBuster API
    CLAIMBUSTER_API_KEY: Optional[str] = os.getenv("CLAIMBUSTER_API_KEY")
    CLAIMBUSTER_URL = "https://idir.uta.edu/claimbuster/api/v2/score/text/"
    
    # WordLift Fact-Checking API
    WORDLIFT_API_KEY: Optional[str] = os.getenv("WORDLIFT_API_KEY")
    WORDLIFT_URL = "https://api.wordlift.io/fact-check/v1"
    
    # Media Bias / Fact Check (MBFC) Data API
    MBFC_API_KEY: Optional[str] = os.getenv("MBFC_API_KEY")
    MBFC_URL = "https://api.mediabiasfactcheck.com/v1"
    
    # Fake News Detection (RapidAPI)
    RAPIDAPI_KEY: Optional[str] = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST = "fake-news-detector1.p.rapidapi.com"
    RAPIDAPI_URL = f"https://{RAPIDAPI_HOST}/api/v1/detect"
    
    # Timeouts y configuración general
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    @classmethod
    def is_google_configured(cls) -> bool:
        """Verificar si Google API está configurada"""
        return cls.GOOGLE_FACT_CHECK_API_KEY is not None
    
    @classmethod
    def is_claimbuster_configured(cls) -> bool:
        """Verificar si ClaimBuster API está configurada"""
        return cls.CLAIMBUSTER_API_KEY is not None
    
    @classmethod
    def is_wordlift_configured(cls) -> bool:
        """Verificar si WordLift API está configurada"""
        return cls.WORDLIFT_API_KEY is not None
    
    @classmethod
    def is_mbfc_configured(cls) -> bool:
        """Verificar si MBFC API está configurada"""
        return cls.MBFC_API_KEY is not None
    
    @classmethod
    def is_rapidapi_configured(cls) -> bool:
        """Verificar si RapidAPI está configurada"""
        return cls.RAPIDAPI_KEY is not None
    
    @classmethod
    def get_configured_apis(cls) -> list[str]:
        """Obtener lista de APIs configuradas"""
        apis = []
        if cls.is_google_configured():
            apis.append("google_fact_check")
        if cls.is_claimbuster_configured():
            apis.append("claimbuster")
        if cls.is_wordlift_configured():
            apis.append("wordlift")
        if cls.is_mbfc_configured():
            apis.append("mbfc")
        if cls.is_rapidapi_configured():
            apis.append("rapidapi")
        return apis

api_config = APIConfig()