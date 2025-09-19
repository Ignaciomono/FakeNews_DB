@echo off
echo.
echo ==========================================
echo 🚀 INSTALACION COMPLETA - FAKENEWS_DB
echo ==========================================
echo.
echo Este script instalara todo lo necesario:
echo - Entorno virtual Python
echo - Todas las dependencias de IA
echo - Configuracion de base de datos
echo - Verificacion del sistema
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no encontrado
    echo.
    echo 💡 Instala Python desde: https://www.python.org/downloads/
    echo    - Asegurate de marcar "Add to PATH"
    echo    - Version minima requerida: Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version
echo.

REM Verificar PostgreSQL
echo 🔍 Verificando PostgreSQL...
pg_config --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PostgreSQL no detectado en PATH
    echo.
    echo 📋 INSTRUCCIONES POSTGRESQL:
    echo    1. Descarga PostgreSQL: https://www.postgresql.org/download/
    echo    2. Durante instalacion, usa password: postgres
    echo    3. Crea base de datos: fakenews_db
    echo    4. O ejecuta: createdb -U postgres fakenews_db
    echo.
    set /p continue="Continuar con instalacion? (s/n): "
    if /i not "%continue%"=="s" exit /b 1
) else (
    echo ✅ PostgreSQL encontrado
    pg_config --version
)

echo.
echo ==========================================
echo 📦 INSTALANDO DEPENDENCIAS
echo ==========================================
echo.

REM Crear entorno virtual
if not exist "venv" (
    echo 🔄 Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

REM Activar entorno virtual
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo 🔄 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias básicas primero
echo.
echo 📥 Instalando dependencias básicas...
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic python-multipart python-dotenv requests bleach asyncpg aiohttp beautifulsoup4

if errorlevel 1 (
    echo ❌ Error instalando dependencias básicas
    pause
    exit /b 1
)

echo ✅ Dependencias básicas instaladas

REM Instalar dependencias de IA (más pesadas)
echo.
echo 🤖 Instalando dependencias de IA...
echo ⏳ AVISO: Esto puede tardar 5-10 minutos dependiendo de tu conexión
echo.

pip install transformers torch newspaper3k lxml[html_clean]

if errorlevel 1 (
    echo ⚠️  Error instalando algunas dependencias de IA
    echo 💡 El sistema funcionará con modelo simulado
    echo.
    set /p continue="Continuar? (s/n): "
    if /i not "%continue%"=="s" exit /b 1
) else (
    echo ✅ Dependencias de IA instaladas correctamente
)

echo.
echo ==========================================
echo 🛠️  CONFIGURANDO PROYECTO
echo ==========================================
echo.

REM Crear archivo .env si no existe
if not exist ".env" (
    echo 📝 Creando archivo de configuracion .env...
    copy .env.example .env >nul
    echo ✅ Archivo .env creado
    echo.
    echo ⚠️  IMPORTANTE: Edita .env con tus credenciales PostgreSQL
    echo    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fakenews_db
) else (
    echo ✅ Archivo .env ya existe
)

REM Configurar base de datos
echo.
echo 🗄️  Configurando base de datos...
alembic upgrade head

if errorlevel 1 (
    echo ❌ Error configurando base de datos
    echo.
    echo 💡 SOLUCION:
    echo    1. Verifica que PostgreSQL esté corriendo
    echo    2. Crea la base de datos: createdb -U postgres fakenews_db
    echo    3. Edita .env con las credenciales correctas
    echo.
    pause
    exit /b 1
)

echo ✅ Base de datos configurada correctamente

echo.
echo ==========================================
echo 🧪 VERIFICANDO INSTALACION
echo ==========================================
echo.

REM Ejecutar test del sistema
echo 🔍 Ejecutando test completo del sistema...
python test_ai.py

echo.
echo ==========================================
echo 🎉 INSTALACION COMPLETADA
echo ==========================================
echo.

echo ✅ Sistema FakeNews_DB instalado correctamente!
echo.
echo 🚀 COMO USAR:
echo.
echo 1. Iniciar servidor:
echo    python main.py
echo.
echo 2. Abrir documentacion:
echo    http://localhost:8000/docs
echo.
echo 3. Ejecutar tests:
echo    python test_ai.py
echo.
echo 📁 ARCHIVOS IMPORTANTES:
echo    - main.py          : Servidor principal
echo    - test_ai.py       : Test completo del sistema
echo    - .env             : Configuracion (editar si es necesario)
echo    - README.md        : Documentacion completa
echo.
echo 🔗 URLS DEL SISTEMA:
echo    - API: http://localhost:8000
echo    - Docs: http://localhost:8000/docs
echo    - Health: http://localhost:8000/health
echo.

pause