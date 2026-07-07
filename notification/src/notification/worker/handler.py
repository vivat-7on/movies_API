import uuid

from notification.core.exceptions import NotificationNotFound
from notification.db.tables import NotificationStatus
from notification.interfaces.notification_repo import INotificationRepository
from notification.services.auth_client import AuthClient
from notification.services.email_sender import EmailSender
from notification.services.template_renderer import TemplateRenderer


class NotificationHandler:
    def __init__(
        self,
        repo: INotificationRepository,
        auth_client: AuthClient,
        email_sender: EmailSender,
        template_renderer: TemplateRenderer,
    ) -> None:
        self.repo = repo
        self.auth_client = auth_client
        self.email_sender = email_sender
        self.template_renderer = template_renderer

    async def handle(self, notification_id: uuid.UUID) -> None:
        notification = await self.repo.get_by_id(
            notification_id=notification_id,
        )

        if notification is None:
            raise NotificationNotFound(
                f"Notification with {notification_id} not found",
            )

        await self.repo.update_status(
            notification=notification,
            status=NotificationStatus.PROCESSING,
        )

        user = await self.auth_client.get_user_by_id(
            user_id=notification.user_id,
        )

        subject, body = await self.template_renderer.render(
            template_code=notification.template_code,
            context={
                "first_name": user.first_name,
                **notification.payload,
            },
        )

        await self.email_sender.send(
            email=user.email,
            subject=subject,
            body=body,
        )

        await self.repo.update_status(
            notification=notification,
            status=NotificationStatus.SENT,
        )
