from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES, QUERY_PARAMS
from src.models.timestamp import TimestampMixin

__Base = DATABASE_INIT().BASE_TYPE


class ModStatistic(__Base, TimestampMixin):
    """Modelo para la relación entre mods y estadísticas (tabla intermedia)"""
    __tablename__ = TABLE_NAMES.MODS_ESTADISTICAS

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    mod_id = Column(Integer, ForeignKey(TABLE_NAMES.MODS + QUERY_PARAMS.JOIN_BY_ID), nullable=False, index=True)
    download_pc = Column(Integer, default=0)
    download_android = Column(Integer, default=0)
    searchs = Column(Integer, default=0)
    views = Column(Integer, default=0)

    # Relaciones
    mod = relationship("Mod", backref="mod_statistics")