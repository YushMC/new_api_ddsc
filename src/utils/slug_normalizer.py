import unicodedata
import re


def normalize_slug(text: str) -> str:
    """
    Normaliza un texto para usar como slug o identifier.
    - Elimina acentos y caracteres diacríticos
    - Convierte a minúsculas
    - Reemplaza espacios por guiones
    - Elimina caracteres especiales
    - Limpia guiones múltiples y de bordes
    
    Ejemplos:
    - "Acción" -> "accion"
    - "C++ Mod" -> "c-mod"
    - "Sci-Fi (2024)" -> "sci-fi-2024"
    """
    # Remover acentos y diacríticos
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Reemplazar espacios por guiones
    text = text.replace(" ", "-")
    
    # Remover caracteres especiales, mantener solo letras, números y guiones
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Remover guiones múltiples
    text = re.sub(r'-+', '-', text)
    
    # Remover guiones al inicio y final
    text = text.strip('-')
    
    return text


def normalize_identifier(name: str) -> str:
    """Alias para normalize_slug, mantener compatibilidad"""
    return normalize_slug(name)
