from datetime import date
from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase


class CollectionBase(BaseModel):
    """Base schema para colecciones"""
    name: str
    description: str | None = None
    is_seasonal: bool = False
    start_date: date | None = None
    end_date: date | None = None


class CollectionCreate(CollectionBase):
    """Schema para crear colecciones"""
    pass


class CollectionUpdate(BaseModel):
    """Schema para actualizar colecciones"""
    name: str | None = None
    description: str | None = None
    is_seasonal: bool | None = None
    start_date: date | None = None
    end_date: date | None = None


class CollectionSeasonalUpdate(BaseModel):
    """Schema para actualizar si la colección es por temporada"""
    is_seasonal: bool


class CollectionDatesUpdate(BaseModel):
    """Schema para actualizar fechas de temporada"""
    start_date: date | None = None
    end_date: date | None = None


class CollectionStatusRequest(BaseModel):
    """Schema para activar/desactivar una colección"""
    is_active: bool


class CollectionResponse(CollectionBase, TimestampBase):
    """Schema para respuesta de colecciones"""
    id: int
