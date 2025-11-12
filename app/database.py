from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, NullPool
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.config import settings

# Configuración síncrona para Alembic (comentada - solo usar async)
# SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuración asíncrona para FastAPI
# Remover ?sslmode=require porque asyncpg usa ssl=True por defecto
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("?sslmode=require", "")

# En serverless (Vercel), usar NullPool para no mantener conexiones persistentes
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=NullPool,  # Sin pool de conexiones para serverless
    echo=False,
    connect_args={
        "server_settings": {"application_name": "fakenews_api"},
        "command_timeout": 60,
        "ssl": "require",  # SSL habilitado para Neon
    }
)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
)

Base = declarative_base()

# Dependency para obtener la sesión de base de datos
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Función para crear las tablas
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)