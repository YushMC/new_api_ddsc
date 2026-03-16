"""
Servicio para enviar notificaciones a Discord
"""
import aiohttp
import asyncio
from src.conf.discord_config import DiscordConfig
from src.models.enums import UserRolEnum
from typing import Optional, Dict, Any
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
        
        genres = ", ".join([g.name for g in mod.genres]) if mod.genres else "Sin asignar"
        
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
    async def notify_mod_approved(mod: Any, approved_by: Any) -> bool:
        """
        Notifica cuando un mod es aprobado por admin
        
        Args:
            mod: Objeto del mod
            approved_by: Usuario que aprobó (EDITOR/OWNER)
        
        Returns:
            True si se envió exitosamente
        """
        if not DiscordConfig.is_configured():
            return False
        
        try:
            embed = DiscordNotifier._format_embed_approved(mod, approved_by)
            await DiscordNotifier._send_webhook(embed)
            return True
        except Exception as e:
            logger.error(f"Error notificando aprobación de mod a Discord: {e}")
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
        
        genres = ", ".join([g.name for g in mod.genres]) if mod.genres else "Sin asignar"
        
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
    def _format_embed_approved(mod: Any, approved_by: Any) -> Dict[str, Any]:
        """Formatea embed para aprobación de mod"""
        
        # Obtener el creator del mod si existe
        creator = mod.created_by if hasattr(mod, 'created_by') else "Desconocido"
        
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
