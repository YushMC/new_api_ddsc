"""
Configuración para notificaciones a Discord
"""
import os

class DiscordConfig:
    """Configuración centralizada para Discord"""
    
    # URLs
    WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "")
    
    # Colores para embeds (formato decimal)
    COLOR_PENDING = 0xFF0000          # Rojo - Pendiente aprobación
    COLOR_APPROVED = 0x00FF00         # Verde - Aprobado automáticamente
    COLOR_UPDATED = 0xFFA500          # Naranja - Actualizado
    COLOR_APPROVED_ADMIN = 0x00DD00   # Verde oscuro - Aprobado por admin
    
    @staticmethod
    def is_configured() -> bool:
        """Verifica si Discord está configurado"""
        return bool(DiscordConfig.WEBHOOK_URL and DiscordConfig.WEBHOOK_URL.strip())
    
    @staticmethod
    def get_mod_url(mod_slug: str) -> str:
        """Genera URL al mod en el frontend"""
        if not DiscordConfig.FRONTEND_BASE_URL:
            # Si no hay frontend, retornar URL a API
            return f"http://localhost:8000/mod/{mod_slug}"
        
        base_url = DiscordConfig.FRONTEND_BASE_URL.rstrip("/")
        return f"{base_url}/mods/{mod_slug}"
