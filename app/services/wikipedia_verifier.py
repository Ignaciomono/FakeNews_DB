"""
Servicio de Verificación con Wikipedia y Wikidata (100% GRATIS)
Verifica personas y eventos automáticamente sin base de datos estática
"""
import aiohttp
import logging
from typing import Dict, Optional, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class WikipediaVerifier:
    """Verificador de personas y eventos usando Wikipedia/Wikidata (APIs gratuitas)"""
    
    WIKIPEDIA_API_URL = "https://es.wikipedia.org/w/api.php"
    WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
    WIKIDATA_ENTITY_URL = "https://www.wikidata.org/wiki/Special:EntityData/{}.json"
    
    @staticmethod
    async def search_person(person_name: str, language: str = "es") -> Optional[Dict]:
        """
        Busca una persona en Wikipedia y obtiene información básica
        
        Args:
            person_name: Nombre de la persona a buscar
            language: Código de idioma (default: es)
            
        Returns:
            Dict con información de la persona o None si no se encuentra
        """
        try:
            # Buscar en Wikipedia
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": person_name,
                "srlimit": 1,
                "utf8": 1
            }
            
            # User-Agent requerido por Wikipedia
            headers = {
                "User-Agent": "DeepFakeDetector/1.0 (Educational Project; Contact: test@example.com)"
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    WikipediaVerifier.WIKIPEDIA_API_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Wikipedia search failed: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    if not data.get("query", {}).get("search"):
                        logger.info(f"No Wikipedia results for: {person_name}")
                        return None
                    
                    # Obtener el primer resultado
                    first_result = data["query"]["search"][0]
                    page_id = first_result["pageid"]
                    title = first_result["title"]
                    
                    # Obtener contenido de la página
                    return await WikipediaVerifier._get_page_content(page_id, title)
                    
        except Exception as e:
            logger.error(f"Error searching Wikipedia for {person_name}: {e}")
            return None
    
    @staticmethod
    async def _get_page_content(page_id: int, title: str) -> Dict:
        """Obtiene el contenido completo de una página de Wikipedia"""
        try:
            params = {
                "action": "query",
                "format": "json",
                "pageids": page_id,
                "prop": "extracts|info|pageprops",
                "exintro": 1,
                "explaintext": 1,
                "inprop": "url"
            }
            
            headers = {
                "User-Agent": "DeepFakeDetector/1.0 (Educational Project; Contact: test@example.com)"
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    WikipediaVerifier.WIKIPEDIA_API_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    page_data = data["query"]["pages"][str(page_id)]
                    
                    extract = page_data.get("extract", "")
                    
                    # Extraer información de nacimiento/muerte del extracto
                    birth_date = WikipediaVerifier._extract_birth_date(extract)
                    death_date = WikipediaVerifier._extract_death_date(extract)
                    
                    result = {
                        "name": title,
                        "page_id": page_id,
                        "url": page_data.get("fullurl", ""),
                        "summary": extract[:500],  # Primeros 500 caracteres
                        "birth_date": birth_date,
                        "death_date": death_date,
                        "is_alive": death_date is None,
                        "source": "wikipedia",
                        "verified": True
                    }
                    
                    # Si encontramos Wikidata ID, obtener más datos
                    wikidata_id = page_data.get("pageprops", {}).get("wikibase_item")
                    if wikidata_id:
                        wikidata_info = await WikipediaVerifier._get_wikidata_info(wikidata_id)
                        if wikidata_info:
                            result.update(wikidata_info)
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error getting page content: {e}")
            return None
    
    @staticmethod
    def _extract_birth_date(text: str) -> Optional[str]:
        """Extrae fecha de nacimiento del texto de Wikipedia"""
        # Patrones comunes: (Madrid, 24 de junio de 1987) o nacido el 24 de junio de 1987
        patterns = [
            r'\(.*?(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})\)',
            r'nacid[oa]\s+el\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            r'\(.*?(\d{4})\)',  # Solo año en paréntesis
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def _extract_death_date(text: str) -> Optional[str]:
        """Extrae fecha de muerte del texto de Wikipedia"""
        # Patrones: falleció el X, murió el X, (1987-2024)
        patterns = [
            r'falleci[óo]\s+el\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            r'muri[óo]\s+el\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            r'\d{4}\s*[-–]\s*(\d{4})',  # Años: 1987-2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    async def _get_wikidata_info(wikidata_id: str) -> Optional[Dict]:
        """Obtiene información estructurada de Wikidata"""
        try:
            url = WikipediaVerifier.WIKIDATA_ENTITY_URL.format(wikidata_id)
            
            headers = {
                "User-Agent": "DeepFakeDetector/1.0 (Educational Project; Contact: test@example.com)"
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    entity = data.get("entities", {}).get(wikidata_id, {})
                    
                    claims = entity.get("claims", {})
                    
                    # P569: date of birth, P570: date of death
                    birth_claim = claims.get("P569", [{}])[0]
                    death_claim = claims.get("P570", [{}])[0]
                    
                    result = {}
                    
                    # Fecha de nacimiento
                    if birth_claim.get("mainsnak", {}).get("datavalue"):
                        birth_time = birth_claim["mainsnak"]["datavalue"]["value"].get("time")
                        if birth_time:
                            result["birth_date_wikidata"] = birth_time.lstrip("+")
                    
                    # Fecha de muerte
                    if death_claim.get("mainsnak", {}).get("datavalue"):
                        death_time = death_claim["mainsnak"]["datavalue"]["value"].get("time")
                        if death_time:
                            result["death_date_wikidata"] = death_time.lstrip("+")
                            result["is_alive"] = False
                    else:
                        result["is_alive"] = True
                    
                    result["wikidata_id"] = wikidata_id
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error getting Wikidata info: {e}")
            return None
    
    @staticmethod
    async def verify_person_death(person_name: str, claimed_date: Optional[str] = None) -> Dict:
        """
        Verifica si una persona ha muerto y cuándo
        
        Args:
            person_name: Nombre de la persona
            claimed_date: Fecha reclamada (opcional)
            
        Returns:
            Dict con resultado de verificación
        """
        # Buscar persona en Wikipedia
        person_info = await WikipediaVerifier.search_person(person_name)
        
        if not person_info:
            return {
                "verified": False,
                "found": False,
                "person": person_name,
                "message": f"No se encontró información de {person_name} en Wikipedia",
                "confidence": 0.3
            }
        
        # Si la persona está viva
        if person_info.get("is_alive"):
            return {
                "verified": True,
                "found": True,
                "person": person_name,
                "is_alive": True,
                "death_claim": False,
                "message": f"{person_name} está vivo según Wikipedia/Wikidata",
                "confidence": 0.90,
                "source": person_info.get("url")
            }
        
        # Si la persona ha muerto
        death_date = person_info.get("death_date_wikidata") or person_info.get("death_date")
        
        if not death_date:
            return {
                "verified": False,
                "found": True,
                "person": person_name,
                "message": f"Se encontró {person_name} pero no hay fecha de muerte clara",
                "confidence": 0.5
            }
        
        # Verificar fecha si se proporcionó
        if claimed_date:
            # Comparar fechas (simplificado - mejorar con parsing de fechas)
            claimed_normalized = claimed_date.lower().strip()
            
            if claimed_normalized in death_date.lower():
                return {
                    "verified": True,
                    "found": True,
                    "person": person_name,
                    "is_alive": False,
                    "death_date": death_date,
                    "date_matches": True,
                    "message": f"{person_name} falleció el {death_date} - Fecha correcta",
                    "confidence": 0.90,
                    "source": person_info.get("url")
                }
            else:
                return {
                    "verified": True,
                    "found": True,
                    "person": person_name,
                    "is_alive": False,
                    "death_date": death_date,
                    "date_matches": False,
                    "claimed_date": claimed_date,
                    "message": f"{person_name} falleció el {death_date}, no {claimed_date}",
                    "confidence": 0.95,
                    "source": person_info.get("url")
                }
        
        # Sin fecha reclamada, solo confirmar muerte
        return {
            "verified": True,
            "found": True,
            "person": person_name,
            "is_alive": False,
            "death_date": death_date,
            "message": f"{person_name} falleció el {death_date}",
            "confidence": 0.85,
            "source": person_info.get("url")
        }


# Instancia global
wikipedia_verifier = WikipediaVerifier()
