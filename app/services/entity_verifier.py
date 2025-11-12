"""
Servicio de Verificación de Entidades y Eventos
Detecta personas, eventos y fechas para verificar hechos reales
"""
import spacy
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re
from typing import Dict, List, Tuple, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class EntityVerifier:
    def __init__(self):
        try:
            self.nlp = spacy.load("es_core_news_sm")
            logger.info("Modelo spaCy en español cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando modelo spaCy: {e}")
            self.nlp = None
        
        # Alias de personas conocidas (para detectar variantes)
        self.person_aliases = {
            # Políticos chilenos
            "piñera": "sebastián piñera",
            "bachelet": "michelle bachelet",
            "boric": "gabriel boric",
            "sebastián piñera": "sebastián piñera",
            "michelle bachelet": "michelle bachelet",
            "gabriel boric": "gabriel boric",
            
            # Deportistas internacionales
            "messi": "lionel messi",
            "lionel messi": "lionel messi",
            "cristiano": "cristiano ronaldo",
            "cristiano ronaldo": "cristiano ronaldo",
            "neymar": "neymar jr",
            "neymar jr": "neymar jr",
            "mbappé": "kylian mbappé",
            "kylian mbappé": "kylian mbappé",
            "casemiro": "casemiro",
            
            # Deportistas chilenos
            "alexis": "alexis sánchez",
            "alexis sánchez": "alexis sánchez",
            "arturo vidal": "arturo vidal",
            "vidal": "arturo vidal",
            "claudio bravo": "claudio bravo",
            
            # Políticos internacionales
            "biden": "joe biden",
            "joe biden": "joe biden",
            "trump": "donald trump",
            "donald trump": "donald trump",
            "milei": "javier milei",
            "javier milei": "javier milei",
            "lula": "lula da silva",
            "lula da silva": "lula da silva",
        }
        
        # Base de datos de eventos verificados (expandir con base de datos real)
        self.verified_events = {
            # Políticos chilenos
            "sebastián piñera": {
                "muerte": {
                    "fecha": "2024-02-06",
                    "fuente": "Reuters, CNN, BBC",
                    "verificado": True
                },
                "retiro_futbol": False,
                "alpacas": False
            },
            "michelle bachelet": {
                "muerte": None,  # Viva
                "retiro_politica": False
            },
            "gabriel boric": {
                "muerte": None,  # Vivo
                "renuncia": False
            },
            
            # Deportistas internacionales
            "lionel messi": {
                "muerte": None,  # Vivo
                "retiro_futbol": False,  # Aún activo en Inter Miami (2025)
                "alpacas": False,  # Nunca anunció criar alpacas
                "ranking_chilenos": False,  # No hace rankings públicos de jugadores
                "activo": True
            },
            "cristiano ronaldo": {
                "muerte": None,
                "retiro_futbol": False,  # Activo en Al-Nassr
                "activo": True
            },
            "neymar jr": {
                "muerte": None,
                "retiro_futbol": False,
                "activo": True
            },
            
            # Políticos internacionales
            "joe biden": {
                "muerte": None,
                "presidente_usa": True  # Hasta 2025
            },
            "donald trump": {
                "muerte": None,
                "presidente_usa": False  # Ex-presidente
            },
            "javier milei": {
                "muerte": None,
                "presidente_argentina": True  # Desde 2023
            }
        }
        
        # Palabras clave para eventos
        self.event_keywords = {
            "muerte": ["murió", "falleció", "muerte", "muerto", "fallecido", "óbito"],
            "terremoto": ["terremoto", "sismo", "temblor"],
            "incendio": ["incendio", "fuego", "quemó"],
            "accidente": ["accidente", "choque", "colisión"],
            "elección": ["elegido", "electo", "ganó elección"],
            "renuncia": ["renunció", "renuncia", "dimitió"]
        }
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extrae entidades del texto usando spaCy NER + diccionario de personas conocidas
        """
        if not self.nlp:
            return {"persons": [], "locations": [], "dates": [], "events": []}
        
        try:
            doc = self.nlp(text)
            
            entities = {
                "persons": [],
                "locations": [],
                "organizations": [],
                "dates": [],
                "events": []
            }
            
            # Extraer entidades nombradas con spaCy
            for ent in doc.ents:
                if ent.label_ == "PER":  # Persona
                    entities["persons"].append(ent.text)
                elif ent.label_ == "LOC":  # Localización
                    entities["locations"].append(ent.text)
                elif ent.label_ == "ORG":  # Organización
                    entities["organizations"].append(ent.text)
                elif ent.label_ == "DATE" or ent.label_ == "TIME":  # Fecha/tiempo
                    entities["dates"].append(ent.text)
            
            # MEJORA: Buscar personas conocidas en el texto (incluso sin nombre completo)
            text_lower = text.lower()
            for alias, full_name in self.person_aliases.items():
                if alias in text_lower and full_name not in [p.lower() for p in entities["persons"]]:
                    entities["persons"].append(full_name.title())
            
            # Detectar eventos basados en palabras clave
            for event_type, keywords in self.event_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        # MEJORA: Verificar contexto de "muerte"
                        if event_type == "muerte":
                            # Si "muerte" está cerca de palabras como "pena", "violadores", "medidas", etc.
                            # NO es sobre la muerte de la persona mencionada
                            political_keywords = ["pena", "violadores", "medidas", "implementar", 
                                                "política", "ley", "decreto", "asegurar la muerte"]
                            
                            # Buscar si alguna palabra política está cerca de "muerte"
                            words = text_lower.split()
                            keyword_pos = None
                            for i, word in enumerate(words):
                                if keyword in word:
                                    keyword_pos = i
                                    break
                            
                            if keyword_pos is not None:
                                # Contexto: 5 palabras antes y después
                                context_start = max(0, keyword_pos - 5)
                                context_end = min(len(words), keyword_pos + 5)
                                context = " ".join(words[context_start:context_end])
                                
                                # Si hay keywords políticos en el contexto, NO es muerte de persona
                                if any(pk in context for pk in political_keywords):
                                    logger.info(f"⚠️ 'Muerte' detectada en contexto político, no es muerte de persona")
                                    continue  # Saltar este evento
                        
                        entities["events"].append({
                            "type": event_type,
                            "keyword": keyword
                        })
                        break  # Solo un keyword por tipo
            
            logger.info(f"Entidades extraídas: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extrayendo entidades: {e}")
            return {"persons": [], "locations": [], "dates": [], "events": []}
    
    def parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """
        Convierte fechas relativas (ayer, hoy, hace 2 días) a datetime
        """
        date_str_lower = date_str.lower().strip()
        today = datetime.now()
        
        # Mapeo de fechas relativas
        relative_dates = {
            "hoy": today,
            "ayer": today - timedelta(days=1),
            "anteayer": today - timedelta(days=2),
            "hace una semana": today - timedelta(weeks=1),
            "hace un mes": today - timedelta(days=30),
        }
        
        # Buscar coincidencias exactas
        for key, value in relative_dates.items():
            if key in date_str_lower:
                return value
        
        # Intentar detectar "hace X días/semanas/meses"
        patterns = [
            (r"hace (\d+) días?", lambda x: today - timedelta(days=int(x))),
            (r"hace (\d+) semanas?", lambda x: today - timedelta(weeks=int(x))),
            (r"hace (\d+) meses?", lambda x: today - timedelta(days=int(x)*30)),
        ]
        
        for pattern, calculator in patterns:
            match = re.search(pattern, date_str_lower)
            if match:
                return calculator(match.group(1))
        
        # Intentar parsear fecha absoluta
        try:
            return date_parser.parse(date_str, fuzzy=True)
        except:
            return None
    
    async def verify_death_event(self, person_name: str, claimed_date: Optional[str] = None) -> Dict:
        """
        Verifica si una persona murió en la fecha indicada
        Primero busca en base de datos local, luego en Wikipedia si no se encuentra
        """
        person_lower = person_name.lower()
        
        # Normalizar nombre (quitar títulos, etc)
        person_lower = person_lower.replace("presidente ", "").replace("ex presidente ", "")
        person_lower = person_lower.replace("ministra ", "").replace("ministro ", "")
        
        # PASO 1: Buscar en base de datos local (rápido)
        for known_person, events in self.verified_events.items():
            if known_person in person_lower or person_lower in known_person:
                death_info = events.get("muerte")
                
                if death_info is None:
                    # Persona viva
                    return {
                        "verified": True,
                        "is_true": False,
                        "confidence": 0.95,
                        "reason": f"{person_name} está vivo/a según información verificada",
                        "source": "Base de datos interna"
                    }
                
                if claimed_date:
                    parsed_date = self.parse_relative_date(claimed_date)
                    actual_date = datetime.strptime(death_info["fecha"], "%Y-%m-%d")
                    
                    if parsed_date:
                        days_diff = abs((parsed_date - actual_date).days)
                        
                        if days_diff == 0:
                            return {
                                "verified": True,
                                "is_true": True,
                                "confidence": 0.95,
                                "reason": f"{person_name} falleció el {death_info['fecha']}",
                                "source": death_info["fuente"]
                            }
                        else:
                            return {
                                "verified": True,
                                "is_true": False,
                                "confidence": 0.95,
                                "reason": f"{person_name} falleció el {death_info['fecha']}, no {claimed_date}",
                                "source": death_info["fuente"],
                                "actual_date": death_info["fecha"]
                            }
                
                # Sin fecha específica, solo confirmar que murió
                return {
                    "verified": True,
                    "is_true": True,
                    "confidence": 0.85,
                    "reason": f"{person_name} falleció el {death_info['fecha']}",
                    "source": death_info["fuente"],
                    "actual_date": death_info["fecha"]
                }
        
        # PASO 2: No encontrado en base de datos - Buscar en Wikipedia (API gratuita)
        logger.info(f"🌐 {person_name} no está en BD local, consultando Wikipedia...")
        
        try:
            from app.services.wikipedia_verifier import wikipedia_verifier
            wiki_result = await wikipedia_verifier.verify_person_death(person_name, claimed_date)
            
            if wiki_result.get("found"):
                logger.info(f"✅ Wikipedia encontró información de {person_name}")
                
                # Traducir resultado de Wikipedia a nuestro formato
                if wiki_result.get("is_alive"):
                    return {
                        "verified": True,
                        "is_true": False,
                        "confidence": wiki_result.get("confidence", 0.90),
                        "reason": wiki_result.get("message"),
                        "source": f"Wikipedia: {wiki_result.get('source', 'N/A')}"
                    }
                
                # Si murió, verificar fecha
                if wiki_result.get("death_date"):
                    if wiki_result.get("date_matches") is False:
                        return {
                            "verified": True,
                            "is_true": False,
                            "confidence": 0.95,
                            "reason": wiki_result.get("message"),
                            "source": f"Wikipedia: {wiki_result.get('source', 'N/A')}",
                            "actual_date": wiki_result.get("death_date")
                        }
                    elif wiki_result.get("date_matches") is True:
                        return {
                            "verified": True,
                            "is_true": True,
                            "confidence": 0.90,
                            "reason": wiki_result.get("message"),
                            "source": f"Wikipedia: {wiki_result.get('source', 'N/A')}"
                        }
                    else:
                        # Muerte confirmada pero sin comparación de fecha
                        return {
                            "verified": True,
                            "is_true": True,
                            "confidence": 0.85,
                            "reason": wiki_result.get("message"),
                            "source": f"Wikipedia: {wiki_result.get('source', 'N/A')}"
                        }
            
        except Exception as e:
            logger.error(f"❌ Error consultando Wikipedia: {e}")
        
        # PASO 3: No encontrado en ninguna fuente
        return {
            "verified": False,
            "is_true": None,
            "confidence": 0.3,
            "reason": f"No hay información verificada sobre {person_name} en BD ni Wikipedia",
            "source": None
        }
    
    async def verify_claim(self, text: str) -> Dict:
        """
        Verifica un claim completo extrayendo entidades y eventos
        """
        entities = self.extract_entities(text)
        
        verification_results = {
            "has_entities": len(entities["persons"]) > 0 or len(entities["events"]) > 0,
            "entities": entities,
            "verifications": [],
            "overall_verdict": None,
            "confidence": 0.5
        }
        
        # PASO 1: Verificar claims absurdos (alpacas, rankings falsos, etc.)
        absurd_check = self._check_absurd_claims(text, entities)
        if absurd_check:
            return absurd_check
        
        # PASO 2: Verificar claims políticos controversiales sin fuente
        political_check = self._check_controversial_political_claims(text, entities)
        if political_check:
            return political_check
        
        # PASO 3: Si hay personas y eventos de muerte, verificar
        if entities["persons"] and any(e.get("type") == "muerte" for e in entities["events"]):
            for person in entities["persons"]:
                # Buscar fecha en el texto (dates detectadas por NER o palabras clave)
                claimed_date = None
                
                # Buscar fechas detectadas por spaCy
                if entities["dates"]:
                    claimed_date = entities["dates"][0]
                else:
                    # Buscar palabras clave de tiempo en el texto
                    text_lower = text.lower()
                    time_keywords = ["ayer", "hoy", "anteayer", "hace", "días", "semanas"]
                    for keyword in time_keywords:
                        if keyword in text_lower:
                            # Extraer fragmento relevante
                            words = text_lower.split()
                            for i, word in enumerate(words):
                                if keyword in word:
                                    # Tomar contexto alrededor (hasta 3 palabras)
                                    start = max(0, i-1)
                                    end = min(len(words), i+3)
                                    claimed_date = " ".join(words[start:end])
                                    break
                            break
                
                verification = await self.verify_death_event(person, claimed_date)
                verification_results["verifications"].append({
                    "person": person,
                    "event": "muerte",
                    "claimed_date": claimed_date,
                    "result": verification
                })
        
        # Determinar veredicto general
        if verification_results["verifications"]:
            # Si alguna verificación es definitiva
            for v in verification_results["verifications"]:
                if v["result"]["verified"]:
                    verification_results["overall_verdict"] = "fake" if not v["result"]["is_true"] else "real"
                    verification_results["confidence"] = v["result"]["confidence"]
                    verification_results["explanation"] = v["result"]["reason"]
                    break
        
        return verification_results
    
    def _check_absurd_claims(self, text: str, entities: Dict) -> Optional[Dict]:
        """
        Detecta claims absurdos o verificables contra la base de datos
        Ejemplos: "Messi criar alpacas", "Messi hace ranking de chilenos"
        """
        text_lower = text.lower()
        
        # Detectar personas en el claim
        if not entities["persons"]:
            return None
        
        for person in entities["persons"]:
            normalized_person = self.person_aliases.get(person.lower(), person.lower())
            
            # Verificar si la persona está en nuestra base de datos
            if normalized_person not in self.verified_events:
                continue
            
            person_data = self.verified_events[normalized_person]
            
            # CHECK 1: Retiro del fútbol cuando están activos
            if person_data.get("retiro_futbol") is False and person_data.get("activo") is True:
                retirement_keywords = ["retiro", "retira", "deja el fútbol", "deja el futbol", 
                                     "abandona el fútbol", "abandona el futbol", "se retira"]
                if any(keyword in text_lower for keyword in retirement_keywords):
                    return {
                        "has_entities": True,
                        "entities": entities,
                        "verifications": [{
                            "person": normalized_person,
                            "claim": "retiro_futbol",
                            "status": "ACTIVO - No se ha retirado"
                        }],
                        "overall_verdict": "fake",
                        "confidence": 0.90,
                        "explanation": f"{normalized_person.title()} sigue activo en el fútbol profesional - No hay anuncio oficial de retiro"
                    }
            
            # CHECK 2: Claims absurdos específicos (alpacas, etc.)
            absurd_activities = {
                "alpacas": ["alpaca", "alpacas", "criar alpacas"],
                "ranking_chilenos": ["chilenos", "ranking", "peor rendimiento", "mejores chilenos"],
                "cambio_profesion": ["dedicarse a", "cambiar de profesión", "nueva carrera"]
            }
            
            for activity_key, keywords in absurd_activities.items():
                if person_data.get(activity_key) is False:
                    if any(keyword in text_lower for keyword in keywords):
                        activity_names = {
                            "alpacas": "criar alpacas en la Patagonia",
                            "ranking_chilenos": "hacer rankings públicos de jugadores chilenos",
                            "cambio_profesion": "cambiar de profesión"
                        }
                        
                        return {
                            "has_entities": True,
                            "entities": entities,
                            "verifications": [{
                                "person": normalized_person,
                                "claim": activity_key,
                                "status": "FALSO - Nunca anunciado"
                            }],
                            "overall_verdict": "fake",
                            "confidence": 0.95,
                            "explanation": f"{normalized_person.title()} nunca ha anunciado {activity_names.get(activity_key, activity_key)} - Claim sin fuente verificable"
                        }
        
        return None
    
    def _check_controversial_political_claims(self, text: str, entities: Dict) -> Optional[Dict]:
        """
        Detecta claims políticos controversiales que requieren verificación especial
        
        Ejemplos:
        - Pena de muerte
        - Aborto
        - Políticas extremas
        - Declaraciones sin fuente
        
        Returns:
            Dict con indicador de que es claim político sin verificar
        """
        text_lower = text.lower()
        
        # Keywords de políticas controversiales
        controversial_topics = {
            "pena_muerte": ["pena de muerte", "pena capital", "muerte de violadores", 
                          "muerte de criminales", "ejecutar", "ejecución"],
            "derechos_humanos": ["aborto", "eutanasia", "matrimonio igualitario"],
            "medidas_extremas": ["prohibir", "ilegalizar", "encarcelar por", "multar por"],
            "violencia_politica": ["golpe de estado", "intervención militar", "estado de sitio"]
        }
        
        # Detectar si el claim contiene algún tema controversial
        detected_topic = None
        for topic, keywords in controversial_topics.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topic = topic
                break
        
        if not detected_topic:
            return None
        
        # Detectar si menciona políticos o gobierno
        political_keywords = [
            "gobierno", "presidente", "ministro", "diputado", "senador",
            "administración", "régimen", "gestión", "política", "partido"
        ]
        
        has_political_context = any(keyword in text_lower for keyword in political_keywords)
        
        # Detectar si menciona una persona política específica
        has_politician = False
        if entities.get("persons"):
            # Lista de políticos conocidos (se puede expandir)
            known_politicians = [
                "milei", "javier milei", "biden", "trump", "macri", 
                "fernández", "cristina", "lula", "bolsonaro"
            ]
            for person in entities["persons"]:
                if any(politician in person.lower() for politician in known_politicians):
                    has_politician = True
                    break
        
        # Si es un claim político controversial
        if has_political_context or has_politician:
            # Detectar si tiene fuente o es una afirmación sin verificar
            source_indicators = [
                "según", "anunció", "declaró", "confirmó", "informó",
                "fuente:", "según fuentes", "medios informan"
            ]
            
            has_source = any(indicator in text_lower for indicator in source_indicators)
            
            if not has_source:
                # Claim político controversial SIN fuente
                topic_names = {
                    "pena_muerte": "pena de muerte",
                    "derechos_humanos": "derechos humanos",
                    "medidas_extremas": "medidas extremas",
                    "violencia_politica": "violencia política"
                }
                
                return {
                    "has_entities": True,
                    "entities": entities,
                    "verifications": [{
                        "type": "controversial_political_claim",
                        "topic": topic_names.get(detected_topic, detected_topic),
                        "has_source": False,
                        "status": "REQUIERE_VERIFICACION"
                    }],
                    "overall_verdict": "needs_verification",  # Nuevo tipo de veredicto
                    "confidence": 0.50,
                    "explanation": f"Claim político sobre {topic_names.get(detected_topic, detected_topic)} sin fuente verificable - Requiere verificación con fuentes oficiales"
                }
        
        return None

# Instancia global
entity_verifier = EntityVerifier()
