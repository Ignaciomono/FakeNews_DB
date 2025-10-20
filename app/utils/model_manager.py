"""
Gestor de modelos de Fake News de Hugging Face
"""
from typing import Dict, List
from enum import Enum

class FakeNewsModel(str, Enum):
    """Modelos disponibles para detección de fake news"""
    
    # RoBERTa fine-tuned - Mejor para textos en inglés
    ROBERTA_FAKE_NEWS = "hamzab/roberta-fake-news-classification"
    
    # BERT especializado - Balance entre velocidad y precisión
    BERT_FAKE_NEWS = "jy46604790/Fake-News-Bert-Detect"
    
    # BERT mini - Más rápido, menor precisión
    BERT_MINI_FAKE_NEWS = "mrm8488/bert-mini-finetuned-fake-news-detection"
    
    # Modelos en español
    FAKE_NEWS_SPANISH = "GonzaloA/fake-news-detection-spanish"
    BETO_FAKE_NEWS = "Narrativa/beto-fake-news-detection"
    
    # BERT base - Buen rendimiento general
    BERT_BASE_FAKE_NEWS = "elozano/bert-base-cased-fake-news"


class ModelInfo:
    """Información detallada de cada modelo"""
    
    MODELS_INFO: Dict[str, Dict] = {
        "hamzab/roberta-fake-news-classification": {
            "name": "RoBERTa Fake News Classifier",
            "language": "English",
            "description": "RoBERTa model fine-tuned on fake news dataset",
            "accuracy": "~92%",
            "speed": "Medium",
            "best_for": "General fake news detection in English"
        },
        "jy46604790/Fake-News-Bert-Detect": {
            "name": "BERT Fake News Detector",
            "language": "English",
            "description": "BERT model specialized in fake news detection",
            "accuracy": "~89%",
            "speed": "Medium",
            "best_for": "Balanced performance for English news"
        },
        "mrm8488/bert-mini-finetuned-fake-news-detection": {
            "name": "BERT Mini Fake News",
            "language": "English",
            "description": "Lightweight BERT model for faster inference",
            "accuracy": "~85%",
            "speed": "Fast",
            "best_for": "High-volume processing, speed priority"
        },
        "GonzaloA/fake-news-detection-spanish": {
            "name": "Spanish Fake News Detector",
            "language": "Spanish",
            "description": "Model trained specifically for Spanish fake news",
            "accuracy": "~88%",
            "speed": "Medium",
            "best_for": "Spanish language news detection"
        },
        "Narrativa/beto-fake-news-detection": {
            "name": "BETO Fake News (Spanish)",
            "language": "Spanish",
            "description": "BETO (Spanish BERT) for fake news detection",
            "accuracy": "~87%",
            "speed": "Medium",
            "best_for": "Spanish news, Latin American context"
        },
        "elozano/bert-base-cased-fake-news": {
            "name": "BERT Base Fake News",
            "language": "English",
            "description": "BERT base model fine-tuned for fake news",
            "accuracy": "~90%",
            "speed": "Medium-Slow",
            "best_for": "High accuracy English news detection"
        }
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Dict:
        """Obtiene información de un modelo específico"""
        return cls.MODELS_INFO.get(model_name, {
            "name": model_name,
            "language": "Unknown",
            "description": "Custom model",
            "accuracy": "Unknown",
            "speed": "Unknown",
            "best_for": "Custom use case"
        })
    
    @classmethod
    def list_all_models(cls) -> List[Dict]:
        """Lista todos los modelos disponibles con su información"""
        return [
            {
                "model_id": model_id,
                **info
            }
            for model_id, info in cls.MODELS_INFO.items()
        ]
    
    @classmethod
    def get_spanish_models(cls) -> List[str]:
        """Obtiene solo los modelos en español"""
        return [
            model_id 
            for model_id, info in cls.MODELS_INFO.items() 
            if info["language"] == "Spanish"
        ]
    
    @classmethod
    def get_english_models(cls) -> List[str]:
        """Obtiene solo los modelos en inglés"""
        return [
            model_id 
            for model_id, info in cls.MODELS_INFO.items() 
            if info["language"] == "English"
        ]


# Instancia global
model_manager = ModelInfo()
