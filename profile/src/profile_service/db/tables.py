import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

metadata = MetaData(schema="profile")


class BaseTable(DeclarativeBase):
    metadata = metadata


class ProfileTable(BaseTable):
    __tablename__ = "profiles"

    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            name="uq_profiles_user_id",
        ),
        sa.UniqueConstraint(
            "phone",
            name="uq_profiles_phone",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        sa.String(16),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    middle_name: Mapped[str | None] = mapped_column(
        sa.String(100),
        nullable=True,
    )
    last_name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
