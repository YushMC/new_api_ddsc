"""
Servicio para enviar notificaciones a Discord
"""
import aiohttp
import asyncio
from src.conf.discord_config import DiscordConfig
from src.models.enums import UserRolEnum
from typing import Optional, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Maneja el envío de notificaciones a Discord mediante webhooks"""
    
    @staticmethod
    def _safe_enum_value(value: Any) -> str:
        """
        Safely extracts enum value or converts to string
        Handles both enum objects and string values from JWT tokens
        
        Args:
            value: Enum object or string
        
        Returns:
            String representation of the value
        """
        if hasattr(value, 'value'):
            return value.value
        return str(value)
    
    @staticmethod
    async def notify_mod_created(mod: Any, user: Any) -> bool:
        """
        Notifica cuando se crea un nuevo mod
        
        Args:
            mod: Objeto del mod creado
            user: Usuario que creó el mod
        
        Returns:
            True si se envió exitosamente, False si fallo (no interrumpe API)
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            is_approved = user.rol != UserRolEnum.UPLOADER
            embed = DiscordNotifier._format_embed_created(mod, user, is_approved)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando creación de mod a Discord: {e}")
            return False
    
    @staticmethod
    async def notify_mod_updated(mod: Any, user: Any, changes: Dict[str, Dict[str, Any]]) -> bool:
        """
        Notifica cuando se actualiza un mod
        
        Args:
            mod: Objeto del mod actualizado
            user: Usuario que actualizó
            changes: Dict con cambios ({"field": {"old": value, "new": value}})
        
        Returns:
            True si se envió exitosamente, False si falló
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            # Detectar si hubo aprobación
            if "required_revision" in changes:
                old_val = changes["required_revision"]["old"]
                new_val = changes["required_revision"]["new"]
                
                # Si cambió de True (pendiente) a False (aprobado)
                if old_val == True and new_val == False:
                    embed = DiscordNotifier._format_embed_approved(mod, user)
                    await DiscordNotifier._send_webhook(embed)
                    return True
            
            # Si hay otros cambios, notificar actualización
            embed = DiscordNotifier._format_embed_updated(mod, user, changes)
            await DiscordNotifier._send_webhook(embed)
            return True
            
        except Exception as e:
            logger.error(f"Error notificando actualización de mod a Discord: {e}")
            return False
    
    @staticmethod
    async def notify_mod_completed(mod: Any) -> bool:
        """
        Notifica cuando un mod está completo (tiene imágenes y créditos)
        
        Args:
            mod: Objeto del mod completo
        
        Returns:
            True si se envió exitosamente, False si fallo (no interrumpe API)
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_completed(mod)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando completamiento de mod a Discord: {e}")
            return False
    
    @staticmethod
    def _format_embed_completed(mod: Any) -> Dict[str, Any]:
        """Formatea embed para mod completado (con imágenes y créditos)"""
        
        # Contar créditos por tipo
        creators_count = 0
        translators_count = 0
        porters_count = 0
        images_count = 0
        
        if hasattr(mod, 'credits') and mod.credits:
            from src.models.enums import CreditsTypeEnum
            for credit in mod.credits:
                if credit.is_active:
                    if credit.type == CreditsTypeEnum.ORIGINAL_CREATOR:
                        creators_count += 1
                    elif credit.type == CreditsTypeEnum.TRANSLATOR:
                        translators_count += 1
                    elif credit.type == CreditsTypeEnum.PORTER:
                        porters_count += 1
        
        if hasattr(mod, 'images') and mod.images:
            images_count = len([img for img in mod.images if img.is_active])
        
        # Extraer géneros de la relación intermedia mod_genres
        genres = "Sin asignar"
        if hasattr(mod, 'mod_genres') and mod.mod_genres:
            genre_names = [mg.genre.name for mg in mod.mod_genres if mg.is_active and mg.genre]
            if genre_names:
                genres = ", ".join(genre_names)
        
        embed = {
            "title": "🎉 MOD COMPLETADO",
            "color": DiscordConfig.COLOR_APPROVED,
            "description": f"El mod tiene todas las secciones completadas: imágenes y créditos",
            "fields": [
                {
                    "name": "📛 Nombre",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "🎭 Personaje",
                    "value": mod.character.value if hasattr(mod.character, 'value') else str(mod.character),
                    "inline": True
                },
                {
                    "name": "⏱️ Duración",
                    "value": mod.duration.value if hasattr(mod.duration, 'value') else str(mod.duration),
                    "inline": True
                },
                {
                    "name": "🖼️ Imágenes",
                    "value": f"{images_count} imagen(es)",
                    "inline": True
                },
                {
                    "name": "👥 Créditos",
                    "value": f"👨‍💻 {creators_count} | 🌐 {translators_count} | 📱 {porters_count}",
                    "inline": True
                },
                {
                    "name": "📊 Estado",
                    "value": mod.status.value if hasattr(mod.status, 'value') else str(mod.status),
                    "inline": True
                },
                {
                    "name": "🏷️ Géneros",
                    "value": genres,
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Completado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    async def notify_mod_approved(mod: Any, approved_by: Any, creator_name: Optional[str] = None) -> bool:
        """
        Notifica cuando un mod es aprobado por admin
        
        Args:
            mod: Objeto del mod
            approved_by: Usuario que aprobó (EDITOR/OWNER)
            creator_name: Nombre del creador del mod (resuelto desde created_by ID)
        
        Returns:
            True si se envió exitosamente
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_approved(mod, approved_by, creator_name)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando aprobación de mod a Discord: {e}")
            return False
    
    @staticmethod
    async def notify_mod_rejected(mod: Any, rejected_by: Any, creator_name: Optional[str] = None) -> bool:
        """
        Notifica cuando un mod es rechazado por admin
        
        Args:
            mod: Objeto del mod
            rejected_by: Usuario que rechazó (EDITOR/OWNER)
            creator_name: Nombre del creador del mod (resuelto desde created_by ID)
        
        Returns:
            True si se envió exitosamente
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_rejected(mod, rejected_by, creator_name)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando rechazo de mod a Discord: {e}")
            return False
    
    @staticmethod
    async def notify_mod_deleted(mod: Any, deleted_by: Any, creator_name: Optional[str] = None) -> bool:
        """
        Notifica cuando un mod es eliminado (soft delete)
        
        Args:
            mod: Objeto del mod
            deleted_by: Usuario que eliminó
            creator_name: Nombre del creador del mod (resuelto desde created_by ID)
        
        Returns:
            True si se envió exitosamente
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_deleted(mod, deleted_by, creator_name)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando eliminación de mod a Discord: {e}")
            return False
    
    @staticmethod
    async def notify_mod_restored(mod: Any, restored_by: Any, creator_name: Optional[str] = None) -> bool:
        """
        Notifica cuando un mod es restaurado
        
        Args:
            mod: Objeto del mod
            restored_by: Usuario que restauró
            creator_name: Nombre del creador del mod (resuelto desde created_by ID)
        
        Returns:
            True si se envió exitosamente
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_restored(mod, restored_by, creator_name)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando restauración de mod a Discord: {e}")
            return False
    
    @staticmethod
    def _format_embed_created(mod: Any, user: Any, is_approved: bool) -> Dict[str, Any]:
        """Formatea embed para creación de mod"""
        
        if is_approved:
            color = DiscordConfig.COLOR_APPROVED
            title = "✅ NUEVO MOD - APROBADO"
            status_text = "✅ Automáticamente Aprobado"
        else:
            color = DiscordConfig.COLOR_PENDING
            title = "📝 NUEVO MOD - PENDIENTE APROBACIÓN"
            status_text = "⏳ Requiere Revisión"
        
        # Extraer géneros de la relación intermedia mod_genres
        genres = "Sin asignar"
        if hasattr(mod, 'mod_genres') and mod.mod_genres:
            genre_names = [mg.genre.name for mg in mod.mod_genres if mg.is_active and mg.genre]
            if genre_names:
                genres = ", ".join(genre_names)
        
        embed = {
            "title": title,
            "color": color,
            "description": mod.description[:200] + "..." if len(mod.description or "") > 200 else mod.description,
            "fields": [
                {
                    "name": "👤 Creador",
                    "value": f"{user.name} ({DiscordNotifier._safe_enum_value(user.rol)})",
                    "inline": True
                },
                {
                    "name": "📛 Nombre",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "🎭 Personaje",
                    "value": mod.character.value if hasattr(mod.character, 'value') else str(mod.character),
                    "inline": True
                },
                {
                    "name": "⏱️ Duración",
                    "value": mod.duration.value if hasattr(mod.duration, 'value') else str(mod.duration),
                    "inline": True
                },
                {
                    "name": "📊 Estado",
                    "value": mod.status.value if hasattr(mod.status, 'value') else str(mod.status),
                    "inline": True
                },
                {
                    "name": "🔒 Revisión",
                    "value": status_text,
                    "inline": True
                },
                {
                    "name": "🏷️ Géneros",
                    "value": genres,
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Creado: {mod.created_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.created_at, 'strftime') else mod.created_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_updated(mod: Any, user: Any, changes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Formatea embed para actualización de mod"""
        
        # Filtrar cambios relacionados con auditoría
        display_changes = {k: v for k, v in changes.items() 
                          if k not in ['created_by', 'updated_by', 'created_at', 'is_active']}
        
        fields = [
            {
                "name": "👤 Actualizado por",
                "value": f"{user.name} ({DiscordNotifier._safe_enum_value(user.rol)})",
                "inline": True
            },
            {
                "name": "📛 Mod",
                "value": mod.name,
                "inline": True
            }
        ]
        
        # Agregar cambios realizados
        if display_changes:
            changes_text = ""
            for field, change in display_changes.items():
                old_val = change["old"]
                new_val = change["new"]
                
                # Convertir valores enum a string
                if hasattr(old_val, 'value'):
                    old_val = old_val.value
                if hasattr(new_val, 'value'):
                    new_val = new_val.value
                
                changes_text += f"• **{field}**: `{old_val}` → `{new_val}`\n"
            
            fields.append({
                "name": "📝 Cambios",
                "value": changes_text,
                "inline": False
            })
        
        fields.append({
            "name": "🔗 Ver Mod",
            "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
            "inline": False
        })
        
        embed = {
            "title": "🔄 MOD ACTUALIZADO",
            "color": DiscordConfig.COLOR_UPDATED,
            "fields": fields,
            "footer": {
                "text": f"ID: {mod.id} • Actualizado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_approved(mod: Any, approved_by: Any, creator_name: Optional[str] = None) -> Dict[str, Any]:
        """Formatea embed para aprobación de mod"""
        
        # Usar creator_name resuelto, o fallback a "Desconocido"
        creator = creator_name if creator_name else "Desconocido"
        
        embed = {
            "title": "✅ MOD APROBADO",
            "color": DiscordConfig.COLOR_APPROVED_ADMIN,
            "description": "Este mod ahora es visible públicamente",
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "👤 Creador",
                    "value": creator,
                    "inline": True
                },
                {
                    "name": "✅ Aprobado por",
                    "value": f"{approved_by.name} ({DiscordNotifier._safe_enum_value(approved_by.rol)})",
                    "inline": True
                },
                {
                    "name": "📝 Descripción",
                    "value": mod.description[:150] + "..." if len(mod.description or "") > 150 else mod.description,
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Aprobado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_rejected(mod: Any, rejected_by: Any, creator_name: Optional[str] = None) -> Dict[str, Any]:
        """Formatea embed para rechazo de mod"""
        
        # Usar creator_name resuelto, o fallback a "Desconocido"
        creator = creator_name if creator_name else "Desconocido"
        
        embed = {
            "title": "❌ MOD RECHAZADO",
            "color": 0xFF0000,  # Rojo - Rechazado
            "description": "Este mod ha sido rechazado y requiere revisión",
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "👤 Creador",
                    "value": creator,
                    "inline": True
                },
                {
                    "name": "❌ Rechazado por",
                    "value": f"{rejected_by.name} ({DiscordNotifier._safe_enum_value(rejected_by.rol)})",
                    "inline": True
                },
                {
                    "name": "📝 Descripción",
                    "value": mod.description[:150] + "..." if len(mod.description or "") > 150 else mod.description,
                    "inline": False
                },
                {
                    "name": "💬 Comentarios",
                    "value": mod.comments if mod.comments else "Sin comentarios",
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Rechazado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_deleted(mod: Any, deleted_by: Any, creator_name: Optional[str] = None) -> Dict[str, Any]:
        """Formatea embed para eliminación de mod"""
        
        # Usar creator_name resuelto, o fallback a "Desconocido"
        creator = creator_name if creator_name else "Desconocido"
        
        embed = {
            "title": "🗑️ MOD ELIMINADO",
            "color": 0x808080,  # Gris - Eliminado
            "description": "Este mod ha sido eliminado",
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "👤 Creador",
                    "value": creator,
                    "inline": True
                },
                {
                    "name": "🗑️ Eliminado por",
                    "value": f"{deleted_by.name} ({DiscordNotifier._safe_enum_value(deleted_by.rol)})",
                    "inline": True
                },
                {
                    "name": "📝 Descripción",
                    "value": mod.description[:150] + "..." if len(mod.description or "") > 150 else mod.description,
                    "inline": False
                },
                {
                    "name": "💬 Razón de eliminación",
                    "value": mod.comments if mod.comments else "Sin especificar",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Eliminado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_restored(mod: Any, restored_by: Any, creator_name: Optional[str] = None) -> Dict[str, Any]:
        """Formatea embed para restauración de mod"""
        
        # Usar creator_name resuelto, o fallback a "Desconocido"
        creator = creator_name if creator_name else "Desconocido"
        
        embed = {
            "title": "✅ MOD RESTAURADO",
            "color": 0x00DD00,  # Verde oscuro - Restaurado
            "description": "Este mod ha sido restaurado y es visible nuevamente",
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "👤 Creador",
                    "value": creator,
                    "inline": True
                },
                {
                    "name": "✅ Restaurado por",
                    "value": f"{restored_by.name} ({DiscordNotifier._safe_enum_value(restored_by.rol)})",
                    "inline": True
                },
                {
                    "name": "📝 Descripción",
                    "value": mod.description[:150] + "..." if len(mod.description or "") > 150 else mod.description,
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Restaurado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    async def notify_genres_added(mod: Any, genres: list, user: Any) -> bool:
        """
        Notifica cuando se agregan géneros a un mod
        
        Args:
            mod: Objeto del mod
            genres: Lista de géneros agregados
            user: Usuario que agregó los géneros
        
        Returns:
            True si se envió exitosamente, False si falló
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_genres_added(mod, genres, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando adición de géneros a Discord: {e}")
            return False
    
    @staticmethod
    async def notify_genres_removed(mod: Any, genres: list, user: Any) -> bool:
        """
        Notifica cuando se remueven géneros de un mod
        
        Args:
            mod: Objeto del mod
            genres: Lista de géneros removidos
            user: Usuario que removió los géneros
        
        Returns:
            True si se envió exitosamente, False si falló
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_genres_removed(mod, genres, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando remoción de géneros a Discord: {e}")
            return False
    
    @staticmethod
    def _format_embed_genres_added(mod: Any, genres: list, user: Any) -> Dict[str, Any]:
        """Formatea embed para adición de géneros"""
        
        genres_text = ", ".join([g if isinstance(g, str) else g.name for g in genres])
        
        embed = {
            "title": "🏷️ GÉNEROS AGREGADOS",
            "color": 0x7B68EE,  # Medium Purple
            "description": f"Se han agregado nuevos géneros al mod",
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "👤 Actualizado por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "📚 Géneros Agregados",
                    "value": genres_text,
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Actualizado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_genres_removed(mod: Any, genres: list, user: Any) -> Dict[str, Any]:
        """Formatea embed para remoción de géneros"""
        
        genres_text = ", ".join([g if isinstance(g, str) else g.name for g in genres])
        
        embed = {
            "title": "🏷️ GÉNEROS REMOVIDOS",
            "color": 0xFF69B4,  # Hot Pink
            "description": f"Se han removido géneros del mod",
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "👤 Actualizado por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "📚 Géneros Removidos",
                    "value": genres_text,
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {mod.id} • Actualizado: {mod.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(mod.updated_at, 'strftime') else mod.updated_at}"
            }
        }
        
        return {"embeds": [embed]}
    
    # ═════════════════════════════════════════════════════════════════════════════
    # NOTIFICACIONES PARA GÉNEROS
    # ═════════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    async def notify_genre_status_changed(genre: Any, user: Any, is_active: bool) -> bool:
        """Notifica cuando se activa o desactiva un género"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_genre_status_changed(genre, user, is_active)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando cambio de estado de género: {e}")
            return False
    
    @staticmethod
    def _format_embed_genre_status_changed(genre: Any, user: Any, is_active: bool) -> Dict[str, Any]:
        """Formatea embed para cambio de estado de género"""
        if is_active:
            title = "✅ GÉNERO ACTIVADO"
            color = 0x00DD00  # Verde
            description = "Este género ha sido activado"
        else:
            title = "🚫 GÉNERO DESACTIVADO"
            color = 0x808080  # Gris
            description = "Este género ha sido desactivado"
        
        embed = {
            "title": title,
            "color": color,
            "description": description,
            "fields": [
                {
                    "name": "🏷️ Género",
                    "value": genre.name,
                    "inline": True
                },
                {
                    "name": "👤 Cambiado por",
                    "value": f"{user.name}",
                    "inline": True
                }
            ],
            "footer": {
                "text": f"ID: {genre.id} • Actualizado: {genre.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(genre.updated_at, 'strftime') else genre.updated_at}"
            }
        }
        return {"embeds": [embed]}
    
    # ═════════════════════════════════════════════════════════════════════════════
    # NOTIFICACIONES PARA COLECCIONES
    # ═════════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    async def notify_collection_created(collection: Any, user: Any) -> bool:
        """Notifica cuando se crea una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_collection_created(collection, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando creación de colección: {e}")
            return False
    
    @staticmethod
    async def notify_collection_updated(collection: Any, user: Any, changes: Dict[str, Dict[str, Any]]) -> bool:
        """Notifica cuando se actualiza una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_collection_updated(collection, user, changes)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando actualización de colección: {e}")
            return False
    
    @staticmethod
    async def notify_collection_deleted(collection: Any, user: Any) -> bool:
        """Notifica cuando se elimina una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_collection_deleted(collection, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando eliminación de colección: {e}")
            return False
    
    @staticmethod
    async def notify_collection_reactivated(collection: Any, user: Any) -> bool:
        """Notifica cuando se restaura una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_collection_reactivated(collection, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando restauración de colección: {e}")
            return False
    
    @staticmethod
    def _format_embed_collection_created(collection: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para creación de colección"""
        embed = {
            "title": "🎁 NUEVA COLECCIÓN",
            "color": 0x00AA00,  # Verde
            "description": collection.description[:200] + "..." if len(collection.description or "") > 200 else collection.description,
            "fields": [
                {
                    "name": "👤 Creador",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "📦 Colección",
                    "value": collection.name,
                    "inline": True
                },
                {
                    "name": "🔗 Ver Colección",
                    "value": f"[Ir a la colección]({DiscordConfig.FRONTEND_BASE_URL}/colecciones/{collection.id})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {collection.id} • Creado: {collection.created_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(collection.created_at, 'strftime') else collection.created_at}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_collection_updated(collection: Any, user: Any, changes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Formatea embed para actualización de colección"""
        display_changes = {k: v for k, v in changes.items() 
                          if k not in ['created_by', 'updated_by', 'created_at', 'is_active']}
        
        fields = [
            {
                "name": "👤 Actualizado por",
                "value": f"{user.name}",
                "inline": True
            },
            {
                "name": "📦 Colección",
                "value": collection.name,
                "inline": True
            }
        ]
        
        if display_changes:
            changes_text = ""
            for field, change in display_changes.items():
                old_val = change["old"]
                new_val = change["new"]
                changes_text += f"• **{field}**: `{old_val}` → `{new_val}`\n"
            
            fields.append({
                "name": "📝 Cambios",
                "value": changes_text,
                "inline": False
            })
        
        fields.append({
            "name": "🔗 Ver Colección",
            "value": f"[Ir a la colección]({DiscordConfig.FRONTEND_BASE_URL}/colecciones/{collection.id})",
            "inline": False
        })
        
        embed = {
            "title": "🔄 COLECCIÓN ACTUALIZADA",
            "color": 0x0099FF,  # Azul
            "fields": fields,
            "footer": {
                "text": f"ID: {collection.id} • Actualizado: {collection.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(collection.updated_at, 'strftime') else collection.updated_at}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_collection_deleted(collection: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para eliminación de colección"""
        embed = {
            "title": "🗑️ COLECCIÓN ELIMINADA",
            "color": 0x808080,  # Gris
            "description": "Esta colección ha sido eliminada",
            "fields": [
                {
                    "name": "📦 Colección",
                    "value": collection.name,
                    "inline": True
                },
                {
                    "name": "👤 Eliminada por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "📝 Descripción",
                    "value": collection.description[:150] + "..." if len(collection.description or "") > 150 else collection.description,
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {collection.id} • Eliminado: {collection.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(collection.updated_at, 'strftime') else collection.updated_at}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_collection_reactivated(collection: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para restauración de colección"""
        embed = {
            "title": "✅ COLECCIÓN RESTAURADA",
            "color": 0x00DD00,  # Verde oscuro
            "description": "Esta colección ha sido restaurada",
            "fields": [
                {
                    "name": "📦 Colección",
                    "value": collection.name,
                    "inline": True
                },
                {
                    "name": "👤 Restaurada por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Colección",
                    "value": f"[Ir a la colección]({DiscordConfig.FRONTEND_BASE_URL}/colecciones/{collection.id})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {collection.id} • Restaurado: {collection.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(collection.updated_at, 'strftime') else collection.updated_at}"
            }
        }
        return {"embeds": [embed]}
    
    # ═════════════════════════════════════════════════════════════════════════════
    # NOTIFICACIONES PARA MODS EN COLECCIONES
    # ═════════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    async def notify_mod_added_to_collection(mod: Any, collection: Any, user: Any) -> bool:
        """Notifica cuando se agrega un mod a una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_mod_added_to_collection(mod, collection, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando adición de mod a colección: {e}")
            return False
    
    @staticmethod
    async def notify_mod_removed_from_collection(mod: Any, collection: Any, user: Any) -> bool:
        """Notifica cuando se remueve un mod de una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_mod_removed_from_collection(mod, collection, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando remoción de mod de colección: {e}")
            return False
    
    @staticmethod
    def _format_embed_mod_added_to_collection(mod: Any, collection: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para adición de mod a colección"""
        embed = {
            "title": "📌 MOD AGREGADO A COLECCIÓN",
            "color": 0x00AA00,  # Verde
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "📦 Colección",
                    "value": collection.name,
                    "inline": True
                },
                {
                    "name": "👤 Actualizado por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Mod ID: {mod.id} • Colección ID: {collection.id}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_mod_removed_from_collection(mod: Any, collection: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para remoción de mod de colección"""
        embed = {
            "title": "📌 MOD REMOVIDO DE COLECCIÓN",
            "color": 0xFF69B4,  # Rosa
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "📦 Colección",
                    "value": collection.name,
                    "inline": True
                },
                {
                    "name": "👤 Actualizado por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Mod ID: {mod.id} • Colección ID: {collection.id}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    async def notify_mods_collection_reactivated(mod: Any, collection: Any, user: Any) -> bool:
        """Notifica cuando se reactiva un mod en una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_mods_collection_reactivated(mod, collection, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando reactivación de mod en colección: {e}")
            return False
    
    @staticmethod
    async def notify_mods_collection_deactivated(mod: Any, collection: Any, user: Any) -> bool:
        """Notifica cuando se desactiva un mod en una colección"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_mods_collection_deactivated(mod, collection, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando desactivación de mod en colección: {e}")
            return False
    
    @staticmethod
    def _format_embed_mods_collection_reactivated(mod: Any, collection: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para reactivación de mod en colección"""
        embed = {
            "title": "✅ MOD REACTIVADO EN COLECCIÓN",
            "color": 0x00AA00,  # Verde
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "📦 Colección",
                    "value": collection.name,
                    "inline": True
                },
                {
                    "name": "👤 Actualizado por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Mod ID: {mod.id} • Colección ID: {collection.id}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_mods_collection_deactivated(mod: Any, collection: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para desactivación de mod en colección"""
        embed = {
            "title": "❌ MOD DESACTIVADO EN COLECCIÓN",
            "color": 0xFF0000,  # Rojo
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "📦 Colección",
                    "value": collection.name,
                    "inline": True
                },
                {
                    "name": "👤 Actualizado por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Mod ID: {mod.id} • Colección ID: {collection.id}"
            }
        }
        return {"embeds": [embed]}
    
    # ═════════════════════════════════════════════════════════════════════════════
    # NOTIFICACIONES PARA IMÁGENES
    # ═════════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    async def notify_image_uploaded(image: Any, mod: Any, user: Any) -> bool:
        """Notifica cuando se sube una imagen"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_image_uploaded(image, mod, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando carga de imagen: {e}")
            return False
    
    @staticmethod
    async def notify_image_replaced(image: Any, mod: Any, user: Any) -> bool:
        """Notifica cuando se reemplaza una imagen"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_image_replaced(image, mod, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando reemplazo de imagen: {e}")
            return False
    
    @staticmethod
    async def notify_image_deleted(image: Any, mod: Any, user: Any) -> bool:
        """Notifica cuando se elimina una imagen"""
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_image_deleted(image, mod, user)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando eliminación de imagen: {e}")
            return False
    
    @staticmethod
    def _get_image_type_emoji(image_type: str) -> str:
        """Obtiene emoji según tipo de imagen"""
        type_map = {
            "logo": "🎭",
            "main": "🖼️",
            "screenshot": "📸"
        }
        return type_map.get(image_type, "🖼️")
    
    @staticmethod
    def _get_image_type_name(image_type: str) -> str:
        """Obtiene nombre legible del tipo de imagen"""
        type_map = {
            "logo": "Logo",
            "main": "Imagen Principal",
            "screenshot": "Captura de Pantalla"
        }
        return type_map.get(image_type, image_type)
    
    @staticmethod
    def _format_embed_image_uploaded(image: Any, mod: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para carga de imagen"""
        img_type = DiscordNotifier._get_image_type_name(image.type)
        img_emoji = DiscordNotifier._get_image_type_emoji(image.type)
        
        embed = {
            "title": f"{img_emoji} IMAGEN SUBIDA",
            "color": 0x00AA00,  # Verde
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "🖼️ Tipo",
                    "value": img_type,
                    "inline": True
                },
                {
                    "name": "👤 Subida por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Imagen",
                    "value": f"[Ver]({image.url})",
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "thumbnail": {
                "url": image.url,
                "height": 100,
                "width": 100
            },
            "footer": {
                "text": f"ID: {image.id} • Creado: {image.created_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(image.created_at, 'strftime') else image.created_at}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_image_replaced(image: Any, mod: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para reemplazo de imagen"""
        img_type = DiscordNotifier._get_image_type_name(image.type)
        img_emoji = DiscordNotifier._get_image_type_emoji(image.type)
        
        embed = {
            "title": f"{img_emoji} IMAGEN REEMPLAZADA",
            "color": 0x0099FF,  # Azul
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "🖼️ Tipo",
                    "value": img_type,
                    "inline": True
                },
                {
                    "name": "👤 Reemplazada por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Imagen",
                    "value": f"[Ver]({image.url})",
                    "inline": False
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "thumbnail": {
                "url": image.url,
                "height": 100,
                "width": 100
            },
            "footer": {
                "text": f"ID: {image.id} • Actualizado: {image.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(image.updated_at, 'strftime') else image.updated_at}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    def _format_embed_image_deleted(image: Any, mod: Any, user: Any) -> Dict[str, Any]:
        """Formatea embed para eliminación de imagen"""
        img_type = DiscordNotifier._get_image_type_name(image.type)
        img_emoji = DiscordNotifier._get_image_type_emoji(image.type)
        
        embed = {
            "title": f"{img_emoji} IMAGEN ELIMINADA",
            "color": 0x808080,  # Gris
            "fields": [
                {
                    "name": "📛 Mod",
                    "value": mod.name,
                    "inline": True
                },
                {
                    "name": "🖼️ Tipo",
                    "value": img_type,
                    "inline": True
                },
                {
                    "name": "👤 Eliminada por",
                    "value": f"{user.name}",
                    "inline": True
                },
                {
                    "name": "🔗 Ver Mod",
                    "value": f"[Ir al mod]({DiscordConfig.get_mod_url(mod.slug)})",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"ID: {image.id} • Eliminado: {image.updated_at.strftime('%d/%m/%Y %H:%M UTC') if hasattr(image.updated_at, 'strftime') else image.updated_at}"
            }
        }
        return {"embeds": [embed]}
    
    @staticmethod
    async def _send_webhook(payload: Dict[str, Any]) -> bool:
        """
        Envía el webhook a Discord
        
        Args:
            payload: Dict con los embeds a enviar
        
        Returns:
            True si fue exitoso
        """
        if not DiscordConfig.WEBHOOK_URL:
            logger.warning("DISCORD_WEBHOOK_URL no configurado")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    DiscordConfig.WEBHOOK_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 204:  # Discord retorna 204 en éxito
                        logger.info("Notificación enviada a Discord exitosamente")
                        return True
                    else:
                        logger.error(f"Error enviando webhook: {response.status} - {await response.text()}")
                        return False
        except asyncio.TimeoutError:
            logger.error("Timeout enviando webhook a Discord")
            return False
        except Exception as e:
            logger.error(f"Error en _send_webhook: {e}")
            return False
