from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import time
import logging

from app.database import get_db
from app.schemas.news import (
    AnalyzeRequest, AnalysisResult, DetailedAnalysisResult,
    SourceType, AnalysisLabel
)
from app.models.news import NewsAnalysis, AnalysisMetric
from app.services.ai_analyzer import ai_analyzer
from app.services.entity_verifier import entity_verifier
from app.services.external_apis import ExternalAPIsService
from app.services.news_api_service import news_api_service
from app.utils.content_extractor import content_extractor
from app.utils.security import security_utils, rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analysis"])

@router.post("/", response_model=AnalysisResult)
async def analyze_content(
    request: Request,
    db: AsyncSession = Depends(get_db),
    # Parámetros opcionales para diferentes tipos de análisis
    text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Analiza contenido de diferentes fuentes para detectar fake news.
    
    Acepta uno de los siguientes:
    - text: Texto directo para analizar
    - url: URL de un artículo de noticias
    - file: Archivo de texto (.txt, .docx, .pdf)
    """
    
    # Rate limiting
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Intenta nuevamente más tarde."
        )
    
    # Validar que se proporcione exactamente una fuente
    sources_provided = sum([bool(text), bool(url), bool(file)])
    if sources_provided != 1:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar exactamente una fuente: text, url, o file"
        )
    
    try:
        # Determinar tipo de fuente y extraer contenido
        if text:
            content, source_type = await _process_text(text)
            source_url = None
            file_name = None
            
        elif url:
            content, source_type = await _process_url(url)
            source_url = url
            file_name = None
            
        elif file:
            content, source_type = await _process_file(file)
            source_url = None
            file_name = file.filename
        
        # Validar contenido extraído
        if not content or len(content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer contenido suficiente para análisis"
            )
        
        # PASO 1: Verificación con NER (entidades conocidas) + Wikipedia API - PRIORIDAD ALTA
        ner_result = await entity_verifier.verify_claim(content)
        
        # PASO 2: Google Fact Check API (verificación externa) - PRIORIDAD MEDIA
        fact_check_result = None
        try:
            external_api_service = ExternalAPIsService()
            fact_check_result = await external_api_service.check_with_google_factcheck(content[:500])  # Límite de 500 chars
            if fact_check_result and fact_check_result.get("claims"):
                logger.info(f"Google Fact Check encontró {len(fact_check_result['claims'])} resultados")
        except Exception as e:
            logger.warning(f"Error en Google Fact Check: {e}")
        
        # PASO 3: NewsAPI - Buscar noticias recientes (para claims políticos/actuales)
        news_result = None
        try:
            # Extraer personas del NER para búsqueda más precisa
            person_name = None
            if ner_result and ner_result.get("entities", {}).get("persons"):
                person_name = ner_result["entities"]["persons"][0]
            
            news_result = await news_api_service.verify_political_claim(content[:100], person_name)
            if news_result and news_result.get("found_articles"):
                logger.info(f"📰 NewsAPI encontró {news_result.get('total_results', 0)} artículos")
        except Exception as e:
            logger.warning(f"Error en NewsAPI: {e}")
        
        # PASO 4: Análisis con modelos de IA (sentimiento/patrones) - FALLBACK
        score, label, confidence, analysis_time_ms = await ai_analyzer.analyze_text(content)
        
        # PASO 5: Combinar resultados NER + Fact Check + NewsAPI + AI
        final_score = score
        final_label = label
        final_confidence = confidence
        verification_method = "AI_MODELS"
        verification_sources = []
        
        # Prioridad 1: NER tiene un veredicto claro
        if ner_result and ner_result.get("overall_verdict") is not None:
            verification_method = "NER_ENTITIES"
            verification_sources.append("entity_verification")
            
            if ner_result["overall_verdict"] == "fake":
                final_score = 0.0 + (ner_result["confidence"] * 0.1)  # 0.0 - 0.1 range
                final_label = AnalysisLabel.FAKE
                final_confidence = ner_result["confidence"]
                logger.info(f"✅ NER detectó FAKE: {ner_result.get('explanation', 'Sin explicación')}")
                
            elif ner_result["overall_verdict"] == "real":
                final_score = 0.9 + (ner_result["confidence"] * 0.1)  # 0.9 - 1.0 range
                final_label = AnalysisLabel.REAL
                final_confidence = ner_result["confidence"]
                logger.info(f"✅ NER detectó REAL: {ner_result.get('explanation', 'Sin explicación')}")
            
            elif ner_result["overall_verdict"] == "needs_verification":
                # Claim político controversial sin fuente - requiere verificación externa
                verification_method = "POLITICAL_CLAIM_UNVERIFIED"
                verification_sources.append("political_detector")
                
                # Intentar verificar con NewsAPI o Fact Check
                if news_result and news_result.get("found_articles") and news_result.get("relevant_articles", 0) > 0:
                    # NewsAPI encontró artículos relevantes
                    verdict = news_result.get("verdict", "uncertain")
                    if verdict == "likely_true":
                        final_score = 0.70
                        final_label = AnalysisLabel.REAL
                        final_confidence = 0.75
                        verification_method = "POLITICAL_CLAIM_NEWS"
                        verification_sources.append("newsapi")
                    elif verdict == "possibly_true":
                        final_score = 0.55
                        final_label = AnalysisLabel.UNCERTAIN
                        final_confidence = 0.60
                        verification_method = "POLITICAL_CLAIM_NEWS"
                        verification_sources.append("newsapi")
                    else:
                        final_score = 0.50
                        final_label = AnalysisLabel.UNCERTAIN
                        final_confidence = 0.55
                else:
                    # Sin verificación externa - marcar como UNCERTAIN con baja confianza
                    final_score = 0.50
                    final_label = AnalysisLabel.UNCERTAIN
                    final_confidence = 0.50
                    logger.info(f"⚠️ Claim político sin verificar: {ner_result.get('explanation', 'Sin fuente')}")
        
        # Prioridad 2: Google Fact Check tiene resultados
        elif fact_check_result and fact_check_result.get("claims"):
            verification_method = "FACT_CHECK_API"
            verification_sources.append("google_factcheck")
            
            # Analizar el primer claim encontrado
            first_claim = fact_check_result["claims"][0]
            claim_review = first_claim.get("claimReview", [{}])[0]
            
            rating = claim_review.get("textualRating", "").lower()
            
            # Mapear ratings de Fact Check a nuestro sistema
            if any(word in rating for word in ["false", "falso", "fake", "incorrecto"]):
                final_score = 0.1
                final_label = AnalysisLabel.FAKE
                final_confidence = 0.85
                logger.info(f"✅ Fact Check detectó FAKE: {rating}")
            elif any(word in rating for word in ["true", "verdadero", "correcto", "verified"]):
                final_score = 0.9
                final_label = AnalysisLabel.REAL
                final_confidence = 0.85
                logger.info(f"✅ Fact Check detectó REAL: {rating}")
            else:
                # Rating mixto o incierto
                final_score = 0.5
                final_label = AnalysisLabel.UNCERTAIN
                final_confidence = 0.65
                logger.info(f"⚠️ Fact Check incierto: {rating}")
        
        # Prioridad 3: NewsAPI tiene artículos relevantes
        elif news_result and news_result.get("found_articles"):
            verification_method = "NEWS_API"
            verification_sources.append("newsapi")
            
            verdict = news_result.get("verdict", "uncertain")
            news_confidence = news_result.get("confidence", 0.5)
            
            if verdict == "likely_true":
                final_score = 0.75
                final_label = AnalysisLabel.REAL
                final_confidence = news_confidence
                logger.info(f"📰 NewsAPI: Claim probablemente verdadero ({news_result.get('relevant_articles', 0)} artículos)")
            elif verdict == "possibly_true":
                final_score = 0.60
                final_label = AnalysisLabel.UNCERTAIN
                final_confidence = news_confidence
                logger.info(f"📰 NewsAPI: Claim posiblemente verdadero (requiere más verificación)")
            else:
                final_score = 0.50
                final_label = AnalysisLabel.UNCERTAIN
                final_confidence = news_confidence
                logger.info(f"📰 NewsAPI: Noticias encontradas pero sin conclusión clara")
        
        # Prioridad 4: Fallback a modelos AI
        else:
            verification_sources.append("ai_models")
            logger.info("⚠️ NER, Fact Check y NewsAPI sin resultados, usando modelos AI")
        
        # Obtener información del modelo
        model_info = await ai_analyzer.get_model_info()
        
        # Guardar en base de datos
        analysis = NewsAnalysis(
            content=content,
            source_type=source_type.value,
            source_url=source_url,
            file_name=file_name,
            score=final_score,
            label=final_label.value,
            confidence=final_confidence,
            model_version=model_info.get("model_name", "unknown"),
            analysis_time_ms=analysis_time_ms,
            content_length=len(content)
        )
        
        db.add(analysis)
        await db.flush()  # Para obtener el ID
        
        # Crear métricas adicionales
        metrics = AnalysisMetric(
            analysis_id=analysis.id,
            word_count=len(content.split()),
            sentence_count=content.count('.') + content.count('!') + content.count('?'),
            extraction_success=True,
            extraction_method="direct" if source_type == SourceType.TEXT else "extraction"
        )
        
        db.add(metrics)
        await db.commit()
        
        logger.info(f"Análisis completado - ID: {analysis.id}, Label: {label.value}, Score: {score:.3f}")
        
        return AnalysisResult(
            id=analysis.id,
            score=score,
            label=label,
            confidence=confidence,
            model_version=model_info.get("model_name", "unknown"),
            analysis_time_ms=analysis_time_ms,
            content_length=len(content),
            source_type=source_type,
            created_at=analysis.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor durante el análisis"
        )

@router.get("/{analysis_id}", response_model=DetailedAnalysisResult)
async def get_analysis_details(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los detalles completos de un análisis específico"""
    
    try:
        # Buscar análisis con métricas
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        
        result = await db.execute(
            select(NewsAnalysis)
            .options(selectinload(NewsAnalysis.metrics))
            .where(NewsAnalysis.id == analysis_id)
        )
        
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Análisis con ID {analysis_id} no encontrado"
            )
        
        # Construir respuesta con métricas
        metrics_data = None
        if analysis.metrics:
            metric = analysis.metrics[0]  # Debería haber solo una métrica por análisis
            metrics_data = {
                "word_count": metric.word_count,
                "sentence_count": metric.sentence_count,
                "readability_score": metric.readability_score,
                "extraction_success": metric.extraction_success,
                "extraction_method": metric.extraction_method
            }
        
        return DetailedAnalysisResult(
            id=analysis.id,
            score=analysis.score,
            label=AnalysisLabel(analysis.label),
            confidence=analysis.confidence,
            model_version=analysis.model_version,
            analysis_time_ms=analysis.analysis_time_ms,
            content_length=analysis.content_length,
            source_type=SourceType(analysis.source_type),
            created_at=analysis.created_at,
            content=analysis.content,
            source_url=analysis.source_url,
            file_name=analysis.file_name,
            metrics=metrics_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles del análisis {analysis_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

# Funciones auxiliares

async def _process_text(text: str) -> tuple[str, SourceType]:
    """Procesa y valida texto directo"""
    
    # Sanitizar texto
    clean_text = security_utils.sanitize_text(text)
    
    # Validar longitud
    if not security_utils.validate_content_length(clean_text):
        raise HTTPException(
            status_code=400,
            detail=f"Texto muy largo. Máximo {security_utils.settings.MAX_CONTENT_LENGTH} caracteres."
        )
    
    return clean_text, SourceType.TEXT

async def _process_url(url: str) -> tuple[str, SourceType]:
    """Procesa y extrae contenido de URL"""
    
    # Validar URL
    if not content_extractor.validate_url(url):
        raise HTTPException(
            status_code=400,
            detail="URL no válida o no permitida"
        )
    
    # Extraer contenido
    content, method, success = await content_extractor.extract_from_url(url)
    
    if not success or not content:
        raise HTTPException(
            status_code=400,
            detail="No se pudo extraer contenido de la URL proporcionada"
        )
    
    # Sanitizar contenido extraído
    clean_content = security_utils.sanitize_text(content)
    
    return clean_content, SourceType.URL

async def _process_file(file: UploadFile) -> tuple[str, SourceType]:
    """Procesa y extrae contenido de archivo"""
    
    # Validar archivo
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nombre de archivo requerido"
        )
    
    if not security_utils.is_safe_filename(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Nombre de archivo no válido"
        )
    
    if not security_utils.allowed_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Use: .txt, .doc, .docx, .pdf, .rtf"
        )
    
    # Leer contenido del archivo
    try:
        file_content = await file.read()
        
        # Validar tamaño
        if not security_utils.validate_file_size(len(file_content)):
            raise HTTPException(
                status_code=400,
                detail=f"Archivo muy grande. Máximo {security_utils.settings.MAX_FILE_SIZE_MB} MB."
            )
        
        # Por ahora, solo procesamos archivos de texto plano
        # En producción, agregarías parsers para DOC, PDF, etc.
        if file.filename.lower().endswith('.txt'):
            content = file_content.decode('utf-8', errors='ignore')
        else:
            raise HTTPException(
                status_code=400,
                detail="Por ahora solo se soportan archivos .txt"
            )
        
        # Sanitizar contenido
        clean_content = security_utils.sanitize_text(content)
        
        if len(clean_content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="El archivo no contiene suficiente texto para análisis"
            )
        
        return clean_content, SourceType.FILE
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="No se pudo leer el archivo. Asegúrese de que esté en formato UTF-8."
        )
    except Exception as e:
        logger.error(f"Error procesando archivo: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error procesando archivo"
        )