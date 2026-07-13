from profile.db.connection import (
    create_async_engine_from_settings,
    create_session_factory,
    get_postgres_session,
)
from profile.db.settings import PostgresSettings
from profile.repositories.profiles import ProfileRepo
from profile.services.profiles import ProfileService
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

postgres_settings = PostgresSettings()
async_engine = create_async_engine_from_settings(settings=postgres_settings)
session_factory = create_session_factory(async_engine=async_engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_postgres_session(session_factory=session_factory):
        yield session


def create_profile_repo(
    session: AsyncSession = Depends(get_async_session),
) -> ProfileRepo:
    return ProfileRepo(session=session)


def create_profile_service(
    repo: ProfileRepo = Depends(create_profile_repo),
) -> ProfileService:
    return ProfileService(repo=repo)
