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

    async def mark_as_sent(self, notification: Notification) -> None: ...

    async def mark_as_failed(
        self,
        notification: Notification,
        error: str,
    ) -> None: ...
