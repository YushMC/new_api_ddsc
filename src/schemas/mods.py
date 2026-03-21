from datetime import datetime

from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase
from src.models.enums import StatusEnum, DurationEnum, CharacterEnum, ModTypeEnum
from src.schemas.credits import CreditsInfo
from src.schemas.imagenes import ImageResponse
from src.schemas.generos import GenreResponse


class ModBase(BaseModel):
    name: str
    description: str | None = None
    slug: str | None = None
    type: ModTypeEnum = ModTypeEnum.TRANSLATION

    status: StatusEnum
    duration: DurationEnum
    character: CharacterEnum = CharacterEnum.MC

    dowload_pc: str | None = None
    dowload_android: str | None = None

    required_revision: bool = False

    created_at: datetime | None = None
    deleted_at: datetime | None = None
    approved_at: datetime | None = None
    rejected_at: datetime | None = None

    deleted_by: int | None = None
    approved_by: int | None = None
    rejected_by: int | None = None
    comments: str | None = None

class ModCommplete(ModBase, TimestampBase):
    id: int
    credits: CreditsInfo | None = None
    images: list[ImageResponse] = []
    genres: list[GenreResponse] = []

class ModRejectRequest(BaseModel):
    """Schema para rechazar un mod"""
    comments: str

class ModDeleteRequest(BaseModel):
    """Schema para eliminar un mod"""
    reason: str

class ModGenreAdd(BaseModel):
    """Schema para agregar géneros a un mod"""
    genre_ids: list[int]

