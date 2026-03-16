from pydantic import BaseModel, Field
from src.schemas.timestamp import TimestampBase
from typing import Optional

class GenreBase(BaseModel):
    """Base schema para géneros"""
    name: str = Field(..., min_length=1, max_length=100)

class GenreCreate(GenreBase):
    """Schema para crear géneros"""
    pass

class GenreResponse(GenreBase, TimestampBase):
    """Schema de respuesta de género"""
    id: int

    
