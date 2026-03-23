from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase


class ModsCollectionBase(BaseModel):
    """Base schema para relación mods-colecciones"""
    mod_id: int
    collection_id: int


class ModsCollectionCreate(ModsCollectionBase):
    """Schema para crear relación mods-colecciones"""
    pass


class ModsCollectionResponse(ModsCollectionBase, TimestampBase):
    """Schema para respuesta de relación mods-colecciones"""
    id: int


class ModsCollectionResponseWithCollectionName(BaseModel):
    """Schema para respuesta de relación mods-colecciones con nombre de colección"""
    id: int
    mod_id: int
    collection_name: str
    is_active: bool
