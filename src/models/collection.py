from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES
from src.models.timestamp import TimestampMixin

__Base = DATABASE_INIT().BASE_TYPE


class Collection(__Base, TimestampMixin):
    """Modelo para la tabla de colecciones"""
    __tablename__ = TABLE_NAMES.COLECTIONS

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    name= Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)