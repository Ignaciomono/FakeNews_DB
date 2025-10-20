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
from app.services.ai_analyzer import ai_analyzer
from app.utils.content_extractor import content_extractor
from app.utils.security import security_utils, rate_limiter

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
        
        # Ejecutar análisis de IA
        score, label, confidence, analysis_time_ms = await ai_analyzer.analyze_text(content)
        
        # Obtener información del modelo
        model_info = await ai_analyzer.get_model_info()
        
        # Guardar en base de datos
        analysis = NewsAnalysis(
            content=content,
            source_type=source_type.value,
            source_url=source_url,
            file_name=file_name,
            score=score,
            label=label.value,
            confidence=confidence,
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