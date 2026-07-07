import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification.db.tables import Notification, NotificationStatus
from notification.interfaces.notification_repo import INotificationRepository


class NotificationRepository(INotificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(
        self,
        notification: Notification,
    ) -> Notification:
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def get_by_id(
        self,
        notification_id: uuid.UUID,
    ) -> Notification | None:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        notification: Notification,
        status: NotificationStatus,
    ) -> None:
        notification.status = status
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def mark_as_sent(self, notification: Notification) -> None:
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.datetime.now()
        await self.session.flush()
