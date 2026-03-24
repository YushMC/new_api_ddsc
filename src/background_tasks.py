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


def notify_mod_approved(mod: Any, approved_by: Any, creator_name: Optional[str] = None) -> None:
    """
    Ejecuta la notificación de aprobación de Discord de forma asincrónica
    
    Args:
        mod: Objeto del mod
        approved_by: Usuario que aprobó
        creator_name: Nombre del creador del mod
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_mod_approved(mod, approved_by, creator_name))
    except Exception as e:
        logger.error(f"Error en background task notify_mod_approved: {e}")


def notify_mod_completed(mod: Any) -> None:
    """
    Ejecuta la notificación de completamiento de mod de forma asincrónica
    
    Args:
        mod: Objeto del mod completado (con imágenes y créditos)
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_mod_completed(mod))
    except Exception as e:
        logger.error(f"Error en background task notify_mod_completed: {e}")


def notify_genres_added(mod: Any, genres: list, user: Any) -> None:
    """
    Ejecuta la notificación de adición de géneros de forma asincrónica
    
    Args:
        mod: Objeto del mod
        genres: Lista de géneros agregados
        user: Usuario que agregó los géneros
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_genres_added(mod, genres, user))
    except Exception as e:
        logger.error(f"Error en background task notify_genres_added: {e}")


def notify_genres_removed(mod: Any, genres: list, user: Any) -> None:
    """
    Ejecuta la notificación de remoción de géneros de forma asincrónica
    
    Args:
        mod: Objeto del mod
        genres: Lista de géneros removidos
        user: Usuario que removió los géneros
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_genres_removed(mod, genres, user))
    except Exception as e:
        logger.error(f"Error en background task notify_genres_removed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# NOTIFICACIONES PARA GÉNEROS
# ═════════════════════════════════════════════════════════════════════════════

def notify_genre_status_changed(genre: Any, user: Any, is_active: bool) -> None:
    """Notifica cambio de estado de género (activado/desactivado)"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_genre_status_changed(genre, user, is_active))
    except Exception as e:
        logger.error(f"Error en background task notify_genre_status_changed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# NOTIFICACIONES PARA COLECCIONES
# ═════════════════════════════════════════════════════════════════════════════

def notify_collection_created(collection: Any, user: Any) -> None:
    """Notifica creación de colección"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_collection_created(collection, user))
    except Exception as e:
        logger.error(f"Error en background task notify_collection_created: {e}")


def notify_collection_updated(collection: Any, user: Any, changes: Dict[str, Dict[str, Any]]) -> None:
    """Notifica actualización de colección"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_collection_updated(collection, user, changes))
    except Exception as e:
        logger.error(f"Error en background task notify_collection_updated: {e}")


def notify_collection_status_changed(collection: Any, user: Any, is_active: bool) -> None:
    """Notifica cambio de estado de colección (activada/desactivada)"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if is_active:
            loop.run_until_complete(DiscordNotifier.notify_collection_reactivated(collection, user))
        else:
            loop.run_until_complete(DiscordNotifier.notify_collection_deleted(collection, user))
    except Exception as e:
        logger.error(f"Error en background task notify_collection_status_changed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# NOTIFICACIONES PARA MODS EN COLECCIONES
# ═════════════════════════════════════════════════════════════════════════════

def notify_mod_added_to_collection(mod: Any, collection: Any, user: Any) -> None:
    """Notifica adición de mod a colección"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_mod_added_to_collection(mod, collection, user))
    except Exception as e:
        logger.error(f"Error en background task notify_mod_added_to_collection: {e}")


def notify_mod_removed_from_collection(mod: Any, collection: Any, user: Any) -> None:
    """Notifica remoción de mod de colección"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_mod_removed_from_collection(mod, collection, user))
    except Exception as e:
        logger.error(f"Error en background task notify_mod_removed_from_collection: {e}")


def notify_mods_collection_status_changed(mod: Any, collection: Any, user: Any, is_active: bool) -> None:
    """Notifica cambio de estado en relación mods-colecciones (activada/desactivada)"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if is_active:
            loop.run_until_complete(DiscordNotifier.notify_mods_collection_reactivated(mod, collection, user))
        else:
            loop.run_until_complete(DiscordNotifier.notify_mods_collection_deactivated(mod, collection, user))
    except Exception as e:
        logger.error(f"Error en background task notify_mods_collection_status_changed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# NOTIFICACIONES PARA IMÁGENES
# ═════════════════════════════════════════════════════════════════════════════

def notify_image_uploaded(image: Any, mod: Any, user: Any) -> None:
    """Notifica carga de imagen"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_image_uploaded(image, mod, user))
    except Exception as e:
        logger.error(f"Error en background task notify_image_uploaded: {e}")


def notify_image_replaced(image: Any, mod: Any, user: Any) -> None:
    """Notifica reemplazo de imagen"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_image_replaced(image, mod, user))
    except Exception as e:
        logger.error(f"Error en background task notify_image_replaced: {e}")


def notify_image_deleted(image: Any, mod: Any, user: Any) -> None:
    """Notifica eliminación de imagen"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(DiscordNotifier.notify_image_deleted(image, mod, user))
    except Exception as e:
        logger.error(f"Error en background task notify_image_deleted: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# BANNERS
# ═════════════════════════════════════════════════════════════════════════════

def create_banner_for_approved_mod(mod: Any, approved_by: Any) -> None:
    """
    Crea un banner automáticamente cuando se aprueba un mod
    
    Args:
        mod: Objeto del mod aprobado
        approved_by: Usuario que aprobó el mod
    """
    try:
        from src.conf.database import DATABASE_INIT
        from src.services.banners import CRUD_BANNER
        
        db = DATABASE_INIT().get_db()
        crud = CRUD_BANNER(db)
        
        # Crear banner automático
        crud.create_banner_for_approved_mod(
            mod_id=mod.id,
            mod_name=mod.name,
            created_by=approved_by.id if hasattr(approved_by, 'id') else approved_by
        )
    except Exception as e:
        logger.error(f"Error en background task create_banner_for_approved_mod: {e}")
