from pydantic import BaseModel
from datetime import datetime


class TimestampBase(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
   

    created_by: str
    updated_by: str
   

    is_active: bool = True

    class Config:
        from_attributes = True