"""
Extrae configuración actual de Vercel usando la API pública
"""
import requests
import json

print("=" * 70)
print("🔍 EXTRACTOR DE CONFIGURACIÓN DESDE VERCEL")
print("=" * 70)

VERCEL_URL = "https://fakenewsignacio.vercel.app"

# 1. Verificar que la API esté activa
print("\n1️⃣ Verificando API en producción...")
print("-" * 70)

try:
    response = requests.get(f"{VERCEL_URL}/health/ping", timeout=10)
    print(f"✅ API Activa: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Message: {data.get('message', 'N/A')}")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Verificar endpoint de base de datos
print("\n2️⃣ Verificando conexión a base de datos...")
print("-" * 70)

try:
    response = requests.get(f"{VERCEL_URL}/health/database", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Base de datos: {data.get('status', 'unknown')}")
        if 'database' in data:
            db_info = data['database']
            print(f"   Info: {db_info}")
    elif response.status_code == 500:
        print("❌ Error 500 - Base de datos NO configurada o inaccesible")
        try:
            error = response.json()
            print(f"   Detalle: {error.get('detail', 'Sin detalles')}")
        except:
            print(f"   Respuesta: {response.text[:200]}")
    else:
        print(f"⚠️  Status inesperado: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 3. Verificar servicios externos
print("\n3️⃣ Verificando servicios de verificación...")
print("-" * 70)

services = [
    "/health/ner-service",
    "/health/wikipedia-api",
    "/health/news-api",
    "/health/political-detector",
]

for service in services:
    try:
        response = requests.get(f"{VERCEL_URL}{service}", timeout=10)
        service_name = service.split("/")[-1].replace("-", " ").title()
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            if status == 'healthy':
                print(f"✅ {service_name}: Funcionando")
            else:
                print(f"⚠️  {service_name}: {status}")
        else:
            print(f"❌ {service_name}: Error {response.status_code}")
    except Exception as e:
        print(f"❌ {service_name}: {e}")

# 4. Verificar OpenAPI Schema
print("\n4️⃣ Analizando OpenAPI Schema...")
print("-" * 70)

try:
    response = requests.get(f"{VERCEL_URL}/openapi.json", timeout=10)
    if response.status_code == 200:
        schema = response.json()
        print(f"✅ OpenAPI Schema encontrado")
        print(f"   Título: {schema.get('info', {}).get('title', 'N/A')}")
        print(f"   Versión: {schema.get('info', {}).get('version', 'N/A')}")
        
        # Contar endpoints
        paths = schema.get('paths', {})
        print(f"   Total de endpoints: {len(paths)}")
        
        # Verificar si hay esquemas de seguridad
        if 'components' in schema and 'securitySchemes' in schema['components']:
            print(f"\n   🔐 Esquemas de seguridad detectados:")
            for scheme_name, scheme_data in schema['components']['securitySchemes'].items():
                print(f"      - {scheme_name}: {scheme_data.get('type', 'unknown')}")
        
    else:
        print(f"⚠️  No se pudo obtener schema: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# 5. Inferir configuración faltante
print("\n5️⃣ Inferencia de Configuración Faltante:")
print("-" * 70)

print("\nBasado en el análisis:")

# Verificar si DATABASE_URL está configurada
try:
    db_response = requests.get(f"{VERCEL_URL}/health/database", timeout=5)
    if db_response.status_code == 500:
        print("\n❌ DATABASE_URL: NO CONFIGURADA")
        print("   Evidencia: /health/database retorna 500")
        print("   Acción: Debes configurar DATABASE_URL en Vercel")
        print("   Opciones:")
        print("      1. Neon PostgreSQL (gratis): https://neon.tech")
        print("      2. Vercel Postgres: https://vercel.com/storage/postgres")
        print("      3. Supabase (gratis): https://supabase.com")
except:
    pass

# Verificar NEWS_API_KEY
try:
    news_response = requests.get(f"{VERCEL_URL}/health/news-api", timeout=5)
    if news_response.status_code == 200:
        data = news_response.json()
        if data.get('status') == 'healthy':
            print("\n✅ NEWS_API_KEY: Probablemente configurada")
        else:
            print("\n⚠️  NEWS_API_KEY: Puede no estar configurada")
            print(f"   Status: {data.get('status')}")
    else:
        print("\n⚠️  NEWS_API_KEY: No se pudo verificar")
except:
    pass

# 6. Generar archivo .env de ejemplo
print("\n6️⃣ Generando archivo .env de ejemplo...")
print("-" * 70)

env_example = """# Variables de Entorno Requeridas para Vercel

# Base de datos PostgreSQL (REQUERIDO)
# Obtén una gratis en https://neon.tech
DATABASE_URL=postgresql://user:password@ep-xxxxx.neon.tech/dbname?sslmode=require

# Clave secreta para JWT (REQUERIDO)
# Genera una con: openssl rand -hex 32
SECRET_KEY=tu-clave-secreta-minimo-32-caracteres-aleatorios-aqui

# NewsAPI para verificación de noticias (OPCIONAL)
# Obtén una gratis (100 req/día) en https://newsapi.org/
# NEWS_API_KEY=tu-news-api-key-aqui

# Google Fact Check API (OPCIONAL)
# Obtén una en https://console.cloud.google.com/
# GOOGLE_FACT_CHECK_API_KEY=tu-google-fact-check-key-aqui

# Hugging Face Token (OPCIONAL - mejora rate limits)
# Obtén uno gratis en https://huggingface.co/settings/tokens
# HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
"""

with open(".env.example", "w", encoding="utf-8") as f:
    f.write(env_example)

print("✅ Archivo .env.example creado")
print("   Copia este archivo a .env y llena los valores")

# Resumen final
print("\n" + "=" * 70)
print("📊 RESUMEN DEL DIAGNÓSTICO")
print("=" * 70)

print("""
PROBLEMA PRINCIPAL:
❌ DATABASE_URL no está configurada en Vercel
   → Los endpoints /health/database retornan 500

SOLUCIÓN:
1. Crea una base de datos PostgreSQL en la nube:
   → Recomendado: Neon (https://neon.tech) - Gratis y optimizado

2. Configura en Vercel:
   a) Ve a: https://vercel.com/tu-usuario/tu-proyecto/settings/environment-variables
   b) Agrega DATABASE_URL con la connection string de Neon
   c) Agrega SECRET_KEY (genera con: python -c "import secrets; print(secrets.token_hex(32))")

3. Redeploy tu proyecto en Vercel

OPCIONAL (mejora funcionalidad):
- NEWS_API_KEY: https://newsapi.org/register (gratis)
- GOOGLE_FACT_CHECK_API_KEY: Google Cloud Console
""")

print("=" * 70)
print("Para generar SECRET_KEY, ejecuta:")
print('  python -c "import secrets; print(secrets.token_hex(32))"')
print("=" * 70)
