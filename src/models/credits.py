from sqlalchemy import Column, Integer, String, Boolean, Enum
from src.models.enums import CreditsTypeEnum
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES

__Base = DATABASE_INIT().BASE_TYPE


class Credit(__Base):

    __tablename__ = TABLE_NAMES.CREDITOS

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False, index=True)

    id_user = Column(Integer)
    id_mod = Column(Integer)

    name = Column(String(100))

    type = Column(Enum(CreditsTypeEnum), nullable=False, default=CreditsTypeEnum.ORIGINAL_CREATOR)

    is_active = Column(Boolean, default=True)