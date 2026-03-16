"""
Contexto global para almacenar información del usuario actual durante la ejecución de una request
"""
from contextvars import ContextVar
from typing import Optional

current_user: ContextVar[Optional[str]] = ContextVar("current_user", default=None)

def set_current_user(user_name: str) -> None:
    """Establece el usuario actual en el contexto de la request"""
    current_user.set(user_name)

def get_current_user_name() -> Optional[str]:
    """Obtiene el nombre del usuario actual"""
    return current_user.get()

def clear_current_user() -> None:
    """Limpia el usuario actual del contexto"""
    current_user.set(None)
