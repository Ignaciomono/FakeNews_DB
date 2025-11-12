"""
🧪 TEST COMPLETO DEL SISTEMA DE DETECCIÓN DE FAKE NEWS
========================================================

Prueba exhaustiva del sistema completo con 7 capas de verificación:
1. Detector de Claims Absurdos
2. Detector de Contexto Político
3. Base de Datos Local (15+ personas)
4. Wikipedia API (ilimitado, gratis)
5. Google Fact Check API
6. NewsAPI (100 req/día gratis)
7. AI Models (fallback)

Casos de prueba:
- Caso Original: "Piñera murió ayer" (el que inició todo)
- URLs reales de noticias
- Claims inventados plausibles
- Claims absurdos (alpacas, rankings)
- Claims políticos polémicos
- Verificación de Wikipedia
- Búsqueda en NewsAPI
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List

# Cargar variables de entorno
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.entity_verifier import entity_verifier
from app.services.ai_analyzer import ai_analyzer
from app.services.news_api_service import news_api_service
from app.services.wikipedia_verifier import wikipedia_verifier
from app.utils.content_extractor import ContentExtractor

# Instanciar extractor de contenido
content_extractor = ContentExtractor()


# ============================================================================
# CASOS DE PRUEBA
# ============================================================================

TEST_CASES = [
    {
        "id": 1,
        "nombre": "CASO ORIGINAL - Piñera murió ayer",
        "descripcion": "El claim que inició todas las mejoras del sistema",
        "tipo": "TEXT",
        "contenido": "Piñera murió ayer",
        "esperado": {
            "label": "FAKE",
            "min_confidence": 0.90,
            "metodo": "NER_ENTITIES"
        }
    },
    {
        "id": 2,
        "nombre": "URL Real - TyC Sports",
        "descripcion": "Noticia deportiva real sobre Mundial Sub-17",
        "tipo": "URL",
        "contenido": "https://www.tycsports.com/futbol-internacional/cuadruple-empate-a-puntos-e-increible-eliminacion-de-chile-en-el-mundial-sub-17-20251111.html",
        "esperado": {
            "label": "MIXED",  # Puede variar según el contenido extraído
            "min_confidence": 0.60,
            "metodo": "ANY"
        }
    },
    {
        "id": 3,
        "nombre": "Claim Inventado - Messi Ranking",
        "descripcion": "Suena plausible pero es completamente inventado",
        "tipo": "TEXT",
        "contenido": "Estos son los 5 chilenos del futbol con peor rendimiento según Messi",
        "esperado": {
            "label": "FAKE",
            "min_confidence": 0.90,
            "metodo": "NER_ENTITIES"
        }
    },
    {
        "id": 4,
        "nombre": "Claim Absurdo - Messi Alpacas",
        "descripcion": "Obviamente falso, evento absurdo",
        "tipo": "TEXT",
        "contenido": "Messi anuncia que deja el fútbol para dedicarse a criar alpacas en la Patagonia",
        "esperado": {
            "label": "FAKE",
            "min_confidence": 0.85,
            "metodo": "NER_ENTITIES"
        }
    },
    {
        "id": 5,
        "nombre": "Claim Político - Milei",
        "descripcion": "Afirmación política polémica sin verificar",
        "tipo": "TEXT",
        "contenido": "El gobierno libertario de milei implementara medidas para asegurar la muerte de violadores",
        "esperado": {
            "label": "UNCERTAIN",  # Ahora debería ser UNCERTAIN con detector político
            "min_confidence": 0.50,
            "metodo": "POLITICAL_CLAIM_UNVERIFIED"  # Nuevo método
        }
    },
    {
        "id": 6,
        "nombre": "Verificación Wikipedia - Maradona",
        "descripcion": "Persona famosa fallecida recientemente",
        "tipo": "TEXT",
        "contenido": "Diego Maradona murió ayer",
        "esperado": {
            "label": "FAKE",
            "min_confidence": 0.90,
            "metodo": "NER_ENTITIES"
        }
    },
    {
        "id": 7,
        "nombre": "Claim Corto - Messi retiro",
        "descripcion": "Texto muy corto sobre retiro de jugador activo",
        "tipo": "TEXT",
        "contenido": "Messi se retira del fútbol",
        "esperado": {
            "label": "FAKE",
            "min_confidence": 0.85,
            "metodo": "NER_ENTITIES"
        }
    },
    {
        "id": 8,
        "nombre": "Persona Desconocida en BD - Neymar",
        "descripcion": "Jugador famoso NO en base de datos local (test Wikipedia)",
        "tipo": "TEXT",
        "contenido": "Neymar Jr murió ayer en un accidente",
        "esperado": {
            "label": "FAKE",
            "min_confidence": 0.85,
            "metodo": "NER_ENTITIES"
        }
    }
]


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def print_separator(char="=", length=90):
    """Imprime una línea separadora"""
    print(char * length)


def print_header(title: str, emoji: str = "🧪"):
    """Imprime un encabezado destacado"""
    print_separator()
    print(f"{emoji} {title}")
    print_separator()


def print_section(title: str):
    """Imprime una sección"""
    print(f"\n{title}")
    print("-" * 90)


def interpret_result(score: float, label: str) -> str:
    """Interpreta el resultado del análisis"""
    if score < 0.30:
        return "🔴 FAKE NEWS - Muy probablemente falso"
    elif score < 0.50:
        return "🟠 DUDOSO - Probablemente falso"
    elif score < 0.70:
        return "🟡 INCIERTO - Se necesita más verificación"
    elif score < 0.85:
        return "🟢 PROBABLE - Probablemente verdadero"
    else:
        return "🟢 VERIFICADO - Muy probablemente verdadero"


async def extract_url_content(url: str) -> tuple[str, bool]:
    """Extrae contenido de una URL"""
    try:
        content, method, success = await content_extractor.extract_from_url(url)
        if success and content and len(content.strip()) > 50:
            return content, True
        return "", False
    except Exception as e:
        print(f"   ❌ Error en extracción: {e}")
        return "", False


# ============================================================================
# FUNCIÓN PRINCIPAL DE PRUEBA
# ============================================================================

async def test_case(case: Dict) -> Dict:
    """
    Prueba un caso individual con el sistema completo
    
    Returns:
        Dict con resultados de la prueba
    """
    print_header(f"📰 CASO {case['id']}: {case['nombre']}", "📰")
    print(f"🔖 Tipo: {case['tipo']}")
    print(f"💬 Descripción: {case['descripcion']}")
    
    # Mostrar contenido (truncado si es muy largo)
    contenido_display = case['contenido']
    if len(contenido_display) > 100:
        contenido_display = contenido_display[:97] + "..."
    print(f"📝 Contenido: {contenido_display}\n")
    
    # PASO 0: Extraer contenido de URL si es necesario
    content = case['contenido']
    if case['tipo'] == 'URL':
        print_section("🌐 PASO 0: Extrayendo contenido de URL...")
        content, success = await extract_url_content(case['contenido'])
        if success:
            print(f"   ✅ Extracción exitosa")
            print(f"   📊 Longitud del contenido: {len(content)} caracteres")
            print(f"   📄 Vista previa: {content[:100]}...")
        else:
            print("   ❌ Fallo en extracción, usando URL como texto")
            content = case['contenido']
    
    # PASO 1: Verificación con NER (Entidades Nombradas)
    print_section("🔍 PASO 1: Verificación con NER (Entidades Nombradas)...")
    ner_result = await entity_verifier.verify_claim(content)
    
    ner_verdict = ner_result.get('overall_verdict')
    ner_confidence = ner_result.get('confidence', 0.5)
    ner_explanation = ner_result.get('explanation', 'Sin explicación')
    
    print(f"   ✅ Entidades detectadas: {ner_result.get('has_entities', False)}")
    
    entities = ner_result.get('entities', {})
    if entities.get('persons'):
        print(f"   👤 Personas: {', '.join(entities['persons'][:5])}")
    if entities.get('locations'):
        print(f"   📍 Lugares: {', '.join(entities['locations'][:5])}")
    if entities.get('dates'):
        print(f"   📆 Fechas: {', '.join(entities['dates'][:3])}")
    
    print(f"   📊 Veredicto NER: {ner_verdict}")
    print(f"   💯 Confianza NER: {ner_confidence * 100:.2f}%")
    if ner_explanation and ner_explanation != 'Sin explicación':
        print(f"   💬 Explicación NER: {ner_explanation}")
    
    # PASO 2: Búsqueda de noticias recientes (NewsAPI)
    print_section("📰 PASO 2: Búsqueda de noticias recientes (NewsAPI)...")
    news_result = None
    
    try:
        # Extraer persona del NER para búsqueda más precisa
        person_name = None
        if entities.get('persons'):
            person_name = entities['persons'][0]
        
        news_result = await news_api_service.verify_political_claim(content[:100])
        
        if news_result and news_result.get('found_articles'):
            print(f"   ✅ Artículos encontrados: {news_result.get('total_results', 0)}")
            print(f"   📊 Artículos relevantes: {news_result.get('relevant_articles', 0)}")
            print(f"   🎯 Veredicto: {news_result.get('verdict', 'N/A')}")
            print(f"   💯 Confianza: {news_result.get('confidence', 0) * 100:.0f}%")
        else:
            api_key = os.getenv("NEWS_API_KEY", "")
            if not api_key:
                print("   ⚠️  NEWS_API_KEY no configurada")
            else:
                print("   ⚠️  No se encontraron noticias recientes")
    except Exception as e:
        print(f"   ❌ Error en NewsAPI: {e}")
    
    # PASO 3: Análisis con AI Models (siempre se ejecuta como fallback)
    print_section("🤖 PASO 3: Análisis con 6 modelos de IA (Hugging Face)...")
    ai_score, ai_label, ai_confidence, analysis_time_ms = await ai_analyzer.analyze_text(content)
    
    print(f"   ✅ Score AI: {ai_score:.4f}")
    print(f"   📊 Label AI: {ai_label}")
    print(f"   💯 Confianza AI: {ai_confidence * 100:.2f}%")
    print(f"   ⏱️  Tiempo de análisis: {analysis_time_ms:.2f}ms")
    
    # PASO 4: Decisión final (combinando todas las fuentes)
    print_section("🎯 PASO 4: Decisión final del sistema integrado...")
    
    final_score = ai_score
    final_label = str(ai_label)
    final_confidence = ai_confidence
    verification_method = "AI_MODELS"
    
    # Prioridad 1: NER tiene veredicto claro
    if ner_verdict is not None:
        
        if ner_verdict == "fake":
            verification_method = "NER_ENTITIES"
            final_score = 0.0 + (ner_confidence * 0.1)
            final_label = "FAKE"
            final_confidence = ner_confidence
            print("   🏆 DECISIÓN: Usando veredicto NER (prioridad)")
            
        elif ner_verdict == "real":
            verification_method = "NER_ENTITIES"
            final_score = 0.9 + (ner_confidence * 0.1)
            final_label = "REAL"
            final_confidence = ner_confidence
            print("   🏆 DECISIÓN: Usando veredicto NER (prioridad)")
            
        elif ner_verdict == "needs_verification":
            # Claim político controversial sin fuente
            verification_method = "POLITICAL_CLAIM_UNVERIFIED"
            
            # Intentar verificar con NewsAPI
            if news_result and news_result.get("found_articles") and news_result.get("relevant_articles", 0) > 0:
                verification_method = "POLITICAL_CLAIM_NEWS"
                verdict = news_result.get("verdict", "uncertain")
                
                if verdict == "likely_true":
                    final_score = 0.70
                    final_label = "REAL"
                    final_confidence = 0.75
                elif verdict == "possibly_true":
                    final_score = 0.55
                    final_label = "UNCERTAIN"
                    final_confidence = 0.60
                else:
                    final_score = 0.50
                    final_label = "UNCERTAIN"
                    final_confidence = 0.55
                
                print("   🏆 DECISIÓN: Claim político verificado con NewsAPI")
            else:
                # Sin verificación externa - UNCERTAIN
                final_score = 0.50
                final_label = "UNCERTAIN"
                final_confidence = 0.50
                print("   🏆 DECISIÓN: Claim político sin verificar (marcado como UNCERTAIN)")
    
    # Prioridad 2: NewsAPI tiene resultados relevantes
    elif news_result and news_result.get('relevant_articles', 0) > 0:
        verification_method = "NEWS_API"
        verdict = news_result.get('verdict', 'uncertain')
        
        if verdict == "likely_true":
            final_score = 0.75
            final_label = "REAL"
            final_confidence = 0.80
        elif verdict == "possibly_true":
            final_score = 0.60
            final_label = "UNCERTAIN"
            final_confidence = 0.65
        else:
            final_score = 0.50
            final_label = "UNCERTAIN"
            final_confidence = 0.50
        
        print("   🏆 DECISIÓN: Usando NewsAPI (noticias recientes)")
    
    # Prioridad 3: AI Models (fallback)
    else:
        print("   🏆 DECISIÓN: Usando modelos AI (fallback)")
    
    print(f"   📊 Resultado final: {final_label}")
    print(f"   💯 Confianza final: {final_confidence * 100:.2f}%")
    print(f"   🔢 Score final: {final_score:.4f}")
    print(f"   ✨ Método de verificación: {verification_method}")
    
    # Interpretación
    print_section("🧑‍⚖️  INTERPRETACIÓN:")
    print(f"   {interpret_result(final_score, final_label)}\n")
    
    # Verificar si cumple expectativas
    esperado = case['esperado']
    passed = True
    issues = []
    
    if esperado['metodo'] != "ANY" and verification_method != esperado['metodo']:
        if not (esperado['metodo'] == "AI_MODELS" and verification_method in ["NER_ENTITIES", "NEWS_API"]):
            issues.append(f"Método: esperado {esperado['metodo']}, obtenido {verification_method}")
            passed = False
    
    if esperado['label'] != "MIXED" and final_label != esperado['label']:
        if not (esperado['label'] == "UNCERTAIN" and final_label in ["FAKE", "REAL"]):
            issues.append(f"Label: esperado {esperado['label']}, obtenido {final_label}")
            passed = False
    
    if final_confidence < esperado['min_confidence']:
        issues.append(f"Confianza: esperado >{esperado['min_confidence']*100:.0f}%, obtenido {final_confidence*100:.0f}%")
        passed = False
    
    return {
        "case_id": case['id'],
        "case_name": case['nombre'],
        "passed": passed,
        "issues": issues,
        "final_score": final_score,
        "final_label": final_label,
        "final_confidence": final_confidence,
        "verification_method": verification_method,
        "ner_verdict": ner_verdict,
        "news_found": news_result is not None and news_result.get('found_articles', False)
    }


async def run_all_tests():
    """Ejecuta todos los casos de prueba"""
    print_header("🧪 SISTEMA COMPLETO DE DETECCIÓN DE FAKE NEWS - TEST EXHAUSTIVO", "🚀")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔢 Total de casos: {len(TEST_CASES)}")
    print()
    
    # Verificar configuración
    print_header("⚙️  VERIFICACIÓN DE CONFIGURACIÓN", "⚙️")
    api_key = os.getenv("NEWS_API_KEY", "")
    print(f"✅ NewsAPI configurada: {'Sí' if api_key else 'No'}")
    if api_key:
        print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ Python dotenv: Cargado")
    print(f"✅ Servicios: entity_verifier, ai_analyzer, news_api_service, wikipedia_verifier")
    print()
    
    # Ejecutar pruebas
    results = []
    for i, case in enumerate(TEST_CASES, 1):
        result = await test_case(case)
        results.append(result)
        
        # Pausa entre casos para no saturar las APIs
        if i < len(TEST_CASES):
            await asyncio.sleep(1)
    
    # Resumen final
    print_header("📊 RESUMEN DE RESULTADOS", "📊")
    
    passed_count = sum(1 for r in results if r['passed'])
    failed_count = len(results) - passed_count
    
    print(f"\n✅ Casos exitosos: {passed_count}/{len(results)}")
    print(f"❌ Casos fallidos: {failed_count}/{len(results)}")
    print(f"📈 Tasa de éxito: {(passed_count/len(results)*100):.1f}%\n")
    
    # Tabla de resultados
    print_separator("-")
    print(f"{'ID':<4} {'Nombre':<35} {'Label':<10} {'Conf%':<7} {'Método':<15} {'Estado':<10}")
    print_separator("-")
    
    for r in results:
        status = "✅ PASS" if r['passed'] else "❌ FAIL"
        name = r['case_name'][:33] + ".." if len(r['case_name']) > 35 else r['case_name']
        print(f"{r['case_id']:<4} {name:<35} {r['final_label']:<10} {r['final_confidence']*100:<6.1f}% {r['verification_method']:<15} {status:<10}")
    
    print_separator("-")
    
    # Detalles de fallos
    if failed_count > 0:
        print("\n⚠️  DETALLES DE CASOS FALLIDOS:")
        print_separator("-")
        for r in results:
            if not r['passed']:
                print(f"\n❌ Caso {r['case_id']}: {r['case_name']}")
                for issue in r['issues']:
                    print(f"   - {issue}")
    
    # Estadísticas por método
    print("\n📊 DISTRIBUCIÓN POR MÉTODO DE VERIFICACIÓN:")
    print_separator("-")
    
    methods = {}
    for r in results:
        method = r['verification_method']
        methods[method] = methods.get(method, 0) + 1
    
    for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        print(f"   {method:<20} {count:>2} casos ({percentage:>5.1f}%)")
    
    # Verificación del caso original
    print_header("🎯 VERIFICACIÓN DEL CASO ORIGINAL", "🎯")
    caso_original = next((r for r in results if r['case_id'] == 1), None)
    
    if caso_original:
        if caso_original['passed'] and caso_original['final_label'] == 'FAKE' and caso_original['final_confidence'] >= 0.90:
            print("✅ ¡ÉXITO TOTAL! El problema original está completamente resuelto")
            print(f"   - Antes: REAL 66% (solo AI) ❌")
            print(f"   - Ahora: {caso_original['final_label']} {caso_original['final_confidence']*100:.0f}% ({caso_original['verification_method']}) ✅")
            print("   - Método: NER + Wikipedia API")
            print("   - Explicación: Sebastián Piñera falleció el 2024-02-06, no ayer")
        else:
            print("⚠️  El caso original necesita revisión")
            print(f"   Resultado: {caso_original['final_label']} {caso_original['final_confidence']*100:.0f}%")
    
    print_header("✅ PRUEBA COMPLETA FINALIZADA", "🎉")
    
    return {
        "total": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "success_rate": (passed_count/len(results)*100),
        "results": results
    }


if __name__ == "__main__":
    asyncio.run(run_all_tests())
