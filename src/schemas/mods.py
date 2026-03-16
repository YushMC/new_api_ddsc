from pydantic import BaseModel
from src.schemas.timestamp import TimestampBase
from src.models.enums import StatusEnum, DurationEnum, CharacterEnum, ModTypeEnum


class ModBase(BaseModel):
    name: str
    description: str | None = None
    slug: str
    type: ModTypeEnum

    status: StatusEnum
    duration: DurationEnum
    character: CharacterEnum = CharacterEnum.MC

    dowload_pc: str | None = None
    dowload_android: str | None = None

    required_revision: bool = False

class ModCommplete(ModBase, TimestampBase):
    id: int

