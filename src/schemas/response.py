"""
Esquemas de respuesta estandarizados para toda la API
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class TimestampInfo(BaseModel):
    """
    Información de auditoria y timestamps de un recurso
    
    Campos genéricos:
    - created_at, created_by: Creación
    - updated_at, updated_by: Última actualización
    - is_active: Estado del recurso
    
    Campos específicos de Mods:
    - approved_at, approved_by: Aprobación del mod
    - deleted_at, deleted_by: Eliminación (soft delete)
    
    Ejemplo:
    {
        "created_at": "2024-03-16T10:30:00Z",
        "created_by": "uploader",
        "updated_at": "2024-03-16T11:45:00Z",
        "updated_by": "editor",
        "approved_at": "2024-03-16T12:00:00Z",
        "approved_by": "owner",
        "deleted_at": null,
        "deleted_by": null,
        "is_active": true
    }
    """
    created_at: Optional[datetime] = Field(None, description="Fecha de creación")
    created_by: Optional[str] = Field(None, description="Usuario que creó el recurso")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    updated_by: Optional[str] = Field(None, description="Usuario que actualizó el recurso")
    approved_at: Optional[datetime] = Field(None, description="Fecha de aprobación (específico de Mods)")
    approved_by: Optional[str] = Field(None, description="Usuario que aprobó (específico de Mods)")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación (soft delete, específico de Mods)")
    deleted_by: Optional[str] = Field(None, description="Usuario que eliminó (específico de Mods)")
    is_active: bool = Field(True, description="Si el recurso está activo")
    
    class Config:
        from_attributes = True


class DataWithInfo(BaseModel, Generic[T]):
    """
    Estructura de datos con información de timestamp separada
    
    Ejemplo:
    {
        "resource": {
            "id": 1,
            "name": "My Mod",
            "slug": "my-mod"
        },
        "info": {
            "created_at": "2024-03-16T10:30:00Z",
            "created_by": "admin",
            "updated_at": "2024-03-16T11:45:00Z",
            "updated_by": "editor",
            "is_active": true
        }
    }
    """
    resource: T = Field(..., description="Datos del recurso")
    info: TimestampInfo = Field(..., description="Información de auditoria y timestamps")
    
    class Config:
        from_attributes = True


class ApiResponse(BaseModel, Generic[T]):
    """
    Estructura estandarizada de respuesta API
    
    Ejemplo:
    {
        "response": "success",
        "message": "Usuario creado exitosamente",
        "data": {
            "id": 1,
            "name": "admin",
            "role": "owner"
        }
    }
    """
    response: str = Field(..., description="Estado: 'success', 'error', 'created', 'updated', 'deleted'")
    message: str = Field(..., description="Mensaje descriptivo de la operación")
    data: Optional[T] = Field(None, description="Datos de la respuesta (puede ser null)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "response": "success",
                "message": "Operación completada exitosamente",
                "data": {}
            }
        }

class ApiErrorResponse(BaseModel):
    """
    Estructura estandarizada de respuesta de error
    
    Ejemplo:
    {
        "response": "error",
        "message": "Usuario no encontrado",
        "data": null
    }
    """
    response: str = Field("error", description="Siempre 'error'")
    message: str = Field(..., description="Descripción del error")
    data: Optional[Any] = Field(None, description="Datos adicionales del error (null por defecto)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "response": "error",
                "message": "El recurso no fue encontrado",
                "data": None
            }
        }

class ApiListResponse(BaseModel, Generic[T]):
    """
    Estructura estandarizada para respuestas con listas
    
    Ejemplo:
    {
        "response": "success",
        "message": "Géneros obtenidos exitosamente",
        "data": [
            {"id": 1, "name": "Action", "identifier": "action"},
            {"id": 2, "name": "Horror", "identifier": "horror"}
        ]
    }
    """
    response: str = Field("success", description="Estado de la respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    data: list[T] = Field(default_factory=list, description="Lista de elementos")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "response": "success",
                "message": "Lista obtenida exitosamente",
                "data": []
            }
        }
