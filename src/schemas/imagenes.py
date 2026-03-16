from pydantic import BaseModel, Field
from src.models.enums import ImageTypeEnum
from src.schemas.timestamp import TimestampBase
from typing import Optional

class ImageBase(BaseModel):
    """Base schema para imágenes"""
    url: str = Field(..., max_length=500)
    type: ImageTypeEnum

class ImageCreateFormData(BaseModel):
    """Schema para crear imágenes con FormData"""
    mod_id: int
    image_type: ImageTypeEnum

class ImageCreate(ImageBase):
    """Schema para crear imágenes"""
    mod_id: int

class ImageUpdate(BaseModel):
    """Schema para actualizar imágenes"""
    url: Optional[str] = Field(None, max_length=500)
    type: Optional[ImageTypeEnum] = None

class ImageResponse(ImageBase, TimestampBase):
    """Schema de respuesta de imagen"""
    id: int
    mod_id: int

    class Config:
        from_attributes = True

