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
                return_all_scores=True
            )
        else:
            # Modelo alternativo
            pipe = pipeline(
                "text-classification",
                model=model_name,
                return_all_scores=True
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
    
    async def analyze_text(self, text: str) -> Tuple[float, AnalysisLabel, float, int]:
        """
        Analiza un texto y retorna el resultado.
        
        Returns:
            Tuple[float, AnalysisLabel, float, int]: (score, label, confidence, tiempo_ms)
        """
        if not self.is_loaded:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            if self.pipeline == "mock":
                result = await self._mock_analysis(text)
            else:
                result = await self._real_analysis(text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            score, label, confidence = result
            return score, label, confidence, processing_time
            
        except Exception as e:
            logger.error(f"Error en análisis de IA: {e}")
            # Retornar resultado por defecto en caso de error
            processing_time = int((time.time() - start_time) * 1000)
            return 0.5, AnalysisLabel.UNCERTAIN, 0.1, processing_time
    
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
        
        if isinstance(results, list) and len(results) > 0:
            # Si tenemos múltiples scores, tomamos el más alto
            best_result = max(results, key=lambda x: x['score'])
            
            # Adaptamos el resultado para fake news
            # Esto es una simplificación - en producción necesitarías un modelo específico
            label = best_result['label'].upper()
            confidence = best_result['score']
            
            # Mapear labels a nuestro sistema
            if 'TOXIC' in label or 'NEGATIVE' in label:
                # Contenido tóxico/negativo puede indicar fake news
                score = 1.0 - confidence  # Invertir para que 0 = fake, 1 = real
                predicted_label = AnalysisLabel.FAKE if confidence > 0.7 else AnalysisLabel.UNCERTAIN
            else:
                # Contenido no tóxico puede ser más confiable
                score = confidence
                predicted_label = AnalysisLabel.REAL if confidence > 0.7 else AnalysisLabel.UNCERTAIN
            
            return score, predicted_label, confidence
        
        # Resultado por defecto
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