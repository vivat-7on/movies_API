import uuid
from dataclasses import dataclass

from notification.db.tables import Notification, NotificationStatus
from notification.interfaces.notification_repo import INotificationRepository
from notification.interfaces.publisher import IRabbitPublisher
from notification.schemas.events import (
    BroadcastEvent,
    NewMovieEvent,
    UserRegisteredEvent,
)


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
            template_code="welcome",
            event_type="user_registered",
            payload=data.payload,
        )
        notification = await self.repo.create_notification(
            notification=notification,
        )
        await self.repo.update_status(
            notification=notification,
            status=NotificationStatus.QUEUED,
        )
        await self.repo.commit()
        await self.publisher.publish(notification_id=notification.id)
        return notification.id

    async def create_broadcast_notifications(
        self,
        data: BroadcastEvent,
    ) -> list[uuid.UUID]:
        notification_ids = []

        for user_id in data.user_ids:
            notification = Notification(
                user_id=user_id,
                template_code=data.template_code,
                event_type="broadcast",
                payload=data.payload,
            )
            notification = await self.repo.create_notification(
                notification=notification,
            )

            await self.repo.update_status(
                notification=notification,
                status=NotificationStatus.QUEUED,
            )
            await self.repo.commit()

            await self.publisher.publish(notification_id=notification.id)
            notification_ids.append(notification.id)

        return notification_ids

    async def create_new_movie_notification(
        self,
        data: NewMovieEvent,
    ) -> list[uuid.UUID]:
        notification_ids = []

        for user_id in data.user_ids:
            notification = Notification(
                user_id=user_id,
                template_code="new_movie",
                event_type="new_movie",
                payload={"movie_title": data.movie_title},
            )
            notification = await self.repo.create_notification(
                notification=notification,
            )
            await self.repo.update_status(
                notification=notification,
                status=NotificationStatus.QUEUED,
            )

            await self.repo.commit()
            await self.publisher.publish(notification_id=notification.id)

            notification_ids.append(notification.id)

        return notification_ids

    async def get_notification_by_id(
        self,
        notification_id: uuid.UUID,
    ) -> Notification | None:
        notification = await self.repo.get_by_id(notification_id)

        if notification is None:
            return None

        return notification
