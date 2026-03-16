"""
Esquemas de respuesta estandarizados para toda la API
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

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
