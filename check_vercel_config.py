"""
Verificador de configuración para Vercel Serverless
Detecta problemas comunes en deployments
"""
import os
import sys

print("=" * 70)
print("🚀 VERIFICADOR DE CONFIGURACIÓN VERCEL")
print("=" * 70)

# 1. Verificar variables de entorno requeridas
print("\n1️⃣ Variables de Entorno Requeridas:")
print("-" * 70)

required_vars = {
    "DATABASE_URL": "URL de conexión a PostgreSQL",
    "SECRET_KEY": "Clave secreta para JWT (mínimo 32 caracteres)"
}

optional_vars = {
    "NEWS_API_KEY": "NewsAPI para verificación de noticias",
    "GOOGLE_FACT_CHECK_API_KEY": "Google Fact Check API",
    "HF_API_TOKEN": "Hugging Face token (opcional, mejora rate limits)"
}

missing_required = []
configured_optional = []

for var, description in required_vars.items():
    value = os.getenv(var)
    if value:
        if var == "SECRET_KEY":
            if len(value) < 32:
                print(f"⚠️  {var}: Configurada pero MUY CORTA ({len(value)} chars)")
                print(f"   Recomendado: Mínimo 32 caracteres")
            else:
                print(f"✅ {var}: Configurada ({len(value)} chars)")
        elif var == "DATABASE_URL":
            # Ocultar password
            if "@" in value:
                parts = value.split("@")
                safe_url = parts[0].split(":")[0] + ":****@" + parts[1]
                print(f"✅ {var}: {safe_url}")
            else:
                print(f"✅ {var}: {value[:30]}...")
        else:
            print(f"✅ {var}: Configurada")
    else:
        print(f"❌ {var}: NO CONFIGURADA")
        print(f"   Descripción: {description}")
        missing_required.append(var)

print(f"\n   Variables opcionales:")
for var, description in optional_vars.items():
    value = os.getenv(var)
    if value:
        print(f"   ✅ {var}: Configurada")
        configured_optional.append(var)
    else:
        print(f"   ⚠️  {var}: No configurada (opcional)")

# 2. Verificar formato de DATABASE_URL para Vercel
print("\n2️⃣ Análisis de DATABASE_URL para Vercel:")
print("-" * 70)

db_url = os.getenv("DATABASE_URL")
if db_url:
    issues = []
    
    # Verificar protocolo
    if db_url.startswith("postgres://"):
        issues.append("URL usa 'postgres://' (legacy Heroku)")
        print("⚠️  Protocolo: postgres:// (debe ser postgresql://)")
        print("   Solución: Cambiar a 'postgresql://'")
    elif db_url.startswith("postgresql://"):
        print("✅ Protocolo: postgresql://")
    else:
        issues.append("Protocolo desconocido")
        print("❌ Protocolo desconocido")
    
    # Verificar SSL
    if "sslmode" in db_url or "ssl=true" in db_url:
        print("✅ SSL: Configurado en URL")
    else:
        issues.append("SSL no configurado")
        print("⚠️  SSL: NO configurado")
        print("   Para Vercel/producción DEBE tener SSL")
        print("   Agregar: ?sslmode=require al final de la URL")
    
    # Verificar provider común
    if "neon.tech" in db_url:
        print("✅ Provider: Neon PostgreSQL (recomendado para Vercel)")
    elif "vercel-storage" in db_url:
        print("✅ Provider: Vercel Postgres")
    elif "supabase" in db_url:
        print("✅ Provider: Supabase PostgreSQL")
    elif "railway" in db_url:
        print("✅ Provider: Railway PostgreSQL")
    elif "localhost" in db_url:
        print("⚠️  Provider: localhost (solo desarrollo)")
        issues.append("Base de datos local, no funcionará en Vercel")
    else:
        print("ℹ️  Provider: Desconocido")
    
    if issues:
        print(f"\n   ⚠️  {len(issues)} problema(s) detectado(s):")
        for issue in issues:
            print(f"      - {issue}")
else:
    print("❌ DATABASE_URL no configurada")

# 3. Verificar configuración de Vercel
print("\n3️⃣ Configuración para Vercel:")
print("-" * 70)

if os.path.exists("vercel.json"):
    print("✅ vercel.json encontrado")
    
    import json
    try:
        with open("vercel.json") as f:
            config = json.load(f)
        
        # Verificar configuraciones importantes
        if "buildCommand" in config:
            print(f"   Build Command: {config['buildCommand']}")
        
        if "framework" in config:
            print(f"   Framework: {config['framework']}")
        
        if "routes" in config or "rewrites" in config:
            print("   ✅ Routes/Rewrites configurados")
        
    except Exception as e:
        print(f"   ⚠️  Error leyendo vercel.json: {e}")
else:
    print("⚠️  vercel.json NO encontrado")
    print("   Se usará detección automática de Vercel")

# 4. Verificar archivos requeridos
print("\n4️⃣ Archivos Requeridos:")
print("-" * 70)

required_files = {
    "requirements.txt": "Dependencias Python",
    "main.py": "Punto de entrada de FastAPI",
    "app/__init__.py": "Package Python",
}

for file, description in required_files.items():
    if os.path.exists(file):
        print(f"✅ {file}: Existe")
    else:
        print(f"❌ {file}: NO ENCONTRADO")
        print(f"   {description}")

# 5. Recomendaciones para Vercel
print("\n5️⃣ Recomendaciones para Despliegue en Vercel:")
print("-" * 70)

recommendations = []

if db_url and "localhost" in db_url:
    recommendations.append({
        "title": "⚠️  Base de datos local detectada",
        "solution": "Usar base de datos en la nube:",
        "options": [
            "Neon PostgreSQL (https://neon.tech) - GRATIS, optimizado para serverless",
            "Vercel Postgres (https://vercel.com/storage/postgres) - Integrado",
            "Supabase (https://supabase.com) - GRATIS hasta 500MB",
            "Railway (https://railway.app) - GRATIS con límites"
        ]
    })

if db_url and "sslmode" not in db_url and "ssl=true" not in db_url:
    recommendations.append({
        "title": "⚠️  SSL no configurado",
        "solution": "Agregar SSL a DATABASE_URL:",
        "options": [
            "Para Neon: ?sslmode=require",
            "Para Supabase: ?sslmode=verify-full",
            "Para Railway: ?sslmode=require"
        ]
    })

if not os.getenv("NEWS_API_KEY"):
    recommendations.append({
        "title": "ℹ️  NewsAPI no configurada",
        "solution": "Opcional pero recomendado para mejor verificación:",
        "options": [
            "1. Ve a https://newsapi.org/",
            "2. Crea cuenta gratis (100 req/día)",
            "3. Agrega NEWS_API_KEY a variables de entorno en Vercel"
        ]
    })

if recommendations:
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{rec['title']}")
        print(f"   {rec['solution']}")
        for opt in rec['options']:
            print(f"      - {opt}")
else:
    print("✅ Todo configurado correctamente para Vercel")

# 6. Ejemplo de DATABASE_URL correcta
print("\n6️⃣ Ejemplo de DATABASE_URL para Vercel:")
print("-" * 70)
print("""
Para Neon PostgreSQL (recomendado):
postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/dbname?sslmode=require

Para Vercel Postgres:
postgres://default:xxxxx@ep-xxxxx-pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb?sslmode=require

Para Supabase:
postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=verify-full

⚠️  IMPORTANTE:
- DEBE incluir ?sslmode=require (o verify-full)
- DEBE ser accesible desde internet (no localhost)
- DEBE tener credenciales válidas
""")

# Resumen final
print("\n" + "=" * 70)
print("📊 RESUMEN DE CONFIGURACIÓN")
print("=" * 70)

total_checks = len(required_vars) + 3  # vars + db format + vercel.json + requirements
passed = len(required_vars) - len(missing_required)
if db_url and "sslmode" in db_url:
    passed += 1
if os.path.exists("vercel.json"):
    passed += 1
if os.path.exists("requirements.txt"):
    passed += 1

percentage = int((passed / total_checks) * 100)

print(f"Checks completados: {passed}/{total_checks} ({percentage}%)")
print(f"Variables opcionales: {len(configured_optional)}/{len(optional_vars)}")

if missing_required:
    print(f"\n❌ Variables requeridas faltantes: {', '.join(missing_required)}")

if percentage == 100:
    print("\n🎉 Configuración lista para Vercel!")
elif percentage >= 60:
    print("\n⚠️  Configuración funcional pero con mejoras recomendadas")
else:
    print("\n❌ Configuración incompleta - revisar errores arriba")

print("\n" + "=" * 70)
print("Para configurar variables en Vercel:")
print("1. Ve a tu proyecto en vercel.com")
print("2. Settings → Environment Variables")
print("3. Agrega DATABASE_URL y otras variables")
print("4. Redeploy el proyecto")
print("=" * 70)
