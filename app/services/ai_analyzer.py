try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

import asyncio
import time
import logging
import random
from typing import Tuple, Dict, Optional
from app.config import settings
from app.schemas.news import AnalysisLabel

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Servicio de análisis de IA para detección de fake news"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.model_name = settings.AI_MODEL_NAME
        self.backup_model = settings.AI_MODEL_BACKUP
        self.is_loaded = False
        self.model_version = "1.0.0"
    
    async def initialize(self):
        """Inicializa el modelo de IA"""
        if self.is_loaded:
            return
        
        # Si transformers no está disponible, usar directamente el mock
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers no disponible. Usando modelo MOCK para pruebas.")
            await self._load_mock_model()
            return
        
        try:
            logger.info(f"Cargando modelo principal: {self.model_name}")
            await self._load_model(self.model_name)
            
        except Exception as e:
            logger.error(f"Error cargando modelo principal: {e}")
            logger.info(f"Intentando cargar modelo de respaldo: {self.backup_model}")
            
            try:
                await self._load_model(self.backup_model)
                self.model_name = self.backup_model
                
            except Exception as e2:
                logger.error(f"Error cargando modelo de respaldo: {e2}")
                # Usar modelo mock como último recurso
                await self._load_mock_model()
    
    async def _load_model(self, model_name: str):
        """Carga un modelo específico"""
        loop = asyncio.get_event_loop()
        
        # Ejecutar la carga del modelo en un thread pool
        model_data = await loop.run_in_executor(
            None, 
            self._load_model_sync, 
            model_name
        )
        
        self.model = model_data['model']
        self.tokenizer = model_data['tokenizer'] 
        self.pipeline = model_data['pipeline']
        self.is_loaded = True
        
        logger.info(f"Modelo {model_name} cargado exitosamente")
    
    def _load_model_sync(self, model_name: str) -> Dict:
        """Carga síncrona del modelo"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers no está disponible")
            
        # Para análisis de fake news, usaremos un enfoque diferente
        # Cargaremos un modelo de análisis de sentimientos como base
        # y adaptaremos la salida para fake news detection
        
        if "toxic" in model_name.lower():
            # Modelo de toxicidad que puede adaptarse para fake news
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            pipe = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                top_k=1  # Solo el resultado top
            )
        else:
            # Modelo alternativo
            pipe = pipeline(
                "text-classification",
                model=model_name,
                top_k=1  # Solo el resultado top
            )
            tokenizer = pipe.tokenizer
            model = pipe.model
        
        return {
            'model': model,
            'tokenizer': tokenizer,
            'pipeline': pipe
        }
    
    async def _load_mock_model(self):
        """Carga un modelo mock para development/testing"""
        self.model = "mock"
        self.tokenizer = "mock"
        self.pipeline = "mock"
        self.model_name = "mock-model"
        self.is_loaded = True
        logger.warning("Usando modelo mock para análisis")
    
    async def analyze_text(self, text: str) -> Dict:
        """
        Analiza un texto y retorna el resultado en formato dict.
        
        Returns:
            Dict: {"score": float, "label": str, "confidence": float, "model_used": str}
        """
        if not self.is_loaded:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            if self.pipeline == "mock":
                score, label, confidence = await self._mock_analysis(text)
                model_used = "mock-model"
            else:
                score, label, confidence = await self._real_analysis(text)
                model_used = self.model_name
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "score": score,
                "label": label.value if hasattr(label, 'value') else str(label),
                "confidence": confidence,
                "model_used": model_used,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de IA: {e}")
            # Retornar resultado por defecto en caso de error
            processing_time = int((time.time() - start_time) * 1000)
            return {
                "score": 0.5,
                "label": AnalysisLabel.UNCERTAIN.value,
                "confidence": 0.1,
                "model_used": "error-fallback",
                "processing_time_ms": processing_time
            }
    
    async def _real_analysis(self, text: str) -> Tuple[float, AnalysisLabel, float]:
        """Análisis real usando el modelo cargado"""
        loop = asyncio.get_event_loop()
        
        # Ejecutar la inferencia en un thread pool
        result = await loop.run_in_executor(
            None,
            self._inference_sync,
            text
        )
        
        return self._interpret_results(result)
    
    def _inference_sync(self, text: str):
        """Inferencia síncrona del modelo"""
        # Truncar texto si es muy largo
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        # Ejecutar pipeline
        results = self.pipeline(text)
        return results
    
    def _interpret_results(self, results) -> Tuple[float, AnalysisLabel, float]:
        """Interpreta los resultados del modelo para fake news detection"""
        
        try:
            # El pipeline puede retornar diferentes formatos
            if isinstance(results, list):
                if len(results) > 0:
                    # Si es una lista de resultados, tomar el primero o el de mayor score
                    if isinstance(results[0], dict):
                        # Formato: [{'label': 'POSITIVE', 'score': 0.99}]
                        best_result = max(results, key=lambda x: x['score']) if len(results) > 1 else results[0]
                    else:
                        # Formato alternativo
                        best_result = results[0]
                else:
                    # Lista vacía
                    return 0.5, AnalysisLabel.UNCERTAIN, 0.1
            elif isinstance(results, dict):
                # Resultado directo en formato dict
                best_result = results
            else:
                # Formato desconocido
                logger.warning(f"Formato de resultado desconocido: {type(results)}")
                return 0.5, AnalysisLabel.UNCERTAIN, 0.1
            
            # Extraer información del resultado
            label = str(best_result.get('label', 'UNKNOWN')).upper()
            confidence = float(best_result.get('score', 0.5))
            
            # Mapear labels a nuestro sistema de fake news
            # Esto es una adaptación - idealmente necesitarías un modelo específico para fake news
            if 'TOXIC' in label or 'NEGATIVE' in label or 'HATE' in label:
                # Contenido tóxico/negativo/hate puede indicar mayor probabilidad de fake news
                score = 1.0 - confidence  # Invertir: contenido tóxico = más probable fake
                predicted_label = AnalysisLabel.FAKE if confidence > 0.6 else AnalysisLabel.UNCERTAIN
            elif 'POSITIVE' in label or 'NON_TOXIC' in label:
                # Contenido positivo/no tóxico puede ser más confiable
                score = confidence
                predicted_label = AnalysisLabel.REAL if confidence > 0.6 else AnalysisLabel.UNCERTAIN
            else:
                # Label desconocido
                score = 0.5
                predicted_label = AnalysisLabel.UNCERTAIN
            
            # Asegurar que el score esté en rango válido
            score = max(0.0, min(1.0, score))
            confidence = max(0.0, min(1.0, confidence))
            
            return score, predicted_label, confidence
            
        except Exception as e:
            logger.error(f"Error interpretando resultados: {e}")
            return 0.5, AnalysisLabel.UNCERTAIN, 0.1
    
    async def _mock_analysis(self, text: str) -> Tuple[float, AnalysisLabel, float]:
        """Análisis mock para development"""
        import hashlib
        
        # Simular algo de processing time
        await asyncio.sleep(0.1)
        
        # Generar resultado determinístico basado en el texto
        text_hash = hashlib.md5(text.encode()).hexdigest()
        hash_int = int(text_hash[:8], 16)
        
        # Simular score entre 0.0 y 1.0
        score = (hash_int % 1000) / 1000.0
        confidence = 0.8 + (hash_int % 200) / 1000.0  # Entre 0.8 y 1.0
        
        # Determinar label basado en el score
        if score < 0.3:
            label = AnalysisLabel.FAKE
        elif score > 0.7:
            label = AnalysisLabel.REAL
        else:
            label = AnalysisLabel.UNCERTAIN
        
        return score, label, confidence
    
    async def analyze_url(self, url: str) -> Dict:
        """
        Analiza una URL extrayendo el contenido y analizándolo.
        
        Args:
            url: URL a analizar
            
        Returns:
            Dict: Resultado del análisis
        """
        try:
            # Importar el extractor de contenido
            from app.utils.content_extractor import ContentExtractor
            
            extractor = ContentExtractor()
            content = await extractor.extract_from_url(url)
            
            if not content.get('text'):
                return {
                    "score": 0.5,
                    "label": AnalysisLabel.UNCERTAIN.value,
                    "confidence": 0.1,
                    "model_used": "no-content",
                    "processing_time_ms": 0,
                    "error": "No se pudo extraer contenido de la URL"
                }
            
            # Analizar el texto extraído
            result = await self.analyze_text(content['text'])
            result['url'] = url
            result['title'] = content.get('title', '')
            
            return result
            
        except Exception as e:
            logger.error(f"Error analizando URL {url}: {e}")
            return {
                "score": 0.5,
                "label": AnalysisLabel.UNCERTAIN.value,
                "confidence": 0.1,
                "model_used": "error",
                "processing_time_ms": 0,
                "error": str(e)
            }
    
    def get_model_info(self) -> Dict:
        """Retorna información del modelo actual"""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "is_loaded": self.is_loaded,
            "is_mock": self.pipeline == "mock"
        }

# Instancia global del analizador
ai_analyzer = AIAnalyzer()