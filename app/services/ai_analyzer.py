import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

import aiohttp
from app.config import settings

logger = logging.getLogger(__name__)

class FakeNewsLabel(Enum):
    FAKE = "fake"
    REAL = "real"
    UNCERTAIN = "uncertain"

class AIAnalyzer:
    def __init__(self):
        self.session = None
        self.is_loaded = False
        self.model_name = settings.HF_MODEL_NAME
        self.api_url = f"{settings.HF_API_URL}{self.model_name}"
        
        self.headers = {"Content-Type": "application/json"}
        if settings.HF_API_TOKEN:
            self.headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"
    
    async def initialize(self):
        try:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout, headers=self.headers)
            self.is_loaded = True
        except Exception as e:
            logger.warning(f"Error: {e}")
            self.is_loaded = True
    
    async def analyze_text(self, text):
        try:
            if not self.session:
                await self.initialize()
            
            cleaned_text = text.strip()[:500] if text else "empty"
            api_result = await self._call_api(cleaned_text)
            
            if api_result:
                return self._process_result(api_result)
            else:
                return self._fallback_analysis(cleaned_text)
                
        except Exception as e:
            return (0.5, 0.5, FakeNewsLabel.UNCERTAIN)
    
    async def _call_api(self, text):
        try:
            payload = {"inputs": text}
            async with self.session.post(self.api_url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except:
            return None
    
    def _process_result(self, result):
        try:
            if not result:
                return (0.5, 0.5, FakeNewsLabel.UNCERTAIN)
            
            best = max(result, key=lambda x: x.get('score', 0))
            label_str = best.get('label', '').upper()
            score = best.get('score', 0.5)
            
            if label_str == 'NEGATIVE' and score > 0.7:
                return (0.8, score, FakeNewsLabel.FAKE)
            elif label_str == 'POSITIVE' and score > 0.7:
                return (0.2, score, FakeNewsLabel.REAL)
            else:
                return (0.5, 0.6, FakeNewsLabel.UNCERTAIN)
        except:
            return (0.5, 0.5, FakeNewsLabel.UNCERTAIN)
    
    def _fallback_analysis(self, text):
        fake_words = ['falso', 'mentira', 'fake', 'hoax', 'bulo']
        real_words = ['oficial', 'confirmado', 'gobierno', 'estudio']
        
        text_lower = text.lower()
        fake_score = sum(1 for word in fake_words if word in text_lower)
        real_score = sum(1 for word in real_words if word in text_lower)
        
        if fake_score > real_score:
            return (0.7, 0.7, FakeNewsLabel.FAKE)
        elif real_score > fake_score:
            return (0.3, 0.7, FakeNewsLabel.REAL)
        else:
            return (0.5, 0.6, FakeNewsLabel.UNCERTAIN)
    
    async def get_model_info(self):
        return {
            "model_name": self.model_name,
            "is_loaded": self.is_loaded,
            "version": "2.0.0",
            "type": "external_api"
        }
    
    async def cleanup(self):
        if self.session:
            await self.session.close()

ai_analyzer = AIAnalyzer()
