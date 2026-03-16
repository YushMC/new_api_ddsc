from pydantic import BaseModel
from datetime import datetime


class TimestampBase(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    approved_at: datetime | None = None

    created_by: str
    updated_by: str
    deleted_by: str | None = None

    is_active: bool = True

    class Config:
        from_attributes = True