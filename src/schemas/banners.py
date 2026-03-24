from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.enums import BannerTypeEnum


class BannerBase(BaseModel):
    """Base schema para Banner"""
    title: str
    message: str
    style: Optional[str] = "info"
    url: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerCreate(BannerBase):
    """Schema para crear un Banner (manual)"""
    type: BannerTypeEnum = BannerTypeEnum.MANUAL


class BannerCreateAuto(BannerBase):
    """Schema para crear un Banner automático (mod_approved)"""
    type: BannerTypeEnum = BannerTypeEnum.MOD_APPROVED
    id_mod: int


class BannerUpdate(BaseModel):
    """Schema para actualizar un Banner"""
    title: Optional[str] = None
    message: Optional[str] = None
    style: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerResponse(BaseModel):
    """Schema de respuesta para Banner"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    type: BannerTypeEnum
    title: str
    message: str
    id_mod: Optional[int] = None
    created_by: int
    style: Optional[str] = "info"
    url: Optional[str] = None
    is_active: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BannerResponseComplete(BannerResponse):
    """Schema completo con relaciones"""
    user: Optional[dict] = None
    mod: Optional[dict] = None
