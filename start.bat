@echo off
echo 🚀 INICIANDO BACKEND FAKE NEWS
echo.
echo ✅ Configuración PostgreSQL:
echo    Base de datos: fakenews_db
echo    Usuario: postgres / Password: postgres
echo.

cd /d "%~dp0"

REM Activar entorno virtual
echo 📦 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Crear tablas en la base de datos (si no existen)
echo 🗄️ Configurando base de datos...
alembic upgrade head

REM Iniciar servidor
echo 🌐 Iniciando servidor FastAPI...
echo.
echo 📍 URLs importantes:
echo    - Servidor: http://localhost:8000
echo    - Documentación API: http://localhost:8000/docs
echo    - Redoc: http://localhost:8000/redoc
echo.
python main.py

pause