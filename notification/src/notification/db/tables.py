import datetime
import uuid
from enum import StrEnum

import sqlalchemy as sa
from sqlalchemy import MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata = MetaData(schema="notification")


class BaseTable(DeclarativeBase):
    metadata = metadata


class NotificationStatus(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"


class Notification(BaseTable):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    template_code: Mapped[str] = mapped_column(sa.String, nullable=False)
    event_type: Mapped[str] = mapped_column(sa.String, nullable=False)
    payload: Mapped[dict] = mapped_column(sa.JSON, nullable=False, default=dict)
    status: Mapped[NotificationStatus] = mapped_column(
        sa.String,
        nullable=False,
        index=True,
        default=NotificationStatus.CREATED,
    )
    last_error: Mapped[str | None] = mapped_column(
        sa.String,
        nullable=True,
    )
    attempts: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    sent_at: Mapped[datetime.datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
