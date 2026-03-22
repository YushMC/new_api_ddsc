from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase


class ModStatisticBase(BaseModel):
    """Base schema para estadísticas de mods"""
    download_pc: int = 0
    download_android: int = 0
    searchs: int = 0


class ModStatisticCreate(ModStatisticBase):
    """Schema para crear estadísticas de un mod"""
    mod_id: int


class ModStatisticCreateRequest(BaseModel):
    """Schema para crear estadísticas de un mod (solo requiere mod_id)"""
    mod_id: int


class ModStatisticUpdate(BaseModel):
    """Schema para actualizar estadísticas (incremental)"""
    download_pc: int = 0
    download_android: int = 0
    searchs: int = 0


class ModStatisticIncrement(BaseModel):
    """Schema para incrementar un campo específico de estadísticas (siempre suma 1)"""
    pass  # No necesita parámetros, siempre suma 1


class ModStatisticStatusRequest(BaseModel):
    """Schema para activar/desactivar una estadística"""
    is_active: bool


class ModStatisticsRequest(BaseModel):
    """Schema para obtener estadísticas de múltiples mods"""
    mod_ids: list[int]


class ModStatisticResponse(ModStatisticBase, TimestampBase):
    """Schema para respuesta de estadísticas"""
    id: int
    mod_name: str


def transform_statistic_to_response(statistic_obj) -> dict:
    """
    Transforma un objeto ModStatistic a diccionario compatible con ModStatisticResponse
    Reemplaza mod_id con mod_name del objeto relacionado
    """
    return {
        "id": statistic_obj.id,
        "mod_name": statistic_obj.mod.name if statistic_obj.mod else None,
        "download_pc": statistic_obj.download_pc,
        "download_android": statistic_obj.download_android,
        "searchs": statistic_obj.searchs,
        "created_by": statistic_obj.created_by,
        "created_at": statistic_obj.created_at,
        "updated_by": statistic_obj.updated_by,
        "updated_at": statistic_obj.updated_at,
        "is_active": statistic_obj.is_active if hasattr(statistic_obj, 'is_active') else None
    }
