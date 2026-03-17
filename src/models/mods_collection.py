from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES, QUERY_PARAMS
from src.models.timestamp import TimestampMixin

__Base = DATABASE_INIT().BASE_TYPE


class ModsCollection(__Base, TimestampMixin):
    """Modelo para la relación entre mods y colecciones (tabla intermedia)"""
    __tablename__ = TABLE_NAMES.MODS_COLECTIONS

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    mod_id = Column(Integer, ForeignKey(TABLE_NAMES.MODS + QUERY_PARAMS.JOIN_BY_ID), nullable=False, index=True)
    collection_id = Column(Integer, ForeignKey(TABLE_NAMES.COLECTIONS + QUERY_PARAMS.JOIN_BY_ID), nullable=False, index=True)

    # Relaciones
    mod = relationship("Mod", backref="mods_collections")
    collection = relationship("Collection", backref="mods_collections")
