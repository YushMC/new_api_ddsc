from sqlalchemy import  Column, Integer, String, Text, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES
from src.models.enums import StatusEnum, DurationEnum, CharacterEnum, ModTypeEnum

from src.models.timestamp import TimestampMixin

__Base = DATABASE_INIT().BASE_TYPE

class Mod(__Base, TimestampMixin): 
    __tablename__ = TABLE_NAMES.MODS

    id= Column(Integer, primary_key=True, index=True, autoincrement="auto")
    name=Column(String(200), nullable=False, index=True)
    description=Column(Text)
    slug=Column(String(200), nullable=False)
    type=Column(Enum(ModTypeEnum), nullable=False, default=ModTypeEnum.TRANSLATION)
    status=Column(Enum(StatusEnum), nullable=False, default=StatusEnum.STABLE)
    duration=Column(Enum(DurationEnum), nullable=False, default=DurationEnum.SHORT)
    character=Column(Enum(CharacterEnum), nullable=False, default=CharacterEnum.MC)
    download_pc=Column(String(500))
    download_android=Column(String(500))
    is_c_rated=Column(Boolean, default=False)
    required_revision = Column(Boolean, default=False)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    rejected_by = Column(Integer)
    rejected_at = Column(DateTime)
    comments = Column(Text, nullable=True)
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime)
    images = relationship(
        "Image",
        back_populates="mod",
        cascade="all, delete"
    )
    mod_genres = relationship("ModGenre", back_populates="mod", cascade="all, delete")
    credits = relationship(
        "Credit",
        cascade="all, delete",
        lazy="joined"
    )

