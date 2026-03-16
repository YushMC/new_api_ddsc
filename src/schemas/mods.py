from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase
from src.models.enums import StatusEnum, DurationEnum, CharacterEnum


class ModBase(BaseModel):
    name: str
    description: str | None = None
    slug: str

    status: StatusEnum
    duration: DurationEnum
    character: CharacterEnum = CharacterEnum.MC

    dowload_pc: str | None = None
    dowload_android: str | None = None

    required_revision: bool = False
    aproved_by: str | None = None

class ModCommplete(ModBase, TimestampBase):
    id: int

