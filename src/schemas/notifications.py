from pydantic import BaseModel
from src.models.enums import NotificationTypeEnum, NotificationStatusEnum
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    id: int
    id_user: int
    id_mod: int
    type: NotificationTypeEnum
    status: NotificationStatusEnum
    title: str
    message: Optional[str] = None
    action_by: Optional[str] = None
    mod_name: Optional[str] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    id_user: int
    id_mod: int
    type: NotificationTypeEnum
    title: str
    message: Optional[str] = None
    action_by: Optional[str] = None
    mod_name: Optional[str] = None
