"""
Middleware para establecer el contexto del usuario actual en cada request
"""
from fastapi import Request
from src.conf.context import set_current_user_id, clear_current_user


async def user_context_middleware(request: Request, call_next):
    """
    Middleware que establece el ID del usuario actual en el contexto de la request.
    Esto permite que los modelos accedan al usuario actual para auditoría.
    """
    # Intentar extraer el usuario del token
    try:
        # Obtener el token del header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            from src.utils.jwt import JWT_TOKEN
            token = auth_header[7:]  # Remover "Bearer "
            jwt_handler = JWT_TOKEN()
            payload = jwt_handler.decode_token(token)
            if payload:
                set_current_user_id(int(payload.get("sub", 0)))
    except Exception:
        # Si no se puede extraer el usuario, usar 0 (sistema)
        set_current_user_id(0)
    
    try:
        response = await call_next(request)
    finally:
        # Limpiar el contexto después de procesar la request
        clear_current_user()
    
    return response
