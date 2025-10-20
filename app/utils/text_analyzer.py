"""
Analizador de características de texto para detectar señales de fake news
"""
import re
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class TextFeatures:
    """Características extraídas del texto"""
    # Características de estilo
    exclamation_ratio: float  # Proporción de signos de exclamación
    caps_ratio: float  # Proporción de texto en MAYÚSCULAS
    question_ratio: float  # Proporción de signos de interrogación
    
    # Características de contenido
    sensational_words: int  # Palabras sensacionalistas
    clickbait_patterns: int  # Patrones de clickbait
    unverifiable_claims: int  # Afirmaciones no verificables
    extraordinary_claims: int = 0  # Afirmaciones extraordinarias (unicornios, aliens, etc.)
    
    # Características de credibilidad
    has_sources: bool  # Menciona fuentes
    has_dates: bool  # Incluye fechas específicas
    has_numbers: bool  # Incluye datos numéricos
    
    # Score final de características (0-1, donde 0 es más probable fake)
    feature_score: float


class TextAnalyzer:
    """Analiza características del texto que indican fake news"""
    
    # Palabras sensacionalistas comunes en fake news
    SENSATIONAL_WORDS = [
        'urgente', 'alerta', 'shock', 'increíble', 'impactante', 'impresionante',
        'secreto', 'oculto', 'prohibido', 'censurado', 'verdad', 'revelado',
        'exclusivo', 'bomba', 'escándalo', 'peligro', 'milagro', 'mágico',
        'urgent', 'alert', 'shocking', 'unbelievable', 'amazing', 'secret',
        'hidden', 'banned', 'censored', 'truth', 'revealed', 'exclusive',
        'scandal', 'danger', 'miracle', 'magic'
    ]
    
    # Patrones de clickbait
    CLICKBAIT_PATTERNS = [
        r'no vas a creer',
        r'no creerás',
        r'lo que pasó después',
        r'te sorprenderá',
        r'quedarás en shock',
        r'nadie esperaba',
        r'los [0-9]+ [a-záéíóú]+ que',
        r'[0-9]+ cosas que',
        r'won\'t believe',
        r'you won\'t believe',
        r'what happened next',
        r'will shock you',
        r'number [0-9]+ will',
        r'doctors hate',
        r'this one trick',
    ]
    
    # Palabras que indican afirmaciones no verificables
    UNVERIFIABLE_WORDS = [
        'dicen que', 'se rumorea', 'según fuentes', 'algunos expertos',
        'se dice que', 'supuestamente', 'aparentemente', 'parece que',
        'se inventa', 'inventado', 'falso', 'mentira', 'engaño',
        'sources say', 'allegedly', 'reportedly', 'apparently', 'supposedly'
    ]
    
    # Palabras que indican eventos extraordinarios que requieren verificación
    EXTRAORDINARY_CLAIMS = [
        'unicornio', 'unicornios', 'alien', 'aliens', 'ovni', 'ovnis',
        'extraterrestre', 'extraterrestres', 'milagro', 'milagros',
        'sobrenatural', 'paranormal', 'fantasma', 'fantasmas',
        'monstruo', 'monstruos', 'criatura', 'criaturas',
        'unicorn', 'unicorns', 'ufo', 'alien', 'ghost', 'monster'
    ]
    
    # Palabras que indican credibilidad
    SOURCE_INDICATORS = [
        'estudio', 'investigación', 'universidad', 'científicos', 'doctor',
        'profesor', 'experto', 'según', 'de acuerdo', 'publicado en',
        'study', 'research', 'university', 'scientists', 'doctor',
        'professor', 'expert', 'according to', 'published in'
    ]
    
    def analyze(self, text: str) -> TextFeatures:
        """Analiza el texto y extrae características"""
        text_lower = text.lower()
        text_len = len(text)
        
        if text_len == 0:
            return self._default_features()
        
        # Características de estilo
        exclamation_ratio = text.count('!') / max(text_len / 100, 1)
        caps_words = len(re.findall(r'\b[A-ZÁÉÍÓÚ]{3,}\b', text))
        caps_ratio = caps_words / max(len(text.split()), 1)
        question_ratio = text.count('?') / max(text_len / 100, 1)
        
        # Características de contenido
        sensational_words = sum(1 for word in self.SENSATIONAL_WORDS if word in text_lower)
        
        clickbait_patterns = sum(
            1 for pattern in self.CLICKBAIT_PATTERNS 
            if re.search(pattern, text_lower)
        )
        
        unverifiable_claims = sum(
            1 for phrase in self.UNVERIFIABLE_WORDS 
            if phrase in text_lower
        )
        
        # Nueva característica: afirmaciones extraordinarias
        extraordinary_claims = sum(
            1 for word in self.EXTRAORDINARY_CLAIMS
            if word in text_lower
        )
        
        # Características de credibilidad
        has_sources = any(word in text_lower for word in self.SOURCE_INDICATORS)
        has_dates = bool(re.search(r'\b(19|20)\d{2}\b', text))  # Años 1900-2099
        has_numbers = bool(re.search(r'\b\d+\b', text))
        
        # Calcular score de características (0-1, donde 1 es más creíble)
        feature_score = self._calculate_feature_score(
            exclamation_ratio, caps_ratio, question_ratio,
            sensational_words, clickbait_patterns, unverifiable_claims,
            has_sources, has_dates, has_numbers, extraordinary_claims
        )
        
        return TextFeatures(
            exclamation_ratio=exclamation_ratio,
            caps_ratio=caps_ratio,
            question_ratio=question_ratio,
            sensational_words=sensational_words,
            clickbait_patterns=clickbait_patterns,
            unverifiable_claims=unverifiable_claims,
            extraordinary_claims=extraordinary_claims,
            has_sources=has_sources,
            has_dates=has_dates,
            has_numbers=has_numbers,
            feature_score=feature_score
        )
    
    def _calculate_feature_score(
        self, 
        exclamation_ratio: float,
        caps_ratio: float,
        question_ratio: float,
        sensational_words: int,
        clickbait_patterns: int,
        unverifiable_claims: int,
        has_sources: bool,
        has_dates: bool,
        has_numbers: bool,
        extraordinary_claims: int = 0
    ) -> float:
        """
        Calcula un score basado en características (0-1)
        0 = muy probable fake news
        1 = muy probable legítimo
        """
        score = 1.0
        
        # Penalizar características negativas
        score -= min(exclamation_ratio * 0.1, 0.3)  # Muchos ! son sospechosos
        score -= min(caps_ratio * 0.5, 0.3)  # MAYÚSCULAS son sospechosas
        score -= min(question_ratio * 0.05, 0.1)  # Muchos ? pueden ser clickbait
        score -= min(sensational_words * 0.05, 0.3)  # Palabras sensacionalistas
        score -= min(clickbait_patterns * 0.15, 0.3)  # Patrones de clickbait
        score -= min(unverifiable_claims * 0.08, 0.2)  # Afirmaciones no verificables
        
        # NUEVA REGLA: Penalizar fuertemente afirmaciones extraordinarias sin fuentes
        if extraordinary_claims > 0 and not has_sources:
            score -= min(extraordinary_claims * 0.25, 0.5)  # Penalización fuerte
        
        # Recompensar características positivas
        if has_sources:
            score += 0.15  # Aumentado de 0.1
        if has_dates:
            score += 0.05
        if has_numbers:
            score += 0.05
        
        # Mantener en rango 0-1
        return max(0.0, min(1.0, score))
    
    def _default_features(self) -> TextFeatures:
        """Retorna características por defecto para texto vacío"""
        return TextFeatures(
            exclamation_ratio=0.0,
            caps_ratio=0.0,
            question_ratio=0.0,
            sensational_words=0,
            clickbait_patterns=0,
            unverifiable_claims=0,
            extraordinary_claims=0,
            has_sources=False,
            has_dates=False,
            has_numbers=False,
            feature_score=0.5
        )
    
    def get_recommendation(self, features: TextFeatures, ai_score: float) -> Tuple[float, str]:
        """
        Combina el score del modelo de IA con el análisis de características
        Retorna: (score_final, explicación)
        """
        # Peso: 60% modelo de IA, 40% análisis de características
        final_score = (ai_score * 0.6) + (features.feature_score * 0.4)
        
        # Generar explicación
        warnings = []
        
        if features.exclamation_ratio > 2:
            warnings.append("uso excesivo de signos de exclamación")
        if features.caps_ratio > 0.3:
            warnings.append("texto en MAYÚSCULAS")
        if features.sensational_words > 3:
            warnings.append("lenguaje sensacionalista")
        if features.clickbait_patterns > 0:
            warnings.append("patrones de clickbait")
        if features.unverifiable_claims > 1:
            warnings.append("afirmaciones no verificables")
        
        positives = []
        if features.has_sources:
            positives.append("menciona fuentes")
        if features.has_dates:
            positives.append("incluye fechas")
        if features.has_numbers:
            positives.append("incluye datos")
        
        explanation = ""
        if warnings:
            explanation = f"⚠️ Señales de alerta: {', '.join(warnings)}. "
        if positives:
            explanation += f"✓ Aspectos positivos: {', '.join(positives)}."
        
        if not warnings and not positives:
            explanation = "Análisis basado principalmente en el modelo de IA."
        
        return final_score, explanation.strip()


# Instancia global
text_analyzer = TextAnalyzer()
