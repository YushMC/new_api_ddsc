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
    mod_id: int
