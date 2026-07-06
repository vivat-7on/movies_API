import uuid
from dataclasses import dataclass

from notification.db.tables import Notification
from notification.interfaces.notification_repo import INotificationRepository
from notification.interfaces.publisher import IRabbitPublisher
from notification.schemas.events import UserRegisteredEvent


@dataclass(frozen=True)
class NotificationService:
    repo: INotificationRepository
    publisher: IRabbitPublisher

    async def create_user_registered_notification(
        self,
        data: UserRegisteredEvent,
    ) -> uuid.UUID:
        notification = Notification(
            user_id=data.user_id,
            template_code=data.template_code,
            event_type="user_registered",
            payload=data.payload,
        )
        notification = await self.repo.create_notification(
            notification=notification,
        )
        await self.publisher.publish(notification_id=notification.id)

        return notification.id
