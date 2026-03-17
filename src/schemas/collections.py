from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase


class CollectionBase(BaseModel):
    """Base schema para colecciones"""
    name: str
    description: str | None = None


class CollectionCreate(CollectionBase):
    """Schema para crear colecciones"""
    pass


class CollectionUpdate(BaseModel):
    """Schema para actualizar colecciones"""
    name: str | None = None
    description: str | None = None


class CollectionResponse(CollectionBase, TimestampBase):
    """Schema para respuesta de colecciones"""
    id: int
