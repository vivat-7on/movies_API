import asyncio
import uuid

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from notification.worker.notification_worker import NotificationWorker


class RabbitConsumer:
    def __init__(
        self,
        queue: aio_pika.Queue,
        worker: NotificationWorker,
    ) -> None:
        self.queue = queue
        self.worker = worker

    async def consume(self) -> None:
        await self.queue.consume(self.process_message)
        await asyncio.Future()

    async def process_message(
        self,
        message: AbstractIncomingMessage,
    ) -> None:
        async with message.process():
            notification_id = uuid.UUID(message.body.decode())

            await self.worker.process(notification_id=notification_id)
