"""
Script para crear las tablas en Neon PostgreSQL
"""
import asyncio
import os

# Configurar DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_0thzVcyex6wo@ep-fancy-wildflower-ac8i5g4l-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"

from app.database import create_tables

async def main():
    print("🔧 Creando tablas en Neon PostgreSQL...")
    try:
        await create_tables()
        print("✅ Tablas creadas exitosamente!")
        print("\nTablas creadas:")
        print("  - users (id, email, hashed_password, full_name, is_active, created_at)")
        print("  - news (id, title, content, url, publication_date, author, is_fake, ...)")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
