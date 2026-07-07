from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from notification.broker.publisher import RabbitPublisher
from notification.broker.settings import RabbitSettings
from notification.db.connection import (
    create_async_engine_from_settings,
    create_session_factory,
    get_postgres_session,
)
from notification.db.repository import NotificationRepository
from notification.db.settings import PostgresSettings
from notification.services.notification import NotificationService

postgres_settings = PostgresSettings()
async_engine = create_async_engine_from_settings(settings=postgres_settings)
session_factory = create_session_factory(async_engine=async_engine)

rabbit_settings = RabbitSettings()


async def create_rabbit_publisher(request: Request) -> RabbitPublisher:
    return RabbitPublisher(
        exchange=request.app.state.rabbit_channel.default_exchange,
        queue_name="notifications",
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_postgres_session(session_factory=session_factory):
        yield session


def create_notification_repo(
    session: AsyncSession = Depends(get_async_session),
) -> NotificationRepository:
    return NotificationRepository(session=session)


def create_notification_service(
    repo: NotificationRepository = Depends(create_notification_repo),
    publisher: RabbitPublisher = Depends(create_rabbit_publisher),
) -> NotificationService:
    return NotificationService(
        repo=repo,
        publisher=publisher,
    )
