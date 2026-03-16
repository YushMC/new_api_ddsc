from sqlalchemy import Column, Integer, String
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES
from src.models.timestamp import TimestampMixin

__Base = DATABASE_INIT().BASE_TYPE

class Genre(__Base, TimestampMixin):
    __tablename__ = TABLE_NAMES.GENEROS
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    name = Column(String(100), nullable=False)
    identifier = Column(String(100), nullable=False, unique=True, index=True)