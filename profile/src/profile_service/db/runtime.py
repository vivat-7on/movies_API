from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from profile_service.db.connection import (
    create_async_engine_from_settings,
    create_session_factory,
)
from profile_service.db.settings import get_postgres_settings


@lru_cache
def get_async_engine() -> AsyncEngine:
    settings = get_postgres_settings()

    return create_async_engine_from_settings(settings=settings)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return create_session_factory(
        async_engine=get_async_engine(),
    )
