from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.orm import declared_attr
from datetime import datetime, UTC
from src.conf.context import get_current_user_id

class TimestampMixin:

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    @declared_attr
    def created_by(cls):
        return Column(Integer, default=lambda: get_current_user_id() or 0)

    @declared_attr
    def updated_by(cls):
        return Column(Integer, default=lambda: get_current_user_id() or 0, onupdate=lambda: get_current_user_id() or 0)

    is_active = Column(Boolean, default=True)