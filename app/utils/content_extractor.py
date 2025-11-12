import requests
try:
    import newspaper
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

from bs4 import BeautifulSoup
import re
import asyncio
import aiohttp
from typing import Optional, Tuple
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extractor de contenido de URLs de noticias"""
    
    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT
        self.max_content_length = settings.MAX_CONTENT_LENGTH
    
    async def extract_from_url(self, url: str) -> Tuple[Optional[str], str, bool]:
        """
        Extrae contenido de una URL.
        
        Returns:
            Tuple[Optional[str], str, bool]: (contenido, método_usado, éxito)
        """
        # En ambientes serverless, newspaper3k causa problemas de event loop
        # Usar solo BeautifulSoup que es async nativo
        content, success = await self._extract_with_beautifulsoup(url)
        if success and content:
            return content, "beautifulsoup", True
        
        # Fallback a newspaper solo si BeautifulSoup falla Y estamos en ambiente no-serverless
        if NEWSPAPER_AVAILABLE and not self._is_serverless():
            try:
                content, success = await self._extract_with_newspaper(url)
                if success and content:
                    return content, "newspaper", True
            except Exception as e:
                logger.warning(f"Newspaper fallback falló: {e}")
        
        return None, "none", False
    
    def _is_serverless(self) -> bool:
        """Detecta si estamos corriendo en ambiente serverless (Vercel, AWS Lambda, etc)"""
        import os
        return any([
            os.environ.get('VERCEL'),
            os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
            os.environ.get('NETLIFY'),
        ])
    
    async def _extract_with_newspaper(self, url: str) -> Tuple[Optional[str], bool]:
        """Extrae contenido usando newspaper3k"""
        try:
            if not NEWSPAPER_AVAILABLE:
                return None, False
            
            # Usar asyncio.to_thread para evitar problemas de event loop en serverless
            try:
                article = await asyncio.to_thread(self._newspaper_extract_sync, url)
            except AttributeError:
                # Fallback para Python < 3.9 o ambientes sin to_thread
                # En serverless de Vercel, mejor no usar newspaper
                logger.warning("asyncio.to_thread no disponible, saltando newspaper")
                return None, False
            
            if article and article.text:
                # Limpiar y truncar contenido
                content = self._clean_content(article.text)
                return content, True
            
            return None, False
            
        except Exception as e:
            logger.error(f"Error extrayendo con newspaper: {e}")
            return None, False
    
    def _newspaper_extract_sync(self, url: str):
        """Función síncrona para newspaper3k"""
        try:
            if not NEWSPAPER_AVAILABLE:
                return None
                
            article = Article(url)
            article.download()
            article.parse()
            return article
        except Exception as e:
            logger.error(f"Error en newspaper sync: {e}")
            return None
    
    async def _extract_with_beautifulsoup(self, url: str) -> Tuple[Optional[str], bool]:
        """Extrae contenido usando BeautifulSoup como fallback"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None, False
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remover scripts, styles y otros elementos no deseados
                    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                        script.decompose()
                    
                    # Buscar contenido en orden de prioridad
                    content = self._extract_article_content(soup)
                    
                    if content:
                        content = self._clean_content(content)
                        return content, True
                    
                    return None, False
                    
        except Exception as e:
            logger.error(f"Error extrayendo con BeautifulSoup: {e}")
            return None, False
    
    def _extract_article_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el contenido del artículo usando selectores comunes"""
        
        # Selectores comunes para contenido de artículos
        selectors = [
            'article',
            '[class*="article-content"]',
            '[class*="post-content"]',
            '[class*="entry-content"]',
            '[class*="content-body"]',
            '[class*="story-body"]',
            '[class*="article-body"]',
            '[id*="article-content"]',
            '[id*="post-content"]',
            'main',
            '.content',
            '#content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # Tomar el primer elemento que tenga suficiente texto
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 200:  # Mínimo 200 caracteres
                        return text
        
        # Si no encuentra selectores específicos, buscar párrafos
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            if len(content) > 200:
                return content
        
        # Último recurso: todo el texto del body
        body = soup.find('body')
        if body:
            return body.get_text(strip=True)
        
        return None
    
    def _clean_content(self, content: str) -> str:
        """Limpia y procesa el contenido extraído"""
        if not content:
            return ""
        
        # Normalizar espacios en blanco
        content = re.sub(r'\s+', ' ', content)
        
        # Remover caracteres de control
        content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
        
        # Truncar si es muy largo
        if len(content) > self.max_content_length:
            content = content[:self.max_content_length] + "..."
        
        return content.strip()
    
    def validate_url(self, url: str) -> bool:
        """Valida que la URL sea segura para extraer"""
        if not url or not isinstance(url, str):
            return False
        
        # Verificar esquema
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Lista de dominios bloqueados (ejemplo)
        blocked_domains = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '192.168.',
            '10.',
            '172.16.',
            '172.17.',
            '172.18.',
            '172.19.',
            '172.20.',
            '172.21.',
            '172.22.',
            '172.23.',
            '172.24.',
            '172.25.',
            '172.26.',
            '172.27.',
            '172.28.',
            '172.29.',
            '172.30.',
            '172.31.'
        ]
        
        url_lower = url.lower()
        for domain in blocked_domains:
            if domain in url_lower:
                return False
        
        return True

# Instancia global del extractor
content_extractor = ContentExtractor()