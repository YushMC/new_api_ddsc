from pydantic import BaseModel, Field
from src.schemas.timestamp import TimestampBase
from typing import Optional

class GenreBase(BaseModel):
    """Base schema para géneros"""
    name: str = Field(..., min_length=1, max_length=100)

class GenreCreate(GenreBase):
    """Schema para crear géneros"""
    pass

class GenreStatusRequest(BaseModel):
    """Schema para activar/desactivar un género"""
    is_active: bool

class GenreResponse(GenreBase, TimestampBase):
    """Schema de respuesta de género"""
    id: int
    identifier: str = Field(..., min_length=1, max_length=100, description="Identificador único en minúsculas")

    
