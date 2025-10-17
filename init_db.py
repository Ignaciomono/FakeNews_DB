"""
Script para inicializar la base de datos en Vercel/Neon
Aplica migraciones de Alembic automáticamente
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Ejecuta las migraciones de Alembic"""
    try:
        logger.info("🔄 Iniciando migraciones de base de datos...")
        
        # Verificar que existe DATABASE_URL
        if not os.getenv("DATABASE_URL"):
            logger.warning("⚠️  DATABASE_URL no configurada, saltando migraciones")
            return False
        
        # Verificar que existe el directorio de alembic
        if not Path("alembic").exists():
            logger.error("❌ Directorio alembic no encontrado")
            return False
        
        # Ejecutar migraciones
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Migraciones aplicadas correctamente")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ Error en migraciones: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error ejecutando migraciones: {e}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 Inicializando base de datos...")
    
    # Ejecutar migraciones
    success = run_migrations()
    
    if success:
        logger.info("✅ Base de datos inicializada correctamente")
        sys.exit(0)
    else:
        logger.warning("⚠️  Migraciones no aplicadas, continuando de todas formas...")
        sys.exit(0)  # No fallar el deploy

if __name__ == "__main__":
    main()
