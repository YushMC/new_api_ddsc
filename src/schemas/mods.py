from datetime import datetime

from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase
from src.models.enums import StatusEnum, DurationEnum, CharacterEnum, ModTypeEnum
from src.schemas.credits import CreditsInfo


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

    deleted_at: datetime | None = None
    approved_at: datetime | None = None

    deleted_by: str | None = None
    approved_by: str | None = None

class ModCommplete(ModBase, TimestampBase):
    id: int
    credits: CreditsInfo | None = None

