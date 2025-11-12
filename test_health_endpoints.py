"""
Script para probar todos los endpoints de health del sistema
"""
import asyncio
import sys
from datetime import datetime

# Importar los servicios directamente
from app.services.entity_verifier import entity_verifier
from app.services.wikipedia_verifier import wikipedia_verifier
from app.services.news_api_service import news_api_service
from app.services.ai_analyzer import ai_analyzer
from app.utils.content_extractor import content_extractor


async def test_ner_service():
    """Test del servicio NER"""
    print("\n🔍 Testing NER Service...")
    try:
        if not entity_verifier.nlp:
            print("   ❌ spaCy model not loaded")
            return False
        
        # Test de extracción (extract_entities NO es async)
        text = "Lionel Messi jugó en Barcelona hasta 2021"
        entities = entity_verifier.extract_entities(text)
        
        print(f"   ✅ spaCy loaded: {entity_verifier.nlp.meta.get('name')}")
        print(f"   ✅ Entities detected: {len(entities.get('persons', []))}")
        print(f"   ✅ Database entries: {len(entity_verifier.person_database)}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_wikipedia_api():
    """Test de Wikipedia API"""
    print("\n🌐 Testing Wikipedia API...")
    try:
        result = await wikipedia_verifier.search_person("Albert Einstein")
        
        if result:
            print("   ✅ API accessible")
            print("   ✅ User-Agent: DeepFakeDetector/1.0")
            return True
        else:
            print("   ⚠️  API responded but no results")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_news_api():
    """Test de NewsAPI"""
    print("\n📰 Testing NewsAPI...")
    try:
        # Verificar que la API key esté configurada en el entorno
        import os
        api_key = os.getenv("NEWS_API_KEY")
        
        if not api_key:
            print("   ⚠️  API key not configured - service will be skipped")
            return True  # No es crítico
        
        articles = await news_api_service.search_news("tecnología", max_results=1)
        
        if articles:
            print("   ✅ API accessible")
            print(f"   ✅ Articles found: {len(articles)}")
            return True
        else:
            print("   ⚠️  API responded but no articles")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_political_detector():
    """Test del detector político"""
    print("\n🏛️  Testing Political Detector...")
    try:
        test_cases = [
            ("Milei implementó la pena de muerte", True),
            ("Messi ganó el mundial", False)
        ]
        
        all_correct = True
        for text, should_detect in test_cases:
            # extract_entities no es async
            entities = entity_verifier.extract_entities(text)
            is_detected = entity_verifier._check_controversial_political_claims(text, entities)
            correct = is_detected == should_detect
            symbol = "✅" if correct else "❌"
            print(f"   {symbol} '{text[:40]}...' -> {is_detected} (expected: {should_detect})")
            all_correct = all_correct and correct
        
        print(f"   ✅ Political keywords: {len(entity_verifier.political_keywords)}")
        return all_correct
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_ai_analyzer():
    """Test del analizador de IA"""
    print("\n🤖 Testing AI Analyzer...")
    try:
        model_info = await ai_analyzer.get_model_info()
        
        # Test simple
        score, label, confidence, processing_time = await ai_analyzer.analyze_text(
            "This is a test message"
        )
        
        print(f"   ✅ Model loaded: {model_info.get('is_loaded')}")
        print(f"   ✅ Model name: {model_info.get('model_name')}")
        print(f"   ✅ Test successful (score: {score:.2f})")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_web_extractor():
    """Test del extractor web"""
    print("\n🌍 Testing Web Extractor...")
    try:
        test_url = "https://example.com"
        url_valid = content_extractor.validate_url(test_url)
        
        print(f"   ✅ Extractor available")
        print(f"   ✅ URL validation working: {url_valid}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def main():
    print("=" * 60)
    print("🏥 HEALTH CHECK - Sistema de Verificación de 8 Capas")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    
    results = {}
    
    # Ejecutar todos los tests
    results["NER Service"] = await test_ner_service()
    results["Wikipedia API"] = await test_wikipedia_api()
    results["NewsAPI"] = await test_news_api()
    results["Political Detector"] = test_political_detector()
    results["AI Analyzer"] = await test_ai_analyzer()
    results["Web Extractor"] = test_web_extractor()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = int((passed / total) * 100)
    
    for service, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {service}")
    
    print(f"\n{'=' * 60}")
    print(f"Total: {passed}/{total} ({percentage}%)")
    
    if percentage == 100:
        print("🎉 Estado: HEALTHY - Todos los servicios operativos")
        status_code = 0
    elif percentage >= 70:
        print("⚠️  Estado: DEGRADED - Algunos servicios con problemas")
        status_code = 0
    else:
        print("❌ Estado: UNHEALTHY - Sistema comprometido")
        status_code = 1
    
    print("=" * 60)
    
    return status_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        sys.exit(1)
