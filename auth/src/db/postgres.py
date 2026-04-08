from datetime import datetime
from typing import Annotated, AsyncGenerator

from sqlalchemy import func
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from ..core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.async_url, echo=True, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime,
    mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    ),
]


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
