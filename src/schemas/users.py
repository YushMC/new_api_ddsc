from pydantic import BaseModel, EmailStr, Field
from src.models.enums import UserRolEnum
from typing import Optional

class UserBase(BaseModel):
    """Base schema para usuarios"""
    name: str = Field(..., min_length=1, max_length=100)
    contact: Optional[str] = Field(None, max_length=500)
    logo: Optional[str] = Field(None, max_length=500)
    about_me: Optional[str] = Field(None)
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
    about_me: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schema de respuesta con token"""
    access_token: str
    token_type: str = "bearer"

class BootstrapResponse(BaseModel):
    """Schema de respuesta para bootstrap del primer usuario"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    message: str
    warning: str

    class Config:
        from_attributes = True

class UpdatePasswordRequest(BaseModel):
    """Schema para actualizar contraseña"""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

class UpdateContactRequest(BaseModel):
    """Schema para actualizar contacto"""
    contact: str = Field(..., min_length=1, max_length=500)

class UpdateUserLogoResponse(BaseModel):
    """Schema de respuesta para actualización de logo"""
    id: int
    name: str
    logo: Optional[str]
    message: str

    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    """Schema para actualizar perfil (name y about_me)"""
    name: str = Field(..., min_length=1, max_length=100)
    about_me: Optional[str] = Field(None)

class UpdateRoleRequest(BaseModel):
    """Schema para actualizar el rol de un usuario"""
    role: UserRolEnum

class AdminRestorePasswordRequest(BaseModel):
    """Schema para que un admin restaure la contraseña de un usuario"""
    new_password: str = Field(..., min_length=6)
