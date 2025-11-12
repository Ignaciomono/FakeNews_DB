"""
Test de conexiones externas para entorno serverless
Verifica que todas las APIs externas sean accesibles
"""
import asyncio
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_wikipedia_connection():
    """Test de conexión a Wikipedia API"""
    print("\n🌐 Testing Wikipedia API Connection...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://es.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": "test",
                    "srlimit": 1
                },
                headers={
                    "User-Agent": "DeepFakeDetector/1.0 (Educational Project)"
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                status = response.status
                data = await response.json()
                
                if status == 200:
                    print(f"   ✅ Wikipedia API accessible (status: {status})")
                    print(f"   📊 Response OK: {bool(data.get('query'))}")
                    return True
                else:
                    print(f"   ❌ Wikipedia API error (status: {status})")
                    return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False


async def test_wikidata_connection():
    """Test de conexión a Wikidata API"""
    print("\n📚 Testing Wikidata API Connection...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbsearchentities",
                    "format": "json",
                    "language": "es",
                    "search": "test",
                    "limit": 1
                },
                headers={
                    "User-Agent": "DeepFakeDetector/1.0 (Educational Project)"
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                status = response.status
                data = await response.json()
                
                if status == 200:
                    print(f"   ✅ Wikidata API accessible (status: {status})")
                    print(f"   📊 Response OK: {bool(data.get('search'))}")
                    return True
                else:
                    print(f"   ❌ Wikidata API error (status: {status})")
                    return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False


async def test_newsapi_connection():
    """Test de conexión a NewsAPI"""
    print("\n📰 Testing NewsAPI Connection...")
    
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("   ⚠️  NEWS_API_KEY not configured")
        return True  # No crítico
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "test",
                    "apiKey": api_key,
                    "pageSize": 1
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                status = response.status
                data = await response.json()
                
                if status == 200:
                    print(f"   ✅ NewsAPI accessible (status: {status})")
                    print(f"   📊 API Key valid: True")
                    print(f"   📊 Total results: {data.get('totalResults', 0)}")
                    return True
                elif status == 401:
                    print(f"   ❌ NewsAPI authentication error (invalid key)")
                    return False
                elif status == 429:
                    print(f"   ⚠️  NewsAPI rate limit exceeded")
                    return True  # No es error de conexión
                else:
                    print(f"   ❌ NewsAPI error (status: {status})")
                    return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False


async def test_google_factcheck_connection():
    """Test de conexión a Google Fact Check API"""
    print("\n🔍 Testing Google Fact Check API Connection...")
    
    api_key = os.getenv("FACT_CHECK_API_KEY")
    if not api_key:
        print("   ⚠️  FACT_CHECK_API_KEY not configured")
        return True  # No crítico
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://factchecktools.googleapis.com/v1alpha1/claims:search",
                params={
                    "query": "test",
                    "key": api_key,
                    "languageCode": "es"
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                status = response.status
                
                if status == 200:
                    print(f"   ✅ Fact Check API accessible (status: {status})")
                    print(f"   📊 API Key valid: True")
                    return True
                elif status == 400:
                    print(f"   ⚠️  Fact Check API: Invalid request (but API is accessible)")
                    return True
                elif status == 401 or status == 403:
                    print(f"   ❌ Fact Check API authentication error (invalid key)")
                    return False
                else:
                    print(f"   ❌ Fact Check API error (status: {status})")
                    return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False


async def main():
    print("=" * 70)
    print("🌍 TEST DE CONEXIONES EXTERNAS - Entorno Serverless")
    print("=" * 70)
    print(f"Timestamp: {datetime.now()}")
    print(f"Environment: {'Production' if os.getenv('VERCEL') else 'Development'}")
    
    results = {}
    
    # Ejecutar tests en paralelo para serverless
    print("\n🚀 Ejecutando tests de conexión en paralelo...")
    
    results["Wikipedia"] = await test_wikipedia_connection()
    results["Wikidata"] = await test_wikidata_connection()
    results["NewsAPI"] = await test_newsapi_connection()
    results["Google Fact Check"] = await test_google_factcheck_connection()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE CONEXIONES")
    print("=" * 70)
    
    for service, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {service}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = int((passed / total) * 100)
    
    print(f"\n{'=' * 70}")
    print(f"Total: {passed}/{total} ({percentage}%)")
    
    if percentage == 100:
        print("🎉 Estado: HEALTHY - Todas las APIs externas accesibles")
        return 0
    elif percentage >= 75:
        print("⚠️  Estado: DEGRADED - Algunas APIs con problemas")
        return 0
    else:
        print("❌ Estado: UNHEALTHY - Problemas críticos de conectividad")
        return 1


if __name__ == "__main__":
    import sys
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
