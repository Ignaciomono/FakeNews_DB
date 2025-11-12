from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union
import time
import logging

from app.database import get_db
from app.schemas.news import (
    AnalyzeRequest, AnalysisResult, DetailedAnalysisResult,
    SourceType, AnalysisLabel
)
from app.models.news import NewsAnalysis, AnalysisMetric
from app.services.ai_analyzer import ai_analyzer, FakeNewsLabel
from app.services.entity_verifier import entity_verifier
from app.services.external_apis import ExternalAPIsService
from app.services.news_api_service import news_api_service
from app.utils.content_extractor import content_extractor
from app.utils.security import security_utils, rate_limiter
from app.utils.text_analyzer import text_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analysis"])

@router.post("/", response_model=AnalysisResult)
async def analyze_content(
    request: Request,
    db: AsyncSession = Depends(get_db),
    # Parámetros opcionales para diferentes tipos de análisis
    text: Optional[str] = Form(default=None),
    url: Optional[str] = Form(default=None),
    file: Union[UploadFile, str, None] = File(default=None)
):
    """
    Analiza contenido de diferentes fuentes para detectar fake news.
    
    Acepta uno de los siguientes:
    - text: Texto directo para analizar
    - url: URL de un artículo de noticias
    - file: Archivo de texto (.txt, .docx, .pdf)
    
    Acepta tanto Form-data como JSON.
    """
    
    # Normalizar valores vacíos a None
    if text is not None and (text.strip() == "" or text.strip().lower() == "string"):
        text = None
    if url is not None and (url.strip() == "" or url.strip().lower() == "string"):
        url = None
    if file is not None and (not hasattr(file, 'filename') or not file.filename):
        file = None
    
    # Si no se recibieron parámetros de Form, intentar leer JSON del body
    if not any([text, url, file]):
        try:
            body = await request.json()
            text = body.get("text")
            url = body.get("url")
            # Normalizar de nuevo después de leer JSON
            if text and text.strip() == "":
                text = None
            if url and url.strip() == "":
                url = None
        except:
            pass
    
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
            fact_check_result = await external_api_service.check_with_google_factcheck(content[:500])
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
        
        # PASO 4: Análisis de IA (fallback)
        score, ai_label, confidence, analysis_time_ms = await ai_analyzer.analyze_text(content)
        
        # PASO 5: Combinar resultados NER + Fact Check + NewsAPI + AI
        final_score = score
        final_label = ai_label
        final_confidence = confidence
        verification_method = "AI_MODELS"
        verification_sources = []
        
        # Prioridad 1: NER tiene un veredicto claro
        if ner_result and ner_result.get("overall_verdict") is not None:
            
            if ner_result["overall_verdict"] == "fake":
                verification_method = "NER_ENTITIES"
                verification_sources.append("entity_verification")
                final_score = 0.0 + (ner_result["confidence"] * 0.1)
                final_label = FakeNewsLabel.FAKE
                final_confidence = ner_result["confidence"]
                logger.info(f"✅ NER detectó FAKE: {ner_result.get('explanation', 'Sin explicación')}")
                
            elif ner_result["overall_verdict"] == "real":
                verification_method = "NER_ENTITIES"
                verification_sources.append("entity_verification")
                final_score = 0.9 + (ner_result["confidence"] * 0.1)
                final_label = FakeNewsLabel.REAL
                final_confidence = ner_result["confidence"]
                logger.info(f"✅ NER detectó REAL: {ner_result.get('explanation', 'Sin explicación')}")
            
            elif ner_result["overall_verdict"] == "needs_verification":
                # Claim político controversial sin fuente
                verification_method = "POLITICAL_CLAIM_UNVERIFIED"
                verification_sources.append("political_detector")
                
                # Intentar verificar con NewsAPI
                if news_result and news_result.get("found_articles") and news_result.get("relevant_articles", 0) > 0:
                    verification_method = "POLITICAL_CLAIM_NEWS"
                    verification_sources.append("newsapi")
                    verdict = news_result.get("verdict", "uncertain")
                    
                    if verdict == "likely_true":
                        final_score = 0.70
                        final_label = FakeNewsLabel.REAL
                        final_confidence = 0.75
                    elif verdict == "possibly_true":
                        final_score = 0.55
                        final_label = FakeNewsLabel.UNCERTAIN
                        final_confidence = 0.60
                    else:
                        final_score = 0.50
                        final_label = FakeNewsLabel.UNCERTAIN
                        final_confidence = 0.55
                    
                    logger.info(f"📰 Claim político verificado con NewsAPI: {verdict}")
                else:
                    # Sin verificación externa - UNCERTAIN
                    final_score = 0.50
                    final_label = FakeNewsLabel.UNCERTAIN
                    final_confidence = 0.50
                    logger.info(f"⚠️ Claim político sin verificar: {ner_result.get('explanation', 'Sin fuente')}")
        
        # Prioridad 2: Google Fact Check tiene resultados
        elif fact_check_result and fact_check_result.get("claims"):
            verification_method = "FACT_CHECK_API"
            verification_sources.append("google_factcheck")
            
            first_claim = fact_check_result["claims"][0]
            claim_review = first_claim.get("claimReview", [{}])[0]
            rating = claim_review.get("textualRating", "").lower()
            
            if any(word in rating for word in ["false", "falso", "fake", "incorrecto"]):
                final_score = 0.1
                final_label = FakeNewsLabel.FAKE
                final_confidence = 0.85
                logger.info(f"✅ Fact Check detectó FAKE: {rating}")
            elif any(word in rating for word in ["true", "verdadero", "correcto", "verified"]):
                final_score = 0.9
                final_label = FakeNewsLabel.REAL
                final_confidence = 0.85
                logger.info(f"✅ Fact Check detectó REAL: {rating}")
            else:
                final_score = 0.5
                final_label = FakeNewsLabel.UNCERTAIN
                final_confidence = 0.65
                logger.info(f"⚠️ Fact Check incierto: {rating}")
        
        # Prioridad 3: NewsAPI tiene artículos relevantes
        elif news_result and news_result.get("found_articles") and news_result.get("relevant_articles", 0) > 0:
            verification_method = "NEWS_API"
            verification_sources.append("newsapi")
            verdict = news_result.get("verdict", "uncertain")
            
            if verdict == "likely_true":
                final_score = 0.75
                final_label = FakeNewsLabel.REAL
                final_confidence = 0.80
                logger.info(f"📰 NewsAPI: Claim probablemente verdadero")
            elif verdict == "possibly_true":
                final_score = 0.60
                final_label = FakeNewsLabel.UNCERTAIN
                final_confidence = 0.65
                logger.info(f"📰 NewsAPI: Claim posiblemente verdadero (requiere más verificación)")
            else:
                final_score = 0.50
                final_label = FakeNewsLabel.UNCERTAIN
                final_confidence = 0.55
                logger.info(f"📰 NewsAPI: Noticias encontradas pero sin conclusión clara")
        
        # 2. Análisis de características del texto
        features = text_analyzer.analyze(content)
        combined_score, feature_explanation = text_analyzer.get_recommendation(features, final_score)
        
        # 3. Generar warnings basados en características
        warnings = []
        if features.sensational_words > 3:
            warnings.append(f"Detectadas {features.sensational_words} palabras sensacionalistas")
        if features.clickbait_patterns > 0:
            warnings.append(f"Detectados {features.clickbait_patterns} patrones de clickbait")
        if features.caps_ratio > 0.3:
            warnings.append("Uso excesivo de MAYÚSCULAS")
        if features.exclamation_ratio > 2:
            warnings.append("Uso excesivo de signos de exclamación")
        if features.unverifiable_claims > 1:
            warnings.append(f"Detectadas {features.unverifiable_claims} afirmaciones no verificables")
        if features.extraordinary_claims > 0 and not features.has_sources:
            warnings.append(f"⚠️ CRÍTICO: Afirmaciones extraordinarias sin fuentes verificables detectadas")
        
        # Agregar explicación NER si existe
        if ner_result and ner_result.get("explanation"):
            warnings.insert(0, f"🔍 Verificación: {ner_result['explanation']}")
        
        # 4. Ajustar label final si es necesario
        if verification_method == "AI_MODELS":
            # Solo aplicar análisis de features si usamos AI
            if combined_score < 0.35:
                final_label = FakeNewsLabel.FAKE
            elif combined_score > 0.65:
                final_label = FakeNewsLabel.REAL
            else:
                final_label = FakeNewsLabel.UNCERTAIN
            final_score = combined_score
        
        # Obtener información del modelo
        model_info = await ai_analyzer.get_model_info()
        
        # Guardar en base de datos (usando score combinado)
        analysis = NewsAnalysis(
            content=content,
            source_type=source_type.value,
            source_url=source_url,
            file_name=file_name,
            score=final_score,  # Usar score final (NER/NewsAPI/AI)
            label=final_label.value,  # Usar label final
            confidence=final_confidence if verification_method != "AI_MODELS" else confidence,
            model_version=verification_method,  # Guardar método de verificación
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
        
        logger.info(f"Análisis completado - ID: {analysis.id}, Label: {final_label.value}, Combined Score: {combined_score:.3f}, AI Score: {score:.3f}")
        
        return AnalysisResult(
            id=analysis.id,
            score=final_score,  # Score final
            label=final_label,  # Label final
            confidence=final_confidence if verification_method != "AI_MODELS" else confidence,
            model_version=verification_method,  # Método de verificación usado
            analysis_time_ms=analysis_time_ms,
            content_length=len(content),
            source_type=source_type,
            combined_score=final_score,
            feature_analysis={
                "ai_score": score,
                "feature_score": features.feature_score if verification_method == "AI_MODELS" else None,
                "explanation": feature_explanation if verification_method == "AI_MODELS" else ner_result.get("explanation", ""),
                "verification_method": verification_method,
                "verification_sources": verification_sources,
                "sensational_words": features.sensational_words,
                "clickbait_patterns": features.clickbait_patterns,
                "caps_ratio": round(features.caps_ratio, 2),
                "exclamation_ratio": round(features.exclamation_ratio, 2),
                "has_sources": features.has_sources,
                "has_dates": features.has_dates
            },
            warnings=warnings if warnings else None,
            created_at=analysis.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en análisis: {type(e).__name__}: {str(e)}", exc_info=True)
        await db.rollback()
        
        # Devolver error más descriptivo
        error_detail = f"Error interno del servidor: {type(e).__name__}"
        if str(e):
            error_detail += f" - {str(e)}"
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
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