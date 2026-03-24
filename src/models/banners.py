from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES
from src.models.enums import BannerTypeEnum
from src.models.timestamp import TimestampMixin
from datetime import datetime, UTC

__Base = DATABASE_INIT().BASE_TYPE


class Banner(__Base, TimestampMixin):
    """
    Tabla para banners/notificaciones superiores que aparecen en la página web
    
    Tipos de banners:
    - mod_approved: Se crea automáticamente cuando se aprueba un nuevo mod
    - manual: Creado manualmente por EDITOR/OWNER
    """
    __tablename__ = TABLE_NAMES.BANNERS

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    
    # Tipo de banner
    type = Column(Enum(BannerTypeEnum), nullable=False, index=True)
    
    # Título del banner
    title = Column(String(255), nullable=False)
    
    # Mensaje/contenido del banner
    message = Column(Text, nullable=False)
    
    # Relación opcional con mod (si es de tipo mod_approved)
    id_mod = Column(Integer, ForeignKey("mods.id"), nullable=True, index=True)
    
    # Usuario que creó/aprobó el banner
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Color o estilo del banner (ej: success, info, warning, error)
    style = Column(String(50), default="info")
    
    # URL opcional a la que redirige el banner
    url = Column(String(500), nullable=True)
    
    # Si el banner está activo
    is_active = Column(Boolean, default=True, index=True)
    
    # Fecha de inicio de visualización
    start_date = Column(DateTime, nullable=True)
    
    # Fecha de fin de visualización
    end_date = Column(DateTime, nullable=True)

    # Relaciones
    mod = relationship("Mod", foreign_keys=[id_mod])
    user = relationship("User", foreign_keys=[created_by])
