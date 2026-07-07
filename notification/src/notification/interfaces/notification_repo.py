import uuid
from typing import Protocol

from notification.db.tables import Notification, NotificationStatus


class INotificationRepository(Protocol):
    async def create_notification(
        self,
        notification: Notification,
    ) -> Notification: ...

    async def get_by_id(
        self,
        notification_id: uuid.UUID,
    ) -> Notification | None: ...

    async def update_status(
        self,
        notification: Notification,
        status: NotificationStatus,
    ) -> None: ...

    async def commit(self) -> None: ...
