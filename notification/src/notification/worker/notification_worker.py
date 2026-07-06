import logging
import uuid

from notification.db.repository import NotificationRepository
from notification.services.auth_client import AuthClient
from notification.services.email_sender import EmailSender
from notification.services.template_renderer import TemplateRenderer
from notification.worker.handler import NotificationHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NotificationWorker:
    def __init__(
        self,
        session_factory,
        auth_client: AuthClient,
        email_sender: EmailSender,
        template_renderer: TemplateRenderer,
    ) -> None:
        self.session_factory = session_factory
        self.auth_client = auth_client
        self.email_sender = email_sender
        self.template_renderer = template_renderer

    async def process(self, notification_id: uuid.UUID) -> None:
        logger.debug("Processing notification: %s", notification_id)

        async with self.session_factory() as session:
            repo = NotificationRepository(session=session)
            handler = NotificationHandler(
                repo=repo,
                auth_client=self.auth_client,
                email_sender=self.email_sender,
                template_renderer=self.template_renderer,
            )

            try:
                await handler.handle(notification_id=notification_id)
                await session.commit()

                logger.debug("Notification %s sent", notification_id)

            except Exception:
                await session.rollback()
                logger.debug("Notification %s didn't send", notification_id)
                raise
