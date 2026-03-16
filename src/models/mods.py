from sqlalchemy import  Column, Integer, String, Text, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES
from src.models.enums import StatusEnum, DurationEnum, CharacterEnum, ModTypeEnum

from src.models.relations import mods_genres
from src.models.timestamp import TimestampMixin

__Base = DATABASE_INIT().BASE_TYPE

class Mod(__Base, TimestampMixin): 
    __tablename__ = TABLE_NAMES.MODS

    id= Column(Integer, primary_key=True, index=True, autoincrement="auto")
    name=Column(String(200), nullable=False, index=True)
    description=Column(Text)
    slug=Column(String(200), nullable=False)
    type=Column(Enum(ModTypeEnum), nullable=False)
    status=Column(Enum(StatusEnum), nullable=False)
    duration=Column(Enum(DurationEnum), nullable=False)
    character=Column(Enum(CharacterEnum), nullable=False, default=CharacterEnum.MC)
    dowload_pc=Column(String(500))
    dowload_android=Column(String(500))
    required_revision = Column(Boolean, default=False)
    approved_at = Column(DateTime, nullable=True)
    images = relationship(
        "Image",
        back_populates="mod",
        cascade="all, delete"
    )
    genres = relationship("Genre", secondary=mods_genres)

