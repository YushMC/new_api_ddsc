from pydantic import BaseModel, Field
from src.models.enums import CreditsTypeEnum
from typing import Optional


class CreditBase(BaseModel):
    """Base schema para créditos"""
    name: Optional[str] = Field(None, max_length=100, description="Nombre del crédito (si no está registrado)")
    id_mod: int = Field(..., description="ID del mod")
    id_user: Optional[int] = Field(None, description="ID del usuario (si está registrado)")
    type: CreditsTypeEnum = Field(..., description="Tipo de crédito: original_creator, translator, porter")


class CreditCreate(CreditBase):
    """Schema para crear créditos"""
    pass


class CreditUserInfo(BaseModel):
    """Info del usuario asociado al crédito (similar a UserResponse)"""
    id: Optional[int] = Field(None, description="ID del usuario")
    name: str = Field(..., description="Nombre del usuario o crédito")
    contact: Optional[str] = Field(None, description="Contacto del usuario")
    logo: Optional[str] = Field(None, description="Logo del usuario")

    class Config:
        from_attributes = True


class CreditResponse(BaseModel):
    """Schema de respuesta de crédito"""
    id: int
    id_mod: int
    id_user: Optional[int] = None
    name: Optional[str] = None
    type: CreditsTypeEnum
    is_active: bool

    # Información del usuario si existe
    user: Optional[CreditUserInfo] = Field(None, description="Información del usuario si existe")

    class Config:
        from_attributes = True


class CreditsInfo(BaseModel):
    """
    Información de créditos de un mod, organizados por tipo.
    
    Ejemplo:
    {
        "creators": [
            {
                "id": 1,
                "id_mod": 5,
                "id_user": null,
                "name": "Juan Pérez",
                "type": "original_creator",
                "is_active": true,
                "user": null
            }
        ],
        "translators": [
            {
                "id": 2,
                "id_mod": 5,
                "id_user": 3,
                "name": "Carlos",
                "type": "translator",
                "is_active": true,
                "user": {
                    "id": 3,
                    "name": "Carlos",
                    "contact": "carlos@example.com",
                    "logo": "https://..."
                }
            }
        ],
        "porters": [
            {
                "id": 3,
                "id_mod": 5,
                "id_user": 4,
                "name": "Android Dev",
                "type": "porter",
                "is_active": true,
                "user": {
                    "id": 4,
                    "name": "Android Dev",
                    "contact": null,
                    "logo": null
                }
            }
        ]
    }
    """
    creators: list[CreditResponse] = Field(
        default_factory=list,
        description="Lista de creadores originales"
    )
    translators: list[CreditResponse] = Field(
        default_factory=list,
        description="Lista de traductores"
    )
    porters: list[CreditResponse] = Field(
        default_factory=list,
        description="Lista de porteadores"
    )

    class Config:
        from_attributes = True
