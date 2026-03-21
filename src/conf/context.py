"""
Contexto global para almacenar información del usuario actual durante la ejecución de una request
"""
from contextvars import ContextVar
from typing import Optional

current_user_id: ContextVar[Optional[int]] = ContextVar("current_user_id", default=None)

def set_current_user_id(user_id: int) -> None:
    """Establece el ID del usuario actual en el contexto de la request"""
    current_user_id.set(user_id)

def get_current_user_id() -> Optional[int]:
    """Obtiene el ID del usuario actual"""
    return current_user_id.get()

def clear_current_user() -> None:
    """Limpia el usuario actual del contexto"""
    current_user_id.set(None)
