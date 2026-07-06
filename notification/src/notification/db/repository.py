from notification.db.tables import Notification
from notification.interfaces.notification_repo import INotificationRepository
from sqlalchemy.ext.asyncio import AsyncSession


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
