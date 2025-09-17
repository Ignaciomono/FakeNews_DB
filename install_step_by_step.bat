@echo off
echo 🚀 INSTALACION POR PASOS - FAKE NEWS DETECTOR
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version
echo.

REM Crear entorno virtual
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

REM Activar entorno virtual
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo 📋 SELECCIONA UNA OPCION:
echo.
echo 1. Instalación BÁSICA (rápida, sin IA)
echo 2. Instalación COMPLETA (lenta, con IA)
echo 3. Solo actualizar pip
echo 4. Salir
echo.
set /p choice="Ingresa tu opción (1-4): "

if "%choice%"=="1" (
    echo.
    echo 📥 Instalando dependencias básicas...
    pip install --upgrade pip
    pip install -r requirements_basic.txt
    goto :basic_complete
)

if "%choice%"=="2" (
    echo.
    echo 📥 Instalando todas las dependencias (puede tardar 10-15 minutos)...
    echo Presiona Ctrl+C si quieres cancelar y usar opción 1
    timeout /t 5
    pip install --upgrade pip
    pip install -r requirements.txt
    goto :complete
)

if "%choice%"=="3" (
    echo.
    echo 🔄 Actualizando pip...
    pip install --upgrade pip
    echo ✅ Pip actualizado
    goto :end
)

if "%choice%"=="4" (
    goto :end
)

echo ❌ Opción no válida
goto :end

:basic_complete
echo.
echo ✅ INSTALACIÓN BÁSICA COMPLETADA!
echo.
echo 🔧 SIGUIENTE PASOS:
echo 1. Editar .env (ya creado) - configurar PostgreSQL
echo 2. Ejecutar: alembic upgrade head  
echo 3. Ejecutar: python main.py
echo.
echo 💾 Base de datos PostgreSQL configurada:
echo    - Base de datos: fakenews_db
echo    - Usuario: postgres  
echo    - Password: postgres
echo    - Host: localhost:5432
echo.
echo ⚠️  NOTA: El sistema usará un modelo MOCK de IA para pruebas
echo    Para IA real, ejecuta después: pip install transformers torch newspaper3k
echo.
goto :end

:complete
echo.
echo ✅ INSTALACIÓN COMPLETA TERMINADA!
echo.
echo 🔧 SIGUIENTE PASOS:
echo 1. Configurar PostgreSQL
echo 2. Editar .env con tus credenciales
echo 3. Ejecutar: alembic upgrade head
echo 4. Ejecutar: python main.py
echo.

:end
if not exist ".env" (
    echo 📝 Creando archivo .env...
    copy .env.example .env
    echo ⚠️  Recuerda editar .env con tus datos PostgreSQL
)

echo.
echo 📚 Lee README.md para instrucciones detalladas
pause