"""
Utilidades para generar respuestas estandarizadas de la API
"""
from typing import Any, Optional, TypeVar, Generic
from src.schemas.response import ApiResponse, ApiListResponse, ApiErrorResponse

T = TypeVar('T')

class ResponseBuilder:
    """Constructor de respuestas estandarizadas para la API"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Operación completada exitosamente") -> dict:
        """
        Construir respuesta de éxito
        
        Args:
            data: Datos a retornar
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
    def created(data: Any, message: str = "Recurso creado exitosamente") -> dict:
        """
        Construir respuesta de creación exitosa
        
        Args:
            data: Datos del recurso creado
            message: Mensaje descriptivo
            
        Returns:
            Dict con estructura estandarizada
        """
        return {
            "response": "created",
            "message": message,
            "data": data
        }
    
    @staticmethod
    def updated(data: Any, message: str = "Recurso actualizado exitosamente") -> dict:
        """
        Construir respuesta de actualización exitosa
        
        Args:
            data: Datos del recurso actualizado
            message: Mensaje descriptivo
            
        Returns:
            Dict con estructura estandarizada
        """
        return {
            "response": "updated",
            "message": message,
            "data": data
        }
    
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
