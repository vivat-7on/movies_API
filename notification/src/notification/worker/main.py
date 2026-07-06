import asyncio

import aio_pika
from notification.broker.settings import RabbitSettings
from notification.db.connection import (
    create_async_engine_from_settings,
    create_session_factory,
)
from notification.db.settings import PostgresSettings
from notification.services.auth_client import AuthClient
from notification.services.email_sender import EmailSender
from notification.services.template_renderer import TemplateRenderer
from notification.worker.consumer import RabbitConsumer
from notification.worker.notification_worker import NotificationWorker


async def main():
    rabbit_settings = RabbitSettings()

    connection = await aio_pika.connect_robust(rabbit_settings.dsn)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(
            "notifications",
            durable=True,
        )

        postgres_settings = PostgresSettings()
        async_engine = create_async_engine_from_settings(
            settings=postgres_settings,
        )
        session_factory = create_session_factory(async_engine=async_engine)

        auth_client = AuthClient()
        email_sender = EmailSender()
        template_renderer = TemplateRenderer()

        worker = NotificationWorker(
            session_factory=session_factory,
            auth_client=auth_client,
            email_sender=email_sender,
            template_renderer=template_renderer,
        )

        consumer = RabbitConsumer(
            queue=queue,
            worker=worker,
        )

        await consumer.consume()


if __name__ == "__main__":
    asyncio.run(main())
