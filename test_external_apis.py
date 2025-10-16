"""
Script de prueba para las APIs externas de fact-checking
"""
import asyncio
import sys
from app.services.external_apis import (
    google_fact_check_service,
    claimbuster_service,
    wordlift_service,
    mbfc_service,
    rapidapi_service
)
from app.config_apis import api_config


async def test_google_api():
    """Probar Google Fact Check API"""
    print("\n🔍 Probando Google Fact Check API...")
    if not api_config.is_google_configured():
        print("❌ Google API no configurada (GOOGLE_FACT_CHECK_API_KEY)")
        return
    
    result = await google_fact_check_service.check_claim("climate change")
    if result.get("success"):
        print(f"✅ Google API funcionando - {result.get('total_results')} resultados")
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_claimbuster_api():
    """Probar ClaimBuster API"""
    print("\n📊 Probando ClaimBuster API...")
    if not api_config.is_claimbuster_configured():
        print("❌ ClaimBuster API no configurada (CLAIMBUSTER_API_KEY)")
        return
    
    result = await claimbuster_service.score_text("The president announced new policies")
    if result.get("success"):
        print(f"✅ ClaimBuster API funcionando - Score: {result.get('score')}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_wordlift_api():
    """Probar WordLift API"""
    print("\n🧠 Probando WordLift API...")
    if not api_config.is_wordlift_configured():
        print("❌ WordLift API no configurada (WORDLIFT_API_KEY)")
        return
    
    result = await wordlift_service.fact_check("Test content for fact checking")
    if result.get("success"):
        print("✅ WordLift API funcionando")
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_mbfc_api():
    """Probar MBFC API"""
    print("\n📰 Probando MBFC API...")
    if not api_config.is_mbfc_configured():
        print("❌ MBFC API no configurada (MBFC_API_KEY)")
        return
    
    result = await mbfc_service.check_source("https://www.bbc.com")
    if result.get("success"):
        print(f"✅ MBFC API funcionando - Bias: {result.get('bias')}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_rapidapi():
    """Probar RapidAPI Fake News Detection"""
    print("\n🤖 Probando RapidAPI Fake News Detection...")
    if not api_config.is_rapidapi_configured():
        print("❌ RapidAPI no configurada (RAPIDAPI_KEY)")
        return
    
    result = await rapidapi_service.detect_fake_news(
        "This is a test article content",
        "Test Article"
    )
    if result.get("success"):
        print(f"✅ RapidAPI funcionando - Fake: {result.get('is_fake')}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    """Ejecutar todas las pruebas"""
    print("="*60)
    print("🧪 PRUEBA DE APIs EXTERNAS DE FACT-CHECKING")
    print("="*60)
    
    # Mostrar APIs configuradas
    configured = api_config.get_configured_apis()
    print(f"\n📋 APIs configuradas: {len(configured)}")
    for api in configured:
        print(f"   ✓ {api}")
    
    if not configured:
        print("\n❌ No hay APIs configuradas!")
        print("   Configure al menos una API en el archivo .env")
        print("\n📝 Variables disponibles:")
        print("   - GOOGLE_FACT_CHECK_API_KEY")
        print("   - CLAIMBUSTER_API_KEY")
        print("   - WORDLIFT_API_KEY")
        print("   - MBFC_API_KEY")
        print("   - RAPIDAPI_KEY")
        sys.exit(1)
    
    # Ejecutar pruebas
    await test_google_api()
    await test_claimbuster_api()
    await test_wordlift_api()
    await test_mbfc_api()
    await test_rapidapi()
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())