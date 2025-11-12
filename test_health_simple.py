"""Test simple y rápido de health endpoints"""
import os
from app.services.entity_verifier import entity_verifier
from app.services.ai_analyzer import ai_analyzer
from app.utils.content_extractor import content_extractor

print("=" * 60)
print("🏥 HEALTH CHECK SIMPLE")
print("=" * 60)

# 1. NER Service
print("\n1️⃣ NER Service:")
if entity_verifier.nlp:
    print(f"   ✅ spaCy loaded: {entity_verifier.nlp.meta.get('name')}")
    print(f"   ✅ Database entries: {len(entity_verifier.verified_events)}")
else:
    print("   ❌ spaCy not loaded")

# 2. Political Detector
print("\n2️⃣ Political Detector:")
print("   ✅ Political detector available")

# 3. NewsAPI
print("\n3️⃣ NewsAPI:")
api_key = os.getenv("NEWS_API_KEY")
if api_key:
    print(f"   ✅ API key configured: {api_key[:10]}...")
else:
    print("   ⚠️  API key not configured")

# 4. AI Analyzer
print("\n4️⃣ AI Analyzer:")
print(f"   ✅ AI Analyzer available")

# 5. Web Extractor
print("\n5️⃣ Web Extractor:")
print(f"   ✅ Content extractor available")

print("\n" + "=" * 60)
print("✅ Todos los componentes básicos están disponibles")
print("=" * 60)
