from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from profile_service.db.connection import get_postgres_session
from profile_service.db.runtime import session_factory
from profile_service.repositories.profiles import ProfileRepo
from profile_service.services.profiles import ProfileService


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
