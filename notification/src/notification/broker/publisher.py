import uuid

import aio_pika

from notification.interfaces.publisher import IRabbitPublisher


class RabbitPublisher(IRabbitPublisher):
    def __init__(
        self,
        exchange: aio_pika.Exchange,
        queue_name: str = "notifications",
    ) -> None:
        self.exchange = exchange
        self.queue_name = queue_name

    async def publish(self, notification_id: uuid.UUID) -> None:
        message = aio_pika.Message(
            body=str(notification_id).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.exchange.publish(
            message,
            routing_key=self.queue_name,
        )
