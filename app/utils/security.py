import bleach
import re
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Utilidades de seguridad y sanitización"""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitiza texto para prevenir ataques"""
        if not text:
            return ""
        
        # Remover HTML/XML tags
        text = bleach.clean(text, tags=[], strip=True)
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        
        # Remover caracteres de control
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        return text.strip()
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Valida el tamaño del archivo"""
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # MB a bytes
        return file_size <= max_size
    
    @staticmethod
    def validate_content_length(content: str) -> bool:
        """Valida la longitud del contenido"""
        return len(content) <= settings.MAX_CONTENT_LENGTH
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Verifica que el nombre del archivo sea seguro"""
        if not filename:
            return False
        
        # Caracteres peligrosos
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        
        for char in dangerous_chars:
            if char in filename:
                return False
        
        # Nombres reservados en Windows
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    @staticmethod
    def allowed_file_extension(filename: str) -> bool:
        """Verifica que la extensión del archivo sea permitida"""
        allowed_extensions = {'.txt', '.doc', '.docx', '.pdf', '.rtf'}
        
        if '.' not in filename:
            return False
        
        extension = '.' + filename.rsplit('.', 1)[1].lower()
        return extension in allowed_extensions

class RateLimiter:
    """Rate limiter simple en memoria"""
    
    def __init__(self):
        self.requests = {}  # IP -> [timestamps]
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 500
    
    def is_allowed(self, client_ip: str) -> bool:
        """Verifica si la IP puede hacer más requests"""
        import time
        
        current_time = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Limpiar requests antiguos (más de 1 hora)
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] 
            if current_time - ts < 3600
        ]
        
        # Verificar límite por hora
        if len(self.requests[client_ip]) >= self.max_requests_per_hour:
            return False
        
        # Verificar límite por minuto
        recent_requests = [
            ts for ts in self.requests[client_ip]
            if current_time - ts < 60
        ]
        
        if len(recent_requests) >= self.max_requests_per_minute:
            return False
        
        # Agregar request actual
        self.requests[client_ip].append(current_time)
        return True

# Instancias globales
security_utils = SecurityUtils()
rate_limiter = RateLimiter()