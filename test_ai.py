#!/usr/bin/env python3
"""
Test Completo del Sistema de IA - FakeNews_DB
==============================================

Este script verifica y prueba completamente el sistema de detección de fake news
incluyendo dependencias, modelos de IA, API endpoints y funcionalidad completa.

Uso:
    python test_ai.py

Autor: FakeNews_DB Team
Versión: 1.0.0
"""

import asyncio
import sys
import os
import time
import requests
import json
from typing import Dict, List, Optional

# Añadir el directorio app al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class AISystemTester:
    """Tester completo del sistema de IA"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {
            "dependencies": {},
            "ai_engine": {},
            "api_endpoints": {},
            "performance": {}
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
    
    def test_dependencies(self) -> bool:
        """Verifica todas las dependencias de IA"""
        self.print_header("VERIFICACIÓN DE DEPENDENCIAS")
        
        dependencies = {
            "torch": "PyTorch (Deep Learning Framework)",
            "transformers": "Transformers (Hugging Face)",
            "newspaper": "Newspaper3k (Web Scraping)",
            "bs4": "BeautifulSoup4 (HTML Parser)",
            "requests": "Requests (HTTP Client)",
            "fastapi": "FastAPI (Web Framework)",
            "sqlalchemy": "SQLAlchemy (ORM)"
        }
        
        all_passed = True
        
        for dep, description in dependencies.items():
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
                
                print(f"✅ {description:<35} v{version}")
                self.results["dependencies"][dep] = {"status": "OK", "version": version}
                
            except ImportError as e:
                print(f"❌ {description:<35} NO INSTALADO")
                self.results["dependencies"][dep] = {"status": "MISSING", "error": str(e)}
                all_passed = False
            except Exception as e:
                print(f"⚠️  {description:<35} ERROR: {e}")
                self.results["dependencies"][dep] = {"status": "ERROR", "error": str(e)}
        
        return all_passed
    
    async def test_ai_engine(self) -> bool:
        """Prueba el motor de IA directamente"""
        self.print_header("PRUEBA DEL MOTOR DE IA")
        
        try:
            from app.services.ai_analyzer import AIAnalyzer
            
            analyzer = AIAnalyzer()
            
            # Test de inicialización
            print("🔄 Inicializando modelo de IA...")
            start_time = time.time()
            await analyzer.initialize()
            init_time = time.time() - start_time
            
            model_info = analyzer.get_model_info()
            
            print(f"✅ Modelo inicializado en {init_time:.2f}s")
            print(f"   📦 Modelo: {model_info['model_name']}")
            print(f"   🏷️  Versión: {model_info['model_version']}")
            print(f"   🤖 Tipo: {'IA Real' if not model_info['is_mock'] else 'Mock/Simulado'}")
            
            self.results["ai_engine"]["initialization"] = {
                "success": True,
                "time_seconds": init_time,
                "model_info": model_info
            }
            
            # Tests de análisis
            test_cases = [
                {
                    "text": "Breaking: Scientists discover miracle cure that doctors don't want you to know!",
                    "expected": "fake",
                    "description": "Texto sensacionalista típico de fake news"
                },
                {
                    "text": "The weather forecast shows partly cloudy skies with temperatures around 20°C.",
                    "expected": "real", 
                    "description": "Información factual típica de noticias reales"
                },
                {
                    "text": "URGENT: Aliens invaded earth and government is hiding the truth from everyone!",
                    "expected": "fake",
                    "description": "Teoría conspiratoria típica"
                },
                {
                    "text": "Stock market closed higher today following positive economic indicators released by the central bank.",
                    "expected": "real",
                    "description": "Noticia económica factual"
                }
            ]
            
            self.print_subheader("Análisis de Textos de Prueba")
            
            analysis_results = []
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n🧪 Test {i}: {test_case['description']}")
                print(f"   📝 Texto: {test_case['text'][:50]}...")
                
                start_time = time.time()
                result = await analyzer.analyze_text(test_case['text'])
                analysis_time = time.time() - start_time
                
                print(f"   🎯 Resultado: {result['label']}")
                print(f"   📊 Score: {result['score']:.3f}")
                print(f"   🔍 Confianza: {result['confidence']:.3f}")
                print(f"   ⏱️  Tiempo: {result.get('processing_time_ms', int(analysis_time*1000))}ms")
                
                # Evaluar si el resultado es razonable
                label_lower = result['label'].lower()
                if test_case['expected'] == "fake" and label_lower in ['fake', 'uncertain']:
                    assessment = "✅ CORRECTO"
                elif test_case['expected'] == "real" and label_lower in ['real', 'uncertain']:
                    assessment = "✅ CORRECTO"
                else:
                    assessment = "⚠️  INESPERADO"
                
                print(f"   {assessment}")
                
                analysis_results.append({
                    "test_case": test_case,
                    "result": result,
                    "analysis_time": analysis_time,
                    "assessment": assessment
                })
            
            self.results["ai_engine"]["analysis_tests"] = analysis_results
            return True
            
        except Exception as e:
            print(f"❌ Error en motor de IA: {e}")
            self.results["ai_engine"]["error"] = str(e)
            return False
    
    def test_server_health(self) -> bool:
        """Verifica que el servidor esté funcionando"""
        self.print_header("VERIFICACIÓN DEL SERVIDOR")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Servidor FastAPI funcionando")
                print(f"   🟢 Estado: {health_data.get('status', 'unknown')}")
                print(f"   🤖 IA: {health_data.get('ai_status', 'unknown')}")
                print(f"   💾 DB: {health_data.get('database_status', 'unknown')}")
                
                self.results["api_endpoints"]["health"] = {
                    "status": "OK",
                    "data": health_data
                }
                return True
            else:
                print(f"❌ Servidor responde con error: {response.status_code}")
                self.results["api_endpoints"]["health"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ No se puede conectar al servidor")
            print("💡 Ejecuta 'python main.py' para iniciar el servidor")
            self.results["api_endpoints"]["health"] = {
                "status": "CONNECTION_ERROR"
            }
            return False
        except Exception as e:
            print(f"❌ Error verificando servidor: {e}")
            self.results["api_endpoints"]["health"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    def test_api_endpoints(self) -> bool:
        """Prueba los endpoints de la API"""
        self.print_subheader("Prueba de Endpoints de API")
        
        if not self.test_server_health():
            return False
        
        # Test del endpoint de análisis
        test_data = {
            "text": "This is a test message for API endpoint verification."
        }
        
        try:
            print("\n🔄 Probando endpoint /analyze...")
            response = requests.post(
                f"{self.base_url}/analyze",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Endpoint /analyze funcionando")
                print(f"   🎯 Label: {result['analysis']['label']}")
                print(f"   📊 Score: {result['analysis']['score']:.3f}")
                print(f"   🆔 ID: {result['analysis']['id']}")
                
                self.results["api_endpoints"]["analyze"] = {
                    "status": "OK",
                    "response": result
                }
                
            else:
                print(f"❌ Error en /analyze: {response.status_code}")
                print(f"   📋 Respuesta: {response.text}")
                self.results["api_endpoints"]["analyze"] = {
                    "status": "ERROR",
                    "code": response.status_code,
                    "response": response.text
                }
                return False
            
            # Test del endpoint de métricas
            print("\n🔄 Probando endpoint /metrics/daily...")
            response = requests.get(f"{self.base_url}/metrics/daily", timeout=10)
            
            if response.status_code == 200:
                metrics = response.json()
                print("✅ Endpoint /metrics/daily funcionando")
                print(f"   📈 Total análisis: {metrics.get('total_analyses', 0)}")
                print(f"   🎭 Fake detectados: {metrics.get('fake_count', 0)}")
                print(f"   ✅ Real detectados: {metrics.get('real_count', 0)}")
                
                self.results["api_endpoints"]["metrics"] = {
                    "status": "OK",
                    "data": metrics
                }
            else:
                print(f"⚠️  Error en /metrics: {response.status_code}")
                self.results["api_endpoints"]["metrics"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
            
            return True
            
        except Exception as e:
            print(f"❌ Error probando endpoints: {e}")
            self.results["api_endpoints"]["error"] = str(e)
            return False
    
    def performance_benchmark(self) -> Dict:
        """Ejecuta un benchmark de rendimiento"""
        self.print_header("BENCHMARK DE RENDIMIENTO")
        
        if not self.test_server_health():
            return {}
        
        test_texts = [
            "Short news text.",
            "Medium length news article with some additional details and context to test processing time.",
            "This is a longer news article that contains multiple sentences and detailed information. It simulates a real-world news article that might be analyzed for fake news detection. The purpose is to test how the system performs with varying text lengths and complexity."
        ]
        
        results = []
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n⏱️  Benchmark {i}: Texto de {len(text)} caracteres")
            
            times = []
            for j in range(3):  # 3 ejecuciones por texto
                try:
                    start = time.time()
                    response = requests.post(
                        f"{self.base_url}/analyze",
                        json={"text": text},
                        timeout=30
                    )
                    end = time.time()
                    
                    if response.status_code == 200:
                        times.append(end - start)
                    else:
                        print(f"   ❌ Error en ejecución {j+1}")
                        
                except Exception as e:
                    print(f"   ❌ Error en ejecución {j+1}: {e}")
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                print(f"   📊 Promedio: {avg_time:.3f}s")
                print(f"   🏃 Mínimo: {min_time:.3f}s")
                print(f"   🐌 Máximo: {max_time:.3f}s")
                
                results.append({
                    "text_length": len(text),
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "executions": len(times)
                })
        
        self.results["performance"]["benchmark"] = results
        return results
    
    def generate_report(self):
        """Genera un reporte final completo"""
        self.print_header("REPORTE FINAL", "=")
        
        # Resumen general
        total_tests = 0
        passed_tests = 0
        
        # Análisis de dependencias
        dep_total = len(self.results["dependencies"])
        dep_passed = sum(1 for dep in self.results["dependencies"].values() if dep["status"] == "OK")
        total_tests += dep_total
        passed_tests += dep_passed
        
        print(f"📦 Dependencias: {dep_passed}/{dep_total} ({'✅' if dep_passed == dep_total else '❌'})")
        
        # Análisis de IA
        ai_status = self.results["ai_engine"].get("initialization", {}).get("success", False)
        total_tests += 1
        if ai_status:
            passed_tests += 1
        print(f"🤖 Motor de IA: {'✅ Funcionando' if ai_status else '❌ Error'}")
        
        # Análisis de API
        api_health = self.results["api_endpoints"].get("health", {}).get("status") == "OK"
        api_analyze = self.results["api_endpoints"].get("analyze", {}).get("status") == "OK"
        total_tests += 2
        if api_health:
            passed_tests += 1
        if api_analyze:
            passed_tests += 1
        
        print(f"🌐 API Endpoints: {int(api_health) + int(api_analyze)}/2 ({'✅' if api_health and api_analyze else '❌'})")
        
        # Score final
        score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 SCORE FINAL: {score:.1f}% ({passed_tests}/{total_tests} tests)")
        
        if score >= 90:
            print("🏆 EXCELENTE: Sistema completamente operativo")
        elif score >= 70:
            print("✅ BUENO: Sistema funcional con problemas menores")
        elif score >= 50:
            print("⚠️  REGULAR: Sistema parcialmente funcional")
        else:
            print("❌ CRÍTICO: Sistema con problemas graves")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        
        if not ai_status:
            print("   - Verificar instalación de dependencias de IA")
            print("   - Ejecutar: pip install -r requirements.txt")
        
        if not api_health:
            print("   - Iniciar servidor: python main.py")
            print("   - Verificar PostgreSQL esté corriendo")
        
        if score == 100:
            print("   - ¡Todo perfecto! Sistema listo para producción 🚀")
        
        print(f"\n📊 URLs de acceso:")
        print(f"   - Documentación: http://localhost:8000/docs")
        print(f"   - Health Check: http://localhost:8000/health")
        print(f"   - Métricas: http://localhost:8000/metrics/daily")
    
    async def run_complete_test(self):
        """Ejecuta todos los tests"""
        print("🚀 INICIANDO TEST COMPLETO DEL SISTEMA DE IA")
        print("=" * 60)
        print("FakeNews_DB - Sistema de Detección de Noticias Falsas")
        print("Test automatizado de funcionalidad completa")
        
        # 1. Test de dependencias
        deps_ok = self.test_dependencies()
        
        # 2. Test del motor de IA
        ai_ok = await self.test_ai_engine()
        
        # 3. Test de endpoints API
        api_ok = self.test_api_endpoints()
        
        # 4. Benchmark de rendimiento
        if api_ok:
            self.performance_benchmark()
        
        # 5. Reporte final
        self.generate_report()

def main():
    """Función principal"""
    tester = AISystemTester()
    
    try:
        asyncio.run(tester.run_complete_test())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error crítico en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()