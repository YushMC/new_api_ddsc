from pydantic import BaseModel, EmailStr, Field
from src.models.enums import UserRolEnum
from typing import Optional

class UserBase(BaseModel):
    """Base schema para usuarios"""
    name: str = Field(..., min_length=1, max_length=100)
    contact: Optional[str] = Field(None, max_length=500)
    logo: Optional[str] = Field(None, max_length=500)
    role: UserRolEnum

class UserCreate(UserBase):
    """Schema para crear usuarios"""
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Schema de respuesta de usuario"""
    id: int
    name: str
    role: UserRolEnum
    logo: Optional[str] = None
    contact: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schema de respuesta con token"""
    access_token: str
    token_type: str = "bearer"
