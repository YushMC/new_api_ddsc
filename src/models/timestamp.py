from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import declared_attr
from datetime import datetime, UTC
from src.conf.context import get_current_user_name

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

    deleted_at = Column(DateTime)
    
    approved_at = Column(DateTime, nullable=True)

    @declared_attr
    def created_by(cls):
        return Column(String(100), default=lambda: get_current_user_name() or "system")

    @declared_attr
    def updated_by(cls):
        return Column(String(100), default=lambda: get_current_user_name() or "system", onupdate=lambda: get_current_user_name() or "system")

    deleted_by = Column(String(100))

    is_active = Column(Boolean, default=True)