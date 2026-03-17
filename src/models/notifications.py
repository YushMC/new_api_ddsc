from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.conf.database import DATABASE_INIT
from src.conf.all_keys import TABLE_NAMES
from src.models.enums import NotificationTypeEnum, NotificationStatusEnum
from src.models.timestamp import TimestampMixin
from datetime import datetime, UTC

__Base = DATABASE_INIT().BASE_TYPE


class Notification(__Base, TimestampMixin):
    """
    Tabla para notificaciones de mods
    
    Tipos de notificaciones:
    - mod_pending_review: Para EDITORS/OWNERS cuando un mod requiere revisión (UPLOADER creó)
    - mod_approved: Para UPLOADERS cuando su mod fue aprobado
    - mod_rejected: Para UPLOADERS cuando su mod fue rechazado (futuro)
    """
    __tablename__ = TABLE_NAMES.NOTIFICATIONS

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    
    # Relación con usuario receptor
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relación con mod
    id_mod = Column(Integer, ForeignKey("mods.id"), nullable=False, index=True)
    
    # Tipo de notificación
    type = Column(Enum(NotificationTypeEnum), nullable=False, index=True)
    
    # Estado de lectura
    status = Column(Enum(NotificationStatusEnum), nullable=False, default=NotificationStatusEnum.UNREAD, index=True)
    
    # Contenido/mensaje
    title = Column(String(200), nullable=False)
    message = Column(Text)
    
    # Quién realizó la acción (nombre del usuario)
    action_by = Column(String(100))
    
    # Para no borrar datos si se elimina el mod
    mod_name = Column(String(200))
    
    # Timestamps de lectura
    read_at = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)

    mod = relationship("Mod", foreign_keys=[id_mod])
    user = relationship("User", foreign_keys=[id_user])
