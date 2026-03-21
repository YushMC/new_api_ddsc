"""
Utilidades para generar respuestas estandarizadas de la API
"""
from typing import Any, Optional, TypeVar, Generic
from src.schemas.response import ApiResponse, ApiListResponse, ApiErrorResponse, TimestampInfo, DataWithInfo

T = TypeVar('T')

# Campos de timestamp que deben ir en el objeto info
TIMESTAMP_FIELDS = {
    # Genéricos
    'created_at', 
    'created_by', 
    'updated_at', 
    'updated_by', 
    'is_active',
    # Específicos de Mods
    'approved_at', 
    'approved_by',
    'rejected_at',
    'rejected_by',
    'deleted_at', 
    'deleted_by'
}

# Campos que deben ir en el objeto credits (para mods)
CREDITS_FIELD = 'credits'

# Campos que NO deben ser extraídos (se mantienen íntegros)
PRESERVED_FIELDS = {'images'}

# Campos _by que contienen IDs de usuario y deben ser resueltos a objetos de usuario
USER_ID_FIELDS = {'created_by', 'updated_by', 'approved_by', 'rejected_by', 'deleted_by'}


def resolve_user_ids(info_data: dict, db) -> dict:
    """
    Resuelve los campos _by (IDs de usuario) a objetos con información del usuario.
    
    Convierte:
        "created_by": 5
    En:
        "created_by": {"id": 5, "name": "admin", "logo": "url"}
    
    Args:
        info_data: Dict con campos de info (ya extraídos por _extract_info)
        db: Session de SQLAlchemy
    
    Returns:
        Dict con los campos _by resueltos a objetos de usuario
    """
    if not info_data or not db:
        return info_data
    
    from src.models.users import User
    
    # Recolectar todos los IDs de usuario únicos (no None, no 0)
    user_ids = set()
    for field in USER_ID_FIELDS:
        val = info_data.get(field)
        if val and isinstance(val, int) and val != 0:
            user_ids.add(val)
    
    if not user_ids:
        return info_data
    
    # Una sola query para obtener todos los usuarios necesarios
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {
        u.id: {"id": u.id, "name": u.name, "logo": u.logo}
        for u in users
    }
    
    # Reemplazar IDs por objetos de usuario
    resolved = dict(info_data)
    for field in USER_ID_FIELDS:
        val = resolved.get(field)
        if val and isinstance(val, int) and val != 0:
            resolved[field] = user_map.get(val, {"id": val, "name": "Desconocido", "logo": None})
        elif field in resolved:
            resolved[field] = None
    
    return resolved

class ResponseBuilder:
    """Constructor de respuestas estandarizadas para la API"""
    
    @staticmethod
    def _extract_info(data: Any) -> tuple[dict, dict, dict | None]:
        """
        Extrae los campos de timestamp y credits de los datos
        
        Args:
            data: Datos que pueden contener campos de timestamp y credits
            
        Returns:
            Tupla de (resource_data, info_data, credits_data)
        """
        if not isinstance(data, dict):
            # Si es un modelo Pydantic, convertir a dict
            if hasattr(data, 'model_dump'):
                data = data.model_dump()
            elif hasattr(data, '__dict__'):
                data = data.__dict__
            else:
                return data, {}, None
        
        resource_data = {}
        info_data = {}
        credits_data = None
        
        for key, value in data.items():
            if key in TIMESTAMP_FIELDS:
                info_data[key] = value
            elif key == CREDITS_FIELD:
                credits_data = value
            elif key in PRESERVED_FIELDS:
                # Mantener campos íntegros sin extraer nada
                resource_data[key] = value
            else:
                resource_data[key] = value
        
        return resource_data, info_data, credits_data
    
    @staticmethod
    def _create_response_with_info(data: Any, response_type: str, message: str, force_info: bool = False, db=None) -> dict:
        """
        Crea una respuesta separando timestamp info y credits
        
        Args:
            data: Datos del recurso
            response_type: Tipo de respuesta (success, created, updated, etc)
            message: Mensaje descriptivo
            force_info: Si True, siempre crea estructura con info aunque sea vacío
            db: Session de SQLAlchemy (opcional). Si se proporciona, resuelve IDs de usuario a objetos
            
        Returns:
            Dict con estructura estandarizada
        """
        if data is None:
            return {
                "response": response_type,
                "message": message,
                "data": None
            }
        
        resource_data, info_data, credits_data = ResponseBuilder._extract_info(data)
        
        # Resolver IDs de usuario a objetos si se proporciona db
        if db and info_data:
            info_data = resolve_user_ids(info_data, db)
        
        # Si no hay campos de timestamp ni credits, retornar sin info (a menos que force_info=True)
        if not info_data and credits_data is None and not force_info:
            return {
                "response": response_type,
                "message": message,
                "data": resource_data
            }
        
        # Crear estructura con info y/o credits
        response_data = {
            "resource": resource_data
        }
        
        if info_data or force_info:
            response_data["info"] = info_data
        
        if credits_data is not None:
            response_data["credits"] = credits_data
        
        return {
            "response": response_type,
            "message": message,
            "data": response_data
        }
    
    @staticmethod
    def success(data: Any = None, message: str = "Operación completada exitosamente", force_info: bool = False, db=None) -> dict:
        """
        Construir respuesta de éxito
        
        Args:
            data: Datos a retornar
            message: Mensaje descriptivo
            force_info: Si True, siempre crea estructura con info
            db: Session de SQLAlchemy (opcional). Si se proporciona, resuelve IDs de usuario a objetos
            
        Returns:
            Dict con estructura estandarizada
        """
        return ResponseBuilder._create_response_with_info(data, "success", message, force_info=force_info, db=db)
    
    @staticmethod
    def created(data: Any, message: str = "Recurso creado exitosamente", force_info: bool = False, db=None) -> dict:
        """
        Construir respuesta de creación exitosa
        
        Args:
            data: Datos del recurso creado
            message: Mensaje descriptivo
            force_info: Si True, siempre crea estructura con info
            db: Session de SQLAlchemy (opcional). Si se proporciona, resuelve IDs de usuario a objetos
            
        Returns:
            Dict con estructura estandarizada
        """
        return ResponseBuilder._create_response_with_info(data, "created", message, force_info=force_info, db=db)
    
    @staticmethod
    def updated(data: Any, message: str = "Recurso actualizado exitosamente", force_info: bool = False, db=None) -> dict:
        """
        Construir respuesta de actualización exitosa
        
        Args:
            data: Datos del recurso actualizado
            message: Mensaje descriptivo
            force_info: Si True, siempre crea estructura con info
            db: Session de SQLAlchemy (opcional). Si se proporciona, resuelve IDs de usuario a objetos
            
        Returns:
            Dict con estructura estandarizada
        """
        return ResponseBuilder._create_response_with_info(data, "updated", message, force_info=force_info, db=db)
    
    @staticmethod
    def deleted(message: str = "Recurso eliminado exitosamente") -> dict:
        """
        Construir respuesta de eliminación exitosa
        
        Args:
            message: Mensaje descriptivo
            
        Returns:
            Dict con estructura estandarizada
        """
        return {
            "response": "deleted",
            "message": message,
            "data": None
        }
    
    @staticmethod
    def list_response(data: list, message: str = "Datos obtenidos exitosamente") -> dict:
        """
        Construir respuesta con lista de elementos
        
        Args:
            data: Lista de elementos
            message: Mensaje descriptivo
            
        Returns:
            Dict con estructura estandarizada
        """
        return {
            "response": "success",
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(message: str, data: Optional[Any] = None) -> dict:
        """
        Construir respuesta de error
        
        Args:
            message: Descripción del error
            data: Datos adicionales del error (opcional)
            
        Returns:
            Dict con estructura estandarizada
        """
        return {
            "response": "error",
            "message": message,
            "data": data
        }
