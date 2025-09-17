@echo off
echo 🧪 PRUEBAS RAPIDAS DEL SISTEMA
echo.

REM Verificar que el servidor está corriendo
echo 📡 Verificando si el servidor está ejecutándose...
timeout /t 2 >nul

curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Servidor no responde en http://localhost:8000
    echo    Asegúrate de que el servidor esté ejecutándose con:
    echo    python main.py
    echo.
    pause
    exit /b 1
)

echo ✅ Servidor respondiendo correctamente
echo.

echo 🔍 Probando endpoint de salud...
curl -s http://localhost:8000/health
echo.
echo.

echo 🧠 Probando análisis de texto...
curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/x-www-form-urlencoded" -d "text=Esta es una noticia de prueba para verificar que el sistema de detección de fake news funciona correctamente."
echo.
echo.

echo 📊 Probando métricas...
curl -s http://localhost:8000/metrics/summary
echo.
echo.

echo 🎉 TODAS LAS PRUEBAS COMPLETADAS
echo.
echo 🌐 URLs importantes:
echo    - API: http://localhost:8000
echo    - Docs: http://localhost:8000/docs
echo    - Health: http://localhost:8000/health
echo.
pause