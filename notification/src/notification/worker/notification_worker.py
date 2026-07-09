import logging
import uuid

from notification.adapters.auth.auth_client import AuthClient
from notification.adapters.email.email_sender import EmailSender
from notification.adapters.templates.template_renderer import TemplateRenderer
from notification.db.repository import NotificationRepository
from notification.db.tables import Notification
from notification.worker.handler import NotificationHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
MAX_ATTEMPTS = 3


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
            handler = self._create_handler(repo=repo)

            try:  # noqa: WPS229
                await handler.handle(notification_id=notification_id)
                await session.commit()

                logger.debug("Notification %s sent", notification_id)

            except Exception as exc:
                await session.rollback()

                notification = await self._mark_as_failed(
                    notification_id=notification_id,
                    exc=exc,
                )
                logger.exception("Notification %s failed", notification_id)
                if notification is not None and notification.attempts < MAX_ATTEMPTS:
                    raise

    def _create_handler(
        self,
        repo: NotificationRepository,
    ) -> NotificationHandler:
        return NotificationHandler(
            repo=repo,
            auth_client=self.auth_client,
            email_sender=self.email_sender,
            template_renderer=self.template_renderer,
        )

    async def _mark_as_failed(
        self,
        notification_id: uuid.UUID,
        exc: Exception,
    ) -> Notification | None:
        async with self.session_factory() as failed_session:
            failed_repo = NotificationRepository(session=failed_session)
            notification = await failed_repo.get_by_id(
                notification_id=notification_id,
            )

            if notification is None:
                return None

            await failed_repo.mark_as_failed(
                notification=notification,
                error=str(exc),
            )
            await failed_session.commit()
            return notification
