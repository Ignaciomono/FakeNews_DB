"""
Script de diagnóstico de base de datos
Verifica la conexión y configuración de PostgreSQL
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

print("=" * 70)
print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
print("=" * 70)

# 1. Verificar variables de entorno
print("\n1️⃣ Variables de entorno:")
print("-" * 70)

db_url = os.getenv("DATABASE_URL")
if db_url:
    # Ocultar password para seguridad
    if "@" in db_url:
        parts = db_url.split("@")
        safe_url = parts[0].split(":")[0] + ":****@" + parts[1]
        print(f"✅ DATABASE_URL configurada: {safe_url}")
    else:
        print(f"✅ DATABASE_URL configurada: {db_url[:30]}...")
else:
    print("❌ DATABASE_URL NO ENCONTRADA")
    print("   Configura en .env o variables de entorno de Vercel")
    sys.exit(1)

print(f"   ENVIRONMENT: {os.getenv('ENVIRONMENT', 'development')}")
print(f"   VERCEL: {os.getenv('VERCEL', 'No')}")

# 2. Verificar formato de URL
print("\n2️⃣ Análisis de DATABASE_URL:")
print("-" * 70)

if db_url.startswith("postgresql://"):
    print("✅ Protocolo correcto: postgresql://")
elif db_url.startswith("postgres://"):
    print("⚠️  Protocolo postgres:// detectado (Heroku legacy)")
    print("   Convirtiendo a postgresql://...")
    db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    print("❌ Protocolo desconocido")
    sys.exit(1)

# Parsear URL
try:
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    
    print(f"   Protocolo: {parsed.scheme}")
    print(f"   Usuario: {parsed.username}")
    print(f"   Host: {parsed.hostname}")
    print(f"   Puerto: {parsed.port or 5432}")
    print(f"   Base de datos: {parsed.path[1:] if parsed.path else 'N/A'}")
    
    # Verificar parámetros SSL
    if "sslmode" in db_url:
        print(f"   ✅ SSL configurado en URL")
    else:
        print(f"   ⚠️  SSL no especificado en URL")
        
except Exception as e:
    print(f"❌ Error parseando URL: {e}")
    sys.exit(1)

# 3. Test de conexión con psycopg2 (síncrono)
print("\n3️⃣ Test de conexión síncrona (psycopg2):")
print("-" * 70)

try:
    import psycopg2
    from psycopg2 import OperationalError
    
    # Convertir URL para psycopg2
    conn_url = db_url.replace("postgres://", "postgresql://", 1)
    
    print("   Intentando conectar...")
    conn = psycopg2.connect(conn_url)
    
    print("   ✅ Conexión exitosa")
    
    # Verificar versión de PostgreSQL
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   PostgreSQL: {version.split(',')[0]}")
    
    # Verificar tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"   Tablas encontradas: {len(tables)}")
    for table in tables:
        print(f"      - {table[0]}")
    
    cursor.close()
    conn.close()
    print("   ✅ Conexión cerrada correctamente")
    
except ImportError:
    print("   ⚠️  psycopg2 no instalado")
    print("   Instalar con: pip install psycopg2-binary")
except OperationalError as e:
    print(f"   ❌ Error de conexión: {e}")
    print("\n   Posibles causas:")
    print("   - Host/puerto incorrecto")
    print("   - Credenciales inválidas")
    print("   - Firewall bloqueando conexión")
    print("   - Base de datos no existe")
    print("   - SSL requerido pero no configurado")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Test de conexión async (asyncpg)
print("\n4️⃣ Test de conexión asíncrona (asyncpg):")
print("-" * 70)

async def test_async_connection():
    try:
        import asyncpg
        
        # Convertir URL para asyncpg
        async_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        async_url = async_url.replace("postgresql+asyncpg://", "postgresql://", 1)  # asyncpg usa postgresql://
        
        print("   Intentando conexión async...")
        
        conn = await asyncpg.connect(async_url)
        print("   ✅ Conexión async exitosa")
        
        # Test query
        version = await conn.fetchval("SELECT version();")
        print(f"   PostgreSQL: {version.split(',')[0]}")
        
        await conn.close()
        print("   ✅ Conexión async cerrada")
        
        return True
        
    except ImportError:
        print("   ⚠️  asyncpg no instalado")
        print("   Instalar con: pip install asyncpg")
        return False
    except Exception as e:
        print(f"   ❌ Error async: {e}")
        return False

try:
    async_result = asyncio.run(test_async_connection())
except Exception as e:
    print(f"   ❌ Error ejecutando async: {e}")
    async_result = False

# 5. Test con SQLAlchemy
print("\n5️⃣ Test con SQLAlchemy (async):")
print("-" * 70)

async def test_sqlalchemy():
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        
        # Crear engine
        async_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        print(f"   URL async: {async_url[:50]}...")
        
        engine = create_async_engine(
            async_url,
            echo=False,
            pool_pre_ping=True,  # Verificar conexión antes de usar
            pool_size=1,
            max_overflow=0,
        )
        
        print("   Engine creado")
        
        # Crear session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        print("   Session factory creada")
        
        # Test query
        async with async_session() as session:
            result = await session.execute(text("SELECT 1 as test"))
            value = result.scalar()
            print(f"   ✅ Query test exitoso: {value}")
            
        await engine.dispose()
        print("   ✅ Engine cerrado")
        
        return True
        
    except ImportError as e:
        print(f"   ⚠️  Falta dependencia: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error SQLAlchemy: {e}")
        import traceback
        traceback.print_exc()
        return False

try:
    sqlalchemy_result = asyncio.run(test_sqlalchemy())
except Exception as e:
    print(f"   ❌ Error: {e}")
    sqlalchemy_result = False

# 6. Resumen
print("\n" + "=" * 70)
print("📊 RESUMEN")
print("=" * 70)

results = {
    "Variables de entorno": bool(db_url),
    "Formato URL": True,
    "SQLAlchemy async": sqlalchemy_result,
}

for check, passed in results.items():
    symbol = "✅" if passed else "❌"
    print(f"{symbol} {check}")

total = sum(results.values())
percentage = int((total / len(results)) * 100)

print(f"\n{'=' * 70}")
print(f"Resultado: {total}/{len(results)} checks pasados ({percentage}%)")

if percentage == 100:
    print("🎉 Base de datos completamente funcional")
elif percentage >= 50:
    print("⚠️  Base de datos con problemas - revisar errores arriba")
else:
    print("❌ Base de datos no accesible - verificar configuración")

print("=" * 70)
