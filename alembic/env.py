import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# --- PASO 1: Asegurarnos de que el proyecto esté en el path de Python ---
# Agrega el directorio raíz del proyecto al path de Python para que encuentre 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- PASO 2: Cargar las variables de entorno desde el archivo .env ---
from dotenv import load_dotenv
load_dotenv()

# --- PASO 3: Importar la Base y TODOS tus modelos ---
# Alembic necesita "ver" los modelos para poder crear las tablas
from app.database import Base
from app.models import news, user

# --- PASO 4: Configuración estándar de Alembic ---
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- PASO 5: Establecer el objetivo para 'autogenerate' ---
target_metadata = Base.metadata

def get_url():
    """Obtiene la URL de la BD desde la configuración y la hace síncrona."""
    from app.config import settings
    # Reemplazamos +asyncpg para que sea síncrono, si existe
    db_url = settings.DATABASE_URL
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")
    return db_url

def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'."""
    # Forzamos a Alembic a usar la URL de nuestra configuración
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

