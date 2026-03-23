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


class CollectionInfo(BaseModel):
    """Schema para información de colección en respuesta"""
    id: int
    name: str
    description: str | None = None
    is_seasonal: bool
    start_date: str | None = None
    end_date: str | None = None
    is_active: bool
    created_at: str
    updated_at: str
    created_by: int
    updated_by: int


class ModsCollectionResponseWithCollection(BaseModel):
    """Schema para respuesta de relación mods-colecciones con objeto completo de colección"""
    id: int
    mod_id: int
    collection: CollectionInfo | None = None
