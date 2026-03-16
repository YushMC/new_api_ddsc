from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES, QUERY_PARAMS
from src.models.enums import ImageTypeEnum
from src.models.timestamp import TimestampMixin

__Base = DATABASE_INIT().BASE_TYPE


class Image(__Base, TimestampMixin):
    __tablename__ = TABLE_NAMES.IMAGENES

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")

    url = Column(String(500), nullable=False)

    type = Column(Enum(ImageTypeEnum), nullable=False)

    mod_id = Column(Integer, ForeignKey(TABLE_NAMES.MODS + QUERY_PARAMS.JOIN_BY_ID))

    mod = relationship("Mods", back_populates=TABLE_NAMES.IMAGENES)

