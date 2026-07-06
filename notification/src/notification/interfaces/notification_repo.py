from typing import Protocol

from notification.db.tables import Notification


class INotificationRepository(Protocol):
    async def create_notification(
        self,
        notification: Notification,
    ) -> Notification: ...
