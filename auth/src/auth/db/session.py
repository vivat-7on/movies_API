from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from auth.core.config import DBSettings


@lru_cache
def get_engine():
    settings = DBSettings()
    return create_async_engine(settings.async_url)


@lru_cache
def get_sessionmaker():
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = get_sessionmaker()
    async with session_maker() as session:
        yield session
