"""
Router para endpoints de APIs externas de fact-checking
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time

from app.schemas.external_apis import (
    GoogleFactCheckRequest,
    ClaimBusterRequest,
    WordLiftRequest,
    MBFCRequest,
    RapidAPIRequest,
    MultiAPIRequest,
    APIStatus
)
from app.services.external_apis import (
    google_fact_check_service,
    claimbuster_service,
    wordlift_service,
    mbfc_service,
    rapidapi_service
)
from app.config_apis import api_config

router = APIRouter(prefix="/fact-check", tags=["External Fact-Checking APIs"])


@router.get("/status", response_model=APIStatus)
async def get_apis_status():
    """
    Obtener estado de configuración de todas las APIs externas
    
    Retorna qué APIs están configuradas y listas para usar
    """
    return {
        "google_fact_check": api_config.is_google_configured(),
        "claimbuster": api_config.is_claimbuster_configured(),
        "wordlift": api_config.is_wordlift_configured(),
        "mbfc": api_config.is_mbfc_configured(),
        "rapidapi": api_config.is_rapidapi_configured(),
        "configured_apis": api_config.get_configured_apis()
    }


@router.post("/google")
async def google_fact_check(request: GoogleFactCheckRequest) -> Dict[str, Any]:
    """
    Verificar claims usando Google Fact Check Tools API
    
    - **query**: Texto del claim a verificar
    - **language_code**: Código de idioma (default: en)
    
    **Requiere**: Variable de entorno `GOOGLE_FACT_CHECK_API_KEY`
    """
    result = await google_fact_check_service.check_claim(
        query=request.query,
        language_code=request.language_code
    )
    
    if not result.get("success", False) and result.get("configured") == False:
        raise HTTPException(status_code=503, detail=result.get("message"))
    
    return result


@router.post("/claimbuster")
async def claimbuster_score(request: ClaimBusterRequest) -> Dict[str, Any]:
    """
    Obtener score de verificabilidad con ClaimBuster API
    
    - **text**: Texto a analizar
    
    ClaimBuster analiza qué tan "verificable" es un claim (0-1 score)
    
    **Requiere**: Variable de entorno `CLAIMBUSTER_API_KEY`
    """
    result = await claimbuster_service.score_text(text=request.text)
    
    if not result.get("success", False) and result.get("configured") == False:
        raise HTTPException(status_code=503, detail=result.get("message"))
    
    return result


@router.post("/wordlift")
async def wordlift_fact_check(request: WordLiftRequest) -> Dict[str, Any]:
    """
    Verificar hechos usando WordLift Fact-Checking API
    
    - **text**: Texto a verificar
    
    WordLift analiza hechos y proporciona verificación semántica
    
    **Requiere**: Variable de entorno `WORDLIFT_API_KEY`
    """
    result = await wordlift_service.fact_check(text=request.text)
    
    if not result.get("success", False) and result.get("configured") == False:
        raise HTTPException(status_code=503, detail=result.get("message"))
    
    return result


@router.post("/mbfc")
async def mbfc_check_source(request: MBFCRequest) -> Dict[str, Any]:
    """
    Verificar sesgo y credibilidad de una fuente con MBFC API
    
    - **url**: URL de la fuente a verificar
    
    Media Bias/Fact Check proporciona información sobre:
    - Sesgo político
    - Credibilidad de la fuente
    - Precisión factual
    
    **Requiere**: Variable de entorno `MBFC_API_KEY`
    """
    result = await mbfc_service.check_source(url=request.url)
    
    if not result.get("success", False) and result.get("configured") == False:
        raise HTTPException(status_code=503, detail=result.get("message"))
    
    return result


@router.post("/rapidapi")
async def rapidapi_detect(request: RapidAPIRequest) -> Dict[str, Any]:
    """
    Detectar fake news usando RapidAPI Fake News Detection
    
    - **text**: Contenido del artículo
    - **title**: Título del artículo (opcional)
    
    Usa modelos de ML para detectar fake news
    
    **Requiere**: Variable de entorno `RAPIDAPI_KEY`
    """
    result = await rapidapi_service.detect_fake_news(
        text=request.text,
        title=request.title
    )
    
    if not result.get("success", False) and result.get("configured") == False:
        raise HTTPException(status_code=503, detail=result.get("message"))
    
    return result


@router.post("/multi-check")
async def multi_api_check(request: MultiAPIRequest) -> Dict[str, Any]:
    """
    Analizar con múltiples APIs simultáneamente
    
    - **text**: Texto a analizar
    - **url**: URL de la fuente (opcional)
    - **title**: Título (opcional)
    - **apis**: Lista de APIs a usar ["google", "claimbuster", "wordlift", "mbfc", "rapidapi"] o ["all"]
    
    Ejecuta fact-checking en múltiples APIs y agrega resultados
    """
    results = {}
    apis_to_use = request.apis
    
    # Si se especifica "all", usar todas las APIs configuradas
    if "all" in apis_to_use:
        apis_to_use = api_config.get_configured_apis()
    
    # Google Fact Check
    if "google" in apis_to_use or "google_fact_check" in apis_to_use:
        if api_config.is_google_configured():
            results["google"] = await google_fact_check_service.check_claim(
                query=request.text
            )
    
    # ClaimBuster
    if "claimbuster" in apis_to_use:
        if api_config.is_claimbuster_configured():
            results["claimbuster"] = await claimbuster_service.score_text(
                text=request.text
            )
    
    # WordLift
    if "wordlift" in apis_to_use:
        if api_config.is_wordlift_configured():
            results["wordlift"] = await wordlift_service.fact_check(
                text=request.text
            )
    
    # MBFC (solo si se proporciona URL)
    if ("mbfc" in apis_to_use) and request.url:
        if api_config.is_mbfc_configured():
            results["mbfc"] = await mbfc_service.check_source(
                url=request.url
            )
    
    # RapidAPI
    if "rapidapi" in apis_to_use:
        if api_config.is_rapidapi_configured():
            results["rapidapi"] = await rapidapi_service.detect_fake_news(
                text=request.text,
                title=request.title or ""
            )
    
    # Crear resumen
    summary = {
        "total_apis_used": len(results),
        "apis_called": list(results.keys()),
        "successful_calls": len([r for r in results.values() if r.get("success", False)]),
        "failed_calls": len([r for r in results.values() if not r.get("success", False)])
    }
    
    return {
        "text": request.text,
        "url": request.url,
        "results": results,
        "summary": summary,
        "timestamp": time.time()
    }