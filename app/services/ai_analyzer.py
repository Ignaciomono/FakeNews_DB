import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import time # <-- 1. Importar el módulo 'time'

import aiohttp
from app.config import settings

logger = logging.getLogger(__name__)

class FakeNewsLabel(Enum):
    FAKE = "FAKE"
    REAL = "REAL"
    UNCERTAIN = "UNCERTAIN"

class AIAnalyzer:
    def __init__(self):
        self.is_loaded = True  # Siempre disponible
        self.model_name = settings.HF_MODEL_NAME
        self.api_url = f"{settings.HF_API_URL}{self.model_name}"
        
        self.headers = {"Content-Type": "application/json"}
        if settings.HF_API_TOKEN:
            self.headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"
    
    async def initialize(self):
        """Mantenido para compatibilidad, pero ya no necesario"""
        self.is_loaded = True
    
    async def analyze_text(self, text: str) -> Tuple[float, FakeNewsLabel, float, int]:
        start_time = time.time()

        try:
            cleaned_text = text.strip()[:500] if text else "empty"
            api_result = await self._call_api(cleaned_text)
            
            if api_result:
                score, label, confidence = self._process_result(api_result)
            else:
                score, label, confidence = self._fallback_analysis(cleaned_text)
                
        except Exception as e:
            score, label, confidence = (0.5, FakeNewsLabel.UNCERTAIN, 0.5)

        end_time = time.time() # <-- 3. Registrar el tiempo de finalización
        analysis_time_ms = int((end_time - start_time) * 1000) # Calcular duración en ms
        
        return score, label, confidence, analysis_time_ms # <-- 4. Devolver los 4 valores
    
    async def _call_api(self, text: str) -> Optional[List[Dict[str, Any]]]:
        try:
            payload = {"inputs": text}
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            # Crear sesión nueva para cada llamada (compatibilidad serverless)
            async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
                async with session.post(self.api_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        # La API de HF puede devolver un dict en lugar de una lista de dicts
                        return data if isinstance(data, list) else [data]
                    return None
        except Exception:
            return None
    
    def _process_result(self, result: List[Dict[str, Any]]) -> Tuple[float, FakeNewsLabel, float]:
        try:
            if not result or not result[0]:
                return (0.5, FakeNewsLabel.UNCERTAIN, 0.5)
            
            # La respuesta de HF es una lista de listas de diccionarios
            best = max(result[0], key=lambda x: x.get('score', 0))
            label_str = best.get('label', '').upper()
            confidence = best.get('score', 0.5)
            
            # Mapeo de score (0.0 a 1.0) donde 0 es FAKE y 1 es REAL
            if "NEGATIVE" in label_str or "FAKE" in label_str:
                score = 1.0 - confidence
                label = FakeNewsLabel.FAKE
            elif "POSITIVE" in label_str or "REAL" in label_str:
                score = confidence
                label = FakeNewsLabel.REAL
            else: # Neutral, Uncertain, etc.
                score = 0.5
                label = FakeNewsLabel.UNCERTAIN

            return score, label, confidence
        except Exception:
            return (0.5, FakeNewsLabel.UNCERTAIN, 0.5)
    
    def _fallback_analysis(self, text: str) -> Tuple[float, FakeNewsLabel, float]:
        fake_words = ['falso', 'mentira', 'fake', 'hoax', 'bulo']
        real_words = ['oficial', 'confirmado', 'gobierno', 'estudio']
        
        text_lower = text.lower()
        fake_score = sum(1 for word in fake_words if word in text_lower)
        real_score = sum(1 for word in real_words if word in text_lower)
        
        if fake_score > real_score:
            return (0.2, FakeNewsLabel.FAKE, 0.7) # Score bajo (fake), confianza alta
        elif real_score > fake_score:
            return (0.8, FakeNewsLabel.REAL, 0.7) # Score alto (real), confianza alta
        else:
            return (0.5, FakeNewsLabel.UNCERTAIN, 0.6)
    
    async def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "is_loaded": self.is_loaded,
            "version": "2.0.0",
            "type": "external_api"
        }
    
    async def cleanup(self):
        # No hay sesión persistente para limpiar
        pass

ai_analyzer = AIAnalyzer()