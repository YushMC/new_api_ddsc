from slowapi import Limiter
from slowapi.util import get_remote_address

# Crear instancia global del limiter
limiter = Limiter(key_func=get_remote_address)

# Configurar límites por endpoint
RATE_LIMIT_DEFAULT = "100/minute"  # 100 peticiones por minuto por IP

# Diccionario de límites específicos por ruta (opcional)
RATE_LIMITS = {
    # Rutas públicas de lectura - límite más alto
    "/mod/random": "1000/minute",
    "/mod/search": "500/minute",
    "/mod/all": "500/minute",
    "/mod/": "500/minute",
    "/genres": "500/minute",
    "/collections": "500/minute",
    
    # Rutas de autenticación - límite más restrictivo
    "/users/login": "10/minute",
    "/users/register": "5/minute",
    "/users/refresh": "30/minute",
    
    # Rutas de modificación - límite restrictivo
    "/mod/": "50/minute",
    "/genres/": "50/minute",
    "/collections/": "50/minute",
    "/credits/": "50/minute",
}
