import uuid

import aio_pika

from notification.interfaces.publisher import IRabbitPublisher


class RabbitPublisher(IRabbitPublisher):
    def __init__(
        self,
        connection: aio_pika.RobustConnection,
        queue_name: str = "notifications",
    ) -> None:
        self.connection = connection
        self.queue_name = queue_name

    async def publish(self, notification_id: uuid.UUID) -> None:
        async with self.connection.channel() as channel:
            await channel.declare_queue(
                self.queue_name,
                durable=True,
            )

            message = aio_pika.Message(
                body=str(notification_id).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await channel.default_exchange.publish(
                message,
                routing_key=self.queue_name,
            )
