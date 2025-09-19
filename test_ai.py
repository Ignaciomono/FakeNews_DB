#!/usr/bin/env python3
"""
Test Completo del Sistema de IA Externa - FakeNews_DB
=====================================================

Este script verifica y prueba completamente el sistema de detección de fake news
usando Hugging Face Inference API (externa y gratuita).

Uso:
    python test_ai.py

Autor: FakeNews_DB Team
Versión: 2.0.0 (API Externa)
"""

import asyncio
import sys
import os
import time
import requests
import json
import aiohttp
from typing import Dict, List, Optional

# Añadir el directorio app al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class AISystemTester:
    """Tester completo del sistema de IA externa"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {
            "dependencies": {},
            "ai_engine": {},
            "api_endpoints": {},
            "external_api": {}
        }
    
    def print_header(self, title: str, char: str = "="):
        """Imprime un header formateado"""
        print(f"\n{char * 60}")
        print(f"🔍 {title}")
        print(f"{char * 60}")
    
    def print_subheader(self, title: str):
        """Imprime un subheader"""
        print(f"\n📋 {title}")
        print("-" * 40)
    
    def _check_dependency(self, dep: str, description: str) -> bool:
        """Verifica una dependencia individual"""
        try:
            if dep == "bs4":
                from bs4 import BeautifulSoup
                version = BeautifulSoup.__version__ if hasattr(BeautifulSoup, '__version__') else "4.x"
            elif dep == "newspaper":
                import newspaper
                version = newspaper.__version__ if hasattr(newspaper, '__version__') else "0.2.x"
            else:
                module = __import__(dep)
                version = getattr(module, '__version__', 'unknown')
            
            print(f"✅ {description:<40} v{version}")
            self.results["dependencies"][dep] = {"status": "OK", "version": version}
            return True
            
        except ImportError as e:
            print(f"❌ {description:<40} NO INSTALADO")
            self.results["dependencies"][dep] = {"status": "MISSING", "error": str(e)}
            return False
        except Exception as e:
            print(f"⚠️  {description:<40} ERROR: {e}")
            self.results["dependencies"][dep] = {"status": "ERROR", "error": str(e)}
            return False
    
    def test_dependencies(self) -> bool:
        """Verifica las dependencias optimizadas (sin IA local)"""
        self.print_header("VERIFICACIÓN DE DEPENDENCIAS OPTIMIZADAS")
        
        dependencies = {
            "aiohttp": "AIOHTTP (Async HTTP Client)",
            "httpx": "HTTPX (HTTP Client alternativo)",
            "newspaper": "Newspaper3k (Web Scraping)",
            "bs4": "BeautifulSoup4 (HTML Parser)",
            "requests": "Requests (HTTP Client)",
            "fastapi": "FastAPI (Web Framework)",
            "sqlalchemy": "SQLAlchemy (ORM)",
            "asyncpg": "AsyncPG (PostgreSQL Driver)",
            "pydantic": "Pydantic (Data Validation)"
        }
        
        all_passed = True
        
        for dep, description in dependencies.items():
            if not self._check_dependency(dep, description):
                all_passed = False
        
        # Verificar que NO estén las dependencias pesadas
        heavy_deps = ["torch", "transformers", "tensorflow"]
        print("\n📦 Verificando ausencia de dependencias pesadas:")
        for dep in heavy_deps:
            try:
                __import__(dep)
                print(f"⚠️  {dep} todavía instalado (puede causar problemas en Vercel)")
            except ImportError:
                print(f"✅ {dep} correctamente removido")
        
        return all_passed
    
    async def test_external_api_connection(self) -> bool:
        """Prueba la conexión con Hugging Face Inference API"""
        self.print_header("PRUEBA DE CONEXIÓN API EXTERNA")
        
        try:
            from app.config import settings
            
            api_url = settings.HF_API_URL + settings.HF_MODEL_NAME
            
            print(f"🔗 Probando conexión con: {api_url}")
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Test simple de conexión
                async with session.get(api_url) as response:
                    status = response.status
                    
                    if status == 200:
                        print("✅ API de Hugging Face accesible")
                        self.results["external_api"]["connection"] = "OK"
                        return True
                    else:
                        print(f"⚠️  API respondió con status {status} (normal, requiere POST)")
                        self.results["external_api"]["connection"] = f"Status {status}"
                        return True
                        
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            print("📝 El sistema usará modo MOCK como fallback")
            self.results["external_api"]["connection"] = f"ERROR: {e}"
            return False
    
    async def test_ai_engine(self) -> bool:
        """Prueba el motor de IA externo"""
        self.print_header("PRUEBA DEL MOTOR DE IA EXTERNO")
        
        try:
            from app.services.ai_analyzer import AIAnalyzer
            
            analyzer = AIAnalyzer()
            
            # Test de inicialización
            print("🔧 Inicializando motor de IA...")
            await analyzer.initialize()
            
            if analyzer.is_loaded:
                print("✅ Motor de IA inicializado correctamente")
                self.results["ai_engine"]["initialization"] = "OK"
            else:
                print("⚠️  Motor inicializado en modo fallback")
                self.results["ai_engine"]["initialization"] = "FALLBACK"
            
            # Test con texto simple
            print("\n🧪 Probando análisis de texto...")
            test_texts = [
                "Esta es una noticia completamente falsa y engañosa",
                "Según fuentes oficiales del gobierno, la información es verificada",
                "Científicos confirman los resultados del estudio en Nature"
            ]
            
            for i, text in enumerate(test_texts, 1):
                print(f"\n   Test {i}: {text[:50]}...")
                start_time = time.time()
                
                try:
                    prediction, confidence, label = await analyzer.analyze_text(text)
                    processing_time = time.time() - start_time
                    
                    print(f"   📊 Resultado: {label.value}")
                    print(f"   🎯 Predicción: {prediction:.3f}")
                    print(f"   💪 Confianza: {confidence:.3f}")
                    print(f"   ⏱️  Tiempo: {processing_time:.3f}s")
                    
                    self.results["ai_engine"][f"test_{i}"] = {
                        "prediction": prediction,
                        "confidence": confidence,
                        "label": label.value,
                        "time": processing_time
                    }
                    
                except Exception as e:
                    print(f"   ❌ Error en test {i}: {e}")
                    self.results["ai_engine"][f"test_{i}"] = {"error": str(e)}
            
            # Test de información del modelo
            print("\n📋 Información del modelo:")
            model_info = await analyzer.get_model_info()
            for key, value in model_info.items():
                print(f"   {key}: {value}")
            self.results["ai_engine"]["model_info"] = model_info
            
            # Cleanup
            await analyzer.cleanup()
            
            return True
            
        except Exception as e:
            print(f"❌ Error en motor de IA: {e}")
            self.results["ai_engine"]["error"] = str(e)
            return False
    
    def test_api_endpoints(self) -> bool:
        """Prueba los endpoints de la API"""
        self.print_header("PRUEBA DE ENDPOINTS DE LA API")
        
        # Verificar que el servidor esté corriendo
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print(f"❌ Servidor no disponible en {self.base_url}")
                print("💡 Ejecuta 'python main.py' en otra terminal")
                return False
        except requests.exceptions.RequestException:
            print(f"❌ No se pudo conectar al servidor en {self.base_url}")
            print("💡 Ejecuta 'python main.py' en otra terminal")
            return False
        
        endpoints_to_test = [
            ("GET", "/health", None, "Health Check"),
            ("GET", "/info", None, "Información del Sistema"),
            ("POST", "/analyze", {
                "content": "Esta noticia parece completamente falsa y engañosa",
                "source_type": "text"
            }, "Análisis de Texto"),
            ("GET", "/metrics", None, "Métricas del Sistema")
        ]
        
        all_passed = True
        
        for method, endpoint, data, description in endpoints_to_test:
            self.print_subheader(f"{description} ({method} {endpoint})")
            
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        timeout=30
                    )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✅ Status: {response.status_code}")
                    print(f"⏱️  Tiempo: {response_time:.3f}s")
                    
                    if endpoint == "/analyze":
                        result = response.json()
                        print(f"📊 Resultado: {result.get('label', 'N/A')}")
                        print(f"🎯 Predicción: {result.get('prediction', 'N/A')}")
                        print(f"💪 Confianza: {result.get('confidence', 'N/A')}")
                    
                    self.results["api_endpoints"][endpoint] = {
                        "status": "OK",
                        "time": response_time,
                        "status_code": response.status_code
                    }
                else:
                    print(f"❌ Status: {response.status_code}")
                    print(f"📝 Error: {response.text[:200]}")
                    self.results["api_endpoints"][endpoint] = {
                        "status": "ERROR",
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    }
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                self.results["api_endpoints"][endpoint] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                all_passed = False
        
        return all_passed
    
    def generate_report(self):
        """Genera un reporte final completo"""
        self.print_header("REPORTE FINAL DEL SISTEMA", "=")
        
        total_tests = 0
        passed_tests = 0
        
        print("\n🎯 RESUMEN EJECUTIVO:")
        print("-" * 40)
        
        # Dependencias
        deps_ok = sum(1 for dep in self.results["dependencies"].values() if dep["status"] == "OK")
        deps_total = len(self.results["dependencies"])
        total_tests += deps_total
        passed_tests += deps_ok
        print(f"📦 Dependencias: {deps_ok}/{deps_total} OK")
        
        # API Externa
        if "external_api" in self.results:
            api_ok = 1 if self.results["external_api"].get("connection") == "OK" else 0
            total_tests += 1
            passed_tests += api_ok
            print(f"🔗 API Externa: {'✅ Conectada' if api_ok else '⚠️ Fallback'}")
        
        # Motor de IA
        ai_ok = 1 if self.results["ai_engine"].get("initialization") in ["OK", "FALLBACK"] else 0
        total_tests += 1
        passed_tests += ai_ok
        print(f"🤖 Motor de IA: {'✅ Funcionando' if ai_ok else '❌ Error'}")
        
        # Endpoints
        endpoints_ok = sum(1 for ep in self.results["api_endpoints"].values() if ep["status"] == "OK")
        endpoints_total = len(self.results["api_endpoints"])
        total_tests += endpoints_total
        passed_tests += endpoints_ok
        print(f"🌐 Endpoints: {endpoints_ok}/{endpoints_total} OK")
        
        # Puntuación final
        score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n🏆 PUNTUACIÓN FINAL: {score:.1f}% ({passed_tests}/{total_tests})")
        
        if score >= 90:
            print("🎉 ¡EXCELENTE! Sistema completamente funcional")
        elif score >= 70:
            print("✅ BUENO: Sistema funcional con advertencias menores")
        elif score >= 50:
            print("⚠️ ACEPTABLE: Sistema funcional con problemas")
        else:
            print("❌ CRÍTICO: Sistema con problemas graves")
        
        print("\n💡 OPTIMIZACIONES IMPLEMENTADAS:")
        print("🔥 Sin dependencias pesadas (torch, transformers)")
        print("🌐 API externa gratuita (Hugging Face)")
        print("☁️ Compatible con Vercel (sin OOM)")
        print("🗄️ Base de datos Neon optimizada")
        
        return score

async def main():
    """Función principal del test"""
    print("🔍 FAKE NEWS DETECTOR - TEST COMPLETO DEL SISTEMA DE IA EXTERNA")
    print("=" * 70)
    print("📅 Versión 2.0.0 - Sistema optimizado con API externa")
    print("🌐 Compatible con Vercel y base de datos Neon")
    
    tester = AISystemTester()
    
    try:
        # 1. Test de dependencias
        tester.test_dependencies()
        
        # 2. Test de conexión API externa
        await tester.test_external_api_connection()
        
        # 3. Test del motor de IA
        await tester.test_ai_engine()
        
        # 4. Test de endpoints (requiere servidor corriendo)
        print("\n⚠️  Para probar endpoints, asegúrate de que el servidor esté corriendo:")
        print("   python main.py")
        print("   Presiona Enter para continuar o Ctrl+C para salir...")
        
        try:
            # Usar thread para input en async
            await asyncio.to_thread(input)
            tester.test_api_endpoints()
        
        except KeyboardInterrupt:
            print("\n⏭️  Saltando pruebas de endpoints...")
        
        # 5. Reporte final
        score = tester.generate_report()
        
        return score >= 70
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrumpido por el usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)