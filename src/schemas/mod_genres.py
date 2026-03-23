from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase


class ModGenreBase(BaseModel):
    """Base schema para relación mod-géneros"""
    mod_id: int
    genre_id: int


class ModGenreCreate(ModGenreBase):
    """Schema para crear relación mod-géneros"""
    pass


class ModGenreResponse(ModGenreBase, TimestampBase):
    """Schema para respuesta de relación mod-géneros"""
    id: int


class GenreInfo(BaseModel):
    """Schema para información de género en respuesta"""
    id: int
    name: str
    identifier: str
    is_active: bool


class ModGenreResponseWithGenre(BaseModel):
    """Schema para respuesta de relación mod-géneros con objeto completo de género"""
    id: int
    mod_id: int
    genre: GenreInfo | None = None
