"""
Background tasks para ejecutar operaciones asincrónicas sin bloquear la respuesta
"""
import asyncio
import logging
from typing import Any, Dict, Optional
from src.utils.discord_notifier import DiscordNotifier

logger = logging.getLogger(__name__)


def notify_mod_created(mod: Any, user: Any) -> None:
    """
    Ejecuta la notificación de Discord de forma asincrónica en un thread separado
    
    Args:
        mod: Objeto del mod creado
        user: Usuario que creó el mod
    """
    try:
        # Obtener o crear el event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No hay event loop en este thread, crear uno nuevo
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Ejecutar la corrutina
        loop.run_until_complete(DiscordNotifier.notify_mod_created(mod, user))
    except Exception as e:
        logger.error(f"Error en background task notify_mod_created: {e}")


def notify_mod_updated(mod: Any, user: Any, changes: Dict[str, Dict[str, Any]]) -> None:
    """
    Ejecuta la notificación de actualización de Discord de forma asincrónica
    
    Args:
        mod: Objeto del mod actualizado
        user: Usuario que actualizó
        changes: Dict con cambios
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_mod_updated(mod, user, changes))
    except Exception as e:
        logger.error(f"Error en background task notify_mod_updated: {e}")


def notify_mod_approved(mod: Any, approved_by: Any) -> None:
    """
    Ejecuta la notificación de aprobación de Discord de forma asincrónica
    
    Args:
        mod: Objeto del mod
        approved_by: Usuario que aprobó
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_mod_approved(mod, approved_by))
    except Exception as e:
        logger.error(f"Error en background task notify_mod_approved: {e}")
