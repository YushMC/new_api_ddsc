from sqlalchemy import Column, Integer, String, Boolean, Enum
from src.models.enums import UserRolEnum
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES

__Base = DATABASE_INIT().BASE_TYPE


class User(__Base):

    __tablename__ = TABLE_NAMES.USERS

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False, index=True)

    name = Column(String(100), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    role = Column(Enum(UserRolEnum), nullable=False)

    logo= Column(String(500))

    contact=Column(String(500))

    is_active = Column(Boolean, default=True)
